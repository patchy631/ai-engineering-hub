from __future__ import annotations

import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal
from typing import Mapping
from typing import Sequence

from narwhals._expression_parsing import ExprKind
from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._expression_parsing import is_elementary_expression
from narwhals._expression_parsing import reuse_series_implementation
from narwhals._pandas_like.expr_cat import PandasLikeExprCatNamespace
from narwhals._pandas_like.expr_dt import PandasLikeExprDateTimeNamespace
from narwhals._pandas_like.expr_list import PandasLikeExprListNamespace
from narwhals._pandas_like.expr_name import PandasLikeExprNameNamespace
from narwhals._pandas_like.expr_str import PandasLikeExprStringNamespace
from narwhals._pandas_like.expr_struct import PandasLikeExprStructNamespace
from narwhals._pandas_like.group_by import AGGREGATIONS_TO_PANDAS_EQUIVALENT
from narwhals._pandas_like.series import PandasLikeSeries
from narwhals.dependencies import get_numpy
from narwhals.dependencies import is_numpy_array
from narwhals.exceptions import ColumnNotFoundError
from narwhals.typing import CompliantExpr
from narwhals.utils import generate_temporary_column_name

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.namespace import PandasLikeNamespace
    from narwhals.dtypes import DType
    from narwhals.utils import Implementation
    from narwhals.utils import Version

WINDOW_FUNCTIONS_TO_PANDAS_EQUIVALENT = {
    "cum_sum": "cumsum",
    "cum_min": "cummin",
    "cum_max": "cummax",
    "cum_prod": "cumprod",
    # Pandas cumcount starts counting from 0 while Polars starts from 1
    # Pandas cumcount counts nulls while Polars does not
    # So, instead of using "cumcount" we use "cumsum" on notna() to get the same result
    "cum_count": "cumsum",
    "rolling_sum": "sum",
    "shift": "shift",
    "rank": "rank",
    "diff": "diff",
}


def window_kwargs_to_pandas_equivalent(
    function_name: str, kwargs: dict[str, object]
) -> dict[str, object]:
    if function_name == "shift":
        pandas_kwargs: dict[str, object] = {"periods": kwargs["n"]}
    elif function_name == "rank":
        _method = kwargs["method"]
        pandas_kwargs = {
            "method": "first" if _method == "ordinal" else _method,
            "ascending": not kwargs["descending"],
            "na_option": "keep",
            "pct": False,
        }
    elif function_name.startswith("cum_"):  # Cumulative operation
        pandas_kwargs = {"skipna": True}
    elif function_name.startswith("rolling_"):  # Rolling operation
        pandas_kwargs = {
            "min_periods": kwargs["min_samples"],
            "window": kwargs["window_size"],
            "center": kwargs["center"],
        }
    else:  # e.g. std, var
        pandas_kwargs = kwargs
    return pandas_kwargs


class PandasLikeExpr(CompliantExpr["PandasLikeDataFrame", PandasLikeSeries]):
    def __init__(
        self: Self,
        call: Callable[[PandasLikeDataFrame], Sequence[PandasLikeSeries]],
        *,
        depth: int,
        function_name: str,
        evaluate_output_names: Callable[[PandasLikeDataFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        implementation: Implementation,
        backend_version: tuple[int, ...],
        version: Version,
        call_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._call = call
        self._depth = depth
        self._function_name = function_name
        self._evaluate_output_names = evaluate_output_names
        self._alias_output_names = alias_output_names
        self._implementation = implementation
        self._backend_version = backend_version
        self._version = version
        self._call_kwargs = call_kwargs or {}

    def __call__(self: Self, df: PandasLikeDataFrame) -> Sequence[PandasLikeSeries]:
        return self._call(df)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"PandasLikeExpr(depth={self._depth}, function_name={self._function_name}, )"
        )

    def __narwhals_namespace__(self: Self) -> PandasLikeNamespace:
        from narwhals._pandas_like.namespace import PandasLikeNamespace

        return PandasLikeNamespace(
            self._implementation, self._backend_version, version=self._version
        )

    def __narwhals_expr__(self) -> None: ...

    def broadcast(self, kind: Literal[ExprKind.AGGREGATION, ExprKind.LITERAL]) -> Self:
        # Make the resulting PandasLikeSeries with `_broadcast=True`. Then,
        # when extracting native objects, `align_and_extract_native` will
        # know what to do.
        def func(df: PandasLikeDataFrame) -> list[PandasLikeSeries]:
            results = []
            for result in self(df):
                result._broadcast = True
                results.append(result)
            return results

        return self.__class__(
            func,
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
            implementation=self._implementation,
            call_kwargs=self._call_kwargs,
        )

    @classmethod
    def from_column_names(
        cls: type[Self],
        evaluate_column_names: Callable[[PandasLikeDataFrame], Sequence[str]],
        /,
        *,
        function_name: str,
        implementation: Implementation,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        def func(df: PandasLikeDataFrame) -> list[PandasLikeSeries]:
            try:
                return [
                    PandasLikeSeries(
                        df._native_frame[column_name],
                        implementation=df._implementation,
                        backend_version=df._backend_version,
                        version=df._version,
                    )
                    for column_name in evaluate_column_names(df)
                ]
            except KeyError as e:
                missing_columns = [
                    x for x in evaluate_column_names(df) if x not in df.columns
                ]
                raise ColumnNotFoundError.from_missing_and_available_column_names(
                    missing_columns=missing_columns,
                    available_columns=df.columns,
                ) from e

        return cls(
            func,
            depth=0,
            function_name=function_name,
            evaluate_output_names=evaluate_column_names,
            alias_output_names=None,
            implementation=implementation,
            backend_version=backend_version,
            version=version,
        )

    @classmethod
    def from_column_indices(
        cls: type[Self],
        *column_indices: int,
        implementation: Implementation,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        def func(df: PandasLikeDataFrame) -> list[PandasLikeSeries]:
            return [
                PandasLikeSeries(
                    df._native_frame.iloc[:, column_index],
                    implementation=df._implementation,
                    backend_version=df._backend_version,
                    version=df._version,
                )
                for column_index in column_indices
            ]

        return cls(
            func,
            depth=0,
            function_name="nth",
            evaluate_output_names=lambda df: [df.columns[i] for i in column_indices],
            alias_output_names=None,
            implementation=implementation,
            backend_version=backend_version,
            version=version,
        )

    def cast(self: Self, dtype: DType | type[DType]) -> Self:
        return reuse_series_implementation(self, "cast", dtype=dtype)

    def __eq__(self: Self, other: PandasLikeExpr | Any) -> Self:  # type: ignore[override]
        return reuse_series_implementation(self, "__eq__", other=other)

    def __ne__(self: Self, other: PandasLikeExpr | Any) -> Self:  # type: ignore[override]
        return reuse_series_implementation(self, "__ne__", other=other)

    def __ge__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__ge__", other=other)

    def __gt__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__gt__", other=other)

    def __le__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__le__", other=other)

    def __lt__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__lt__", other=other)

    def __and__(self: Self, other: PandasLikeExpr | bool | Any) -> Self:
        return reuse_series_implementation(self, "__and__", other=other)

    def __or__(self: Self, other: PandasLikeExpr | bool | Any) -> Self:
        return reuse_series_implementation(self, "__or__", other=other)

    def __add__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__add__", other=other)

    def __sub__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__sub__", other=other)

    def __rsub__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self.alias("literal"), "__rsub__", other=other)

    def __mul__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__mul__", other=other)

    def __truediv__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__truediv__", other=other)

    def __rtruediv__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(
            self.alias("literal"), "__rtruediv__", other=other
        )

    def __floordiv__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__floordiv__", other=other)

    def __rfloordiv__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(
            self.alias("literal"), "__rfloordiv__", other=other
        )

    def __pow__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__pow__", other=other)

    def __rpow__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self.alias("literal"), "__rpow__", other=other)

    def __mod__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self, "__mod__", other=other)

    def __rmod__(self: Self, other: PandasLikeExpr | Any) -> Self:
        return reuse_series_implementation(self.alias("literal"), "__rmod__", other=other)

    # Unary
    def __invert__(self: Self) -> Self:
        return reuse_series_implementation(self, "__invert__")

    # Reductions
    def null_count(self: Self) -> Self:
        return reuse_series_implementation(self, "null_count", returns_scalar=True)

    def n_unique(self: Self) -> Self:
        return reuse_series_implementation(self, "n_unique", returns_scalar=True)

    def sum(self: Self) -> Self:
        return reuse_series_implementation(self, "sum", returns_scalar=True)

    def count(self: Self) -> Self:
        return reuse_series_implementation(self, "count", returns_scalar=True)

    def mean(self: Self) -> Self:
        return reuse_series_implementation(self, "mean", returns_scalar=True)

    def median(self: Self) -> Self:
        return reuse_series_implementation(self, "median", returns_scalar=True)

    def std(self: Self, *, ddof: int) -> Self:
        return reuse_series_implementation(
            self, "std", returns_scalar=True, call_kwargs={"ddof": ddof}
        )

    def var(self: Self, *, ddof: int) -> Self:
        return reuse_series_implementation(
            self, "var", returns_scalar=True, call_kwargs={"ddof": ddof}
        )

    def skew(self: Self) -> Self:
        return reuse_series_implementation(self, "skew", returns_scalar=True)

    def any(self: Self) -> Self:
        return reuse_series_implementation(self, "any", returns_scalar=True)

    def all(self: Self) -> Self:
        return reuse_series_implementation(self, "all", returns_scalar=True)

    def max(self: Self) -> Self:
        return reuse_series_implementation(self, "max", returns_scalar=True)

    def min(self: Self) -> Self:
        return reuse_series_implementation(self, "min", returns_scalar=True)

    def arg_min(self: Self) -> Self:
        return reuse_series_implementation(self, "arg_min", returns_scalar=True)

    def arg_max(self: Self) -> Self:
        return reuse_series_implementation(self, "arg_max", returns_scalar=True)

    # Other

    def clip(self: Self, lower_bound: Any, upper_bound: Any) -> Self:
        return reuse_series_implementation(
            self, "clip", lower_bound=lower_bound, upper_bound=upper_bound
        )

    def is_null(self: Self) -> Self:
        return reuse_series_implementation(self, "is_null")

    def is_nan(self: Self) -> Self:
        return reuse_series_implementation(self, "is_nan")

    def fill_null(
        self: Self,
        value: Self | Any | None,
        strategy: Literal["forward", "backward"] | None,
        limit: int | None,
    ) -> Self:
        return reuse_series_implementation(
            self, "fill_null", value=value, strategy=strategy, limit=limit
        )

    def is_in(self: Self, other: Any) -> Self:
        return reuse_series_implementation(self, "is_in", other=other)

    def arg_true(self: Self) -> Self:
        return reuse_series_implementation(self, "arg_true")

    def ewm_mean(
        self: Self,
        *,
        com: float | None,
        span: float | None,
        half_life: float | None,
        alpha: float | None,
        adjust: bool,
        min_samples: int,
        ignore_nulls: bool,
    ) -> Self:
        return reuse_series_implementation(
            self,
            "ewm_mean",
            com=com,
            span=span,
            half_life=half_life,
            alpha=alpha,
            adjust=adjust,
            min_samples=min_samples,
            ignore_nulls=ignore_nulls,
        )

    def filter(self: Self, *predicates: PandasLikeExpr) -> Self:
        plx = self.__narwhals_namespace__()
        predicate = plx.all_horizontal(*predicates)
        return reuse_series_implementation(self, "filter", predicate=predicate)

    def drop_nulls(self: Self) -> Self:
        return reuse_series_implementation(self, "drop_nulls")

    def replace_strict(
        self: Self,
        old: Sequence[Any] | Mapping[Any, Any],
        new: Sequence[Any],
        *,
        return_dtype: DType | type[DType] | None,
    ) -> Self:
        return reuse_series_implementation(
            self, "replace_strict", old=old, new=new, return_dtype=return_dtype
        )

    def sort(self: Self, *, descending: bool, nulls_last: bool) -> Self:
        return reuse_series_implementation(
            self, "sort", descending=descending, nulls_last=nulls_last
        )

    def abs(self: Self) -> Self:
        return reuse_series_implementation(self, "abs")

    def cum_sum(self: Self, *, reverse: bool) -> Self:
        return reuse_series_implementation(
            self, "cum_sum", call_kwargs={"reverse": reverse}
        )

    def unique(self: Self) -> Self:
        return reuse_series_implementation(self, "unique", maintain_order=False)

    def diff(self: Self) -> Self:
        return reuse_series_implementation(self, "diff")

    def shift(self: Self, n: int) -> Self:
        return reuse_series_implementation(self, "shift", call_kwargs={"n": n})

    def sample(
        self: Self,
        n: int | None,
        *,
        fraction: float | None,
        with_replacement: bool,
        seed: int | None,
    ) -> Self:
        return reuse_series_implementation(
            self,
            "sample",
            n=n,
            fraction=fraction,
            with_replacement=with_replacement,
            seed=seed,
        )

    def alias(self: Self, name: str) -> Self:
        def alias_output_names(names: Sequence[str]) -> Sequence[str]:
            if len(names) != 1:
                msg = f"Expected function with single output, found output names: {names}"
                raise ValueError(msg)
            return [name]

        # Define this one manually, so that we can
        # override `output_names` and not increase depth
        return self.__class__(
            lambda df: [series.alias(name) for series in self._call(df)],
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=alias_output_names,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
            call_kwargs=self._call_kwargs,
        )

    def over(
        self: Self,
        partition_by: Sequence[str],
        kind: ExprKind,
        order_by: Sequence[str] | None,
    ) -> Self:
        if not partition_by:
            # e.g. `nw.col('a').cum_sum().order_by(key)`
            # We can always easily support this as it doesn't require grouping.
            assert order_by is not None  # noqa: S101  # help type-check

            def func(df: PandasLikeDataFrame) -> Sequence[PandasLikeSeries]:
                token = generate_temporary_column_name(8, df.columns)
                df = df.with_row_index(token).sort(
                    *order_by, descending=False, nulls_last=False
                )
                results = self(df)
                sorting_indices = df[token]
                for s in results:
                    s._scatter_in_place(sorting_indices, s)
                return results
        elif not is_elementary_expression(self):
            msg = (
                "Only elementary expressions are supported for `.over` in pandas-like backends.\n\n"
                "Please see: "
                "https://narwhals-dev.github.io/narwhals/pandas_like_concepts/improve_group_by_operation/"
            )
            raise NotImplementedError(msg)
        else:
            function_name: str = re.sub(r"(\w+->)", "", self._function_name)
            pandas_function_name = WINDOW_FUNCTIONS_TO_PANDAS_EQUIVALENT.get(
                function_name,
                AGGREGATIONS_TO_PANDAS_EQUIVALENT.get(function_name),
            )
            if pandas_function_name is None:
                msg = (
                    f"Unsupported function: {function_name} in `over` context.\n\n"
                    f"Supported functions are {', '.join(WINDOW_FUNCTIONS_TO_PANDAS_EQUIVALENT)}\n"
                    f"and {', '.join(AGGREGATIONS_TO_PANDAS_EQUIVALENT)}."
                )
                raise NotImplementedError(msg)
            pandas_kwargs = window_kwargs_to_pandas_equivalent(
                function_name, self._call_kwargs
            )

            def func(df: PandasLikeDataFrame) -> Sequence[PandasLikeSeries]:
                output_names, aliases = evaluate_output_names_and_aliases(self, df, [])
                if function_name == "cum_count":
                    plx = self.__narwhals_namespace__()
                    df = df.with_columns(~plx.col(*output_names).is_null())

                if function_name.startswith("cum_"):
                    reverse = self._call_kwargs["reverse"]
                else:
                    assert "reverse" not in self._call_kwargs  # noqa: S101
                    reverse = False

                if order_by:
                    columns = list(set(partition_by).union(output_names).union(order_by))
                    token = generate_temporary_column_name(8, columns)
                    df = (
                        df[columns]
                        .with_row_index(token)
                        .sort(*order_by, descending=reverse, nulls_last=reverse)
                    )
                    sorting_indices = df[token]
                elif reverse:
                    columns = list(set(partition_by).union(output_names))
                    df = df[columns][::-1]
                if function_name.startswith("rolling"):
                    rolling = df._native_frame.groupby(partition_by)[
                        list(output_names)
                    ].rolling(**pandas_kwargs)
                    assert pandas_function_name is not None  # help mypy  # noqa: S101
                    res_native = getattr(rolling, pandas_function_name)()
                else:
                    res_native = df._native_frame.groupby(partition_by)[
                        list(output_names)
                    ].transform(pandas_function_name, **pandas_kwargs)
                result_frame = df._from_native_frame(res_native).rename(
                    dict(zip(output_names, aliases))
                )
                results = [result_frame[name] for name in aliases]
                if order_by:
                    for s in results:
                        s._scatter_in_place(sorting_indices, s)
                    return results
                if reverse:
                    return [s[::-1] for s in results]
                return results

        return self.__class__(
            func,
            depth=self._depth + 1,
            function_name=self._function_name + "->over",
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )

    def is_unique(self: Self) -> Self:
        return reuse_series_implementation(self, "is_unique")

    def is_first_distinct(self: Self) -> Self:
        return reuse_series_implementation(self, "is_first_distinct")

    def is_last_distinct(self: Self) -> Self:
        return reuse_series_implementation(self, "is_last_distinct")

    def quantile(
        self: Self,
        quantile: float,
        interpolation: Literal["nearest", "higher", "lower", "midpoint", "linear"],
    ) -> Self:
        return reuse_series_implementation(
            self,
            "quantile",
            quantile=quantile,
            interpolation=interpolation,
            returns_scalar=True,
        )

    def head(self: Self, n: int) -> Self:
        return reuse_series_implementation(self, "head", n=n)

    def tail(self: Self, n: int) -> Self:
        return reuse_series_implementation(self, "tail", n=n)

    def round(self: Self, decimals: int) -> Self:
        return reuse_series_implementation(self, "round", decimals=decimals)

    def len(self: Self) -> Self:
        return reuse_series_implementation(self, "len", returns_scalar=True)

    def gather_every(self: Self, n: int, offset: int) -> Self:
        return reuse_series_implementation(self, "gather_every", n=n, offset=offset)

    def mode(self: Self) -> Self:
        return reuse_series_implementation(self, "mode")

    def map_batches(
        self: Self,
        function: Callable[[Any], Any],
        return_dtype: DType | type[DType] | None,
    ) -> Self:
        def func(df: PandasLikeDataFrame) -> list[PandasLikeSeries]:
            input_series_list = self._call(df)
            output_names = [input_series.name for input_series in input_series_list]
            result = [function(series) for series in input_series_list]
            if is_numpy_array(result[0]) or (
                (np := get_numpy()) is not None and np.isscalar(result[0])
            ):
                result = [
                    df.__narwhals_namespace__()
                    ._create_compliant_series(array)
                    .alias(output_name)
                    for array, output_name in zip(result, output_names)
                ]
            if return_dtype is not None:
                result = [series.cast(return_dtype) for series in result]
            return result

        return self.__class__(
            func,
            depth=self._depth + 1,
            function_name=self._function_name + "->map_batches",
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )

    def is_finite(self: Self) -> Self:
        return reuse_series_implementation(self, "is_finite")

    def cum_count(self: Self, *, reverse: bool) -> Self:
        return reuse_series_implementation(
            self, "cum_count", call_kwargs={"reverse": reverse}
        )

    def cum_min(self: Self, *, reverse: bool) -> Self:
        return reuse_series_implementation(
            self, "cum_min", call_kwargs={"reverse": reverse}
        )

    def cum_max(self: Self, *, reverse: bool) -> Self:
        return reuse_series_implementation(
            self, "cum_max", call_kwargs={"reverse": reverse}
        )

    def cum_prod(self: Self, *, reverse: bool) -> Self:
        return reuse_series_implementation(
            self, "cum_prod", call_kwargs={"reverse": reverse}
        )

    def rolling_sum(
        self: Self, window_size: int, *, min_samples: int, center: bool
    ) -> Self:
        return reuse_series_implementation(
            self,
            "rolling_sum",
            call_kwargs={
                "window_size": window_size,
                "min_samples": min_samples,
                "center": center,
            },
        )

    def rolling_mean(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self:
        return reuse_series_implementation(
            self,
            "rolling_mean",
            window_size=window_size,
            min_samples=min_samples,
            center=center,
        )

    def rolling_var(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        return reuse_series_implementation(
            self,
            "rolling_var",
            window_size=window_size,
            min_samples=min_samples,
            center=center,
            ddof=ddof,
        )

    def rolling_std(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        return reuse_series_implementation(
            self,
            "rolling_std",
            window_size=window_size,
            min_samples=min_samples,
            center=center,
            ddof=ddof,
        )

    def rank(
        self: Self,
        method: Literal["average", "min", "max", "dense", "ordinal"],
        *,
        descending: bool,
    ) -> Self:
        return reuse_series_implementation(
            self, "rank", call_kwargs={"method": method, "descending": descending}
        )

    @property
    def str(self: Self) -> PandasLikeExprStringNamespace:
        return PandasLikeExprStringNamespace(self)

    @property
    def dt(self: Self) -> PandasLikeExprDateTimeNamespace:
        return PandasLikeExprDateTimeNamespace(self)

    @property
    def cat(self: Self) -> PandasLikeExprCatNamespace:
        return PandasLikeExprCatNamespace(self)

    @property
    def name(self: Self) -> PandasLikeExprNameNamespace:
        return PandasLikeExprNameNamespace(self)

    @property
    def list(self: Self) -> PandasLikeExprListNamespace:
        return PandasLikeExprListNamespace(self)

    @property
    def struct(self: Self) -> PandasLikeExprStructNamespace:
        return PandasLikeExprStructNamespace(self)
