from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.expr import Expr
    from narwhals.typing import TimeUnit

ExprT = TypeVar("ExprT", bound="Expr")


class ExprDateTimeNamespace(Generic[ExprT]):
    def __init__(self: Self, expr: ExprT) -> None:
        self._expr = expr

    def date(self: Self) -> ExprT:
        """Extract the date from underlying DateTime representation.

        Returns:
            A new expression.

        Raises:
            NotImplementedError: If pandas default backend is being used.

        Examples:
            >>> from datetime import datetime
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {"a": [datetime(2012, 1, 7, 10), datetime(2027, 12, 13)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("a").dt.date()).to_native()
            shape: (2, 1)
            ┌────────────┐
            │ a          │
            │ ---        │
            │ date       │
            ╞════════════╡
            │ 2012-01-07 │
            │ 2027-12-13 │
            └────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.date(), self._expr._metadata
        )

    def year(self: Self) -> ExprT:
        """Extract year from underlying DateTime representation.

        Returns the year number in the calendar date.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {"a": [datetime(1978, 6, 1), datetime(2065, 1, 1)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.year().alias("year"))
            ┌──────────────────┐
            |Narwhals DataFrame|
            |------------------|
            |           a  year|
            |0 1978-06-01  1978|
            |1 2065-01-01  2065|
            └──────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.year(), self._expr._metadata
        )

    def month(self: Self) -> ExprT:
        """Extract month from underlying DateTime representation.

        Returns the month number starting from 1. The return value ranges from 1 to 12.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table({"a": [datetime(1978, 6, 1), datetime(2065, 1, 1)]})
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.month().alias("month")).to_native()
            pyarrow.Table
            a: timestamp[us]
            month: int64
            ----
            a: [[1978-06-01 00:00:00.000000,2065-01-01 00:00:00.000000]]
            month: [[6,1]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.month(),
            self._expr._metadata,
        )

    def day(self: Self) -> ExprT:
        """Extract day from underlying DateTime representation.

        Returns the day of month starting from 1. The return value ranges from 1 to 31. (The last day of month differs by months.)

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table({"a": [datetime(1978, 6, 1), datetime(2065, 1, 1)]})
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.day().alias("day")).to_native()
            pyarrow.Table
            a: timestamp[us]
            day: int64
            ----
            a: [[1978-06-01 00:00:00.000000,2065-01-01 00:00:00.000000]]
            day: [[1,1]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.day(), self._expr._metadata
        )

    def hour(self: Self) -> ExprT:
        """Extract hour from underlying DateTime representation.

        Returns the hour number from 0 to 23.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {"a": [datetime(1978, 1, 1, 1), datetime(2065, 1, 1, 10)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.hour().alias("hour"))
            ┌──────────────────────────────┐
            |      Narwhals DataFrame      |
            |------------------------------|
            |shape: (2, 2)                 |
            |┌─────────────────────┬──────┐|
            |│ a                   ┆ hour │|
            |│ ---                 ┆ ---  │|
            |│ datetime[μs]        ┆ i8   │|
            |╞═════════════════════╪══════╡|
            |│ 1978-01-01 01:00:00 ┆ 1    │|
            |│ 2065-01-01 10:00:00 ┆ 10   │|
            |└─────────────────────┴──────┘|
            └──────────────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.hour(), self._expr._metadata
        )

    def minute(self: Self) -> ExprT:
        """Extract minutes from underlying DateTime representation.

        Returns the minute number from 0 to 59.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {"a": [datetime(1978, 1, 1, 1, 1), datetime(2065, 1, 1, 10, 20)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.minute().alias("minute")).to_native()
                                a  minute
            0 1978-01-01 01:01:00       1
            1 2065-01-01 10:20:00      20
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.minute(),
            self._expr._metadata,
        )

    def second(self: Self) -> ExprT:
        """Extract seconds from underlying DateTime representation.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table(
            ...     {
            ...         "a": [
            ...             datetime(1978, 1, 1, 1, 1, 1),
            ...             datetime(2065, 1, 1, 10, 20, 30),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("a").dt.second().alias("second")).to_native()
            pyarrow.Table
            a: timestamp[us]
            second: int64
            ----
            a: [[1978-01-01 01:01:01.000000,2065-01-01 10:20:30.000000]]
            second: [[1,30]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.second(),
            self._expr._metadata,
        )

    def millisecond(self: Self) -> ExprT:
        """Extract milliseconds from underlying DateTime representation.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table(
            ...     {
            ...         "a": [
            ...             datetime(1978, 1, 1, 1, 1, 1, 0),
            ...             datetime(2065, 1, 1, 10, 20, 30, 67000),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     nw.col("a").dt.millisecond().alias("millisecond")
            ... ).to_native()
            pyarrow.Table
            a: timestamp[us]
            millisecond: int64
            ----
            a: [[1978-01-01 01:01:01.000000,2065-01-01 10:20:30.067000]]
            millisecond: [[0,67]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.millisecond(),
            self._expr._metadata,
        )

    def microsecond(self: Self) -> ExprT:
        """Extract microseconds from underlying DateTime representation.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table(
            ...     {
            ...         "a": [
            ...             datetime(1978, 1, 1, 1, 1, 1, 0),
            ...             datetime(2065, 1, 1, 10, 20, 30, 67000),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     nw.col("a").dt.microsecond().alias("microsecond")
            ... ).to_native()
            pyarrow.Table
            a: timestamp[us]
            microsecond: int64
            ----
            a: [[1978-01-01 01:01:01.000000,2065-01-01 10:20:30.067000]]
            microsecond: [[0,67000]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.microsecond(),
            self._expr._metadata,
        )

    def nanosecond(self: Self) -> ExprT:
        """Extract Nanoseconds from underlying DateTime representation.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table(
            ...     {
            ...         "a": [
            ...             datetime(1978, 1, 1, 1, 1, 1, 0),
            ...             datetime(2065, 1, 1, 10, 20, 30, 67000),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     nw.col("a").dt.nanosecond().alias("nanosecond")
            ... ).to_native()
            pyarrow.Table
            a: timestamp[us]
            nanosecond: int64
            ----
            a: [[1978-01-01 01:01:01.000000,2065-01-01 10:20:30.067000]]
            nanosecond: [[0,67000000]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.nanosecond(),
            self._expr._metadata,
        )

    def ordinal_day(self: Self) -> ExprT:
        """Get ordinal day.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {"a": [datetime(2020, 1, 1), datetime(2020, 8, 3)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(a_ordinal_day=nw.col("a").dt.ordinal_day())
            ┌───────────────────────────┐
            |    Narwhals DataFrame     |
            |---------------------------|
            |           a  a_ordinal_day|
            |0 2020-01-01              1|
            |1 2020-08-03            216|
            └───────────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.ordinal_day(),
            self._expr._metadata,
        )

    def weekday(self: Self) -> ExprT:
        """Extract the week day from the underlying Date representation.

        Returns:
            Returns the ISO weekday number where monday = 1 and sunday = 7

        Examples:
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {"a": [datetime(2020, 1, 1), datetime(2020, 8, 3)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(a_week_day=nw.col("a").dt.weekday())
            ┌────────────────────────┐
            |   Narwhals DataFrame   |
            |------------------------|
            |           a  a_week_day|
            |0 2020-01-01           3|
            |1 2020-08-03           1|
            └────────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.weekday(),
            self._expr._metadata,
        )

    def total_minutes(self: Self) -> ExprT:
        """Get total minutes.

        Returns:
            A new expression.

        Notes:
            The function outputs the total minutes in the int dtype by default,
            however, pandas may change the dtype to float when there are missing values,
            consider using `fill_null()` and `cast` in this case.

        Examples:
            >>> from datetime import timedelta
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {"a": [timedelta(minutes=10), timedelta(minutes=20, seconds=40)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     a_total_minutes=nw.col("a").dt.total_minutes()
            ... ).to_native()
            shape: (2, 2)
            ┌──────────────┬─────────────────┐
            │ a            ┆ a_total_minutes │
            │ ---          ┆ ---             │
            │ duration[μs] ┆ i64             │
            ╞══════════════╪═════════════════╡
            │ 10m          ┆ 10              │
            │ 20m 40s      ┆ 20              │
            └──────────────┴─────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.total_minutes(),
            self._expr._metadata,
        )

    def total_seconds(self: Self) -> ExprT:
        """Get total seconds.

        Returns:
            A new expression.

        Notes:
            The function outputs the total seconds in the int dtype by default,
            however, pandas may change the dtype to float when there are missing values,
            consider using `fill_null()` and `cast` in this case.

        Examples:
            >>> from datetime import timedelta
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {"a": [timedelta(seconds=10), timedelta(seconds=20, milliseconds=40)]}
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     a_total_seconds=nw.col("a").dt.total_seconds()
            ... ).to_native()
            shape: (2, 2)
            ┌──────────────┬─────────────────┐
            │ a            ┆ a_total_seconds │
            │ ---          ┆ ---             │
            │ duration[μs] ┆ i64             │
            ╞══════════════╪═════════════════╡
            │ 10s          ┆ 10              │
            │ 20s 40ms     ┆ 20              │
            └──────────────┴─────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.total_seconds(),
            self._expr._metadata,
        )

    def total_milliseconds(self: Self) -> ExprT:
        """Get total milliseconds.

        Returns:
            A new expression.

        Notes:
            The function outputs the total milliseconds in the int dtype by default,
            however, pandas may change the dtype to float when there are missing values,
            consider using `fill_null()` and `cast` in this case.

        Examples:
            >>> from datetime import timedelta
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {
            ...         "a": [
            ...             timedelta(milliseconds=10),
            ...             timedelta(milliseconds=20, microseconds=40),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     a_total_milliseconds=nw.col("a").dt.total_milliseconds()
            ... ).to_native()
            shape: (2, 2)
            ┌──────────────┬──────────────────────┐
            │ a            ┆ a_total_milliseconds │
            │ ---          ┆ ---                  │
            │ duration[μs] ┆ i64                  │
            ╞══════════════╪══════════════════════╡
            │ 10ms         ┆ 10                   │
            │ 20040µs      ┆ 20                   │
            └──────────────┴──────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.total_milliseconds(),
            self._expr._metadata,
        )

    def total_microseconds(self: Self) -> ExprT:
        """Get total microseconds.

        Returns:
            A new expression.

        Notes:
            The function outputs the total microseconds in the int dtype by default,
            however, pandas may change the dtype to float when there are missing values,
            consider using `fill_null()` and `cast` in this case.

        Examples:
            >>> from datetime import timedelta
            >>> import pyarrow as pa
            >>> import narwhals as nw
            >>> df_native = pa.table(
            ...     {
            ...         "a": [
            ...             timedelta(microseconds=10),
            ...             timedelta(milliseconds=1, microseconds=200),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     a_total_microseconds=nw.col("a").dt.total_microseconds()
            ... ).to_native()
            pyarrow.Table
            a: duration[us]
            a_total_microseconds: int64
            ----
            a: [[10,1200]]
            a_total_microseconds: [[10,1200]]
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.total_microseconds(),
            self._expr._metadata,
        )

    def total_nanoseconds(self: Self) -> ExprT:
        """Get total nanoseconds.

        Returns:
            A new expression.

        Notes:
            The function outputs the total nanoseconds in the int dtype by default,
            however, pandas may change the dtype to float when there are missing values,
            consider using `fill_null()` and `cast` in this case.

        Examples:
            >>> from datetime import timedelta
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {
            ...         "a": pd.to_datetime(
            ...             [
            ...                 "2024-01-01 00:00:00.000000001",
            ...                 "2024-01-01 00:00:00.000000002",
            ...             ]
            ...         )
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(
            ...     a_diff_total_nanoseconds=nw.col("a").diff().dt.total_nanoseconds()
            ... ).to_native()
                                          a  a_diff_total_nanoseconds
            0 2024-01-01 00:00:00.000000001                       NaN
            1 2024-01-01 00:00:00.000000002                       1.0
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.total_nanoseconds(),
            self._expr._metadata,
        )

    def to_string(self: Self, format: str) -> ExprT:  # noqa: A002
        """Convert a Date/Time/Datetime column into a String column with the given format.

        Arguments:
            format: Format to format temporal column with.

        Returns:
            A new expression.

        Notes:
            Unfortunately, different libraries interpret format directives a bit
            differently.

            - Chrono, the library used by Polars, uses `"%.f"` for fractional seconds,
              whereas pandas and Python stdlib use `".%f"`.
            - PyArrow interprets `"%S"` as "seconds, including fractional seconds"
              whereas most other tools interpret it as "just seconds, as 2 digits".

            Therefore, we make the following adjustments:

            - for pandas-like libraries, we replace `"%S.%f"` with `"%S%.f"`.
            - for PyArrow, we replace `"%S.%f"` with `"%S"`.

            Workarounds like these don't make us happy, and we try to avoid them as
            much as possible, but here we feel like it's the best compromise.

            If you just want to format a date/datetime Series as a local datetime
            string, and have it work as consistently as possible across libraries,
            we suggest using:

            - `"%Y-%m-%dT%H:%M:%S%.f"` for datetimes
            - `"%Y-%m-%d"` for dates

            though note that, even then, different tools may return a different number
            of trailing zeros. Nonetheless, this is probably consistent enough for
            most applications.

            If you have an application where this is not enough, please open an issue
            and let us know.

        Examples:
            >>> from datetime import datetime
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame(
            ...     {
            ...         "a": [
            ...             datetime(2020, 3, 1),
            ...             datetime(2020, 5, 1),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("a").dt.to_string("%Y/%m/%d %H:%M:%S"))
            ┌───────────────────────┐
            |  Narwhals DataFrame   |
            |-----------------------|
            |shape: (2, 1)          |
            |┌─────────────────────┐|
            |│ a                   │|
            |│ ---                 │|
            |│ str                 │|
            |╞═════════════════════╡|
            |│ 2020/03/01 00:00:00 │|
            |│ 2020/05/01 00:00:00 │|
            |└─────────────────────┘|
            └───────────────────────┘
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.to_string(format),
            self._expr._metadata,
        )

    def replace_time_zone(self: Self, time_zone: str | None) -> ExprT:
        """Replace time zone.

        Arguments:
            time_zone: Target time zone.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime, timezone
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {
            ...         "a": [
            ...             datetime(2024, 1, 1, tzinfo=timezone.utc),
            ...             datetime(2024, 1, 2, tzinfo=timezone.utc),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("a").dt.replace_time_zone("Asia/Kathmandu")).to_native()
                                      a
            0 2024-01-01 00:00:00+05:45
            1 2024-01-02 00:00:00+05:45
        """
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.replace_time_zone(
                time_zone
            ),
            self._expr._metadata,
        )

    def convert_time_zone(self: Self, time_zone: str) -> ExprT:
        """Convert to a new time zone.

        If converting from a time-zone-naive column, then conversion happens
        as if converting from UTC.

        Arguments:
            time_zone: Target time zone.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import datetime, timezone
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame(
            ...     {
            ...         "a": [
            ...             datetime(2024, 1, 1, tzinfo=timezone.utc),
            ...             datetime(2024, 1, 2, tzinfo=timezone.utc),
            ...         ]
            ...     }
            ... )
            >>> df = nw.from_native(df_native)
            >>> df.select(nw.col("a").dt.convert_time_zone("Asia/Kathmandu")).to_native()
                                      a
            0 2024-01-01 05:45:00+05:45
            1 2024-01-02 05:45:00+05:45
        """
        if time_zone is None:
            msg = "Target `time_zone` cannot be `None` in `convert_time_zone`. Please use `replace_time_zone(None)` if you want to remove the time zone."
            raise TypeError(msg)
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.convert_time_zone(
                time_zone
            ),
            self._expr._metadata,
        )

    def timestamp(self: Self, time_unit: TimeUnit = "us") -> ExprT:
        """Return a timestamp in the given time unit.

        Arguments:
            time_unit: {'ns', 'us', 'ms'}
                Time unit.

        Returns:
            A new expression.

        Examples:
            >>> from datetime import date
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"date": [date(2001, 1, 1), None]})
            >>> df = nw.from_native(df_native)
            >>> df.with_columns(nw.col("date").dt.timestamp("ms").alias("timestamp_ms"))
            ┌─────────────────────────────┐
            |     Narwhals DataFrame      |
            |-----------------------------|
            |shape: (2, 2)                |
            |┌────────────┬──────────────┐|
            |│ date       ┆ timestamp_ms │|
            |│ ---        ┆ ---          │|
            |│ date       ┆ i64          │|
            |╞════════════╪══════════════╡|
            |│ 2001-01-01 ┆ 978307200000 │|
            |│ null       ┆ null         │|
            |└────────────┴──────────────┘|
            └─────────────────────────────┘
        """
        if time_unit not in {"ns", "us", "ms"}:
            msg = (
                "invalid `time_unit`"
                f"\n\nExpected one of {{'ns', 'us', 'ms'}}, got {time_unit!r}."
            )
            raise ValueError(msg)
        return self._expr.__class__(
            lambda plx: self._expr._to_compliant_expr(plx).dt.timestamp(time_unit),
            self._expr._metadata,
        )
