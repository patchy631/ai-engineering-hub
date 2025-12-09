from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._pandas_like.utils import calculate_timestamp_date
from narwhals._pandas_like.utils import calculate_timestamp_datetime
from narwhals._pandas_like.utils import native_to_narwhals_dtype
from narwhals.utils import Implementation
from narwhals.utils import import_dtypes_module

if TYPE_CHECKING:
    try:
        import dask.dataframe.dask_expr as dx
    except ModuleNotFoundError:
        import dask_expr as dx

    from typing_extensions import Self

    from narwhals._dask.expr import DaskExpr
    from narwhals.typing import TimeUnit


class DaskExprDateTimeNamespace:
    def __init__(self: Self, expr: DaskExpr) -> None:
        self._compliant_expr = expr

    def date(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.date, "date")

    def year(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.year, "year")

    def month(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.month, "month")

    def day(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.day, "day")

    def hour(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.hour, "hour")

    def minute(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.minute, "minute")

    def second(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(lambda _input: _input.dt.second, "second")

    def millisecond(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.microsecond // 1000, "millisecond"
        )

    def microsecond(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.microsecond, "microsecond"
        )

    def nanosecond(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.microsecond * 1000 + _input.dt.nanosecond,
            "nanosecond",
        )

    def ordinal_day(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.dayofyear, "ordinal_day"
        )

    def weekday(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.weekday + 1,  # Dask is 0-6
            "weekday",
        )

    def to_string(self: Self, format: str) -> DaskExpr:  # noqa: A002
        return self._compliant_expr._from_call(
            lambda _input, format: _input.dt.strftime(format.replace("%.f", ".%f")),  # noqa: A006
            "strftime",
            format=format,
        )

    def replace_time_zone(self: Self, time_zone: str | None) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input, time_zone: _input.dt.tz_localize(None).dt.tz_localize(
                time_zone
            )
            if time_zone is not None
            else _input.dt.tz_localize(None),
            "tz_localize",
            time_zone=time_zone,
        )

    def convert_time_zone(self: Self, time_zone: str) -> DaskExpr:
        def func(s: dx.Series, time_zone: str) -> dx.Series:
            dtype = native_to_narwhals_dtype(
                s.dtype, self._compliant_expr._version, Implementation.DASK
            )
            if dtype.time_zone is None:  # type: ignore[attr-defined]
                return s.dt.tz_localize("UTC").dt.tz_convert(time_zone)  # pyright: ignore[reportAttributeAccessIssue]
            else:
                return s.dt.tz_convert(time_zone)  # pyright: ignore[reportAttributeAccessIssue]

        return self._compliant_expr._from_call(func, "tz_convert", time_zone=time_zone)

    def timestamp(self: Self, time_unit: TimeUnit) -> DaskExpr:
        def func(s: dx.Series, time_unit: TimeUnit) -> dx.Series:
            dtype = native_to_narwhals_dtype(
                s.dtype, self._compliant_expr._version, Implementation.DASK
            )
            is_pyarrow_dtype = "pyarrow" in str(dtype)
            mask_na = s.isna()
            dtypes = import_dtypes_module(self._compliant_expr._version)
            if dtype == dtypes.Date:
                # Date is only supported in pandas dtypes if pyarrow-backed
                s_cast = s.astype("Int32[pyarrow]")
                result = calculate_timestamp_date(s_cast, time_unit)
            elif isinstance(dtype, dtypes.Datetime):
                original_time_unit = dtype.time_unit
                s_cast = (
                    s.astype("Int64[pyarrow]") if is_pyarrow_dtype else s.astype("int64")
                )
                result = calculate_timestamp_datetime(
                    s_cast, original_time_unit, time_unit
                )
            else:
                msg = "Input should be either of Date or Datetime type"
                raise TypeError(msg)
            return result.where(~mask_na)  # pyright: ignore[reportReturnType]

        return self._compliant_expr._from_call(func, "datetime", time_unit=time_unit)

    def total_minutes(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.total_seconds() // 60, "total_minutes"
        )

    def total_seconds(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.total_seconds() // 1, "total_seconds"
        )

    def total_milliseconds(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.total_seconds() * 1000 // 1, "total_milliseconds"
        )

    def total_microseconds(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.total_seconds() * 1_000_000 // 1,
            "total_microseconds",
        )

    def total_nanoseconds(self: Self) -> DaskExpr:
        return self._compliant_expr._from_call(
            lambda _input: _input.dt.total_seconds() * 1_000_000_000 // 1,
            "total_nanoseconds",
        )
