from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING
from typing import Any
from typing import TypeVar
from typing import overload

import polars as pl

from narwhals.exceptions import ColumnNotFoundError
from narwhals.exceptions import ComputeError
from narwhals.exceptions import InvalidOperationError
from narwhals.exceptions import NarwhalsError
from narwhals.exceptions import ShapeError
from narwhals.utils import import_dtypes_module
from narwhals.utils import isinstance_or_issubclass

if TYPE_CHECKING:
    from narwhals._polars.dataframe import PolarsDataFrame
    from narwhals._polars.dataframe import PolarsLazyFrame
    from narwhals._polars.expr import PolarsExpr
    from narwhals._polars.series import PolarsSeries
    from narwhals.dtypes import DType
    from narwhals.typing import TimeUnit
    from narwhals.utils import Version

    T = TypeVar("T")


@overload
def extract_native(obj: PolarsDataFrame) -> pl.DataFrame: ...


@overload
def extract_native(obj: PolarsLazyFrame) -> pl.LazyFrame: ...


@overload
def extract_native(obj: PolarsSeries) -> pl.Series: ...


@overload
def extract_native(obj: PolarsExpr) -> pl.Expr: ...


@overload
def extract_native(obj: T) -> T: ...


def extract_native(
    obj: PolarsDataFrame | PolarsLazyFrame | PolarsSeries | PolarsExpr | T,
) -> pl.DataFrame | pl.LazyFrame | pl.Series | pl.Expr | T:
    from narwhals._polars.dataframe import PolarsDataFrame
    from narwhals._polars.dataframe import PolarsLazyFrame
    from narwhals._polars.expr import PolarsExpr
    from narwhals._polars.series import PolarsSeries

    if isinstance(obj, (PolarsDataFrame, PolarsLazyFrame)):
        return obj._native_frame
    if isinstance(obj, PolarsSeries):
        return obj._native_series
    if isinstance(obj, PolarsExpr):
        return obj._native_expr
    return obj


def extract_args_kwargs(args: Any, kwargs: Any) -> tuple[list[Any], dict[str, Any]]:
    return [extract_native(arg) for arg in args], {
        k: extract_native(v) for k, v in kwargs.items()
    }


@lru_cache(maxsize=16)
def native_to_narwhals_dtype(
    dtype: pl.DataType,
    version: Version,
    backend_version: tuple[int, ...],
) -> DType:
    dtypes = import_dtypes_module(version)
    if dtype == pl.Float64:
        return dtypes.Float64()
    if dtype == pl.Float32:
        return dtypes.Float32()
    if dtype == getattr(pl, "Int128", None):  # type: ignore[operator]  # pragma: no cover
        # Not available for Polars pre 1.8.0
        return dtypes.Int128()
    if dtype == pl.Int64:
        return dtypes.Int64()
    if dtype == pl.Int32:
        return dtypes.Int32()
    if dtype == pl.Int16:
        return dtypes.Int16()
    if dtype == pl.Int8:
        return dtypes.Int8()
    if dtype == getattr(pl, "UInt128", None):  # type: ignore[operator]  # pragma: no cover
        # Not available for Polars pre 1.8.0
        return dtypes.UInt128()
    if dtype == pl.UInt64:
        return dtypes.UInt64()
    if dtype == pl.UInt32:
        return dtypes.UInt32()
    if dtype == pl.UInt16:
        return dtypes.UInt16()
    if dtype == pl.UInt8:
        return dtypes.UInt8()
    if dtype == pl.String:
        return dtypes.String()
    if dtype == pl.Boolean:
        return dtypes.Boolean()
    if dtype == pl.Object:
        return dtypes.Object()
    if dtype == pl.Categorical:
        return dtypes.Categorical()
    if dtype == pl.Enum:
        return dtypes.Enum()
    if dtype == pl.Date:
        return dtypes.Date()
    if dtype == pl.Datetime:
        dt_time_unit: TimeUnit = getattr(dtype, "time_unit", "us")
        dt_time_zone = getattr(dtype, "time_zone", None)
        return dtypes.Datetime(time_unit=dt_time_unit, time_zone=dt_time_zone)
    if dtype == pl.Duration:
        du_time_unit: TimeUnit = getattr(dtype, "time_unit", "us")
        return dtypes.Duration(time_unit=du_time_unit)
    if dtype == pl.Struct:
        return dtypes.Struct(
            [
                dtypes.Field(
                    field_name,
                    native_to_narwhals_dtype(field_type, version, backend_version),
                )
                for field_name, field_type in dtype  # type: ignore[attr-defined]
            ]
        )
    if dtype == pl.List:
        return dtypes.List(
            native_to_narwhals_dtype(dtype.inner, version, backend_version)  # type: ignore[attr-defined]
        )
    if dtype == pl.Array:
        outer_shape = dtype.width if backend_version < (0, 20, 30) else dtype.size  # type: ignore[attr-defined]
        return dtypes.Array(
            inner=native_to_narwhals_dtype(dtype.inner, version, backend_version),  # type: ignore[attr-defined]
            shape=outer_shape,
        )
    if dtype == pl.Decimal:
        return dtypes.Decimal()
    return dtypes.Unknown()


def narwhals_to_native_dtype(
    dtype: DType | type[DType], version: Version, backend_version: tuple[int, ...]
) -> pl.DataType:
    dtypes = import_dtypes_module(version)
    if dtype == dtypes.Float64:
        return pl.Float64()
    if dtype == dtypes.Float32:
        return pl.Float32()
    if dtype == dtypes.Int128 and getattr(pl, "Int128", None) is not None:
        # Not available for Polars pre 1.8.0
        return pl.Int128()
    if dtype == dtypes.Int64:
        return pl.Int64()
    if dtype == dtypes.Int32:
        return pl.Int32()
    if dtype == dtypes.Int16:
        return pl.Int16()
    if dtype == dtypes.Int8:
        return pl.Int8()
    if dtype == dtypes.UInt64:
        return pl.UInt64()
    if dtype == dtypes.UInt32:
        return pl.UInt32()
    if dtype == dtypes.UInt16:
        return pl.UInt16()
    if dtype == dtypes.UInt8:
        return pl.UInt8()
    if dtype == dtypes.String:
        return pl.String()
    if dtype == dtypes.Boolean:
        return pl.Boolean()
    if dtype == dtypes.Object:  # pragma: no cover
        return pl.Object()
    if dtype == dtypes.Categorical:
        return pl.Categorical()
    if dtype == dtypes.Enum:
        msg = "Converting to Enum is not (yet) supported"
        raise NotImplementedError(msg)
    if dtype == dtypes.Date:
        return pl.Date()
    if dtype == dtypes.Decimal:
        msg = "Casting to Decimal is not supported yet."
        raise NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, dtypes.Datetime):
        return pl.Datetime(dtype.time_unit, dtype.time_zone)  # type: ignore[arg-type]
    if isinstance_or_issubclass(dtype, dtypes.Duration):
        return pl.Duration(dtype.time_unit)  # type: ignore[arg-type]
    if dtype == dtypes.List:
        return pl.List(narwhals_to_native_dtype(dtype.inner, version, backend_version))  # type: ignore[union-attr]
    if dtype == dtypes.Struct:
        return pl.Struct(
            fields=[
                pl.Field(
                    name=field.name,
                    dtype=narwhals_to_native_dtype(field.dtype, version, backend_version),
                )
                for field in dtype.fields  # type: ignore[union-attr]
            ]
        )
    if dtype == dtypes.Array:  # pragma: no cover
        size = dtype.size  # type: ignore[union-attr]
        kwargs = {"width": size} if backend_version < (0, 20, 30) else {"shape": size}
        return pl.Array(
            inner=narwhals_to_native_dtype(dtype.inner, version, backend_version),  # type: ignore[union-attr]
            **kwargs,
        )
    return pl.Unknown()  # pragma: no cover


def convert_str_slice_to_int_slice(
    str_slice: slice, columns: list[str]
) -> tuple[int | None, int | None, int | None]:  # pragma: no cover
    start = columns.index(str_slice.start) if str_slice.start is not None else None
    stop = columns.index(str_slice.stop) + 1 if str_slice.stop is not None else None
    step = str_slice.step
    return (start, stop, step)


def catch_polars_exception(
    exception: Exception, backend_version: tuple[int, ...]
) -> NarwhalsError | Exception:
    if isinstance(exception, pl.exceptions.ColumnNotFoundError):
        return ColumnNotFoundError(str(exception))
    elif isinstance(exception, pl.exceptions.ShapeError):
        return ShapeError(str(exception))
    elif isinstance(exception, pl.exceptions.InvalidOperationError):
        return InvalidOperationError(str(exception))
    elif isinstance(exception, pl.exceptions.ComputeError):
        return ComputeError(str(exception))
    if backend_version >= (1,) and isinstance(exception, pl.exceptions.PolarsError):
        # Old versions of Polars didn't have PolarsError.
        return NarwhalsError(str(exception))
    elif backend_version < (1,) and "polars.exceptions" in str(
        type(exception)
    ):  # pragma: no cover
        # Last attempt, for old Polars versions.
        return NarwhalsError(str(exception))
    # Just return exception as-is.
    return exception
