from __future__ import annotations

from functools import lru_cache
from itertools import chain
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Sequence
from typing import cast
from typing import overload

import pyarrow as pa
import pyarrow.compute as pc

from narwhals.utils import _ExprNamespace
from narwhals.utils import _SeriesNamespace
from narwhals.utils import import_dtypes_module
from narwhals.utils import isinstance_or_issubclass

if TYPE_CHECKING:
    from typing import TypeVar

    from typing_extensions import Self
    from typing_extensions import TypeAlias
    from typing_extensions import TypeIs

    from narwhals._arrow.expr import ArrowExpr
    from narwhals._arrow.series import ArrowSeries
    from narwhals._arrow.typing import ArrowArray
    from narwhals._arrow.typing import ArrowChunkedArray
    from narwhals._arrow.typing import Incomplete
    from narwhals._arrow.typing import StringArray
    from narwhals.dtypes import DType
    from narwhals.typing import _AnyDArray
    from narwhals.utils import Version

    # NOTE: stubs don't allow for `ChunkedArray[StructArray]`
    # Intended to represent the `.chunks` property storing `list[pa.StructArray]`
    ChunkedArrayStructArray: TypeAlias = ArrowChunkedArray

    _T = TypeVar("_T")

    def is_timestamp(t: Any) -> TypeIs[pa.TimestampType[Any, Any]]: ...
    def is_duration(t: Any) -> TypeIs[pa.DurationType[Any]]: ...
    def is_list(t: Any) -> TypeIs[pa.ListType[Any]]: ...
    def is_large_list(t: Any) -> TypeIs[pa.LargeListType[Any]]: ...
    def is_fixed_size_list(t: Any) -> TypeIs[pa.FixedSizeListType[Any, Any]]: ...
    def is_dictionary(
        t: Any,
    ) -> TypeIs[pa.DictionaryType[Any, Any, Any]]: ...
    def extract_regex(
        strings: ArrowChunkedArray,
        /,
        pattern: str,
        *,
        options: Any = None,
        memory_pool: Any = None,
    ) -> ChunkedArrayStructArray: ...
else:
    from pyarrow.compute import extract_regex
    from pyarrow.types import is_dictionary  # noqa: F401
    from pyarrow.types import is_duration
    from pyarrow.types import is_fixed_size_list
    from pyarrow.types import is_large_list
    from pyarrow.types import is_list
    from pyarrow.types import is_timestamp

lit = pa.scalar
"""Alias for `pyarrow.scalar`."""


def extract_py_scalar(value: Any, /) -> Any:
    from narwhals._arrow.series import maybe_extract_py_scalar

    return maybe_extract_py_scalar(value, return_py_scalar=True)


def chunked_array(
    arr: ArrowArray | list[Iterable[pa.Scalar[Any]]] | ArrowChunkedArray,
) -> ArrowChunkedArray:
    if isinstance(arr, pa.ChunkedArray):
        return arr
    if isinstance(arr, list):
        return pa.chunked_array(cast("Any", arr))
    else:
        return pa.chunked_array([arr], arr.type)


def nulls_like(n: int, series: ArrowSeries) -> ArrowArray:
    """Create a strongly-typed Array instance with all elements null.

    Uses the type of `series`, without upseting `mypy`.
    """
    nulls: Incomplete = pa.nulls
    return nulls(n, series._type)


@lru_cache(maxsize=16)
def native_to_narwhals_dtype(dtype: pa.DataType, version: Version) -> DType:
    dtypes = import_dtypes_module(version)
    if pa.types.is_int64(dtype):
        return dtypes.Int64()
    if pa.types.is_int32(dtype):
        return dtypes.Int32()
    if pa.types.is_int16(dtype):
        return dtypes.Int16()
    if pa.types.is_int8(dtype):
        return dtypes.Int8()
    if pa.types.is_uint64(dtype):
        return dtypes.UInt64()
    if pa.types.is_uint32(dtype):
        return dtypes.UInt32()
    if pa.types.is_uint16(dtype):
        return dtypes.UInt16()
    if pa.types.is_uint8(dtype):
        return dtypes.UInt8()
    if pa.types.is_boolean(dtype):
        return dtypes.Boolean()
    if pa.types.is_float64(dtype):
        return dtypes.Float64()
    if pa.types.is_float32(dtype):
        return dtypes.Float32()
    # bug in coverage? it shows `31->exit` (where `31` is currently the line number of
    # the next line), even though both when the if condition is true and false are covered
    if (  # pragma: no cover
        pa.types.is_string(dtype)
        or pa.types.is_large_string(dtype)
        or getattr(pa.types, "is_string_view", lambda _: False)(dtype)
    ):
        return dtypes.String()
    if pa.types.is_date32(dtype):
        return dtypes.Date()
    if is_timestamp(dtype):
        return dtypes.Datetime(time_unit=dtype.unit, time_zone=dtype.tz)
    if is_duration(dtype):
        return dtypes.Duration(time_unit=dtype.unit)
    if pa.types.is_dictionary(dtype):
        return dtypes.Categorical()
    if pa.types.is_struct(dtype):
        return dtypes.Struct(
            [
                dtypes.Field(
                    dtype.field(i).name,
                    native_to_narwhals_dtype(dtype.field(i).type, version),
                )
                for i in range(dtype.num_fields)
            ]
        )
    if is_list(dtype) or is_large_list(dtype):
        return dtypes.List(native_to_narwhals_dtype(dtype.value_type, version))
    if is_fixed_size_list(dtype):
        return dtypes.Array(
            native_to_narwhals_dtype(dtype.value_type, version), dtype.list_size
        )
    if pa.types.is_decimal(dtype):
        return dtypes.Decimal()
    return dtypes.Unknown()  # pragma: no cover


def narwhals_to_native_dtype(dtype: DType | type[DType], version: Version) -> pa.DataType:
    dtypes = import_dtypes_module(version)
    if isinstance_or_issubclass(dtype, dtypes.Decimal):
        msg = "Casting to Decimal is not supported yet."
        raise NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, dtypes.Float64):
        return pa.float64()
    if isinstance_or_issubclass(dtype, dtypes.Float32):
        return pa.float32()
    if isinstance_or_issubclass(dtype, dtypes.Int64):
        return pa.int64()
    if isinstance_or_issubclass(dtype, dtypes.Int32):
        return pa.int32()
    if isinstance_or_issubclass(dtype, dtypes.Int16):
        return pa.int16()
    if isinstance_or_issubclass(dtype, dtypes.Int8):
        return pa.int8()
    if isinstance_or_issubclass(dtype, dtypes.UInt64):
        return pa.uint64()
    if isinstance_or_issubclass(dtype, dtypes.UInt32):
        return pa.uint32()
    if isinstance_or_issubclass(dtype, dtypes.UInt16):
        return pa.uint16()
    if isinstance_or_issubclass(dtype, dtypes.UInt8):
        return pa.uint8()
    if isinstance_or_issubclass(dtype, dtypes.String):
        return pa.string()
    if isinstance_or_issubclass(dtype, dtypes.Boolean):
        return pa.bool_()
    if isinstance_or_issubclass(dtype, dtypes.Categorical):
        return pa.dictionary(pa.uint32(), pa.string())
    if isinstance_or_issubclass(dtype, dtypes.Datetime):
        return pa.timestamp(dtype.time_unit, tz=dtype.time_zone)  # pyright: ignore[reportArgumentType]
    if isinstance_or_issubclass(dtype, dtypes.Duration):
        return pa.duration(dtype.time_unit)
    if isinstance_or_issubclass(dtype, dtypes.Date):
        return pa.date32()
    if isinstance_or_issubclass(dtype, dtypes.List):
        return pa.list_(value_type=narwhals_to_native_dtype(dtype.inner, version=version))
    if isinstance_or_issubclass(dtype, dtypes.Struct):
        return pa.struct(
            [
                (field.name, narwhals_to_native_dtype(field.dtype, version=version))
                for field in dtype.fields
            ]
        )
    if isinstance_or_issubclass(dtype, dtypes.Array):  # pragma: no cover
        inner = narwhals_to_native_dtype(dtype.inner, version=version)
        list_size = dtype.size
        return pa.list_(inner, list_size=list_size)

    msg = f"Unknown dtype: {dtype}"  # pragma: no cover
    raise AssertionError(msg)


def extract_native(
    lhs: ArrowSeries, rhs: ArrowSeries | object
) -> tuple[
    ArrowChunkedArray | pa.Scalar[Any], ArrowChunkedArray | pa.Scalar[Any] | object
]:
    """Extract native objects in binary  operation.

    If the comparison isn't supported, return `NotImplemented` so that the
    "right-hand-side" operation (e.g. `__radd__`) can be tried.

    If one of the two sides has a `_broadcast` flag, then extract the scalar
    underneath it so that PyArrow can do its own broadcasting.
    """
    from narwhals._arrow.dataframe import ArrowDataFrame
    from narwhals._arrow.series import ArrowSeries

    if rhs is None:
        return lhs.native, lit(None, type=lhs._type)

    if isinstance(rhs, ArrowDataFrame):
        return NotImplemented

    if isinstance(rhs, ArrowSeries):
        if lhs._broadcast and not rhs._broadcast:
            return lhs.native[0], rhs.native
        if rhs._broadcast:
            return lhs.native, rhs.native[0]
        return lhs.native, rhs.native

    if isinstance(rhs, list):
        msg = "Expected Series or scalar, got list."
        raise TypeError(msg)
    return lhs.native, rhs


def align_series_full_broadcast(*series: ArrowSeries) -> Sequence[ArrowSeries]:
    # Ensure all of `series` are of the same length.
    lengths = [len(s) for s in series]
    max_length = max(lengths)
    fast_path = all(_len == max_length for _len in lengths)

    if fast_path:
        return series

    is_max_length_gt_1 = max_length > 1
    reshaped = []
    for s, length in zip(series, lengths):
        if is_max_length_gt_1 and length == 1:
            value = s.native[0]
            if s._backend_version < (13,) and hasattr(value, "as_py"):
                value = value.as_py()
            reshaped.append(
                s._from_native_series(pa.array([value] * max_length, type=s._type))
            )
        else:
            reshaped.append(s)

    return reshaped


def extract_dataframe_comparand(
    length: int,
    other: ArrowSeries,
    backend_version: tuple[int, ...],
) -> ArrowChunkedArray:
    """Extract native Series, broadcasting to `length` if necessary."""
    if not other._broadcast:
        return other.native

    import numpy as np  # ignore-banned-import

    value = other.native[0]
    if backend_version < (13,) and hasattr(value, "as_py"):
        value = value.as_py()
    return pa.chunked_array([np.full(shape=length, fill_value=value)])


def horizontal_concat(dfs: list[pa.Table]) -> pa.Table:
    """Concatenate (native) DataFrames horizontally.

    Should be in namespace.
    """
    names = [name for df in dfs for name in df.column_names]

    if len(set(names)) < len(names):  # pragma: no cover
        msg = "Expected unique column names"
        raise ValueError(msg)
    arrays = list(chain.from_iterable(df.itercolumns() for df in dfs))
    return pa.Table.from_arrays(arrays, names=names)


def vertical_concat(dfs: list[pa.Table]) -> pa.Table:
    """Concatenate (native) DataFrames vertically.

    Should be in namespace.
    """
    cols_0 = dfs[0].column_names
    for i, df in enumerate(dfs[1:], start=1):
        cols_current = df.column_names
        if cols_current != cols_0:
            msg = (
                "unable to vstack, column names don't match:\n"
                f"   - dataframe 0: {cols_0}\n"
                f"   - dataframe {i}: {cols_current}\n"
            )
            raise TypeError(msg)

    return pa.concat_tables(dfs)


def diagonal_concat(dfs: list[pa.Table], backend_version: tuple[int, ...]) -> pa.Table:
    """Concatenate (native) DataFrames diagonally.

    Should be in namespace.
    """
    kwargs: dict[str, Any] = (
        {"promote": True}
        if backend_version < (14, 0, 0)
        else {"promote_options": "default"}
    )
    return pa.concat_tables(dfs, **kwargs)


def floordiv_compat(left: Any, right: Any) -> Any:
    # The following lines are adapted from pandas' pyarrow implementation.
    # Ref: https://github.com/pandas-dev/pandas/blob/262fcfbffcee5c3116e86a951d8b693f90411e68/pandas/core/arrays/arrow/array.py#L124-L154
    if isinstance(left, (int, float)):
        left = lit(left)

    if isinstance(right, (int, float)):
        right = lit(right)

    if pa.types.is_integer(left.type) and pa.types.is_integer(right.type):
        divided = pc.divide_checked(left, right)
        if pa.types.is_signed_integer(divided.type):
            # GH 56676
            has_remainder = pc.not_equal(pc.multiply(divided, right), left)
            has_one_negative_operand = pc.less(
                pc.bit_wise_xor(left, right), lit(0, type=divided.type)
            )
            result = pc.if_else(
                pc.and_(has_remainder, has_one_negative_operand),
                # GH: 55561 ruff: ignore
                pc.subtract(divided, lit(1, type=divided.type)),
                divided,
            )
        else:
            result = divided  # pragma: no cover
        result = result.cast(left.type)
    else:
        divided = pc.divide(left, right)
        result = pc.floor(divided)
    return result


def cast_for_truediv(
    arrow_array: ArrowChunkedArray | pa.Scalar[Any],
    pa_object: ArrowChunkedArray | ArrowArray | pa.Scalar[Any],
) -> tuple[
    ArrowChunkedArray | pa.Scalar[Any],
    ArrowChunkedArray | ArrowArray | pa.Scalar[Any],
]:
    # Lifted from:
    # https://github.com/pandas-dev/pandas/blob/262fcfbffcee5c3116e86a951d8b693f90411e68/pandas/core/arrays/arrow/array.py#L108-L122
    # Ensure int / int -> float mirroring Python/Numpy behavior
    # as pc.divide_checked(int, int) -> int
    if pa.types.is_integer(arrow_array.type) and pa.types.is_integer(pa_object.type):
        # GH: 56645.  # noqa: ERA001
        # https://github.com/apache/arrow/issues/35563
        return pc.cast(arrow_array, pa.float64(), safe=False), pc.cast(
            pa_object, pa.float64(), safe=False
        )

    return arrow_array, pa_object


@overload
def convert_slice_to_nparray(num_rows: int, rows_slice: slice) -> _AnyDArray: ...
@overload
def convert_slice_to_nparray(num_rows: int, rows_slice: _T) -> _T: ...
def convert_slice_to_nparray(num_rows: int, rows_slice: slice | _T) -> _AnyDArray | _T:
    if isinstance(rows_slice, slice):
        import numpy as np  # ignore-banned-import

        return np.arange(num_rows)[rows_slice]
    else:
        return rows_slice


def select_rows(
    table: pa.Table, rows: slice | int | Sequence[int] | _AnyDArray
) -> pa.Table:
    if isinstance(rows, slice) and rows == slice(None):
        selected_rows = table
    elif isinstance(rows, Sequence) and not rows:
        selected_rows = table.slice(0, 0)
    else:
        range_ = convert_slice_to_nparray(num_rows=len(table), rows_slice=rows)
        selected_rows = table.take(cast("list[int]", range_))
    return selected_rows


def convert_str_slice_to_int_slice(
    str_slice: slice, columns: list[str]
) -> tuple[int | None, int | None, int | None]:
    start = columns.index(str_slice.start) if str_slice.start is not None else None
    stop = columns.index(str_slice.stop) + 1 if str_slice.stop is not None else None
    step = str_slice.step
    return (start, stop, step)


# Regex for date, time, separator and timezone components
DATE_RE = r"(?P<date>\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}|\d{8})"
SEP_RE = r"(?P<sep>\s|T)"
TIME_RE = r"(?P<time>\d{2}:\d{2}(?::\d{2})?|\d{6}?)"  # \s*(?P<period>[AP]M)?)?
HMS_RE = r"^(?P<hms>\d{2}:\d{2}:\d{2})$"
HM_RE = r"^(?P<hm>\d{2}:\d{2})$"
HMS_RE_NO_SEP = r"^(?P<hms_no_sep>\d{6})$"
TZ_RE = r"(?P<tz>Z|[+-]\d{2}:?\d{2})"  # Matches 'Z', '+02:00', '+0200', '+02', etc.
FULL_RE = rf"{DATE_RE}{SEP_RE}?{TIME_RE}?{TZ_RE}?$"

# Separate regexes for different date formats
YMD_RE = r"^(?P<year>(?:[12][0-9])?[0-9]{2})(?P<sep1>[-/.])(?P<month>0[1-9]|1[0-2])(?P<sep2>[-/.])(?P<day>0[1-9]|[12][0-9]|3[01])$"
DMY_RE = r"^(?P<day>0[1-9]|[12][0-9]|3[01])(?P<sep1>[-/.])(?P<month>0[1-9]|1[0-2])(?P<sep2>[-/.])(?P<year>(?:[12][0-9])?[0-9]{2})$"
MDY_RE = r"^(?P<month>0[1-9]|1[0-2])(?P<sep1>[-/.])(?P<day>0[1-9]|[12][0-9]|3[01])(?P<sep2>[-/.])(?P<year>(?:[12][0-9])?[0-9]{2})$"
YMD_RE_NO_SEP = r"^(?P<year>(?:[12][0-9])?[0-9]{2})(?P<month>0[1-9]|1[0-2])(?P<day>0[1-9]|[12][0-9]|3[01])$"

DATE_FORMATS = (
    (YMD_RE_NO_SEP, "%Y%m%d"),
    (YMD_RE, "%Y-%m-%d"),
    (DMY_RE, "%d-%m-%Y"),
    (MDY_RE, "%m-%d-%Y"),
)
TIME_FORMATS = ((HMS_RE, "%H:%M:%S"), (HM_RE, "%H:%M"), (HMS_RE_NO_SEP, "%H%M%S"))


def _extract_regex_concat_arrays(
    strings: ArrowChunkedArray,
    /,
    pattern: str,
    *,
    options: Any = None,
    memory_pool: Any = None,
) -> pa.StructArray:
    r = pa.concat_arrays(
        extract_regex(strings, pattern, options=options, memory_pool=memory_pool).chunks
    )
    return cast("pa.StructArray", r)


def parse_datetime_format(arr: ArrowChunkedArray) -> str:
    """Try to infer datetime format from StringArray."""
    matches = _extract_regex_concat_arrays(arr.drop_null().slice(0, 10), pattern=FULL_RE)
    if not pc.all(matches.is_valid()).as_py():
        msg = (
            "Unable to infer datetime format, provided format is not supported. "
            "Please report a bug to https://github.com/narwhals-dev/narwhals/issues"
        )
        raise NotImplementedError(msg)

    separators = matches.field("sep")
    tz = matches.field("tz")

    # separators and time zones must be unique
    if pc.count(pc.unique(separators)).as_py() > 1:
        msg = "Found multiple separator values while inferring datetime format."
        raise ValueError(msg)

    if pc.count(pc.unique(tz)).as_py() > 1:
        msg = "Found multiple timezone values while inferring datetime format."
        raise ValueError(msg)

    date_value = _parse_date_format(cast("StringArray", matches.field("date")))
    time_value = _parse_time_format(cast("StringArray", matches.field("time")))

    sep_value = separators[0].as_py()
    tz_value = "%z" if tz[0].as_py() else ""

    return f"{date_value}{sep_value}{time_value}{tz_value}"


def _parse_date_format(arr: StringArray) -> str:
    for date_rgx, date_fmt in DATE_FORMATS:
        matches = pc.extract_regex(arr, pattern=date_rgx)
        if date_fmt == "%Y%m%d" and pc.all(matches.is_valid()).as_py():
            return date_fmt
        elif (
            pc.all(matches.is_valid()).as_py()
            and pc.count(pc.unique(sep1 := matches.field("sep1"))).as_py() == 1
            and pc.count(pc.unique(sep2 := matches.field("sep2"))).as_py() == 1
            and (date_sep_value := sep1[0].as_py()) == sep2[0].as_py()
        ):
            return date_fmt.replace("-", date_sep_value)

    msg = (
        "Unable to infer datetime format. "
        "Please report a bug to https://github.com/narwhals-dev/narwhals/issues"
    )
    raise ValueError(msg)


def _parse_time_format(arr: StringArray) -> str:
    for time_rgx, time_fmt in TIME_FORMATS:
        matches = pc.extract_regex(arr, pattern=time_rgx)
        if pc.all(matches.is_valid()).as_py():
            return time_fmt
    return ""


def pad_series(
    series: ArrowSeries, *, window_size: int, center: bool
) -> tuple[ArrowSeries, int]:
    """Pad series with None values on the left and/or right side, depending on the specified parameters.

    Arguments:
        series: The input ArrowSeries to be padded.
        window_size: The desired size of the window.
        center: Specifies whether to center the padding or not.

    Returns:
        A tuple containing the padded ArrowSeries and the offset value.
    """
    if not center:
        return series, 0
    offset_left = window_size // 2
    # subtract one if window_size is even
    offset_right = offset_left - (window_size % 2 == 0)
    pad_left = pa.array([None] * offset_left, type=series._type)
    pad_right = pa.array([None] * offset_right, type=series._type)
    concat = pa.concat_arrays([pad_left, *series.native.chunks, pad_right])
    return series._from_native_series(concat), offset_left + offset_right


class ArrowSeriesNamespace(_SeriesNamespace["ArrowSeries", "ArrowChunkedArray"]):
    def __init__(self: Self, series: ArrowSeries, /) -> None:
        self._compliant_series = series


class ArrowExprNamespace(_ExprNamespace["ArrowExpr"]):
    def __init__(self: Self, expr: ArrowExpr, /) -> None:
        self._compliant_expr = expr
