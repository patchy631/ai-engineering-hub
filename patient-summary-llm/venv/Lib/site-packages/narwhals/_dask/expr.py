from __future__ import annotations

import re
import warnings
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal
from typing import Sequence

from narwhals._dask.expr_dt import DaskExprDateTimeNamespace
from narwhals._dask.expr_name import DaskExprNameNamespace
from narwhals._dask.expr_str import DaskExprStringNamespace
from narwhals._dask.utils import add_row_index
from narwhals._dask.utils import maybe_evaluate_expr
from narwhals._dask.utils import narwhals_to_native_dtype
from narwhals._expression_parsing import ExprKind
from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._expression_parsing import is_elementary_expression
from narwhals._pandas_like.utils import native_to_narwhals_dtype
from narwhals.exceptions import ColumnNotFoundError
from narwhals.exceptions import InvalidOperationError
from narwhals.typing import CompliantExpr
from narwhals.utils import Implementation
from narwhals.utils import generate_temporary_column_name
from narwhals.utils import not_implemented

if TYPE_CHECKING:
    from narwhals._expression_parsing import ExprKind

    try:
        import dask.dataframe.dask_expr as dx
    except ModuleNotFoundError:
        import dask_expr as dx

    from typing_extensions import Self

    from narwhals._dask.dataframe import DaskLazyFrame
    from narwhals._dask.namespace import DaskNamespace
    from narwhals.dtypes import DType
    from narwhals.utils import Version


class DaskExpr(CompliantExpr["DaskLazyFrame", "dx.Series"]):  # pyright: ignore[reportInvalidTypeArguments] (#2044)
    _implementation: Implementation = Implementation.DASK

    def __init__(
        self: Self,
        call: Callable[[DaskLazyFrame], Sequence[dx.Series]],
        *,
        depth: int,
        function_name: str,
        evaluate_output_names: Callable[[DaskLazyFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        backend_version: tuple[int, ...],
        version: Version,
        # Kwargs with metadata which we may need in group-by agg
        # (e.g. `ddof` for `std` and `var`).
        call_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._call = call
        self._depth = depth
        self._function_name = function_name
        self._evaluate_output_names = evaluate_output_names
        self._alias_output_names = alias_output_names
        self._backend_version = backend_version
        self._version = version
        self._call_kwargs = call_kwargs or {}

    def __call__(self: Self, df: DaskLazyFrame) -> Sequence[dx.Series]:
        return self._call(df)

    def __narwhals_expr__(self) -> None: ...

    def __narwhals_namespace__(self) -> DaskNamespace:  # pragma: no cover
        # Unused, just for compatibility with PandasLikeExpr
        from narwhals._dask.namespace import DaskNamespace

        return DaskNamespace(backend_version=self._backend_version, version=self._version)

    def broadcast(self, kind: Literal[ExprKind.AGGREGATION, ExprKind.LITERAL]) -> Self:
        def func(df: DaskLazyFrame) -> list[dx.Series]:
            return [result[0] for result in self(df)]

        return self.__class__(
            func,
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
            call_kwargs=self._call_kwargs,
        )

    @classmethod
    def from_column_names(
        cls: type[Self],
        evaluate_column_names: Callable[[DaskLazyFrame], Sequence[str]],
        /,
        *,
        function_name: str,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        def func(df: DaskLazyFrame) -> list[dx.Series]:
            try:
                return [
                    df._native_frame[column_name]
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
            backend_version=backend_version,
            version=version,
        )

    @classmethod
    def from_column_indices(
        cls: type[Self],
        *column_indices: int,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        def func(df: DaskLazyFrame) -> list[dx.Series]:
            return [
                df._native_frame.iloc[:, column_index] for column_index in column_indices
            ]

        return cls(
            func,
            depth=0,
            function_name="nth",
            evaluate_output_names=lambda df: [df.columns[i] for i in column_indices],
            alias_output_names=None,
            backend_version=backend_version,
            version=version,
        )

    def _from_call(
        self: Self,
        # First argument to `call` should be `dx.Series`
        call: Callable[..., dx.Series],
        expr_name: str,
        call_kwargs: dict[str, Any] | None = None,
        **expressifiable_args: Self | Any,
    ) -> Self:
        def func(df: DaskLazyFrame) -> list[dx.Series]:
            native_results: list[dx.Series] = []
            native_series_list = self._call(df)
            other_native_series = {
                key: maybe_evaluate_expr(df, value)
                for key, value in expressifiable_args.items()
            }
            for native_series in native_series_list:
                result_native = call(native_series, **other_native_series)
                native_results.append(result_native)
            return native_results

        return self.__class__(
            func,
            depth=self._depth + 1,
            function_name=f"{self._function_name}->{expr_name}",
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
            call_kwargs=call_kwargs,
        )

    def alias(self: Self, name: str) -> Self:
        def alias_output_names(names: Sequence[str]) -> Sequence[str]:
            if len(names) != 1:
                msg = f"Expected function with single output, found output names: {names}"
                raise ValueError(msg)
            return [name]

        return self.__class__(
            self._call,
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
            call_kwargs=self._call_kwargs,
        )

    def __add__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__add__(other), "__add__", other=other
        )

    def __sub__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__sub__(other), "__sub__", other=other
        )

    def __rsub__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: other - _input, "__rsub__", other=other
        ).alias("literal")

    def __mul__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__mul__(other), "__mul__", other=other
        )

    def __truediv__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__truediv__(other), "__truediv__", other=other
        )

    def __rtruediv__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: other / _input, "__rtruediv__", other=other
        ).alias("literal")

    def __floordiv__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__floordiv__(other), "__floordiv__", other=other
        )

    def __rfloordiv__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: other // _input, "__rfloordiv__", other=other
        ).alias("literal")

    def __pow__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__pow__(other), "__pow__", other=other
        )

    def __rpow__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: other**_input, "__rpow__", other=other
        ).alias("literal")

    def __mod__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__mod__(other), "__mod__", other=other
        )

    def __rmod__(self: Self, other: Any) -> Self:
        return self._from_call(
            lambda _input, other: other % _input, "__rmod__", other=other
        ).alias("literal")

    def __eq__(self: Self, other: DaskExpr) -> Self:  # type: ignore[override]
        return self._from_call(
            lambda _input, other: _input.__eq__(other), "__eq__", other=other
        )

    def __ne__(self: Self, other: DaskExpr) -> Self:  # type: ignore[override]
        return self._from_call(
            lambda _input, other: _input.__ne__(other), "__ne__", other=other
        )

    def __ge__(self: Self, other: DaskExpr | Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__ge__(other), "__ge__", other=other
        )

    def __gt__(self: Self, other: DaskExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__gt__(other), "__gt__", other=other
        )

    def __le__(self: Self, other: DaskExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__le__(other), "__le__", other=other
        )

    def __lt__(self: Self, other: DaskExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__lt__(other), "__lt__", other=other
        )

    def __and__(self: Self, other: DaskExpr | Any) -> Self:
        return self._from_call(
            lambda _input, other: _input.__and__(other), "__and__", other=other
        )

    def __or__(self: Self, other: DaskExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__or__(other), "__or__", other=other
        )

    def __invert__(self: Self) -> Self:
        return self._from_call(lambda _input: _input.__invert__(), "__invert__")

    def mean(self: Self) -> Self:
        return self._from_call(lambda _input: _input.mean().to_series(), "mean")

    def median(self: Self) -> Self:
        from narwhals.exceptions import InvalidOperationError

        def func(s: dx.Series) -> dx.Series:
            dtype = native_to_narwhals_dtype(s.dtype, self._version, Implementation.DASK)
            if not dtype.is_numeric():
                msg = "`median` operation not supported for non-numeric input type."
                raise InvalidOperationError(msg)
            return s.median_approximate().to_series()

        return self._from_call(func, "median")

    def min(self: Self) -> Self:
        return self._from_call(lambda _input: _input.min().to_series(), "min")

    def max(self: Self) -> Self:
        return self._from_call(lambda _input: _input.max().to_series(), "max")

    def std(self: Self, ddof: int) -> Self:
        return self._from_call(
            lambda _input: _input.std(ddof=ddof).to_series(),
            "std",
            call_kwargs={"ddof": ddof},
        )

    def var(self: Self, ddof: int) -> Self:
        return self._from_call(
            lambda _input: _input.var(ddof=ddof).to_series(),
            "var",
            call_kwargs={"ddof": ddof},
        )

    def skew(self: Self) -> Self:
        return self._from_call(lambda _input: _input.skew().to_series(), "skew")

    def shift(self: Self, n: int) -> Self:
        return self._from_call(lambda _input: _input.shift(n), "shift")

    def cum_sum(self: Self, *, reverse: bool) -> Self:
        if reverse:  # pragma: no cover
            # https://github.com/dask/dask/issues/11802
            msg = "`cum_sum(reverse=True)` is not supported with Dask backend"
            raise NotImplementedError(msg)

        return self._from_call(lambda _input: _input.cumsum(), "cum_sum")

    def cum_count(self: Self, *, reverse: bool) -> Self:
        if reverse:  # pragma: no cover
            msg = "`cum_count(reverse=True)` is not supported with Dask backend"
            raise NotImplementedError(msg)

        return self._from_call(
            lambda _input: (~_input.isna()).astype(int).cumsum(), "cum_count"
        )

    def cum_min(self: Self, *, reverse: bool) -> Self:
        if reverse:  # pragma: no cover
            msg = "`cum_min(reverse=True)` is not supported with Dask backend"
            raise NotImplementedError(msg)

        return self._from_call(lambda _input: _input.cummin(), "cum_min")

    def cum_max(self: Self, *, reverse: bool) -> Self:
        if reverse:  # pragma: no cover
            msg = "`cum_max(reverse=True)` is not supported with Dask backend"
            raise NotImplementedError(msg)

        return self._from_call(lambda _input: _input.cummax(), "cum_max")

    def cum_prod(self: Self, *, reverse: bool) -> Self:
        if reverse:  # pragma: no cover
            msg = "`cum_prod(reverse=True)` is not supported with Dask backend"
            raise NotImplementedError(msg)

        return self._from_call(lambda _input: _input.cumprod(), "cum_prod")

    def rolling_sum(
        self: Self, window_size: int, *, min_samples: int, center: bool
    ) -> Self:
        return self._from_call(
            lambda _input: _input.rolling(
                window=window_size, min_periods=min_samples, center=center
            ).sum(),
            "rolling_sum",
        )

    def sum(self: Self) -> Self:
        return self._from_call(lambda _input: _input.sum().to_series(), "sum")

    def count(self: Self) -> Self:
        return self._from_call(lambda _input: _input.count().to_series(), "count")

    def round(self: Self, decimals: int) -> Self:
        return self._from_call(lambda _input: _input.round(decimals), "round")

    def unique(self: Self) -> Self:
        return self._from_call(lambda _input: _input.unique(), "unique")

    def drop_nulls(self: Self) -> Self:
        return self._from_call(lambda _input: _input.dropna(), "drop_nulls")

    def abs(self: Self) -> Self:
        return self._from_call(lambda _input: _input.abs(), "abs")

    def all(self: Self) -> Self:
        return self._from_call(
            lambda _input: _input.all(
                axis=None, skipna=True, split_every=False, out=None
            ).to_series(),
            "all",
        )

    def any(self: Self) -> Self:
        return self._from_call(
            lambda _input: _input.any(axis=0, skipna=True, split_every=False).to_series(),
            "any",
        )

    def fill_null(
        self: Self,
        value: Self | Any | None,
        strategy: Literal["forward", "backward"] | None,
        limit: int | None,
    ) -> DaskExpr:
        def func(_input: dx.Series) -> dx.Series:
            if value is not None:
                res_ser = _input.fillna(value)
            else:
                res_ser = (
                    _input.ffill(limit=limit)
                    if strategy == "forward"
                    else _input.bfill(limit=limit)
                )
            return res_ser

        return self._from_call(func, "fillna")

    def clip(
        self: Self,
        lower_bound: Self | Any | None,
        upper_bound: Self | Any | None,
    ) -> Self:
        return self._from_call(
            lambda _input, lower_bound, upper_bound: _input.clip(
                lower=lower_bound, upper=upper_bound
            ),
            "clip",
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

    def diff(self: Self) -> Self:
        return self._from_call(lambda _input: _input.diff(), "diff")

    def n_unique(self: Self) -> Self:
        return self._from_call(
            lambda _input: _input.nunique(dropna=False).to_series(), "n_unique"
        )

    def is_null(self: Self) -> Self:
        return self._from_call(lambda _input: _input.isna(), "is_null")

    def is_nan(self: Self) -> Self:
        def func(_input: dx.Series) -> dx.Series:
            dtype = native_to_narwhals_dtype(
                _input.dtype, self._version, self._implementation
            )
            if dtype.is_numeric():
                return _input != _input  # pyright: ignore[reportReturnType] # noqa: PLR0124
            msg = f"`.is_nan` only supported for numeric dtypes and not {dtype}, did you mean `.is_null`?"
            raise InvalidOperationError(msg)

        return self._from_call(func, "is_null")

    def len(self: Self) -> Self:
        return self._from_call(lambda _input: _input.size.to_series(), "len")

    def quantile(
        self: Self,
        quantile: float,
        interpolation: Literal["nearest", "higher", "lower", "midpoint", "linear"],
    ) -> Self:
        if interpolation == "linear":

            def func(_input: dx.Series, quantile: float) -> dx.Series:
                if _input.npartitions > 1:
                    msg = "`Expr.quantile` is not supported for Dask backend with multiple partitions."
                    raise NotImplementedError(msg)
                return _input.quantile(
                    q=quantile, method="dask"
                ).to_series()  # pragma: no cover

            return self._from_call(func, "quantile", quantile=quantile)
        else:
            msg = "`higher`, `lower`, `midpoint`, `nearest` - interpolation methods are not supported by Dask. Please use `linear` instead."
            raise NotImplementedError(msg)

    def is_first_distinct(self: Self) -> Self:
        def func(_input: dx.Series) -> dx.Series:
            _name = _input.name
            col_token = generate_temporary_column_name(n_bytes=8, columns=[_name])
            frame = add_row_index(
                _input.to_frame(), col_token, self._backend_version, self._implementation
            )
            first_distinct_index = frame.groupby(_name).agg({col_token: "min"})[col_token]
            return frame[col_token].isin(first_distinct_index)

        return self._from_call(func, "is_first_distinct")

    def is_last_distinct(self: Self) -> Self:
        def func(_input: dx.Series) -> dx.Series:
            _name = _input.name
            col_token = generate_temporary_column_name(n_bytes=8, columns=[_name])
            frame = add_row_index(
                _input.to_frame(), col_token, self._backend_version, self._implementation
            )
            last_distinct_index = frame.groupby(_name).agg({col_token: "max"})[col_token]
            return frame[col_token].isin(last_distinct_index)

        return self._from_call(func, "is_last_distinct")

    def is_unique(self: Self) -> Self:
        def func(_input: dx.Series) -> dx.Series:
            _name = _input.name
            return (
                _input.to_frame()
                .groupby(_name, dropna=False)
                .transform("size", meta=(_name, int))
                == 1
            )

        return self._from_call(func, "is_unique")

    def is_in(self: Self, other: Any) -> Self:
        return self._from_call(lambda _input: _input.isin(other), "is_in")

    def null_count(self: Self) -> Self:
        return self._from_call(
            lambda _input: _input.isna().sum().to_series(), "null_count"
        )

    def over(
        self: Self,
        partition_by: Sequence[str],
        kind: ExprKind,
        order_by: Sequence[str] | None,
    ) -> Self:
        # pandas is a required dependency of dask so it's safe to import this
        from narwhals._pandas_like.group_by import AGGREGATIONS_TO_PANDAS_EQUIVALENT

        if not partition_by:
            assert order_by is not None  # help type checkers  # noqa: S101

            # This is something like `nw.col('a').cum_sum().order_by(key)`
            # which we can always easily support, as it doesn't require grouping.
            def func(df: DaskLazyFrame) -> Sequence[dx.Series]:
                return self(df.sort(*order_by, descending=False, nulls_last=False))
        elif not is_elementary_expression(self):  # pragma: no cover
            msg = (
                "Only elementary expressions are supported for `.over` in dask.\n\n"
                "Please see: "
                "https://narwhals-dev.github.io/narwhals/pandas_like_concepts/improve_group_by_operation/"
            )
            raise NotImplementedError(msg)
        else:
            function_name = re.sub(r"(\w+->)", "", self._function_name)
            try:
                dask_function_name = AGGREGATIONS_TO_PANDAS_EQUIVALENT[function_name]
            except KeyError:
                # window functions are unsupported: https://github.com/dask/dask/issues/11806
                msg = (
                    f"Unsupported function: {function_name} in `over` context.\n\n"
                    f"Supported functions are {', '.join(AGGREGATIONS_TO_PANDAS_EQUIVALENT)}\n"
                )
                raise NotImplementedError(msg) from None

            def func(df: DaskLazyFrame) -> Sequence[dx.Series]:
                output_names, aliases = evaluate_output_names_and_aliases(self, df, [])

                with warnings.catch_warnings():
                    # https://github.com/dask/dask/issues/11804
                    warnings.filterwarnings(
                        "ignore",
                        message=".*`meta` is not specified",
                        category=UserWarning,
                    )
                    res_native = df._native_frame.groupby(partition_by)[
                        list(output_names)
                    ].transform(dask_function_name, **self._call_kwargs)
                result_frame = df._from_native_frame(
                    res_native.rename(columns=dict(zip(output_names, aliases)))
                )._native_frame
                return [result_frame[name] for name in aliases]

        return self.__class__(
            func,
            depth=self._depth + 1,
            function_name=self._function_name + "->over",
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
        )

    def cast(self: Self, dtype: DType | type[DType]) -> Self:
        def func(_input: dx.Series) -> dx.Series:
            native_dtype = narwhals_to_native_dtype(dtype, self._version)
            return _input.astype(native_dtype)

        return self._from_call(func, "cast")

    def is_finite(self: Self) -> Self:
        import dask.array as da

        return self._from_call(da.isfinite, "is_finite")

    @property
    def str(self: Self) -> DaskExprStringNamespace:
        return DaskExprStringNamespace(self)

    @property
    def dt(self: Self) -> DaskExprDateTimeNamespace:
        return DaskExprDateTimeNamespace(self)

    @property
    def name(self: Self) -> DaskExprNameNamespace:
        return DaskExprNameNamespace(self)

    arg_min = not_implemented()
    arg_max = not_implemented()
    arg_true = not_implemented()
    head = not_implemented()
    tail = not_implemented()
    mode = not_implemented()
    sort = not_implemented()
    rank = not_implemented()
    sample = not_implemented()
    map_batches = not_implemented()
    ewm_mean = not_implemented()
    rolling_mean = not_implemented()
    rolling_var = not_implemented()
    rolling_std = not_implemented()
    gather_every = not_implemented()
    replace_strict = not_implemented()

    cat = not_implemented()  # pyright: ignore[reportAssignmentType]
    list = not_implemented()  # pyright: ignore[reportAssignmentType]
    struct = not_implemented()  # pyright: ignore[reportAssignmentType]
