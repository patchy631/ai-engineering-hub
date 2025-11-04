from __future__ import annotations

import functools
import re
import warnings
from contextlib import suppress
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import TypeVar
from typing import cast

import pandas as pd

from narwhals.exceptions import ColumnNotFoundError
from narwhals.exceptions import DuplicateError
from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import import_dtypes_module
from narwhals.utils import isinstance_or_issubclass

T = TypeVar("T")

if TYPE_CHECKING:
    from pandas._typing import Dtype as PandasDtype

    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.expr import PandasLikeExpr
    from narwhals._pandas_like.series import PandasLikeSeries
    from narwhals.dtypes import DType
    from narwhals.typing import DTypeBackend
    from narwhals.typing import TimeUnit
    from narwhals.typing import _1DArray

    ExprT = TypeVar("ExprT", bound=PandasLikeExpr)


PANDAS_LIKE_IMPLEMENTATION = {
    Implementation.PANDAS,
    Implementation.CUDF,
    Implementation.MODIN,
}
PD_DATETIME_RGX = r"""^
    datetime64\[
        (?P<time_unit>s|ms|us|ns)                 # Match time unit: s, ms, us, or ns
        (?:,                                      # Begin non-capturing group for optional timezone
            \s*                                   # Optional whitespace after comma
            (?P<time_zone>                        # Start named group for timezone
                [a-zA-Z\/]+                       # Match timezone name, e.g., UTC, America/New_York
                (?:[+-]\d{2}:\d{2})?              # Optional offset in format +HH:MM or -HH:MM
                |                                 # OR
                pytz\.FixedOffset\(\d+\)          # Match pytz.FixedOffset with integer offset in parentheses
            )                                     # End time_zone group
        )?                                        # End optional timezone group
    \]                                            # Closing bracket for datetime64
$"""
PATTERN_PD_DATETIME = re.compile(PD_DATETIME_RGX, re.VERBOSE)
PA_DATETIME_RGX = r"""^
    timestamp\[
        (?P<time_unit>s|ms|us|ns)                 # Match time unit: s, ms, us, or ns
        (?:,                                      # Begin non-capturing group for optional timezone
            \s?tz=                                # Match "tz=" prefix
            (?P<time_zone>                        # Start named group for timezone
                [a-zA-Z\/]*                       # Match timezone name (e.g., UTC, America/New_York)
                (?:                               # Begin optional non-capturing group for offset
                    [+-]\d{2}:\d{2}               # Match offset in format +HH:MM or -HH:MM
                )?                                # End optional offset group
            )                                     # End time_zone group
        )?                                        # End optional timezone group
    \]                                            # Closing bracket for timestamp
    \[pyarrow\]                                   # Literal string "[pyarrow]"
$"""
PATTERN_PA_DATETIME = re.compile(PA_DATETIME_RGX, re.VERBOSE)
PD_DURATION_RGX = r"""^
    timedelta64\[
        (?P<time_unit>s|ms|us|ns)                 # Match time unit: s, ms, us, or ns
    \]                                            # Closing bracket for timedelta64
$"""

PATTERN_PD_DURATION = re.compile(PD_DURATION_RGX, re.VERBOSE)
PA_DURATION_RGX = r"""^
    duration\[
        (?P<time_unit>s|ms|us|ns)                 # Match time unit: s, ms, us, or ns
    \]                                            # Closing bracket for duration
    \[pyarrow\]                                   # Literal string "[pyarrow]"
$"""
PATTERN_PA_DURATION = re.compile(PA_DURATION_RGX, re.VERBOSE)


def align_and_extract_native(
    lhs: PandasLikeSeries, rhs: PandasLikeSeries | object
) -> tuple[pd.Series[Any] | object, pd.Series[Any] | object]:
    """Validate RHS of binary operation.

    If the comparison isn't supported, return `NotImplemented` so that the
    "right-hand-side" operation (e.g. `__radd__`) can be tried.
    """
    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.series import PandasLikeSeries

    lhs_index = lhs._native_series.index

    if isinstance(rhs, PandasLikeDataFrame):
        return NotImplemented

    if lhs._broadcast and isinstance(rhs, PandasLikeSeries) and not rhs._broadcast:
        return lhs._native_series.iloc[0], rhs._native_series

    lhs_native = lhs._native_series
    if isinstance(rhs, PandasLikeSeries):
        if rhs._broadcast:
            return (lhs_native, rhs._native_series.iloc[0])
        rhs_native = rhs._native_series
        if rhs_native.index is not lhs_index:
            return (
                lhs_native,
                set_index(
                    rhs_native,
                    lhs_index,
                    implementation=rhs._implementation,
                    backend_version=rhs._backend_version,
                ),
            )
        return (lhs_native, rhs_native)

    if isinstance(rhs, list):
        msg = "Expected Series or scalar, got list."
        raise TypeError(msg)
    # `rhs` must be scalar, so just leave it as-is
    return lhs_native, rhs


def extract_dataframe_comparand(
    index: pd.Index[Any], other: PandasLikeSeries
) -> pd.Series[Any]:
    """Extract native Series, broadcasting to `length` if necessary."""
    if other._broadcast:
        s = other._native_series
        return s.__class__(s.iloc[0], index=index, dtype=s.dtype, name=s.name)
    if other._native_series.index is not index:
        return set_index(
            other._native_series,
            index,
            implementation=other._implementation,
            backend_version=other._backend_version,
        )
    return other._native_series


def create_compliant_series(
    iterable: Any,
    index: Any = None,
    *,
    implementation: Implementation,
    backend_version: tuple[int, ...],
    version: Version,
) -> PandasLikeSeries:
    from narwhals._pandas_like.series import PandasLikeSeries

    if implementation in PANDAS_LIKE_IMPLEMENTATION:
        series = implementation.to_native_namespace().Series(
            iterable, index=index, name=""
        )
        return PandasLikeSeries(
            series,
            implementation=implementation,
            backend_version=backend_version,
            version=version,
        )
    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def horizontal_concat(
    dfs: list[Any], *, implementation: Implementation, backend_version: tuple[int, ...]
) -> Any:
    """Concatenate (native) DataFrames horizontally.

    Should be in namespace.
    """
    if implementation is Implementation.CUDF:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="The behavior of array concatenation with empty entries is deprecated",
                category=FutureWarning,
            )
            return implementation.to_native_namespace().concat(dfs, axis=1)

    if implementation.is_pandas_like():
        extra_kwargs = (
            {"copy": False}
            if implementation is Implementation.PANDAS and backend_version < (3,)
            else {}
        )
        return implementation.to_native_namespace().concat(dfs, axis=1, **extra_kwargs)

    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def vertical_concat(
    dfs: list[Any], *, implementation: Implementation, backend_version: tuple[int, ...]
) -> Any:
    """Concatenate (native) DataFrames vertically.

    Should be in namespace.
    """
    if not dfs:
        msg = "No dataframes to concatenate"  # pragma: no cover
        raise AssertionError(msg)
    cols_0 = dfs[0].columns
    for i, df in enumerate(dfs[1:], start=1):
        cols_current = df.columns
        if not ((len(cols_current) == len(cols_0)) and (cols_current == cols_0).all()):
            msg = (
                "unable to vstack, column names don't match:\n"
                f"   - dataframe 0: {cols_0.to_list()}\n"
                f"   - dataframe {i}: {cols_current.to_list()}\n"
            )
            raise TypeError(msg)

    if implementation in PANDAS_LIKE_IMPLEMENTATION:
        extra_kwargs = (
            {"copy": False}
            if implementation is Implementation.PANDAS and backend_version < (3,)
            else {}
        )
        return implementation.to_native_namespace().concat(dfs, axis=0, **extra_kwargs)

    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def diagonal_concat(
    dfs: list[Any], *, implementation: Implementation, backend_version: tuple[int, ...]
) -> Any:
    """Concatenate (native) DataFrames diagonally.

    Should be in namespace.
    """
    if not dfs:
        msg = "No dataframes to concatenate"  # pragma: no cover
        raise AssertionError(msg)

    if implementation in PANDAS_LIKE_IMPLEMENTATION:
        extra_kwargs = (
            {"copy": False, "sort": False}
            if implementation is Implementation.PANDAS and backend_version < (1,)
            else {"copy": False}
            if implementation is Implementation.PANDAS and backend_version < (3,)
            else {}
        )
        return implementation.to_native_namespace().concat(dfs, axis=0, **extra_kwargs)

    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def native_series_from_iterable(
    data: Iterable[Any],
    name: str,
    index: Any,
    implementation: Implementation,
) -> Any:
    """Return native series."""
    if implementation in PANDAS_LIKE_IMPLEMENTATION:
        extra_kwargs = {"copy": False} if implementation is Implementation.PANDAS else {}
        if len(index) == 0:
            index = None
        return implementation.to_native_namespace().Series(
            data, name=name, index=index, **extra_kwargs
        )

    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def set_index(
    obj: T,
    index: Any,
    *,
    implementation: Implementation,
    backend_version: tuple[int, ...],
) -> T:
    """Wrapper around pandas' set_axis to set object index.

    We can set `copy` / `inplace` based on implementation/version.
    """
    if implementation is Implementation.CUDF:  # pragma: no cover
        obj = obj.copy(deep=False)  # type: ignore[attr-defined]
        obj.index = index  # type: ignore[attr-defined]
        return obj
    if implementation is Implementation.PANDAS and (
        backend_version < (1,)
    ):  # pragma: no cover
        kwargs = {"inplace": False}
    else:
        kwargs = {}
    if implementation is Implementation.PANDAS and (
        (1, 5) <= backend_version < (3,)
    ):  # pragma: no cover
        kwargs["copy"] = False
    else:  # pragma: no cover
        pass
    return obj.set_axis(index, axis=0, **kwargs)  # type: ignore[attr-defined]


def set_columns(
    obj: T,
    columns: list[str],
    *,
    implementation: Implementation,
    backend_version: tuple[int, ...],
) -> T:
    """Wrapper around pandas' set_axis to set object columns.

    We can set `copy` / `inplace` based on implementation/version.
    """
    if implementation is Implementation.CUDF:  # pragma: no cover
        obj = obj.copy(deep=False)  # type: ignore[attr-defined]
        obj.columns = columns  # type: ignore[attr-defined]
        return obj
    if implementation is Implementation.PANDAS and (
        backend_version < (1,)
    ):  # pragma: no cover
        kwargs = {"inplace": False}
    else:
        kwargs = {}
    if implementation is Implementation.PANDAS and (
        (1, 5) <= backend_version < (3,)
    ):  # pragma: no cover
        kwargs["copy"] = False
    else:  # pragma: no cover
        pass
    return obj.set_axis(columns, axis=1, **kwargs)  # type: ignore[attr-defined]


def rename(
    obj: T,
    *args: Any,
    implementation: Implementation,
    backend_version: tuple[int, ...],
    **kwargs: Any,
) -> T:
    """Wrapper around pandas' rename so that we can set `copy` based on implementation/version."""
    if implementation is Implementation.PANDAS and (
        backend_version >= (3,)
    ):  # pragma: no cover
        return obj.rename(*args, **kwargs)  # type: ignore[attr-defined]
    return obj.rename(*args, **kwargs, copy=False)  # type: ignore[attr-defined]


@functools.lru_cache(maxsize=16)
def non_object_native_to_narwhals_dtype(dtype: str, version: Version) -> DType:
    dtypes = import_dtypes_module(version)
    if dtype in {"int64", "Int64", "Int64[pyarrow]", "int64[pyarrow]"}:
        return dtypes.Int64()
    if dtype in {"int32", "Int32", "Int32[pyarrow]", "int32[pyarrow]"}:
        return dtypes.Int32()
    if dtype in {"int16", "Int16", "Int16[pyarrow]", "int16[pyarrow]"}:
        return dtypes.Int16()
    if dtype in {"int8", "Int8", "Int8[pyarrow]", "int8[pyarrow]"}:
        return dtypes.Int8()
    if dtype in {"uint64", "UInt64", "UInt64[pyarrow]", "uint64[pyarrow]"}:
        return dtypes.UInt64()
    if dtype in {"uint32", "UInt32", "UInt32[pyarrow]", "uint32[pyarrow]"}:
        return dtypes.UInt32()
    if dtype in {"uint16", "UInt16", "UInt16[pyarrow]", "uint16[pyarrow]"}:
        return dtypes.UInt16()
    if dtype in {"uint8", "UInt8", "UInt8[pyarrow]", "uint8[pyarrow]"}:
        return dtypes.UInt8()
    if dtype in {
        "float64",
        "Float64",
        "Float64[pyarrow]",
        "float64[pyarrow]",
        "double[pyarrow]",
    }:
        return dtypes.Float64()
    if dtype in {
        "float32",
        "Float32",
        "Float32[pyarrow]",
        "float32[pyarrow]",
        "float[pyarrow]",
    }:
        return dtypes.Float32()
    if dtype in {"string", "string[python]", "string[pyarrow]", "large_string[pyarrow]"}:
        return dtypes.String()
    if dtype in {"bool", "boolean", "boolean[pyarrow]", "bool[pyarrow]"}:
        return dtypes.Boolean()
    if dtype == "category" or dtype.startswith("dictionary<"):
        return dtypes.Categorical()
    if (match_ := PATTERN_PD_DATETIME.match(dtype)) or (
        match_ := PATTERN_PA_DATETIME.match(dtype)
    ):
        dt_time_unit: TimeUnit = match_.group("time_unit")  # type: ignore[assignment]
        dt_time_zone: str | None = match_.group("time_zone")
        return dtypes.Datetime(dt_time_unit, dt_time_zone)
    if (match_ := PATTERN_PD_DURATION.match(dtype)) or (
        match_ := PATTERN_PA_DURATION.match(dtype)
    ):
        du_time_unit: TimeUnit = match_.group("time_unit")  # type: ignore[assignment]
        return dtypes.Duration(du_time_unit)
    if dtype == "date32[day][pyarrow]":
        return dtypes.Date()
    if dtype.startswith("decimal") and dtype.endswith("[pyarrow]"):
        return dtypes.Decimal()
    return dtypes.Unknown()  # pragma: no cover


def object_native_to_narwhals_dtype(
    series: PandasLikeSeries, version: Version, implementation: Implementation
) -> DType:
    dtypes = import_dtypes_module(version)
    if implementation is Implementation.CUDF:  # pragma: no cover
        # Per conversations with their maintainers, they don't support arbitrary
        # objects, so we can just return String.
        return dtypes.String()

    # Arbitrary limit of 100 elements to use to sniff dtype.
    inferred_dtype = pd.api.types.infer_dtype(series.head(100), skipna=True)
    if inferred_dtype == "string":
        return dtypes.String()
    if inferred_dtype == "empty" and version is not Version.V1:
        # Default to String for empty Series.
        return dtypes.String()
    elif inferred_dtype == "empty":
        # But preserve returning Object in V1.
        return dtypes.Object()
    return dtypes.Object()


def native_to_narwhals_dtype(
    native_dtype: Any, version: Version, implementation: Implementation
) -> DType:
    str_dtype = str(native_dtype)

    if str_dtype.startswith(("large_list", "list", "struct", "fixed_size_list")):
        from narwhals._arrow.utils import (
            native_to_narwhals_dtype as arrow_native_to_narwhals_dtype,
        )

        if hasattr(native_dtype, "to_arrow"):  # pragma: no cover
            # cudf, cudf.pandas
            return arrow_native_to_narwhals_dtype(native_dtype.to_arrow(), version)
        return arrow_native_to_narwhals_dtype(native_dtype.pyarrow_dtype, version)
    if str_dtype != "object":
        return non_object_native_to_narwhals_dtype(str_dtype, version)
    elif implementation is Implementation.DASK:
        # Per conversations with their maintainers, they don't support arbitrary
        # objects, so we can just return String.
        dtypes = import_dtypes_module(version)
        return dtypes.String()
    msg = (
        "Unreachable code, object dtype should be handled separately"  # pragma: no cover
    )
    raise AssertionError(msg)


def get_dtype_backend(dtype: Any, implementation: Implementation) -> DTypeBackend:
    """Get dtype backend for pandas type.

    Matches pandas' `dtype_backend` argument in `convert_dtypes`.
    """
    if implementation is Implementation.CUDF:
        return None
    if hasattr(pd, "ArrowDtype") and isinstance(dtype, pd.ArrowDtype):
        return "pyarrow"
    with suppress(AttributeError):
        sentinel = object()
        if (
            isinstance(dtype, pd.api.extensions.ExtensionDtype)
            and getattr(dtype, "base", sentinel) is None
        ):
            return "numpy_nullable"
    return None


def narwhals_to_native_dtype(  # noqa: PLR0915
    dtype: DType | type[DType],
    dtype_backend: DTypeBackend,
    implementation: Implementation,
    backend_version: tuple[int, ...],
    version: Version,
) -> str | PandasDtype:
    if dtype_backend is not None and dtype_backend not in {"pyarrow", "numpy_nullable"}:
        msg = f"Expected one of {{None, 'pyarrow', 'numpy_nullable'}}, got: '{dtype_backend}'"
        raise ValueError(msg)
    dtypes = import_dtypes_module(version)
    if isinstance_or_issubclass(dtype, dtypes.Decimal):
        msg = "Casting to Decimal is not supported yet."
        raise NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, dtypes.Float64):
        if dtype_backend == "pyarrow":
            return "Float64[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Float64"
        return "float64"
    if isinstance_or_issubclass(dtype, dtypes.Float32):
        if dtype_backend == "pyarrow":
            return "Float32[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Float32"
        return "float32"
    if isinstance_or_issubclass(dtype, dtypes.Int64):
        if dtype_backend == "pyarrow":
            return "Int64[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Int64"
        return "int64"
    if isinstance_or_issubclass(dtype, dtypes.Int32):
        if dtype_backend == "pyarrow":
            return "Int32[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Int32"
        return "int32"
    if isinstance_or_issubclass(dtype, dtypes.Int16):
        if dtype_backend == "pyarrow":
            return "Int16[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Int16"
        return "int16"
    if isinstance_or_issubclass(dtype, dtypes.Int8):
        if dtype_backend == "pyarrow":
            return "Int8[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "Int8"
        return "int8"
    if isinstance_or_issubclass(dtype, dtypes.UInt64):
        if dtype_backend == "pyarrow":
            return "UInt64[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "UInt64"
        return "uint64"
    if isinstance_or_issubclass(dtype, dtypes.UInt32):
        if dtype_backend == "pyarrow":
            return "UInt32[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "UInt32"
        return "uint32"
    if isinstance_or_issubclass(dtype, dtypes.UInt16):
        if dtype_backend == "pyarrow":
            return "UInt16[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "UInt16"
        return "uint16"
    if isinstance_or_issubclass(dtype, dtypes.UInt8):
        if dtype_backend == "pyarrow":
            return "UInt8[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "UInt8"
        return "uint8"
    if isinstance_or_issubclass(dtype, dtypes.String):
        if dtype_backend == "pyarrow":
            return "string[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "string"
        return str
    if isinstance_or_issubclass(dtype, dtypes.Boolean):
        if dtype_backend == "pyarrow":
            return "boolean[pyarrow]"
        elif dtype_backend == "numpy_nullable":
            return "boolean"
        return "bool"
    if isinstance_or_issubclass(dtype, dtypes.Categorical):
        # TODO(Unassigned): is there no pyarrow-backed categorical?
        # or at least, convert_dtypes(dtype_backend='pyarrow') doesn't
        # convert to it?
        return "category"
    if isinstance_or_issubclass(dtype, dtypes.Datetime):
        # Pandas does not support "ms" or "us" time units before version 2.0
        if implementation is Implementation.PANDAS and backend_version < (
            2,
        ):  # pragma: no cover
            dt_time_unit = "ns"
        else:
            dt_time_unit = dtype.time_unit

        if dtype_backend == "pyarrow":
            tz_part = f", tz={tz}" if (tz := dtype.time_zone) else ""
            return f"timestamp[{dt_time_unit}{tz_part}][pyarrow]"
        else:
            tz_part = f", {tz}" if (tz := dtype.time_zone) else ""
            return f"datetime64[{dt_time_unit}{tz_part}]"
    if isinstance_or_issubclass(dtype, dtypes.Duration):
        if implementation is Implementation.PANDAS and backend_version < (
            2,
        ):  # pragma: no cover
            du_time_unit = "ns"
        else:
            du_time_unit = dtype.time_unit
        return (
            f"duration[{du_time_unit}][pyarrow]"
            if dtype_backend == "pyarrow"
            else f"timedelta64[{du_time_unit}]"
        )
    if isinstance_or_issubclass(dtype, dtypes.Date):
        try:
            import pyarrow as pa  # ignore-banned-import
        except ModuleNotFoundError:  # pragma: no cover
            msg = "PyArrow>=11.0.0 is required for `Date` dtype."
        return "date32[pyarrow]"
    if isinstance_or_issubclass(dtype, dtypes.Enum):
        msg = "Converting to Enum is not (yet) supported"
        raise NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, (dtypes.Struct, dtypes.Array, dtypes.List)):
        if implementation is Implementation.PANDAS and backend_version >= (2, 2):
            try:
                import pandas as pd
                import pyarrow as pa  # ignore-banned-import  # noqa: F401
            except ImportError as exc:  # pragma: no cover
                msg = f"Unable to convert to {dtype} to to the following exception: {exc.msg}"
                raise ImportError(msg) from exc
            from narwhals._arrow.utils import (
                narwhals_to_native_dtype as arrow_narwhals_to_native_dtype,
            )

            return pd.ArrowDtype(arrow_narwhals_to_native_dtype(dtype, version=version))
        else:  # pragma: no cover
            msg = (
                f"Converting to {dtype} dtype is not supported for implementation "
                f"{implementation} and version {version}."
            )
            raise NotImplementedError(msg)
    msg = f"Unknown dtype: {dtype}"  # pragma: no cover
    raise AssertionError(msg)


def align_series_full_broadcast(
    *series: PandasLikeSeries,
) -> list[PandasLikeSeries]:
    # Ensure all of `series` have the same length and index. Scalars get broadcasted to
    # the full length of the longest Series. This is useful when you need to construct a
    # full Series anyway (e.g. `DataFrame.select`). It should not be used in binary operations,
    # such as `nw.col('a') - nw.col('a').mean()`, because then it's more efficient to extract
    # the right-hand-side's single element as a scalar.
    native_namespace = series[0].__native_namespace__()

    lengths = [len(s) for s in series]
    max_length = max(lengths)

    idx = series[lengths.index(max_length)]._native_series.index
    reindexed = []
    max_length_gt_1 = max_length > 1
    for s, length in zip(series, lengths):
        s_native = s._native_series
        if max_length_gt_1 and length == 1:
            reindexed.append(
                s._from_native_series(
                    native_namespace.Series(
                        [s_native.iloc[0]] * max_length,
                        index=idx,
                        name=s_native.name,
                        dtype=s_native.dtype,
                    )
                )
            )

        elif s_native.index is not idx:
            reindexed.append(
                s._from_native_series(
                    set_index(
                        s_native,
                        idx,
                        implementation=s._implementation,
                        backend_version=s._backend_version,
                    )
                )
            )
        else:
            reindexed.append(s)
    return reindexed


def to_datetime(implementation: Implementation, *, utc: bool) -> Any:
    if implementation in PANDAS_LIKE_IMPLEMENTATION:
        return functools.partial(
            implementation.to_native_namespace().to_datetime, utc=utc
        )

    else:  # pragma: no cover
        msg = f"Expected pandas-like implementation ({PANDAS_LIKE_IMPLEMENTATION}), found {implementation}"
        raise TypeError(msg)


def int_dtype_mapper(dtype: Any) -> str:
    if "pyarrow" in str(dtype):
        return "Int64[pyarrow]"
    if str(dtype).lower() != str(dtype):  # pragma: no cover
        return "Int64"
    return "int64"


def convert_str_slice_to_int_slice(
    str_slice: slice, columns: pd.Index[str]
) -> tuple[int | None, int | None, int | None]:
    # We can safely cast to int because we know that `columns` doesn't contain duplicates.
    start = (
        cast("int", columns.get_loc(str_slice.start))
        if str_slice.start is not None
        else None
    )
    stop = (
        cast("int", columns.get_loc(str_slice.stop)) + 1
        if str_slice.stop is not None
        else None
    )
    step = str_slice.step
    return (start, stop, step)


def calculate_timestamp_datetime(
    s: pd.Series[int], original_time_unit: str, time_unit: str
) -> pd.Series[int]:
    if original_time_unit == "ns":
        if time_unit == "ns":
            result = s
        elif time_unit == "us":
            result = s // 1_000
        else:
            result = s // 1_000_000
    elif original_time_unit == "us":
        if time_unit == "ns":
            result = s * 1_000
        elif time_unit == "us":
            result = s
        else:
            result = s // 1_000
    elif original_time_unit == "ms":
        if time_unit == "ns":
            result = s * 1_000_000
        elif time_unit == "us":
            result = s * 1_000
        else:
            result = s
    elif original_time_unit == "s":
        if time_unit == "ns":
            result = s * 1_000_000_000
        elif time_unit == "us":
            result = s * 1_000_000
        else:
            result = s * 1_000
    else:  # pragma: no cover
        msg = f"unexpected time unit {original_time_unit}, please report a bug at https://github.com/narwhals-dev/narwhals"
        raise AssertionError(msg)
    return result


def calculate_timestamp_date(s: pd.Series[int], time_unit: str) -> pd.Series[int]:
    s = s * 86_400  # number of seconds in a day
    if time_unit == "ns":
        result = s * 1_000_000_000
    elif time_unit == "us":
        result = s * 1_000_000
    else:
        result = s * 1_000
    return result


def select_columns_by_name(
    df: T,
    column_names: list[str] | _1DArray,  # NOTE: Cannot be a tuple!
    backend_version: tuple[int, ...],
    implementation: Implementation,
) -> T:
    """Select columns by name.

    Prefer this over `df.loc[:, column_names]` as it's
    generally more performant.
    """
    if len(column_names) == df.shape[1] and all(column_names == df.columns):  # type: ignore[attr-defined]
        return df
    if (df.columns.dtype.kind == "b") or (  # type: ignore[attr-defined]
        implementation is Implementation.PANDAS and backend_version < (1, 5)
    ):
        # See https://github.com/narwhals-dev/narwhals/issues/1349#issuecomment-2470118122
        # for why we need this
        available_columns = df.columns.tolist()  # type: ignore[attr-defined]
        missing_columns = [x for x in column_names if x not in available_columns]
        if missing_columns:  # pragma: no cover
            raise ColumnNotFoundError.from_missing_and_available_column_names(
                missing_columns, available_columns
            )
        return df.loc[:, column_names]  # type: ignore[attr-defined]
    try:
        return df[column_names]  # type: ignore[index]
    except KeyError as e:
        available_columns = df.columns.tolist()  # type: ignore[attr-defined]
        missing_columns = [x for x in column_names if x not in available_columns]
        raise ColumnNotFoundError.from_missing_and_available_column_names(
            missing_columns, available_columns
        ) from e


def pivot_table(
    df: PandasLikeDataFrame,
    values: list[str],
    index: list[str],
    columns: list[str],
    aggregate_function: str | None,
) -> Any:
    dtypes = import_dtypes_module(df._version)
    if df._implementation is Implementation.CUDF:
        if any(
            x == dtypes.Categorical
            for x in df.simple_select(*[*values, *index, *columns]).schema.values()
        ):
            msg = "`pivot` with Categoricals is not implemented for cuDF backend"
            raise NotImplementedError(msg)
        # cuDF doesn't support `observed` argument
        result = df._native_frame.pivot_table(
            values=values,
            index=index,
            columns=columns,
            aggfunc=aggregate_function,
            margins=False,
        )
    else:
        result = df._native_frame.pivot_table(
            values=values,
            index=index,
            columns=columns,
            aggfunc=aggregate_function,
            margins=False,
            observed=True,
        )
    return result


def check_column_names_are_unique(columns: pd.Index[str]) -> None:
    try:
        len_unique_columns = len(columns.drop_duplicates())
    except Exception:  # noqa: BLE001  # pragma: no cover
        msg = f"Expected hashable (e.g. str or int) column names, got: {columns}"
        raise ValueError(msg) from None

    if len(columns) != len_unique_columns:
        from collections import Counter

        counter = Counter(columns)
        msg = ""
        for key, value in counter.items():
            if value > 1:
                msg += f"\n- '{key}' {value} times"
        msg = f"Expected unique column names, got:{msg}"
        raise DuplicateError(msg)
