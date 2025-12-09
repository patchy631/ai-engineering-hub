from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._arrow.expr import ArrowExpr
from narwhals._selectors import CompliantSelector
from narwhals._selectors import EagerSelectorNamespace

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.dataframe import ArrowDataFrame
    from narwhals._arrow.series import ArrowSeries
    from narwhals._selectors import EvalNames
    from narwhals._selectors import EvalSeries
    from narwhals.utils import _FullContext


class ArrowSelectorNamespace(EagerSelectorNamespace["ArrowDataFrame", "ArrowSeries"]):
    def _selector(
        self,
        call: EvalSeries[ArrowDataFrame, ArrowSeries],
        evaluate_output_names: EvalNames[ArrowDataFrame],
        /,
    ) -> ArrowSelector:
        return ArrowSelector(
            call,
            depth=0,
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


class ArrowSelector(CompliantSelector["ArrowDataFrame", "ArrowSeries"], ArrowExpr):  # type: ignore[misc]
    def _to_expr(self: Self) -> ArrowExpr:
        return ArrowExpr(
            self._call,
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
        )
