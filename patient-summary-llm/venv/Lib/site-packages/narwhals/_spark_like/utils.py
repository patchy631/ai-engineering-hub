from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from narwhals.exceptions import UnsupportedDTypeError
from narwhals.utils import Implementation
from narwhals.utils import import_dtypes_module
from narwhals.utils import isinstance_or_issubclass

if TYPE_CHECKING:
    from types import ModuleType

    import pyspark.sql.types as pyspark_types
    import sqlframe.base.types as sqlframe_types
    from pyspark.sql import Column
    from typing_extensions import TypeAlias

    from narwhals._spark_like.dataframe import SparkLikeLazyFrame
    from narwhals._spark_like.expr import SparkLikeExpr
    from narwhals.dtypes import DType
    from narwhals.utils import Version

    _NativeDType: TypeAlias = "pyspark_types.DataType | sqlframe_types.DataType"


# NOTE: don't lru_cache this as `ModuleType` isn't hashable
def native_to_narwhals_dtype(
    dtype: _NativeDType, version: Version, spark_types: ModuleType
) -> DType:  # pragma: no cover
    dtypes = import_dtypes_module(version=version)
    if TYPE_CHECKING:
        native = pyspark_types
    else:
        native = spark_types

    if isinstance(dtype, native.DoubleType):
        return dtypes.Float64()
    if isinstance(dtype, native.FloatType):
        return dtypes.Float32()
    if isinstance(dtype, native.LongType):
        return dtypes.Int64()
    if isinstance(dtype, native.IntegerType):
        return dtypes.Int32()
    if isinstance(dtype, native.ShortType):
        return dtypes.Int16()
    if isinstance(dtype, native.ByteType):
        return dtypes.Int8()
    if isinstance(dtype, (native.StringType, native.VarcharType, native.CharType)):
        return dtypes.String()
    if isinstance(dtype, native.BooleanType):
        return dtypes.Boolean()
    if isinstance(dtype, native.DateType):
        return dtypes.Date()
    if isinstance(dtype, native.TimestampNTZType):
        return dtypes.Datetime()
    if isinstance(dtype, native.TimestampType):
        # TODO(marco): is UTC correct, or should we be getting the connection timezone?
        # https://github.com/narwhals-dev/narwhals/issues/2165
        return dtypes.Datetime(time_zone="UTC")
    if isinstance(dtype, native.DecimalType):
        return dtypes.Decimal()
    if isinstance(dtype, native.ArrayType):
        return dtypes.List(
            inner=native_to_narwhals_dtype(
                dtype.elementType, version=version, spark_types=spark_types
            )
        )
    if isinstance(dtype, native.StructType):
        return dtypes.Struct(
            fields=[
                dtypes.Field(
                    name=field.name,
                    dtype=native_to_narwhals_dtype(
                        field.dataType, version=version, spark_types=spark_types
                    ),
                )
                for field in dtype
            ]
        )
    return dtypes.Unknown()


def narwhals_to_native_dtype(
    dtype: DType | type[DType], version: Version, spark_types: ModuleType
) -> pyspark_types.DataType:
    dtypes = import_dtypes_module(version)
    if TYPE_CHECKING:
        native = pyspark_types
    else:
        native = spark_types

    if isinstance_or_issubclass(dtype, dtypes.Float64):
        return native.DoubleType()
    if isinstance_or_issubclass(dtype, dtypes.Float32):
        return native.FloatType()
    if isinstance_or_issubclass(dtype, dtypes.Int64):
        return native.LongType()
    if isinstance_or_issubclass(dtype, dtypes.Int32):
        return native.IntegerType()
    if isinstance_or_issubclass(dtype, dtypes.Int16):
        return native.ShortType()
    if isinstance_or_issubclass(dtype, dtypes.Int8):
        return native.ByteType()
    if isinstance_or_issubclass(dtype, dtypes.String):
        return native.StringType()
    if isinstance_or_issubclass(dtype, dtypes.Boolean):
        return native.BooleanType()
    if isinstance_or_issubclass(dtype, dtypes.Date):
        return native.DateType()
    if isinstance_or_issubclass(dtype, dtypes.Datetime):
        dt_time_zone = dtype.time_zone
        if dt_time_zone is None:
            return native.TimestampNTZType()
        if dt_time_zone != "UTC":  # pragma: no cover
            msg = f"Only UTC time zone is supported for PySpark, got: {dt_time_zone}"
            raise ValueError(msg)
        return native.TimestampType()
    if isinstance_or_issubclass(dtype, (dtypes.List, dtypes.Array)):
        return native.ArrayType(
            elementType=narwhals_to_native_dtype(
                dtype.inner, version=version, spark_types=native
            )
        )
    if isinstance_or_issubclass(dtype, dtypes.Struct):  # pragma: no cover
        return native.StructType(
            fields=[
                native.StructField(
                    name=field.name,
                    dataType=narwhals_to_native_dtype(
                        field.dtype, version=version, spark_types=native
                    ),
                )
                for field in dtype.fields
            ]
        )

    if isinstance_or_issubclass(
        dtype,
        (
            dtypes.UInt64,
            dtypes.UInt32,
            dtypes.UInt16,
            dtypes.UInt8,
            dtypes.Enum,
            dtypes.Categorical,
        ),
    ):  # pragma: no cover
        msg = "Unsigned integer, Enum and Categorical types are not supported by spark-like backend"
        raise UnsupportedDTypeError(msg)

    msg = f"Unknown dtype: {dtype}"  # pragma: no cover
    raise AssertionError(msg)


def evaluate_exprs(
    df: SparkLikeLazyFrame, /, *exprs: SparkLikeExpr
) -> list[tuple[str, Column]]:
    native_results: list[tuple[str, Column]] = []

    for expr in exprs:
        native_series_list = expr._call(df)
        output_names = expr._evaluate_output_names(df)
        if expr._alias_output_names is not None:
            output_names = expr._alias_output_names(output_names)
        if len(output_names) != len(native_series_list):  # pragma: no cover
            msg = f"Internal error: got output names {output_names}, but only got {len(native_series_list)} results"
            raise AssertionError(msg)
        native_results.extend(zip(output_names, native_series_list))

    return native_results


def maybe_evaluate_expr(df: SparkLikeLazyFrame, obj: SparkLikeExpr | object) -> Column:
    from narwhals._spark_like.expr import SparkLikeExpr

    if isinstance(obj, SparkLikeExpr):
        column_results = obj._call(df)
        if len(column_results) != 1:
            msg = "Multi-output expressions (e.g. `nw.all()` or `nw.col('a', 'b')`) not supported in this context"
            raise ValueError(msg)
        return column_results[0]
    return df._F.lit(obj)


def _std(
    _input: Column | str,
    ddof: int,
    np_version: tuple[int, ...],
    functions: Any,
    implementation: Implementation,
) -> Column:
    if implementation is Implementation.SQLFRAME or np_version > (2, 0):
        if ddof == 0:
            return functions.stddev_pop(_input)
        if ddof == 1:
            return functions.stddev_samp(_input)

        n_rows = functions.count(_input)
        return functions.stddev_samp(_input) * functions.sqrt(
            (n_rows - 1) / (n_rows - ddof)
        )

    from pyspark.pandas.spark.functions import stddev

    input_col = functions.col(_input) if isinstance(_input, str) else _input
    return stddev(input_col, ddof=ddof)


def _var(
    _input: Column | str,
    ddof: int,
    np_version: tuple[int, ...],
    functions: Any,
    implementation: Implementation,
) -> Column:
    if implementation is Implementation.SQLFRAME or np_version > (2, 0):
        if ddof == 0:
            return functions.var_pop(_input)
        if ddof == 1:
            return functions.var_samp(_input)

        n_rows = functions.count(_input)
        return functions.var_samp(_input) * (n_rows - 1) / (n_rows - ddof)

    from pyspark.pandas.spark.functions import var

    input_col = functions.col(_input) if isinstance(_input, str) else _input
    return var(input_col, ddof=ddof)
