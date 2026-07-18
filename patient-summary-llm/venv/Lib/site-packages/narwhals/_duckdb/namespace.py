from __future__ import annotations

import operator
from functools import partial
from functools import reduce
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Container
from typing import Literal
from typing import Sequence

from duckdb import CaseExpression
from duckdb import CoalesceOperator
from duckdb import FunctionExpression
from duckdb.typing import BIGINT
from duckdb.typing import VARCHAR

from narwhals._duckdb.expr import DuckDBExpr
from narwhals._duckdb.selectors import DuckDBSelectorNamespace
from narwhals._duckdb.utils import lit
from narwhals._duckdb.utils import maybe_evaluate_expr
from narwhals._duckdb.utils import narwhals_to_native_dtype
from narwhals._expression_parsing import combine_alias_output_names
from narwhals._expression_parsing import combine_evaluate_output_names
from narwhals.typing import CompliantNamespace
from narwhals.utils import Implementation
from narwhals.utils import exclude_column_names
from narwhals.utils import get_column_names
from narwhals.utils import passthrough_column_names

if TYPE_CHECKING:
    import duckdb
    from typing_extensions import Self

    from narwhals._duckdb.dataframe import DuckDBLazyFrame
    from narwhals.dtypes import DType
    from narwhals.utils import Version


class DuckDBNamespace(CompliantNamespace["DuckDBLazyFrame", "duckdb.Expression"]):  # type: ignore[type-var]
    _implementation: Implementation = Implementation.DUCKDB

    def __init__(
        self: Self, *, backend_version: tuple[int, ...], version: Version
    ) -> None:
        self._backend_version = backend_version
        self._version = version

    @property
    def selectors(self: Self) -> DuckDBSelectorNamespace:
        return DuckDBSelectorNamespace(self)

    def all(self: Self) -> DuckDBExpr:
        return DuckDBExpr.from_column_names(
            get_column_names,
            function_name="all",
            backend_version=self._backend_version,
            version=self._version,
        )

    def concat(
        self: Self,
        items: Sequence[DuckDBLazyFrame],
        *,
        how: Literal["horizontal", "vertical", "diagonal"],
    ) -> DuckDBLazyFrame:
        if how == "horizontal":
            msg = "horizontal concat not supported for duckdb. Please join instead"
            raise TypeError(msg)
        if how == "diagonal":
            msg = "Not implemented yet"
            raise NotImplementedError(msg)
        first = items[0]
        schema = first.schema
        if how == "vertical" and not all(x.schema == schema for x in items[1:]):
            msg = "inputs should all have the same schema"
            raise TypeError(msg)
        res = reduce(lambda x, y: x.union(y), (item._native_frame for item in items))
        return first._from_native_frame(res)

    def concat_str(
        self: Self,
        *exprs: DuckDBExpr,
        separator: str,
        ignore_nulls: bool,
    ) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = [s for _expr in exprs for s in _expr(df)]
            null_mask = [s.isnull() for s in cols]

            if not ignore_nulls:
                null_mask_result = reduce(operator.or_, null_mask)
                cols_separated = [
                    y
                    for x in [
                        (col.cast(VARCHAR),)
                        if i == len(cols) - 1
                        else (col.cast(VARCHAR), lit(separator))
                        for i, col in enumerate(cols)
                    ]
                    for y in x
                ]
                result = CaseExpression(
                    condition=~null_mask_result,
                    value=FunctionExpression("concat", *cols_separated),
                )
            else:
                init_value, *values = [
                    CaseExpression(~nm, col.cast(VARCHAR)).otherwise(lit(""))
                    for col, nm in zip(cols, null_mask)
                ]
                separators = (
                    CaseExpression(nm, lit("")).otherwise(lit(separator))
                    for nm in null_mask[:-1]
                )
                result = reduce(
                    lambda x, y: FunctionExpression("concat", x, y),
                    (
                        FunctionExpression("concat", s, v)
                        for s, v in zip(separators, values)
                    ),
                    init_value,
                )

            return [result]

        return DuckDBExpr(
            call=func,
            function_name="concat_str",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def all_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = (c for _expr in exprs for c in _expr(df))
            return [reduce(operator.and_, cols)]

        return DuckDBExpr(
            call=func,
            function_name="all_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def any_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = (c for _expr in exprs for c in _expr(df))
            return [reduce(operator.or_, cols)]

        return DuckDBExpr(
            call=func,
            function_name="or_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def max_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = (c for _expr in exprs for c in _expr(df))
            return [FunctionExpression("greatest", *cols)]

        return DuckDBExpr(
            call=func,
            function_name="max_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def min_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = (c for _expr in exprs for c in _expr(df))
            return [FunctionExpression("least", *cols)]

        return DuckDBExpr(
            call=func,
            function_name="min_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def sum_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = (CoalesceOperator(col, lit(0)) for _expr in exprs for col in _expr(df))
            return [reduce(operator.add, cols)]

        return DuckDBExpr(
            call=func,
            function_name="sum_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def mean_horizontal(self: Self, *exprs: DuckDBExpr) -> DuckDBExpr:
        def func(df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            cols = [c for _expr in exprs for c in _expr(df)]
            return [
                (
                    reduce(operator.add, (CoalesceOperator(col, lit(0)) for col in cols))
                    / reduce(operator.add, (col.isnotnull().cast(BIGINT) for col in cols))
                )
            ]

        return DuckDBExpr(
            call=func,
            function_name="mean_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
            backend_version=self._backend_version,
            version=self._version,
        )

    def when(self: Self, predicate: DuckDBExpr) -> DuckDBWhen:
        return DuckDBWhen(
            predicate,
            self._backend_version,
            version=self._version,
        )

    def col(self: Self, *column_names: str) -> DuckDBExpr:
        return DuckDBExpr.from_column_names(
            passthrough_column_names(column_names),
            function_name="col",
            backend_version=self._backend_version,
            version=self._version,
        )

    def exclude(self: Self, excluded_names: Container[str]) -> DuckDBExpr:
        return DuckDBExpr.from_column_names(
            partial(exclude_column_names, names=excluded_names),
            function_name="exclude",
            backend_version=self._backend_version,
            version=self._version,
        )

    def nth(self: Self, *column_indices: int) -> DuckDBExpr:
        return DuckDBExpr.from_column_indices(
            *column_indices, backend_version=self._backend_version, version=self._version
        )

    def lit(self: Self, value: Any, dtype: DType | None) -> DuckDBExpr:
        def func(_df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            if dtype is not None:
                return [
                    lit(value).cast(
                        narwhals_to_native_dtype(dtype, version=self._version)  # type: ignore[arg-type]
                    )
                ]
            return [lit(value)]

        return DuckDBExpr(
            func,
            function_name="lit",
            evaluate_output_names=lambda _df: ["literal"],
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )

    def len(self: Self) -> DuckDBExpr:
        def func(_df: DuckDBLazyFrame) -> list[duckdb.Expression]:
            return [FunctionExpression("count")]

        return DuckDBExpr(
            call=func,
            function_name="len",
            evaluate_output_names=lambda _df: ["len"],
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )


class DuckDBWhen:
    def __init__(
        self: Self,
        condition: DuckDBExpr,
        backend_version: tuple[int, ...],
        then_value: Any = None,
        otherwise_value: Any = None,
        *,
        version: Version,
    ) -> None:
        self._backend_version = backend_version
        self._condition = condition
        self._then_value = then_value
        self._otherwise_value = otherwise_value
        self._version = version

    def __call__(self: Self, df: DuckDBLazyFrame) -> Sequence[duckdb.Expression]:
        condition = maybe_evaluate_expr(df, self._condition)
        then_value = maybe_evaluate_expr(df, self._then_value)
        if self._otherwise_value is None:
            return [CaseExpression(condition=condition, value=then_value)]
        otherwise_value = maybe_evaluate_expr(df, self._otherwise_value)
        return [
            CaseExpression(condition=condition, value=then_value).otherwise(
                otherwise_value
            )
        ]

    def then(self: Self, value: DuckDBExpr | Any) -> DuckDBThen:
        self._then_value = value

        return DuckDBThen(
            self,
            function_name="whenthen",
            evaluate_output_names=getattr(
                value, "_evaluate_output_names", lambda _df: ["literal"]
            ),
            alias_output_names=getattr(value, "_alias_output_names", None),
            backend_version=self._backend_version,
            version=self._version,
        )


class DuckDBThen(DuckDBExpr):
    def __init__(
        self: Self,
        call: DuckDBWhen,
        *,
        function_name: str,
        evaluate_output_names: Callable[[DuckDBLazyFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._backend_version = backend_version
        self._version = version
        self._call = call
        self._function_name = function_name
        self._evaluate_output_names = evaluate_output_names
        self._alias_output_names = alias_output_names

    def otherwise(self: Self, value: DuckDBExpr | Any) -> DuckDBExpr:
        # type ignore because we are setting the `_call` attribute to a
        # callable object of type `DuckDBWhen`, base class has the attribute as
        # only a `Callable`
        self._call._otherwise_value = value  # type: ignore[attr-defined]
        self._function_name = "whenotherwise"
        return self
