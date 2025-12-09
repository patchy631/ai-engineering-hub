from __future__ import annotations

from collections import OrderedDict
from datetime import timezone
from itertools import starmap
from typing import TYPE_CHECKING
from typing import Mapping

from narwhals.utils import isinstance_or_issubclass

if TYPE_CHECKING:
    from typing import Iterator
    from typing import Sequence

    from typing_extensions import Self

    from narwhals.typing import TimeUnit


def _validate_dtype(dtype: DType | type[DType]) -> None:
    if not isinstance_or_issubclass(dtype, DType):
        msg = (
            f"Expected Narwhals dtype, got: {type(dtype)}.\n\n"
            "Hint: if you were trying to cast to a type, use e.g. nw.Int64 instead of 'int64'."
        )
        raise TypeError(msg)


class DType:
    def __repr__(self: Self) -> str:  # pragma: no cover
        return self.__class__.__qualname__

    @classmethod
    def is_numeric(cls: type[Self]) -> bool:
        return issubclass(cls, NumericType)

    @classmethod
    def is_integer(cls: type[Self]) -> bool:
        return issubclass(cls, IntegerType)

    @classmethod
    def is_signed_integer(cls: type[Self]) -> bool:
        return issubclass(cls, SignedIntegerType)

    @classmethod
    def is_unsigned_integer(cls: type[Self]) -> bool:
        return issubclass(cls, UnsignedIntegerType)

    @classmethod
    def is_float(cls: type[Self]) -> bool:
        return issubclass(cls, FloatType)

    @classmethod
    def is_decimal(cls: type[Self]) -> bool:
        return issubclass(cls, Decimal)

    @classmethod
    def is_temporal(cls: type[Self]) -> bool:
        return issubclass(cls, TemporalType)

    @classmethod
    def is_nested(cls: type[Self]) -> bool:
        return issubclass(cls, NestedType)

    def __eq__(self: Self, other: DType | type[DType]) -> bool:  # type: ignore[override]
        from narwhals.utils import isinstance_or_issubclass

        return isinstance_or_issubclass(other, type(self))

    def __hash__(self: Self) -> int:
        return hash(self.__class__)


class NumericType(DType):
    """Base class for numeric data types."""


class IntegerType(NumericType):
    """Base class for integer data types."""


class SignedIntegerType(IntegerType):
    """Base class for signed integer data types."""


class UnsignedIntegerType(IntegerType):
    """Base class for unsigned integer data types."""


class FloatType(NumericType):
    """Base class for float data types."""


class TemporalType(DType):
    """Base class for temporal data types."""


class NestedType(DType):
    """Base class for nested data types."""


class Decimal(NumericType):
    """Decimal type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s = pl.Series(["1.5"], dtype=pl.Decimal)
        >>> nw.from_native(s, series_only=True).dtype
        Decimal
    """


class Int128(SignedIntegerType):
    """128-bit signed integer type."""


class Int64(SignedIntegerType):
    """64-bit signed integer type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Int64).dtype
        Int64
    """


class Int32(SignedIntegerType):
    """32-bit signed integer type.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>> s_native = pa.chunked_array([[2, 1, 3, 7]])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Int32).dtype
        Int32
    """


class Int16(SignedIntegerType):
    """16-bit signed integer type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Int16).dtype
        Int16
    """


class Int8(SignedIntegerType):
    """8-bit signed integer type.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> s_native = pd.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Int8).dtype
        Int8
    """


class UInt128(UnsignedIntegerType):
    """128-bit unsigned integer type."""


class UInt64(UnsignedIntegerType):
    """64-bit unsigned integer type.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> s_native = pd.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.UInt64).dtype
        UInt64
    """


class UInt32(UnsignedIntegerType):
    """32-bit unsigned integer type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.UInt32).dtype
        UInt32
    """


class UInt16(UnsignedIntegerType):
    """16-bit unsigned integer type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.UInt16).dtype
        UInt16
    """


class UInt8(UnsignedIntegerType):
    """8-bit unsigned integer type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([2, 1, 3, 7])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.UInt8).dtype
        UInt8
    """


class Float64(FloatType):
    """64-bit floating point type.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>> s_native = pa.chunked_array([[0.001, 0.1, 0.01, 0.1]])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Float64).dtype
        Float64
    """


class Float32(FloatType):
    """32-bit floating point type.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([0.001, 0.1, 0.01, 0.1])
        >>> s = nw.from_native(s_native, series_only=True)
        >>> s.cast(nw.Float32).dtype
        Float32
    """


class String(DType):
    """UTF-8 encoded string type.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> s_native = pd.Series(["beluga", "narwhal", "orca", "vaquita"])
        >>> nw.from_native(s_native, series_only=True).dtype
        String
    """


class Boolean(DType):
    """Boolean type.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>> s_native = pa.chunked_array([[True, False, False, True]])
        >>> nw.from_native(s_native, series_only=True).dtype
        Boolean
    """


class Object(DType):
    """Data type for wrapping arbitrary Python objects.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> class Foo: ...
        >>> s_native = pd.Series([Foo(), Foo()])
        >>> nw.from_native(s_native, series_only=True).dtype
        Object
    """


class Unknown(DType):
    """Type representing DataType values that could not be determined statically.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> s_native = pd.Series(pd.period_range("2000-01", periods=4, freq="M"))
        >>> nw.from_native(s_native, series_only=True).dtype
        Unknown
    """


class _DatetimeMeta(type):
    @property
    def time_unit(cls) -> TimeUnit:
        return "us"

    @property
    def time_zone(cls) -> str | None:
        return None


class Datetime(TemporalType, metaclass=_DatetimeMeta):
    """Data type representing a calendar date and time of day.

    Arguments:
        time_unit: Unit of time. Defaults to `'us'` (microseconds).
        time_zone: Time zone string, as defined in zoneinfo (to see valid strings run
            `import zoneinfo; zoneinfo.available_timezones()` for a full list).

    Notes:
        Adapted from [Polars implementation](https://github.com/pola-rs/polars/blob/py-1.7.1/py-polars/polars/datatypes/classes.py#L398-L457)

    Examples:
        >>> from datetime import datetime, timedelta
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = (
        ...     pl.Series([datetime(2024, 12, 9) + timedelta(days=n) for n in range(5)])
        ...     .cast(pl.Datetime("ms"))
        ...     .dt.replace_time_zone("Africa/Accra")
        ... )
        >>> nw.from_native(s_native, series_only=True).dtype
        Datetime(time_unit='ms', time_zone='Africa/Accra')
    """

    def __init__(
        self: Self,
        time_unit: TimeUnit = "us",
        time_zone: str | timezone | None = None,
    ) -> None:
        if time_unit not in {"s", "ms", "us", "ns"}:
            msg = (
                "invalid `time_unit`"
                f"\n\nExpected one of {{'ns','us','ms', 's'}}, got {time_unit!r}."
            )
            raise ValueError(msg)

        if isinstance(time_zone, timezone):
            time_zone = str(time_zone)

        self.time_unit: TimeUnit = time_unit
        self.time_zone: str | None = time_zone

    def __eq__(self: Self, other: object) -> bool:
        # allow comparing object instances to class
        if type(other) is _DatetimeMeta:
            return True
        elif isinstance(other, self.__class__):
            return self.time_unit == other.time_unit and self.time_zone == other.time_zone
        else:  # pragma: no cover
            return False

    def __hash__(self: Self) -> int:  # pragma: no cover
        return hash((self.__class__, self.time_unit, self.time_zone))

    def __repr__(self: Self) -> str:  # pragma: no cover
        class_name = self.__class__.__name__
        return f"{class_name}(time_unit={self.time_unit!r}, time_zone={self.time_zone!r})"


class _DurationMeta(type):
    @property
    def time_unit(cls) -> TimeUnit:
        return "us"


class Duration(TemporalType, metaclass=_DurationMeta):
    """Data type representing a time duration.

    Arguments:
        time_unit: Unit of time. Defaults to `'us'` (microseconds).

    Notes:
        Adapted from [Polars implementation](https://github.com/pola-rs/polars/blob/py-1.7.1/py-polars/polars/datatypes/classes.py#L460-L502)

    Examples:
        >>> from datetime import timedelta
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>> s_native = pa.chunked_array(
        ...     [[timedelta(seconds=d) for d in range(1, 4)]], type=pa.duration("ms")
        ... )
        >>> nw.from_native(s_native, series_only=True).dtype
        Duration(time_unit='ms')
    """

    def __init__(self: Self, time_unit: TimeUnit = "us") -> None:
        if time_unit not in {"s", "ms", "us", "ns"}:
            msg = (
                "invalid `time_unit`"
                f"\n\nExpected one of {{'ns','us','ms', 's'}}, got {time_unit!r}."
            )
            raise ValueError(msg)

        self.time_unit: TimeUnit = time_unit

    def __eq__(self: Self, other: object) -> bool:
        # allow comparing object instances to class
        if type(other) is _DurationMeta:
            return True
        elif isinstance(other, self.__class__):
            return self.time_unit == other.time_unit
        else:  # pragma: no cover
            return False

    def __hash__(self: Self) -> int:  # pragma: no cover
        return hash((self.__class__, self.time_unit))

    def __repr__(self: Self) -> str:  # pragma: no cover
        class_name = self.__class__.__name__
        return f"{class_name}(time_unit={self.time_unit!r})"


class Categorical(DType):
    """A categorical encoding of a set of strings.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series(["beluga", "narwhal", "orca"])
        >>> nw.from_native(s_native, series_only=True).cast(nw.Categorical).dtype
        Categorical
    """


class Enum(DType):
    """A fixed categorical encoding of a unique set of strings.

    Polars has an Enum data type, while pandas and PyArrow do not.

    Examples:
       >>> import polars as pl
       >>> import narwhals as nw
       >>> data = ["beluga", "narwhal", "orca"]
       >>> s_native = pl.Series(data, dtype=pl.Enum(data))
       >>> nw.from_native(s_native, series_only=True).dtype
       Enum
    """


class Field:
    """Definition of a single field within a `Struct` DataType.

    Arguments:
        name: The name of the field within its parent `Struct`.
        dtype: The `DataType` of the field's values.

    Examples:
       >>> import pyarrow as pa
       >>> import narwhals as nw
       >>> data = [{"a": 1, "b": ["narwhal", "beluga"]}, {"a": 2, "b": ["orca"]}]
       >>> ser_pa = pa.chunked_array([data])
       >>> nw.from_native(ser_pa, series_only=True).dtype.fields
       [Field('a', Int64), Field('b', List(String))]
    """

    name: str
    dtype: type[DType] | DType

    def __init__(self: Self, name: str, dtype: type[DType] | DType) -> None:
        self.name = name
        self.dtype = dtype

    def __eq__(self: Self, other: Field) -> bool:  # type: ignore[override]
        return (self.name == other.name) & (self.dtype == other.dtype)

    def __hash__(self: Self) -> int:
        return hash((self.name, self.dtype))

    def __repr__(self: Self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.name!r}, {self.dtype})"


class Struct(NestedType):
    """Struct composite type.

    Arguments:
        fields: The fields that make up the struct. Can be either a sequence of Field
            objects or a mapping of column names to data types.

    Examples:
       >>> import pyarrow as pa
       >>> import narwhals as nw
       >>> s_native = pa.chunked_array(
       ...     [[{"a": 1, "b": ["narwhal", "beluga"]}, {"a": 2, "b": ["orca"]}]]
       ... )
       >>> nw.from_native(s_native, series_only=True).dtype
       Struct({'a': Int64, 'b': List(String)})
    """

    fields: list[Field]

    def __init__(
        self: Self, fields: Sequence[Field] | Mapping[str, DType | type[DType]]
    ) -> None:
        if isinstance(fields, Mapping):
            self.fields = list(starmap(Field, fields.items()))
        else:
            self.fields = list(fields)

    def __eq__(self: Self, other: DType | type[DType]) -> bool:  # type: ignore[override]
        # The comparison allows comparing objects to classes, and specific
        # inner types to those without (eg: inner=None). if one of the
        # arguments is not specific about its inner type we infer it
        # as being equal. (See the List type for more info).
        if type(other) is type and issubclass(other, self.__class__):
            return True
        elif isinstance(other, self.__class__):
            return self.fields == other.fields
        else:
            return False

    def __hash__(self: Self) -> int:
        return hash((self.__class__, tuple(self.fields)))

    def __iter__(self: Self) -> Iterator[tuple[str, DType | type[DType]]]:
        for fld in self.fields:
            yield fld.name, fld.dtype

    def __reversed__(self: Self) -> Iterator[tuple[str, DType | type[DType]]]:
        for fld in reversed(self.fields):
            yield fld.name, fld.dtype

    def __repr__(self: Self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({dict(self)})"

    def to_schema(self: Self) -> OrderedDict[str, DType | type[DType]]:
        """Return Struct dtype as a schema dict.

        Returns:
            Mapping from column name to dtype.
        """
        return OrderedDict(self)


class List(NestedType):
    """Variable length list type.

    Examples:
       >>> import pandas as pd
       >>> import pyarrow as pa
       >>> import narwhals as nw
       >>> s_native = pd.Series(
       ...     [["narwhal", "orca"], ["beluga", "vaquita"]],
       ...     dtype=pd.ArrowDtype(pa.large_list(pa.large_string())),
       ... )
       >>> nw.from_native(s_native, series_only=True).dtype
       List(String)
    """

    inner: DType | type[DType]

    def __init__(self: Self, inner: DType | type[DType]) -> None:
        self.inner = inner

    def __eq__(self: Self, other: DType | type[DType]) -> bool:  # type: ignore[override]
        # This equality check allows comparison of type classes and type instances.
        # If a parent type is not specific about its inner type, we infer it as equal:
        # > list[i64] == list[i64] -> True
        # > list[i64] == list[f32] -> False
        # > list[i64] == list      -> True

        # allow comparing object instances to class
        if type(other) is type and issubclass(other, self.__class__):
            return True
        elif isinstance(other, self.__class__):
            return self.inner == other.inner
        else:
            return False

    def __hash__(self: Self) -> int:
        return hash((self.__class__, self.inner))

    def __repr__(self: Self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self.inner!r})"


class Array(NestedType):
    """Fixed length list type.

    Arguments:
        inner: The datatype of the values within each array.
        shape: The shape of the arrays.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>> s_native = pl.Series([[1, 2], [3, 4], [5, 6]], dtype=pl.Array(pl.Int32, 2))
        >>> nw.from_native(s_native, series_only=True).dtype
        Array(Int32, shape=(2,))
    """

    inner: DType | type[DType]
    size: int
    shape: tuple[int, ...]

    def __init__(
        self: Self, inner: DType | type[DType], shape: int | tuple[int, ...]
    ) -> None:
        inner_shape: tuple[int, ...] = inner.shape if isinstance(inner, Array) else ()
        if isinstance(shape, int):
            self.inner = inner
            self.size = shape
            self.shape = (shape, *inner_shape)

        elif isinstance(shape, tuple) and len(shape) != 0 and isinstance(shape[0], int):
            if len(shape) > 1:
                inner = Array(inner, shape[1:])

            self.inner = inner
            self.size = shape[0]
            self.shape = shape + inner_shape

        else:
            msg = f"invalid input for shape: {shape!r}"
            raise TypeError(msg)

    def __eq__(self: Self, other: DType | type[DType]) -> bool:  # type: ignore[override]
        # This equality check allows comparison of type classes and type instances.
        # If a parent type is not specific about its inner type, we infer it as equal:
        # > array[i64] == array[i64] -> True
        # > array[i64] == array[f32] -> False
        # > array[i64] == array      -> True

        # allow comparing object instances to class
        if type(other) is type and issubclass(other, self.__class__):
            return True
        elif isinstance(other, self.__class__):
            if self.shape != other.shape:
                return False
            else:
                return self.inner == other.inner
        else:
            return False

    def __hash__(self: Self) -> int:
        return hash((self.__class__, self.inner, self.shape))

    def __repr__(self) -> str:
        # Get leaf type
        dtype_ = self
        for _ in self.shape:
            dtype_ = dtype_.inner  # type: ignore[assignment]

        class_name = self.__class__.__name__
        return f"{class_name}({dtype_!r}, shape={self.shape})"


class Date(TemporalType):
    """Data type representing a calendar date.

    Examples:
        >>> from datetime import date, timedelta
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>> s_native = pa.chunked_array(
        ...     [[date(2024, 12, 1) + timedelta(days=d) for d in range(4)]]
        ... )
        >>> nw.from_native(s_native, series_only=True).dtype
        Date
    """
