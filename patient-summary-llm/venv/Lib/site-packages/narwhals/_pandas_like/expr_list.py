from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._expression_parsing import reuse_series_namespace_implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.expr import PandasLikeExpr


class PandasLikeExprListNamespace:
    def __init__(self: Self, expr: PandasLikeExpr) -> None:
        self._expr = expr

    def len(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._expr,
            "list",
            "len",
        )
