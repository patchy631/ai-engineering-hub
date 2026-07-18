from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._expression_parsing import reuse_series_namespace_implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.expr import ArrowExpr


class ArrowExprStructNamespace:
    def __init__(self: Self, expr: ArrowExpr) -> None:
        self._compliant_expr = expr

    def field(self: Self, name: str) -> ArrowExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr,
            "struct",
            "field",
            name=name,
        ).alias(name)
