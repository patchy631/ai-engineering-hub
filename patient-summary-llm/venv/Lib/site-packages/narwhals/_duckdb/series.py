from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._duckdb.utils import native_to_narwhals_dtype
from narwhals.dependencies import get_duckdb

if TYPE_CHECKING:
    from types import ModuleType

    import duckdb
    from typing_extensions import Never
    from typing_extensions import Self

    from narwhals.dtypes import DType
    from narwhals.utils import Version


class DuckDBInterchangeSeries:
    def __init__(self: Self, df: duckdb.DuckDBPyRelation, version: Version) -> None:
        self._native_series = df
        self._version = version

    def __narwhals_series__(self: Self) -> Self:
        return self

    def __native_namespace__(self: Self) -> ModuleType:
        return get_duckdb()  # type: ignore[no-any-return]

    @property
    def dtype(self: Self) -> DType:
        return native_to_narwhals_dtype(str(self._native_series.types[0]), self._version)

    def __getattr__(self: Self, attr: str) -> Never:
        msg = (  # pragma: no cover
            f"Attribute {attr} is not supported for metadata-only dataframes.\n\n"
            "If you would like to see this kind of object better supported in "
            "Narwhals, please open a feature request "
            "at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)  # pragma: no cover
