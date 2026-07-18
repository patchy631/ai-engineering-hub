from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.expr import Expr

ExprT = TypeVar("ExprT", bound="Expr")


class ExprListNamespace(Generic[ExprT]):
    def __init__(self: Self, expr: ExprT) -> None:
        self._expr = expr

    def len(self: Self) -> ExprT:
        """Return the number of elements in each list.

        Null values count towards the total.

        Returns:
            A new expression.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [[1, 2], [3, 4, None], None, []]})
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(a_len=nw.col("a").list.len())
            ┌────────────────────────┐
            |   Narwhals DataFrame   |
            |------------------------|
            |shape: (4, 2)           |
            |┌──────────────┬───────┐|
            |│ a            ┆ a_len │|
            |│ ---          ┆ ---   │|
            |│ list[i64]    ┆ u32   │|
            |╞══════════════╪═══════╡|
            |│ [1, 2]       ┆ 2     │|
            |│ [3, 4, null] ┆ 3     │|
            |│ null         ┆ null  │|
            |│ []           ┆ 0     │|
            |└──────────────┴───────┘|
            └────────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).list.len(),
            self._expr._metadata,
        )
