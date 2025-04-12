from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar

from narwhals._expression_parsing import ExprKind

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.expr import Expr

ExprT = TypeVar("ExprT", bound="Expr")


class ExprCatNamespace(Generic[ExprT]):
    def __init__(self: Self, expr: ExprT) -> None:
        self._expr = expr

    def get_categories(self: Self) -> ExprT:
        """Get unique categories from column.

        Returns:
            A new expression.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {"fruits": ["apple", "mango", "mango"]},
            ...     schema={"fruits": pl.Categorical},
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("fruits").cat.get_categories()).to_native()
            shape: (2, 1)
            ┌────────┐
            │ fruits │
            │ ---    │
            │ str    │
            ╞════════╡
            │ apple  │
            │ mango  │
            └────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).cat.get_categories(),
            self._expr._metadata.with_kind(ExprKind.FILTRATION),
        )
