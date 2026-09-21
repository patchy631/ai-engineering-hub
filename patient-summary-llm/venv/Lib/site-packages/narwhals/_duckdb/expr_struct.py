from __future__ import annotations

from typing import TYPE_CHECKING

from duckdb import FunctionExpression

from narwhals._duckdb.utils import lit

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._duckdb.expr import DuckDBExpr


class DuckDBExprStructNamespace:
    def __init__(self: Self, expr: DuckDBExpr) -> None:
        self._compliant_expr = expr

    def field(self: Self, name: str) -> DuckDBExpr:
        return self._compliant_expr._from_call(
            lambda _input: FunctionExpression("struct_extract", _input, lit(name)),
            "field",
        ).alias(name)
