from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals.dtypes import Array
from narwhals.dtypes import Boolean
from narwhals.dtypes import Categorical
from narwhals.dtypes import Date
from narwhals.dtypes import Datetime as NwDatetime
from narwhals.dtypes import Decimal
from narwhals.dtypes import DType
from narwhals.dtypes import Duration as NwDuration
from narwhals.dtypes import Enum
from narwhals.dtypes import Field
from narwhals.dtypes import Float32
from narwhals.dtypes import Float64
from narwhals.dtypes import FloatType
from narwhals.dtypes import Int8
from narwhals.dtypes import Int16
from narwhals.dtypes import Int32
from narwhals.dtypes import Int64
from narwhals.dtypes import Int128
from narwhals.dtypes import IntegerType
from narwhals.dtypes import List
from narwhals.dtypes import NestedType
from narwhals.dtypes import NumericType
from narwhals.dtypes import Object
from narwhals.dtypes import SignedIntegerType
from narwhals.dtypes import String
from narwhals.dtypes import Struct
from narwhals.dtypes import UInt8
from narwhals.dtypes import UInt16
from narwhals.dtypes import UInt32
from narwhals.dtypes import UInt64
from narwhals.dtypes import UInt128
from narwhals.dtypes import Unknown
from narwhals.dtypes import UnsignedIntegerType

if TYPE_CHECKING:
    from typing_extensions import Self


class Datetime(NwDatetime):
    """Data type representing a calendar date and time of day.

    Arguments:
        time_unit: Unit of time. Defaults to `'us'` (microseconds).
        time_zone: Time zone string, as defined in zoneinfo (to see valid strings run
            `import zoneinfo; zoneinfo.available_timezones()` for a full list).

    Notes:
        Adapted from [Polars implementation](https://github.com/pola-rs/polars/blob/py-1.7.1/py-polars/polars/datatypes/classes.py#L398-L457)
    """

    def __hash__(self: Self) -> int:
        return hash(self.__class__)


class Duration(NwDuration):
    """Data type representing a time duration.

    Arguments:
        time_unit: Unit of time. Defaults to `'us'` (microseconds).

    Notes:
        Adapted from [Polars implementation](https://github.com/pola-rs/polars/blob/py-1.7.1/py-polars/polars/datatypes/classes.py#L460-L502)
    """

    def __hash__(self: Self) -> int:
        return hash(self.__class__)


__all__ = [
    "Array",
    "Boolean",
    "Categorical",
    "DType",
    "Date",
    "Datetime",
    "Decimal",
    "Duration",
    "Enum",
    "Field",
    "Float32",
    "Float64",
    "FloatType",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "Int128",
    "IntegerType",
    "List",
    "NestedType",
    "NumericType",
    "Object",
    "SignedIntegerType",
    "String",
    "Struct",
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "UInt128",
    "Unknown",
    "UnsignedIntegerType",
]
