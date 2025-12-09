from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._expression_parsing import reuse_series_namespace_implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.expr import PandasLikeExpr


class PandasLikeExprCatNamespace:
    def __init__(self: Self, expr: PandasLikeExpr) -> None:
        self._compliant_expr = expr

    def get_categories(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr,
            "cat",
            "get_categories",
        )
