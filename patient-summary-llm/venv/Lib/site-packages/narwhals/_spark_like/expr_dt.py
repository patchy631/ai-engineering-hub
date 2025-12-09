from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import Column
    from typing_extensions import Self

    from narwhals._spark_like.expr import SparkLikeExpr


class SparkLikeExprDateTimeNamespace:
    def __init__(self: Self, expr: SparkLikeExpr) -> None:
        self._compliant_expr = expr

    def date(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.to_date, "date")

    def year(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.year, "year")

    def month(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.month, "month")

    def day(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.day, "day")

    def hour(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.hour, "hour")

    def minute(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.minute, "minute")

    def second(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.second, "second")

    def millisecond(self: Self) -> SparkLikeExpr:
        def _millisecond(_input: Column) -> Column:
            return self._compliant_expr._F.floor(
                (self._compliant_expr._F.unix_micros(_input) % 1_000_000) / 1000
            )

        return self._compliant_expr._from_call(_millisecond, "millisecond")

    def microsecond(self: Self) -> SparkLikeExpr:
        def _microsecond(_input: Column) -> Column:
            return self._compliant_expr._F.unix_micros(_input) % 1_000_000

        return self._compliant_expr._from_call(_microsecond, "microsecond")

    def nanosecond(self: Self) -> SparkLikeExpr:
        def _nanosecond(_input: Column) -> Column:
            return (self._compliant_expr._F.unix_micros(_input) % 1_000_000) * 1000

        return self._compliant_expr._from_call(_nanosecond, "nanosecond")

    def ordinal_day(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            self._compliant_expr._F.dayofyear, "ordinal_day"
        )

    def weekday(self: Self) -> SparkLikeExpr:
        def _weekday(_input: Column) -> Column:
            # PySpark's dayofweek returns 1-7 for Sunday-Saturday
            return (self._compliant_expr._F.dayofweek(_input) + 6) % 7

        return self._compliant_expr._from_call(_weekday, "weekday")
