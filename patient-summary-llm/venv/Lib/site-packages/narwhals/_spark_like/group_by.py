from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._spark_like.dataframe import SparkLikeLazyFrame
    from narwhals._spark_like.expr import SparkLikeExpr


class SparkLikeLazyGroupBy:
    def __init__(
        self: Self,
        compliant_frame: SparkLikeLazyFrame,
        keys: list[str],
        drop_null_keys: bool,  # noqa: FBT001
    ) -> None:
        if drop_null_keys:
            self._compliant_frame = compliant_frame.drop_nulls(subset=None)
        else:
            self._compliant_frame = compliant_frame
        self._keys = keys

    def agg(self: Self, *exprs: SparkLikeExpr) -> SparkLikeLazyFrame:
        agg_columns = []
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

        if not agg_columns:
            return self._compliant_frame._from_native_frame(
                self._compliant_frame._native_frame.select(*self._keys).dropDuplicates()
            )
        return self._compliant_frame._from_native_frame(
            self._compliant_frame._native_frame.groupBy(*self._keys).agg(*agg_columns)
        )
