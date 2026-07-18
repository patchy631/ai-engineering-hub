from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.expr import Expr

ExprT = TypeVar("ExprT", bound="Expr")


class ExprNameNamespace(Generic[ExprT]):
    def __init__(self: Self, expr: ExprT) -> None:
        self._expr = expr

    def keep(self: Self) -> ExprT:
        r"""Keep the original root name of the expression.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("foo").alias("alias_for_foo").name.keep()).columns
            ['foo']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.keep(),
            self._expr._metadata,
        )

    def map(self: Self, function: Callable[[str], str]) -> ExprT:
        r"""Rename the output of an expression by mapping a function over the root name.

        Arguments:
            function: Function that maps a root name to a new name.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> renaming_func = lambda s: s[::-1]  # reverse column name
            >>> df.select(nw.col("foo", "BAR").name.map(renaming_func)).columns
            ['oof', 'RAB']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.map(function),
            self._expr._metadata,
        )

    def prefix(self: Self, prefix: str) -> ExprT:
        r"""Add a prefix to the root column name of the expression.

        Arguments:
            prefix: Prefix to add to the root column name.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("foo", "BAR").name.prefix("with_prefix")).columns
            ['with_prefixfoo', 'with_prefixBAR']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.prefix(prefix),
            self._expr._metadata,
        )

    def suffix(self: Self, suffix: str) -> ExprT:
        r"""Add a suffix to the root column name of the expression.

        Arguments:
            suffix: Suffix to add to the root column name.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("foo", "BAR").name.suffix("_with_suffix")).columns
            ['foo_with_suffix', 'BAR_with_suffix']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.suffix(suffix),
            self._expr._metadata,
        )

    def to_lowercase(self: Self) -> ExprT:
        r"""Make the root column name lowercase.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("foo", "BAR").name.to_lowercase()).columns
            ['foo', 'bar']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.to_lowercase(),
            self._expr._metadata,
        )

    def to_uppercase(self: Self) -> ExprT:
        r"""Make the root column name uppercase.

        Returns:
            A new expression.

        Notes:
            This will undo any previous renaming operations on the expression.
            Due to implementation constraints, this method can only be called as the last
            expression in a chain. Only one name operation per expression will work.

        Examples:
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table({"foo": [1, 2], "BAR": [4, 5]})
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("foo", "BAR").name.to_uppercase()).columns
            ['FOO', 'BAR']
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).name.to_uppercase(),
            self._expr._metadata,
        )
