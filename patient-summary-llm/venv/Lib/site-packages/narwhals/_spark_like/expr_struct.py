from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import Column
    from typing_extensions import Self

    from narwhals._spark_like.expr import SparkLikeExpr


class SparkLikeExprStructNamespace:
    def __init__(self: Self, expr: SparkLikeExpr) -> None:
        self._compliant_expr = expr

    def field(self: Self, name: str) -> SparkLikeExpr:
        def func(_input: Column) -> Column:
            return _input.getField(name)

        return self._compliant_expr._from_call(func, "field").alias(name)
