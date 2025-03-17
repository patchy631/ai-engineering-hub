from __future__ import annotations

from typing import TYPE_CHECKING

from duckdb import FunctionExpression

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._duckdb.expr import DuckDBExpr


class DuckDBExprListNamespace:
    def __init__(self: Self, expr: DuckDBExpr) -> None:
        self._compliant_expr = expr

    def len(self: Self) -> DuckDBExpr:
        return self._compliant_expr._from_call(
            lambda _input: FunctionExpression("len", _input), "len"
        )
