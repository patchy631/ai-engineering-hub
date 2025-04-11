from __future__ import annotations

import operator
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal
from typing import Sequence
from typing import cast

from duckdb import CaseExpression
from duckdb import CoalesceOperator
from duckdb import ColumnExpression
from duckdb import FunctionExpression
from duckdb.typing import DuckDBPyType

from narwhals._duckdb.expr_dt import DuckDBExprDateTimeNamespace
from narwhals._duckdb.expr_list import DuckDBExprListNamespace
from narwhals._duckdb.expr_name import DuckDBExprNameNamespace
from narwhals._duckdb.expr_str import DuckDBExprStringNamespace
from narwhals._duckdb.expr_struct import DuckDBExprStructNamespace
from narwhals._duckdb.utils import lit
from narwhals._duckdb.utils import maybe_evaluate_expr
from narwhals._duckdb.utils import narwhals_to_native_dtype
from narwhals._expression_parsing import ExprKind
from narwhals.typing import CompliantExpr
from narwhals.utils import Implementation
from narwhals.utils import not_implemented

if TYPE_CHECKING:
    import duckdb
    from typing_extensions import Self

    from narwhals._duckdb.dataframe import DuckDBLazyFrame
    from narwhals._duckdb.namespace import DuckDBNamespace
    from narwhals.dtypes import DType
    from narwhals.utils import Version


class DuckDBExpr(CompliantExpr["DuckDBLazyFrame", "duckdb.Expression"]):  # type: ignore[type-var]
    _implementation = Implementation.DUCKDB
    _depth = 0  # Unused, just for compatibility with CompliantExpr

    def __init__(
        self: Self,
        call: Callable[[DuckDBLazyFrame], Sequence[duckdb.Expression]],
        *,
        function_name: str,
        evaluate_output_names: Callable[[DuckDBLazyFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._call = call
        self._function_name = function_name
        self._evaluate_output_names = evaluate_output_names
        self._alias_output_names = alias_output_names
        self._backend_version = backend_version
        self._version = version

    def __call__(self: Self, df: DuckDBLazyFrame) -> Sequence[duckdb.Expression]:
        return self._call(df)

    def __narwhals_expr__(self) -> None: ...

    def __narwhals_namespace__(self) -> DuckDBNamespace:  # pragma: no cover
        # Unused, just for compatibility with PandasLikeExpr
        from narwhals._duckdb.namespace import DuckDBNamespace

        return DuckDBNamespace(
            backend_version=self._backend_version, version=self._version
        )

    def broadcast(self, kind: Literal[ExprKind.AGGREGATION, ExprKind.LITERAL]) -> Self:
        if kind is ExprKind.AGGREGATION:
            msg = "Broadcasting aggregations is not yet supported for DuckDB."
            raise NotImplementedError(msg)
        # For literals, DuckDB does its own broadcasting.
        return self

    @classmethod
    def from_column_names(
        cls: type[Self],
        evaluate_column_names: Callable[[DuckDBLazyFrame], Sequence[str]],
        /,
        *,
        function_name: str,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            return [ColumnExpression(col_name) for col_name in evaluate_column_names(df)]

        return cls(
            func,
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
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            columns = df.columns

            return [ColumnExpression(columns[i]) for i in column_indices]

        return cls(
            func,
            function_name="nth",
            evaluate_output_names=lambda df: [df.columns[i] for i in column_indices],
            alias_output_names=None,
            backend_version=backend_version,
            version=version,
        )

    def _from_call(
        self: Self,
        call: Callable[..., duckdb.Expression],
        expr_name: str,
        **expressifiable_args: Self | Any,
    ) -> Self:
        """Create expression from callable.

        Arguments:
            call: Callable from compliant DataFrame to native Expression
            expr_name: Expression name
            expressifiable_args: arguments pass to expression which should be parsed
                as expressions (e.g. in `nw.col('a').is_between('b', 'c')`)
        """

        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            native_series_list = self._call(df)
            other_native_series = {
                key: maybe_evaluate_expr(df, value)
                for key, value in expressifiable_args.items()
            }
            return [
                call(native_series, **other_native_series)
                for native_series in native_series_list
            ]

        return self.__class__(
            func,
            function_name=f"{self._function_name}->{expr_name}",
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
        )

    def __and__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input & other,
            "__and__",
            other=other,
        )

    def __or__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input | other,
            "__or__",
            other=other,
        )

    def __add__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input + other,
            "__add__",
            other=other,
        )

    def __truediv__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input / other,
            "__truediv__",
            other=other,
        )

    def __rtruediv__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: other.__truediv__(_input), "__rtruediv__", other=other
        ).alias("literal")

    def __floordiv__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__floordiv__(other),
            "__floordiv__",
            other=other,
        )

    def __rfloordiv__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: other.__floordiv__(_input), "__rfloordiv__", other=other
        ).alias("literal")

    def __mod__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input.__mod__(other),
            "__mod__",
            other=other,
        )

    def __rmod__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: other.__mod__(_input), "__rmod__", other=other
        ).alias("literal")

    def __sub__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input - other,
            "__sub__",
            other=other,
        )

    def __rsub__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: other.__sub__(_input), "__rsub__", other=other
        ).alias("literal")

    def __mul__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input * other,
            "__mul__",
            other=other,
        )

    def __pow__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input**other,
            "__pow__",
            other=other,
        )

    def __rpow__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: other.__pow__(_input), "__rpow__", other=other
        ).alias("literal")

    def __lt__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input < other,
            "__lt__",
            other=other,
        )

    def __gt__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input > other,
            "__gt__",
            other=other,
        )

    def __le__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input <= other,
            "__le__",
            other=other,
        )

    def __ge__(self: Self, other: DuckDBExpr) -> Self:
        return self._from_call(
            lambda _input, other: _input >= other,
            "__ge__",
            other=other,
        )

    def __eq__(self: Self, other: DuckDBExpr) -> Self:  # type: ignore[override]
        return self._from_call(
            lambda _input, other: _input == other,
            "__eq__",
            other=other,
        )

    def __ne__(self: Self, other: DuckDBExpr) -> Self:  # type: ignore[override]
        return self._from_call(
            lambda _input, other: _input != other,
            "__ne__",
            other=other,
        )

    def __invert__(self: Self) -> Self:
        invert = cast("Callable[..., duckdb.Expression]", operator.invert)
        return self._from_call(invert, "__invert__")

    def alias(self: Self, name: str) -> Self:
        def alias_output_names(names: Sequence[str]) -> Sequence[str]:
            if len(names) != 1:
                msg = f"Expected function with single output, found output names: {names}"
                raise ValueError(msg)
            return [name]

        return self.__class__(
            self._call,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
        )

    def abs(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("abs", _input), "abs")

    def mean(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("mean", _input), "mean")

    def skew(self: Self) -> Self:
        def func(_input: duckdb.Expression) -> duckdb.Expression:
            count = FunctionExpression("count", _input)
            return CaseExpression(condition=(count == lit(0)), value=lit(None)).otherwise(
                CaseExpression(
                    condition=(count == lit(1)), value=lit(float("nan"))
                ).otherwise(
                    CaseExpression(condition=(count == lit(2)), value=lit(0.0)).otherwise(
                        # Adjust population skewness by correction factor to get sample skewness
                        FunctionExpression("skewness", _input)
                        * (count - lit(2))
                        / FunctionExpression("sqrt", count * (count - lit(1)))
                    )
                )
            )

        return self._from_call(func, "skew")

    def median(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("median", _input), "median"
        )

    def all(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("bool_and", _input), "all"
        )

    def any(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("bool_or", _input), "any"
        )

    def quantile(
        self: Self,
        quantile: float,
        interpolation: Literal["nearest", "higher", "lower", "midpoint", "linear"],
    ) -> Self:
        def func(_input: duckdb.Expression) -> duckdb.Expression:
            if interpolation == "linear":
                return FunctionExpression("quantile_cont", _input, lit(quantile))
            msg = "Only linear interpolation methods are supported for DuckDB quantile."
            raise NotImplementedError(msg)

        return self._from_call(func, "quantile")

    def clip(self: Self, lower_bound: Any, upper_bound: Any) -> Self:
        def func(
            _input: duckdb.Expression, lower_bound: Any, upper_bound: Any
        ) -> duckdb.Expression:
            return FunctionExpression(
                "greatest", FunctionExpression("least", _input, upper_bound), lower_bound
            )

        return self._from_call(
            func, "clip", lower_bound=lower_bound, upper_bound=upper_bound
        )

    def sum(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("sum", _input), "sum")

    def n_unique(self: Self) -> Self:
        def func(_input: duckdb.Expression) -> duckdb.Expression:
            # https://stackoverflow.com/a/79338887/4451315
            return FunctionExpression(
                "array_unique", FunctionExpression("array_agg", _input)
            ) + FunctionExpression(
                "max",
                CaseExpression(condition=_input.isnotnull(), value=lit(0)).otherwise(
                    lit(1)
                ),
            )

        return self._from_call(func, "n_unique")

    def count(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("count", _input), "count"
        )

    def len(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("count"), "len")

    def std(self: Self, ddof: int) -> Self:
        def _std(_input: duckdb.Expression) -> duckdb.Expression:
            n_samples = FunctionExpression("count", _input)
            # NOTE: Not implemented Error: Unable to transform python value of type '<class 'duckdb.duckdb.Expression'>' to DuckDB LogicalType
            return (
                FunctionExpression("stddev_pop", _input)
                * FunctionExpression("sqrt", n_samples)
                / (FunctionExpression("sqrt", (n_samples - ddof)))  # type: ignore[operator]
            )

        return self._from_call(_std, "std")

    def var(self: Self, ddof: int) -> Self:
        def _var(_input: duckdb.Expression) -> duckdb.Expression:
            n_samples = FunctionExpression("count", _input)
            # NOTE: Not implemented Error: Unable to transform python value of type '<class 'duckdb.duckdb.Expression'>' to DuckDB LogicalType
            return FunctionExpression("var_pop", _input) * n_samples / (n_samples - ddof)  # type: ignore[operator, no-any-return]

        return self._from_call(_var, "var")

    def max(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("max", _input), "max")

    def min(self: Self) -> Self:
        return self._from_call(lambda _input: FunctionExpression("min", _input), "min")

    def null_count(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("sum", _input.isnull().cast("int")),
            "null_count",
        )

    def is_null(self: Self) -> Self:
        return self._from_call(lambda _input: _input.isnull(), "is_null")

    def is_nan(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("isnan", _input), "is_nan"
        )

    def is_finite(self: Self) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("isfinite", _input), "is_finite"
        )

    def is_in(self: Self, other: Sequence[Any]) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("contains", lit(other), _input), "is_in"
        )

    def round(self: Self, decimals: int) -> Self:
        return self._from_call(
            lambda _input: FunctionExpression("round", _input, lit(decimals)), "round"
        )

    def fill_null(
        self: Self, value: Self | Any, strategy: Any, limit: int | None
    ) -> Self:
        if strategy is not None:
            msg = "todo"
            raise NotImplementedError(msg)

        def func(_input: duckdb.Expression, value: Any) -> duckdb.Expression:
            return CoalesceOperator(_input, value)

        return self._from_call(func, "fill_null", value=value)

    def cast(self: Self, dtype: DType | type[DType]) -> Self:
        def func(_input: duckdb.Expression) -> duckdb.Expression:
            native_dtype = narwhals_to_native_dtype(dtype, self._version)
            return _input.cast(DuckDBPyType(native_dtype))

        return self._from_call(func, "cast")

    @property
    def str(self: Self) -> DuckDBExprStringNamespace:
        return DuckDBExprStringNamespace(self)

    @property
    def dt(self: Self) -> DuckDBExprDateTimeNamespace:
        return DuckDBExprDateTimeNamespace(self)

    @property
    def name(self: Self) -> DuckDBExprNameNamespace:
        return DuckDBExprNameNamespace(self)

    @property
    def list(self: Self) -> DuckDBExprListNamespace:
        return DuckDBExprListNamespace(self)

    @property
    def struct(self: Self) -> DuckDBExprStructNamespace:
        return DuckDBExprStructNamespace(self)

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
    rolling_sum = not_implemented()
    rolling_mean = not_implemented()
    rolling_var = not_implemented()
    rolling_std = not_implemented()
    gather_every = not_implemented()
    drop_nulls = not_implemented()
    diff = not_implemented()
    unique = not_implemented()
    shift = not_implemented()
    is_unique = not_implemented()
    is_first_distinct = not_implemented()
    is_last_distinct = not_implemented()
    cum_sum = not_implemented()
    cum_count = not_implemented()
    cum_min = not_implemented()
    cum_max = not_implemented()
    cum_prod = not_implemented()
    replace_strict = not_implemented()
    over = not_implemented()

    cat = not_implemented()  # pyright: ignore[reportAssignmentType]
