from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._pandas_like.utils import get_dtype_backend
from narwhals._pandas_like.utils import to_datetime
from narwhals.utils import Implementation

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.series import PandasLikeSeries


class PandasLikeSeriesStringNamespace:
    def __init__(self: Self, series: PandasLikeSeries) -> None:
        self._compliant_series = series

    def len_chars(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.len()
        )

    def replace(
        self: Self, pattern: str, value: str, *, literal: bool, n: int
    ) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.replace(
                pat=pattern, repl=value, n=n, regex=not literal
            ),
        )

    def replace_all(
        self: Self, pattern: str, value: str, *, literal: bool
    ) -> PandasLikeSeries:
        return self.replace(pattern, value, literal=literal, n=-1)

    def strip_chars(self: Self, characters: str | None) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.strip(characters),
        )

    def starts_with(self: Self, prefix: str) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.startswith(prefix),
        )

    def ends_with(self: Self, suffix: str) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.endswith(suffix),
        )

    def contains(self: Self, pattern: str, *, literal: bool) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.contains(
                pat=pattern, regex=not literal
            )
        )

    def slice(self: Self, offset: int, length: int | None) -> PandasLikeSeries:
        stop = offset + length if length else None
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.slice(start=offset, stop=stop),
        )

    def split(self: Self, by: str) -> PandasLikeSeries:
        if (
            self._compliant_series._implementation is not Implementation.CUDF
        ):  # pragma: no cover
            dtype_backend = get_dtype_backend(
                self._compliant_series._native_series.dtype,
                self._compliant_series._implementation,
            )
            if dtype_backend != "pyarrow":
                msg = (
                    "This operation requires a pyarrow-backed series. "
                    "Please refer to https://narwhals-dev.github.io/narwhals/api-reference/narwhals/#narwhals.maybe_convert_dtypes "
                    "and ensure you are using dtype_backend='pyarrow'. "
                    "Additionally, make sure you have pandas version 1.5+ and pyarrow installed. "
                )
                raise TypeError(msg)

        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.split(pat=by),
        )

    def to_datetime(self: Self, format: str | None) -> PandasLikeSeries:  # noqa: A002
        if format is not None and any(x in format for x in ("%z", "Z")):
            # We know that the inputs are timezone-aware, so we can directly pass
            # `utc=True` for better performance.
            return self._compliant_series._from_native_series(
                to_datetime(self._compliant_series._implementation, utc=True)(
                    self._compliant_series._native_series, format=format
                )
            )
        result = self._compliant_series._from_native_series(
            to_datetime(self._compliant_series._implementation, utc=False)(
                self._compliant_series._native_series, format=format
            )
        )
        result_time_zone = result.dtype.time_zone  # type: ignore[attr-defined]
        if result_time_zone is not None and result_time_zone != "UTC":
            result = result.dt.convert_time_zone("UTC")
        return result

    def to_uppercase(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.upper(),
        )

    def to_lowercase(self: Self) -> PandasLikeSeries:
        return self._compliant_series._from_native_series(
            self._compliant_series._native_series.str.lower(),
        )
