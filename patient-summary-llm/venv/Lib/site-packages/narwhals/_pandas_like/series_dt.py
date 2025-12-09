from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from narwhals._pandas_like.utils import calculate_timestamp_date
from narwhals._pandas_like.utils import calculate_timestamp_datetime
from narwhals._pandas_like.utils import int_dtype_mapper
from narwhals.utils import Implementation
from narwhals.utils import import_dtypes_module

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.series import PandasLikeSeries
    from narwhals.typing import TimeUnit


class PandasLikeSeriesDateTimeNamespace:
    def __init__(self: Self, series: PandasLikeSeries) -> None:
        self._compliant_series = series

    def date(self: Self) -> PandasLikeSeries:
        result = self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.date,
        )
        if str(result.dtype).lower() == "object":
            msg = (
                "Accessing `date` on the default pandas backend "
                "will return a Series of type `object`."
                "\nThis differs from polars API and will prevent `.dt` chaining. "
                "Please switch to the `pyarrow` backend:"
                '\ndf.convert_dtypes(dtype_backend="pyarrow")'
            )
            raise NotImplementedError(msg)
        return result

    def year(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.year,
        )

    def month(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.month,
        )

    def day(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.day,
        )

    def hour(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.hour,
        )

    def minute(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.minute,
        )

    def second(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.second,
        )

    def millisecond(self: Self) -> PandasLikeSeries:
        return self.microsecond() // 1000

    def microsecond(self: Self) -> PandasLikeSeries:
        if self._compliant_series._backend_version < (3, 0, 0) and "pyarrow" in str(
            self._compliant_series._native_series.dtype
        ):
            # crazy workaround for https://github.com/pandas-dev/pandas/issues/59154
            import pyarrow.compute as pc  # ignore-banned-import()

            native_series = self._compliant_series._native_series
            arr = native_series.array.__arrow_array__()
            result_arr = pc.add(
                pc.multiply(pc.millisecond(arr), 1000), pc.microsecond(arr)
            )
            result = native_series.__class__(
                native_series.array.__class__(result_arr), name=native_series.name
            )
            return self._compliant_series._from_native_series(result)

        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.microsecond
        )

    def nanosecond(self: Self) -> PandasLikeSeries:
        return (
            self.microsecond() * 1_000
            + self._compliant_series._native_series.dt.nanosecond
        )

    def ordinal_day(self: Self) -> PandasLikeSeries:
        ser = self._compliant_series._native_series
        year_start = ser.dt.year
        result = (
            ser.to_numpy().astype("datetime64[D]")
            - (year_start.to_numpy() - 1970).astype("datetime64[Y]")
        ).astype("int32") + 1
        dtype = "Int64[pyarrow]" if "pyarrow" in str(ser.dtype) else "int32"
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.__class__(
                result, dtype=dtype, name=year_start.name
            )
        )

    def weekday(self: Self) -> PandasLikeSeries:
        return (
            self._compliant_series._from_native_series(
                self._compliant_series._native_series.dt.weekday,
            )
            + 1  # Pandas is 0-6 while Polars is 1-7
        )

    def _get_total_seconds(self: Self) -> Any:
        if hasattr(self._compliant_series._native_series.dt, "total_seconds"):
            return self._compliant_series._native_series.dt.total_seconds()
        else:  # pragma: no cover
            return (
                self._compliant_series._native_series.dt.days * 86400
                + self._compliant_series._native_series.dt.seconds
                + (self._compliant_series._native_series.dt.microseconds / 1e6)
                + (self._compliant_series._native_series.dt.nanoseconds / 1e9)
            )

    def total_minutes(self: Self) -> PandasLikeSeries:
        s = self._get_total_seconds()
        s_sign = (
            2 * (s > 0).astype(int_dtype_mapper(s.dtype)) - 1
        )  # this calculates the sign of each series element
        s_abs = s.abs() // 60
        if ~s.isna().any():
            s_abs = s_abs.astype(int_dtype_mapper(s.dtype))
        return self._compliant_series._from_native_series(s_abs * s_sign)

    def total_seconds(self: Self) -> PandasLikeSeries:
        s = self._get_total_seconds()
        s_sign = (
            2 * (s > 0).astype(int_dtype_mapper(s.dtype)) - 1
        )  # this calculates the sign of each series element
        s_abs = s.abs() // 1
        if ~s.isna().any():
            s_abs = s_abs.astype(int_dtype_mapper(s.dtype))
        return self._compliant_series._from_native_series(s_abs * s_sign)

    def total_milliseconds(self: Self) -> PandasLikeSeries:
        s = self._get_total_seconds() * 1e3
        s_sign = (
            2 * (s > 0).astype(int_dtype_mapper(s.dtype)) - 1
        )  # this calculates the sign of each series element
        s_abs = s.abs() // 1
        if ~s.isna().any():
            s_abs = s_abs.astype(int_dtype_mapper(s.dtype))
        return self._compliant_series._from_native_series(s_abs * s_sign)

    def total_microseconds(self: Self) -> PandasLikeSeries:
        s = self._get_total_seconds() * 1e6
        s_sign = (
            2 * (s > 0).astype(int_dtype_mapper(s.dtype)) - 1
        )  # this calculates the sign of each series element
        s_abs = s.abs() // 1
        if ~s.isna().any():
            s_abs = s_abs.astype(int_dtype_mapper(s.dtype))
        return self._compliant_series._from_native_series(s_abs * s_sign)

    def total_nanoseconds(self: Self) -> PandasLikeSeries:
        s = self._get_total_seconds() * 1e9
        s_sign = (
            2 * (s > 0).astype(int_dtype_mapper(s.dtype)) - 1
        )  # this calculates the sign of each series element
        s_abs = s.abs() // 1
        if ~s.isna().any():
            s_abs = s_abs.astype(int_dtype_mapper(s.dtype))
        return self._compliant_series._from_native_series(s_abs * s_sign)

    def to_string(self: Self, format: str) -> PandasLikeSeries:  # noqa: A002
        # Polars' parser treats `'%.f'` as pandas does `'.%f'`
        # PyArrow interprets `'%S'` as "seconds, plus fractional seconds"
        # and doesn't support `%f`
        if "pyarrow" not in str(self._compliant_series._native_series.dtype):
            format = format.replace("%S%.f", "%S.%f")
        else:
            format = format.replace("%S.%f", "%S").replace("%S%.f", "%S")
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.dt.strftime(format)
        )

    def replace_time_zone(self: Self, time_zone: str | None) -> PandasLikeSeries:
        if time_zone is not None:
            result = self._compliant_series._native_series.dt.tz_localize(
                None
            ).dt.tz_localize(time_zone)
        else:
            result = self._compliant_series._native_series.dt.tz_localize(None)
        return self._compliant_series._from_native_series(result)

    def convert_time_zone(self: Self, time_zone: str) -> PandasLikeSeries:
        if self._compliant_series.dtype.time_zone is None:  # type: ignore[attr-defined]
            result = self._compliant_series._native_series.dt.tz_localize(
                "UTC"
            ).dt.tz_convert(time_zone)
        else:
            result = self._compliant_series._native_series.dt.tz_convert(time_zone)
        return self._compliant_series._from_native_series(result)

    def timestamp(self: Self, time_unit: TimeUnit) -> PandasLikeSeries:
        s = self._compliant_series._native_series
        dtype = self._compliant_series.dtype
        is_pyarrow_dtype = "pyarrow" in str(self._compliant_series._native_series.dtype)
        mask_na = s.isna()
        dtypes = import_dtypes_module(self._compliant_series._version)
        if dtype == dtypes.Date:
            # Date is only supported in pandas dtypes if pyarrow-backed
            s_cast = s.astype("Int32[pyarrow]")
            result = calculate_timestamp_date(s_cast, time_unit)
        elif isinstance(dtype, dtypes.Datetime):
            original_time_unit = dtype.time_unit
            if (
                self._compliant_series._implementation is Implementation.PANDAS
                and self._compliant_series._backend_version < (2,)
            ):  # pragma: no cover
                s_cast = s.view("Int64[pyarrow]") if is_pyarrow_dtype else s.view("int64")
            else:
                s_cast = (
                    s.astype("Int64[pyarrow]") if is_pyarrow_dtype else s.astype("int64")
                )
            result = calculate_timestamp_datetime(s_cast, original_time_unit, time_unit)
        else:
            msg = "Input should be either of Date or Datetime type"
            raise TypeError(msg)
        result[mask_na] = None
        return self._compliant_series._from_native_series(result)
