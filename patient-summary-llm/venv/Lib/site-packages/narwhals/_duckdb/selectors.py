from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._duckdb.expr import DuckDBExpr
from narwhals._selectors import CompliantSelector
from narwhals._selectors import LazySelectorNamespace

if TYPE_CHECKING:
    import duckdb
    from typing_extensions import Self

    from narwhals._duckdb.dataframe import DuckDBLazyFrame
    from narwhals._selectors import EvalNames
    from narwhals._selectors import EvalSeries
    from narwhals.utils import _FullContext


class DuckDBSelectorNamespace(
    LazySelectorNamespace["DuckDBLazyFrame", "duckdb.Expression"]  # type: ignore[type-var]
):
    def _selector(
        self,
        call: EvalSeries[DuckDBLazyFrame, duckdb.Expression],  # type: ignore[type-var]
        evaluate_output_names: EvalNames[DuckDBLazyFrame],
        /,
    ) -> DuckDBSelector:
        return DuckDBSelector(
            call,
            function_name="selector",
            evaluate_output_names=evaluate_output_names,
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )

    def __init__(self: Self, context: _FullContext, /) -> None:
        self._implementation = context._implementation
        self._backend_version = context._backend_version
        self._version = context._version


class DuckDBSelector(  # type: ignore[misc]
    CompliantSelector["DuckDBLazyFrame", "duckdb.Expression"],  # type: ignore[type-var]
    DuckDBExpr,
):
    def _to_expr(self: Self) -> DuckDBExpr:
        return DuckDBExpr(
            self._call,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
        )
