from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import NoReturn

from narwhals._interchange.dataframe import map_interchange_dtype_to_narwhals_dtype

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.dtypes import DType
    from narwhals.utils import Version


class InterchangeSeries:
    def __init__(self: Self, df: Any, version: Version) -> None:
        self._native_series = df
        self._version = version

    def __narwhals_series__(self: Self) -> Self:
        return self

    def __native_namespace__(self: Self) -> NoReturn:
        msg = (
            "Cannot access native namespace for metadata-only series with unknown backend. "
            "If you would like to see this kind of object supported in Narwhals, please "
            "open a feature request at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)

    @property
    def dtype(self: Self) -> DType:
        return map_interchange_dtype_to_narwhals_dtype(
            self._native_series.dtype, version=self._version
        )

    def __getattr__(self: Self, attr: str) -> NoReturn:
        msg = (  # pragma: no cover
            f"Attribute {attr} is not supported for metadata-only dataframes.\n\n"
            "Hint: you probably called `nw.from_native` on an object which isn't fully "
            "supported by Narwhals, yet implements `__dataframe__`. If you would like to "
            "see this kind of object supported in Narwhals, please open a feature request "
            "at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)
