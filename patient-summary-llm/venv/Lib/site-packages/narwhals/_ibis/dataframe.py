from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any

import ibis.selectors as s

from narwhals.dependencies import get_ibis
from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import import_dtypes_module
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from types import ModuleType

    import pandas as pd
    import pyarrow as pa
    from typing_extensions import Self

    from narwhals._ibis.series import IbisInterchangeSeries
    from narwhals.dtypes import DType


@lru_cache(maxsize=16)
def native_to_narwhals_dtype(ibis_dtype: Any, version: Version) -> DType:
    dtypes = import_dtypes_module(version)
    if ibis_dtype.is_int64():
        return dtypes.Int64()
    if ibis_dtype.is_int32():
        return dtypes.Int32()
    if ibis_dtype.is_int16():
        return dtypes.Int16()
    if ibis_dtype.is_int8():
        return dtypes.Int8()
    if ibis_dtype.is_uint64():
        return dtypes.UInt64()
    if ibis_dtype.is_uint32():
        return dtypes.UInt32()
    if ibis_dtype.is_uint16():
        return dtypes.UInt16()
    if ibis_dtype.is_uint8():
        return dtypes.UInt8()
    if ibis_dtype.is_boolean():
        return dtypes.Boolean()
    if ibis_dtype.is_float64():
        return dtypes.Float64()
    if ibis_dtype.is_float32():
        return dtypes.Float32()
    if ibis_dtype.is_string():
        return dtypes.String()
    if ibis_dtype.is_date():
        return dtypes.Date()
    if ibis_dtype.is_timestamp():
        return dtypes.Datetime()
    if ibis_dtype.is_array():
        return dtypes.List(native_to_narwhals_dtype(ibis_dtype.value_type, version))
    if ibis_dtype.is_struct():
        return dtypes.Struct(
            [
                dtypes.Field(
                    ibis_dtype_name,
                    native_to_narwhals_dtype(ibis_dtype_field, version),
                )
                for ibis_dtype_name, ibis_dtype_field in ibis_dtype.items()
            ]
        )
    if ibis_dtype.is_decimal():  # pragma: no cover
        # TODO(unassigned): cover this
        return dtypes.Decimal()
    return dtypes.Unknown()  # pragma: no cover


class IbisLazyFrame:
    _implementation = Implementation.IBIS

    def __init__(
        self, df: Any, *, backend_version: tuple[int, ...], version: Version
    ) -> None:
        self._native_frame = df
        self._version = version
        self._backend_version = backend_version
        validate_backend_version(self._implementation, self._backend_version)

    def __narwhals_dataframe__(self) -> Any:  # pragma: no cover
        # Keep around for backcompat.
        if self._version is not Version.V1:
            msg = "__narwhals_dataframe__ is not implemented for IbisLazyFrame"
            raise AttributeError(msg)
        return self

    def __narwhals_lazyframe__(self) -> Any:
        return self

    def __native_namespace__(self: Self) -> ModuleType:
        return get_ibis()

    def __getitem__(self, item: str) -> IbisInterchangeSeries:
        from narwhals._ibis.series import IbisInterchangeSeries

        return IbisInterchangeSeries(self._native_frame[item], version=self._version)

    def to_pandas(self: Self) -> pd.DataFrame:
        return self._native_frame.to_pandas()

    def to_arrow(self: Self) -> pa.Table:
        return self._native_frame.to_pyarrow()

    def simple_select(self, *column_names: str) -> Self:
        return self._from_native_frame(self._native_frame.select(s.cols(*column_names)))

    def aggregate(self: Self, *exprs: Any) -> Self:
        raise NotImplementedError

    def select(
        self: Self,
        *exprs: Any,
    ) -> Self:
        msg = (
            "`select`-ing not by name is not supported for Ibis backend.\n\n"
            "If you would like to see this kind of object better supported in "
            "Narwhals, please open a feature request "
            "at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)

    def __getattr__(self, attr: str) -> Any:
        if attr == "schema":
            return {
                column_name: native_to_narwhals_dtype(ibis_dtype, self._version)
                for column_name, ibis_dtype in self._native_frame.schema().items()
            }
        elif attr == "columns":
            return list(self._native_frame.columns)
        msg = (
            f"Attribute {attr} is not supported for metadata-only dataframes.\n\n"
            "If you would like to see this kind of object better supported in "
            "Narwhals, please open a feature request "
            "at https://github.com/narwhals-dev/narwhals/issues."
        )
        raise NotImplementedError(msg)

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame, version=version, backend_version=self._backend_version
        )

    def _from_native_frame(self: Self, df: Any) -> Self:
        return self.__class__(
            df, version=self._version, backend_version=self._backend_version
        )

    def collect_schema(self) -> dict[str, DType]:
        return {
            column_name: native_to_narwhals_dtype(ibis_dtype, self._version)
            for column_name, ibis_dtype in self._native_frame.schema().items()
        }
