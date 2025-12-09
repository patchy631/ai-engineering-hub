from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import Column
    from typing_extensions import Self

    from narwhals._spark_like.expr import SparkLikeExpr


class SparkLikeExprStringNamespace:
    def __init__(self: Self, expr: SparkLikeExpr) -> None:
        self._compliant_expr = expr

    def len_chars(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(self._compliant_expr._F.char_length, "len")

    def replace_all(
        self: Self, pattern: str, value: str, *, literal: bool
    ) -> SparkLikeExpr:
        def func(_input: Column) -> Column:
            replace_all_func = (
                self._compliant_expr._F.replace
                if literal
                else self._compliant_expr._F.regexp_replace
            )
            return replace_all_func(
                _input,
                self._compliant_expr._F.lit(pattern),
                self._compliant_expr._F.lit(value),
            )

        return self._compliant_expr._from_call(func, "replace")

    def strip_chars(self: Self, characters: str | None) -> SparkLikeExpr:
        import string

        def func(_input: Column) -> Column:
            to_remove = characters if characters is not None else string.whitespace
            return self._compliant_expr._F.btrim(
                _input, self._compliant_expr._F.lit(to_remove)
            )

        return self._compliant_expr._from_call(func, "strip")

    def starts_with(self: Self, prefix: str) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            lambda _input: self._compliant_expr._F.startswith(
                _input, self._compliant_expr._F.lit(prefix)
            ),
            "starts_with",
        )

    def ends_with(self: Self, suffix: str) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            lambda _input: self._compliant_expr._F.endswith(
                _input, self._compliant_expr._F.lit(suffix)
            ),
            "ends_with",
        )

    def contains(self: Self, pattern: str, *, literal: bool) -> SparkLikeExpr:
        def func(_input: Column) -> Column:
            contains_func = (
                self._compliant_expr._F.contains
                if literal
                else self._compliant_expr._F.regexp
            )
            return contains_func(_input, self._compliant_expr._F.lit(pattern))

        return self._compliant_expr._from_call(func, "contains")

    def slice(self: Self, offset: int, length: int | None) -> SparkLikeExpr:
        # From the docs: https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.functions.substring.html
        # The position is not zero based, but 1 based index.
        def func(_input: Column) -> Column:
            col_length = self._compliant_expr._F.char_length(_input)

            _offset = (
                col_length + self._compliant_expr._F.lit(offset + 1)
                if offset < 0
                else self._compliant_expr._F.lit(offset + 1)
            )
            _length = (
                self._compliant_expr._F.lit(length) if length is not None else col_length
            )
            return _input.substr(_offset, _length)

        return self._compliant_expr._from_call(func, "slice")

    def split(self: Self, by: str) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            lambda _input: self._compliant_expr._F.split(_input, by),
            "split",
        )

    def to_uppercase(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            self._compliant_expr._F.upper, "to_uppercase"
        )

    def to_lowercase(self: Self) -> SparkLikeExpr:
        return self._compliant_expr._from_call(
            self._compliant_expr._F.lower, "to_lowercase"
        )

    def to_datetime(self: Self, format: str | None) -> SparkLikeExpr:  # noqa: A002
        F = self._compliant_expr._F  # noqa: N806
        if not format:
            function = F.to_timestamp
        elif is_naive_format(format):
            function = partial(
                F.to_timestamp_ntz, format=F.lit(strptime_to_pyspark_format(format))
            )
        else:
            format = strptime_to_pyspark_format(format)
            function = partial(F.to_timestamp, format=format)
        return self._compliant_expr._from_call(
            lambda _input: function(F.replace(_input, F.lit("T"), F.lit(" "))),
            "to_datetime",
        )


def is_naive_format(format: str) -> bool:  # noqa: A002
    return not any(x in format for x in ("%s", "%z", "Z"))


def strptime_to_pyspark_format(format: str) -> str:  # noqa: A002
    """Converts a Python strptime datetime format string to a PySpark datetime format string."""
    # Mapping from Python strptime format to PySpark format

    # see https://spark.apache.org/docs/latest/sql-ref-datetime-pattern.html
    # and https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    format_mapping = {
        "%Y": "y",  # Year with century
        "%y": "y",  # Year without century
        "%m": "M",  # Month
        "%d": "d",  # Day of the month
        "%H": "H",  # Hour (24-hour clock) 0-23
        "%I": "h",  # Hour (12-hour clock) 1-12
        "%M": "m",  # Minute
        "%S": "s",  # Second
        "%f": "S",  # Microseconds -> Milliseconds
        "%p": "a",  # AM/PM
        "%a": "E",  # Abbreviated weekday name
        "%A": "E",  # Full weekday name
        "%j": "D",  # Day of the year
        "%z": "Z",  # Timezone offset
        "%s": "X",  # Unix timestamp
    }

    # Replace Python format specifiers with PySpark specifiers
    pyspark_format = format
    for py_format, spark_format in format_mapping.items():
        pyspark_format = pyspark_format.replace(py_format, spark_format)
    return pyspark_format.replace("T", " ")
