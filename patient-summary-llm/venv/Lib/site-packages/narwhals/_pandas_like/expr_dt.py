from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._expression_parsing import reuse_series_namespace_implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.expr import PandasLikeExpr
    from narwhals.typing import TimeUnit


class PandasLikeExprDateTimeNamespace:
    def __init__(self: Self, expr: PandasLikeExpr) -> None:
        self._compliant_expr = expr

    def date(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "date")

    def year(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "year")

    def month(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "month")

    def day(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "day")

    def hour(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "hour")

    def minute(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "minute")

    def second(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(self._compliant_expr, "dt", "second")

    def millisecond(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "millisecond"
        )

    def microsecond(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "microsecond"
        )

    def nanosecond(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "nanosecond"
        )

    def ordinal_day(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "ordinal_day"
        )

    def weekday(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "weekday"
        )

    def total_minutes(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "total_minutes"
        )

    def total_seconds(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "total_seconds"
        )

    def total_milliseconds(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "total_milliseconds"
        )

    def total_microseconds(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "total_microseconds"
        )

    def total_nanoseconds(self: Self) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "total_nanoseconds"
        )

    def to_string(self: Self, format: str) -> PandasLikeExpr:  # noqa: A002
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "to_string", format=format
        )

    def replace_time_zone(self: Self, time_zone: str | None) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "replace_time_zone", time_zone=time_zone
        )

    def convert_time_zone(self: Self, time_zone: str) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "convert_time_zone", time_zone=time_zone
        )

    def timestamp(self: Self, time_unit: TimeUnit) -> PandasLikeExpr:
        return reuse_series_namespace_implementation(
            self._compliant_expr, "dt", "timestamp", time_unit=time_unit
        )
