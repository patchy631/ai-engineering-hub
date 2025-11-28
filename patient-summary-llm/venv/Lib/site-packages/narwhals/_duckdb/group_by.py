from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from duckdb import Expression
    from typing_extensions import Self

    from narwhals._duckdb.dataframe import DuckDBLazyFrame
    from narwhals._duckdb.expr import DuckDBExpr


class DuckDBGroupBy:
    def __init__(
        self: Self,
        compliant_frame: DuckDBLazyFrame,
        keys: list[str],
        drop_null_keys: bool,  # noqa: FBT001
    ) -> None:
        if drop_null_keys:
            self._compliant_frame = compliant_frame.drop_nulls(subset=None)
        else:
            self._compliant_frame = compliant_frame
        self._keys = keys

    def agg(self: Self, *exprs: DuckDBExpr) -> DuckDBLazyFrame:
        agg_columns: list[str | Expression] = list(self._keys)
        df = self._compliant_frame
        for expr in exprs:
            output_names = expr._evaluate_output_names(df)
            aliases = (
                output_names
                if expr._alias_output_names is None
                else expr._alias_output_names(output_names)
            )
            native_expressions = expr(df)
            exclude = (
                self._keys
                if expr._function_name.split("->", maxsplit=1)[0] in {"all", "selector"}
                else []
            )
            agg_columns.extend(
                [
                    native_expression.alias(alias)
                    for native_expression, output_name, alias in zip(
                        native_expressions, output_names, aliases
                    )
                    if output_name not in exclude
                ]
            )

        return self._compliant_frame._from_native_frame(
            self._compliant_frame._native_frame.aggregate(agg_columns)  # type: ignore[arg-type]
        )
