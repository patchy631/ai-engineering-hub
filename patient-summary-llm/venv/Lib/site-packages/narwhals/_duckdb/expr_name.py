from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Callable
from typing import Sequence

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._duckdb.expr import DuckDBExpr


class DuckDBExprNameNamespace:
    def __init__(self: Self, expr: DuckDBExpr) -> None:
        self._compliant_expr = expr

    def keep(self: Self) -> DuckDBExpr:
        return self._from_alias_output_names(alias_output_names=None)

    def map(self: Self, function: Callable[[str], str]) -> DuckDBExpr:
        return self._from_alias_output_names(
            alias_output_names=lambda output_names: [
                function(name) for name in output_names
            ],
        )

    def prefix(self: Self, prefix: str) -> DuckDBExpr:
        return self._from_alias_output_names(
            alias_output_names=lambda output_names: [
                f"{prefix}{output_name}" for output_name in output_names
            ],
        )

    def suffix(self: Self, suffix: str) -> DuckDBExpr:
        return self._from_alias_output_names(
            alias_output_names=lambda output_names: [
                f"{output_name}{suffix}" for output_name in output_names
            ]
        )

    def to_lowercase(self: Self) -> DuckDBExpr:
        return self._from_alias_output_names(
            alias_output_names=lambda output_names: [
                name.lower() for name in output_names
            ],
        )

    def to_uppercase(self: Self) -> DuckDBExpr:
        return self._from_alias_output_names(
            alias_output_names=lambda output_names: [
                name.upper() for name in output_names
            ]
        )

    def _from_alias_output_names(
        self: Self,
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
    ) -> DuckDBExpr:
        return self._compliant_expr.__class__(
            call=self._compliant_expr._call,
            function_name=self._compliant_expr._function_name,
            evaluate_output_names=self._compliant_expr._evaluate_output_names,
            alias_output_names=alias_output_names,
            backend_version=self._compliant_expr._backend_version,
            version=self._compliant_expr._version,
        )
