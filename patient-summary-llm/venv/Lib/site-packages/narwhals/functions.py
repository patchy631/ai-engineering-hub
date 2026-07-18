from __future__ import annotations

import platform
import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Literal
from typing import Mapping
from typing import Protocol
from typing import Sequence
from typing import overload

from narwhals._expression_parsing import ExprKind
from narwhals._expression_parsing import ExprMetadata
from narwhals._expression_parsing import apply_n_ary_operation
from narwhals._expression_parsing import check_expressions_preserve_length
from narwhals._expression_parsing import combine_metadata
from narwhals._expression_parsing import extract_compliant
from narwhals._expression_parsing import infer_kind
from narwhals._expression_parsing import is_scalar_like
from narwhals.dependencies import is_numpy_array
from narwhals.dependencies import is_numpy_array_2d
from narwhals.expr import Expr
from narwhals.schema import Schema
from narwhals.series import Series
from narwhals.translate import from_native
from narwhals.translate import to_native
from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import flatten
from narwhals.utils import is_compliant_expr
from narwhals.utils import is_sequence_but_not_str
from narwhals.utils import parse_version
from narwhals.utils import validate_laziness
from narwhals.utils import validate_native_namespace_and_backend

if TYPE_CHECKING:
    from types import ModuleType

    import polars as pl
    import pyarrow as pa
    from typing_extensions import Self

    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame
    from narwhals.dtypes import DType
    from narwhals.series import Series
    from narwhals.typing import CompliantExpr
    from narwhals.typing import CompliantNamespace
    from narwhals.typing import DTypeBackend
    from narwhals.typing import IntoDataFrameT
    from narwhals.typing import IntoExpr
    from narwhals.typing import IntoFrameT
    from narwhals.typing import IntoSeriesT
    from narwhals.typing import _2DArray

    class ArrowStreamExportable(Protocol):
        def __arrow_c_stream__(
            self, requested_schema: object | None = None
        ) -> object: ...


@overload
def concat(
    items: Iterable[DataFrame[IntoDataFrameT]],
    *,
    how: Literal["horizontal", "vertical", "diagonal"] = "vertical",
) -> DataFrame[IntoDataFrameT]: ...


@overload
def concat(
    items: Iterable[LazyFrame[IntoFrameT]],
    *,
    how: Literal["horizontal", "vertical", "diagonal"] = "vertical",
) -> LazyFrame[IntoFrameT]: ...


@overload
def concat(
    items: Iterable[DataFrame[IntoDataFrameT] | LazyFrame[IntoFrameT]],
    *,
    how: Literal["horizontal", "vertical", "diagonal"] = "vertical",
) -> DataFrame[IntoDataFrameT] | LazyFrame[IntoFrameT]: ...


def concat(
    items: Iterable[DataFrame[IntoDataFrameT] | LazyFrame[IntoFrameT]],
    *,
    how: Literal["horizontal", "vertical", "diagonal"] = "vertical",
) -> DataFrame[IntoDataFrameT] | LazyFrame[IntoFrameT]:
    """Concatenate multiple DataFrames, LazyFrames into a single entity.

    Arguments:
        items: DataFrames, LazyFrames to concatenate.
        how: concatenating strategy:

            - vertical: Concatenate vertically. Column names must match.
            - horizontal: Concatenate horizontally. If lengths don't match, then
                missing rows are filled with null values.
            - diagonal: Finds a union between the column schemas and fills missing column
                values with null.

    Returns:
        A new DataFrame, Lazyframe resulting from the concatenation.

    Raises:
        TypeError: The items to concatenate should either all be eager, or all lazy

    Examples:
        Let's take an example of vertical concatenation:

        >>> import pandas as pd
        >>> import polars as pl
        >>> import pyarrow as pa
        >>> import narwhals as nw

        Let's look at one case a for vertical concatenation (pandas backed):

        >>> df_pd_1 = nw.from_native(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
        >>> df_pd_2 = nw.from_native(pd.DataFrame({"a": [5, 2], "b": [1, 4]}))
        >>> nw.concat([df_pd_1, df_pd_2], how="vertical")
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |        a  b      |
        |     0  1  4      |
        |     1  2  5      |
        |     2  3  6      |
        |     0  5  1      |
        |     1  2  4      |
        └──────────────────┘

        Let's look at one case a for horizontal concatenation (polars backed):

        >>> df_pl_1 = nw.from_native(pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
        >>> df_pl_2 = nw.from_native(pl.DataFrame({"c": [5, 2], "d": [1, 4]}))
        >>> nw.concat([df_pl_1, df_pl_2], how="horizontal")
        ┌───────────────────────────┐
        |    Narwhals DataFrame     |
        |---------------------------|
        |shape: (3, 4)              |
        |┌─────┬─────┬──────┬──────┐|
        |│ a   ┆ b   ┆ c    ┆ d    │|
        |│ --- ┆ --- ┆ ---  ┆ ---  │|
        |│ i64 ┆ i64 ┆ i64  ┆ i64  │|
        |╞═════╪═════╪══════╪══════╡|
        |│ 1   ┆ 4   ┆ 5    ┆ 1    │|
        |│ 2   ┆ 5   ┆ 2    ┆ 4    │|
        |│ 3   ┆ 6   ┆ null ┆ null │|
        |└─────┴─────┴──────┴──────┘|
        └───────────────────────────┘

        Let's look at one case a for diagonal concatenation (pyarrow backed):

        >>> df_pa_1 = nw.from_native(pa.table({"a": [1, 2], "b": [3.5, 4.5]}))
        >>> df_pa_2 = nw.from_native(pa.table({"a": [3, 4], "z": ["x", "y"]}))
        >>> nw.concat([df_pa_1, df_pa_2], how="diagonal")
        ┌──────────────────────────┐
        |    Narwhals DataFrame    |
        |--------------------------|
        |pyarrow.Table             |
        |a: int64                  |
        |b: double                 |
        |z: string                 |
        |----                      |
        |a: [[1,2],[3,4]]          |
        |b: [[3.5,4.5],[null,null]]|
        |z: [[null,null],["x","y"]]|
        └──────────────────────────┘
    """
    if how not in {"horizontal", "vertical", "diagonal"}:  # pragma: no cover
        msg = "Only vertical, horizontal and diagonal concatenations are supported."
        raise NotImplementedError(msg)
    if not items:
        msg = "No items to concatenate"
        raise ValueError(msg)
    items = list(items)
    validate_laziness(items)
    first_item = items[0]
    plx = first_item.__narwhals_namespace__()
    return first_item._from_compliant_dataframe(
        plx.concat([df._compliant_frame for df in items], how=how),
    )


def new_series(
    name: str,
    values: Any,
    dtype: DType | type[DType] | None = None,
    *,
    native_namespace: ModuleType,
) -> Series[Any]:
    """Instantiate Narwhals Series from iterable (e.g. list or array).

    Arguments:
        name: Name of resulting Series.
        values: Values of make Series from.
        dtype: (Narwhals) dtype. If not provided, the native library
            may auto-infer it from `values`.
        native_namespace: The native library to use for DataFrame creation.

    Returns:
        A new Series

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> values = [4, 1, 2, 3]
        >>> nw.new_series(name="a", values=values, dtype=nw.Int32, native_namespace=pd)
        ┌─────────────────────┐
        |   Narwhals Series   |
        |---------------------|
        |0    4               |
        |1    1               |
        |2    2               |
        |3    3               |
        |Name: a, dtype: int32|
        └─────────────────────┘
    """
    return _new_series_impl(
        name,
        values,
        dtype,
        native_namespace=native_namespace,
        version=Version.MAIN,
    )


def _new_series_impl(
    name: str,
    values: Any,
    dtype: DType | type[DType] | None = None,
    *,
    native_namespace: ModuleType,
    version: Version,
) -> Series[Any]:
    implementation = Implementation.from_native_namespace(native_namespace)

    if implementation is Implementation.POLARS:
        if dtype:
            from narwhals._polars.utils import (
                narwhals_to_native_dtype as polars_narwhals_to_native_dtype,
            )

            backend_version = parse_version(native_namespace.__version__)
            dtype_pl = polars_narwhals_to_native_dtype(
                dtype, version=version, backend_version=backend_version
            )
        else:
            dtype_pl = None

        native_series = native_namespace.Series(name=name, values=values, dtype=dtype_pl)
    elif implementation.is_pandas_like():
        if dtype:
            from narwhals._pandas_like.utils import (
                narwhals_to_native_dtype as pandas_like_narwhals_to_native_dtype,
            )

            backend_version = parse_version(native_namespace)
            pd_dtype = pandas_like_narwhals_to_native_dtype(
                dtype, None, implementation, backend_version, version
            )
            native_series = native_namespace.Series(values, name=name, dtype=pd_dtype)
        else:
            native_series = native_namespace.Series(values, name=name)

    elif implementation is Implementation.PYARROW:
        pa_dtype: pa.DataType | None = None
        if dtype:
            from narwhals._arrow.utils import (
                narwhals_to_native_dtype as arrow_narwhals_to_native_dtype,
            )

            pa_dtype = arrow_narwhals_to_native_dtype(dtype, version=version)
        native_series = native_namespace.chunked_array([values], type=pa_dtype)

    elif implementation is Implementation.DASK:  # pragma: no cover
        msg = "Dask support in Narwhals is lazy-only, so `new_series` is not supported"
        raise NotImplementedError(msg)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `from_dict` function in the top-level namespace.
            native_series = native_namespace.new_series(name, values, dtype)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `Series` constructor."
            raise AttributeError(msg) from e
    return from_native(native_series, series_only=True).alias(name)


def from_dict(
    data: Mapping[str, Any],
    schema: Mapping[str, DType] | Schema | None = None,
    *,
    backend: ModuleType | Implementation | str | None = None,
    native_namespace: ModuleType | None = None,
) -> DataFrame[Any]:
    """Instantiate DataFrame from dictionary.

    Indexes (if present, for pandas-like backends) are aligned following
    the [left-hand-rule](../pandas_like_concepts/pandas_index.md/).

    Notes:
        For pandas-like dataframes, conversion to schema is applied after dataframe
        creation.

    Arguments:
        data: Dictionary to create DataFrame from.
        schema: The DataFrame schema as Schema or dict of {name: type}.
        backend: specifies which eager backend instantiate to. Only
            necessary if inputs are not Narwhals Series.

            `backend` can be specified in various ways:

            - As `Implementation.<BACKEND>` with `BACKEND` being `PANDAS`, `PYARROW`,
                `POLARS`, `MODIN` or `CUDF`.
            - As a string: `"pandas"`, `"pyarrow"`, `"polars"`, `"modin"` or `"cudf"`.
            - Directly as a module `pandas`, `pyarrow`, `polars`, `modin` or `cudf`.
        native_namespace: The native library to use for DataFrame creation.

            **Deprecated** (v1.26.0):
                Please use `backend` instead. Note that `native_namespace` is still available
                (and won't emit a deprecation warning) if you use `narwhals.stable.v1`,
                see [perfect backwards compatibility policy](../backcompat.md/).

    Returns:
        A new DataFrame.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> data = {"c": [5, 2], "d": [1, 4]}
        >>> nw.from_dict(data, backend="pandas")
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |        c  d      |
        |     0  5  1      |
        |     1  2  4      |
        └──────────────────┘
    """
    backend = validate_native_namespace_and_backend(
        backend, native_namespace, emit_deprecation_warning=True
    )
    return _from_dict_impl(data, schema, backend=backend)


def _from_dict_impl(
    data: Mapping[str, Any],
    schema: Mapping[str, DType] | Schema | None = None,
    *,
    backend: ModuleType | Implementation | str | None = None,
) -> DataFrame[Any]:
    from narwhals.series import Series

    if not data:
        msg = "from_dict cannot be called with empty dictionary"
        raise ValueError(msg)
    if backend is None:
        for val in data.values():
            if isinstance(val, Series):
                native_namespace = val.__native_namespace__()
                break
        else:
            msg = "Calling `from_dict` without `backend` is only supported if all input values are already Narwhals Series"
            raise TypeError(msg)
        data = {key: to_native(value, pass_through=True) for key, value in data.items()}
        eager_backend = Implementation.from_native_namespace(native_namespace)
    else:
        eager_backend = Implementation.from_backend(backend)
        native_namespace = eager_backend.to_native_namespace()

    supported_eager_backends = (
        Implementation.POLARS,
        Implementation.PANDAS,
        Implementation.PYARROW,
        Implementation.MODIN,
        Implementation.CUDF,
    )
    if eager_backend is not None and eager_backend not in supported_eager_backends:
        msg = f"Unsupported `backend` value.\nExpected one of {supported_eager_backends} or None, got: {eager_backend}."
        raise ValueError(msg)
    if eager_backend is Implementation.POLARS:
        schema_pl = Schema(schema).to_polars() if schema else None
        native_frame = native_namespace.from_dict(data, schema=schema_pl)
    elif eager_backend.is_pandas_like():
        from narwhals._pandas_like.utils import align_and_extract_native

        aligned_data = {}
        left_most_series = None
        for key, native_series in data.items():
            if isinstance(native_series, native_namespace.Series):
                compliant_series = from_native(
                    native_series, series_only=True
                )._compliant_series
                if left_most_series is None:
                    left_most_series = compliant_series
                    aligned_data[key] = native_series
                else:
                    aligned_data[key] = align_and_extract_native(
                        left_most_series, compliant_series
                    )[1]
            else:
                aligned_data[key] = native_series

        native_frame = native_namespace.DataFrame.from_dict(aligned_data)

        if schema:
            from narwhals._pandas_like.utils import get_dtype_backend

            it: Iterable[DTypeBackend] = (
                get_dtype_backend(native_type, eager_backend)
                for native_type in native_frame.dtypes
            )
            pd_schema = Schema(schema).to_pandas(it)
            native_frame = native_frame.astype(pd_schema)

    elif eager_backend is Implementation.PYARROW:
        pa_schema = Schema(schema).to_arrow() if schema is not None else schema
        native_frame = native_namespace.table(data, schema=pa_schema)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `from_dict` function in the top-level namespace.
            native_frame = native_namespace.from_dict(data, schema=schema)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `from_dict` function."
            raise AttributeError(msg) from e
    return from_native(native_frame, eager_only=True)


def from_numpy(
    data: _2DArray,
    schema: Mapping[str, DType] | Schema | Sequence[str] | None = None,
    *,
    native_namespace: ModuleType,
) -> DataFrame[Any]:
    """Construct a DataFrame from a NumPy ndarray.

    Notes:
        Only row orientation is currently supported.

        For pandas-like dataframes, conversion to schema is applied after dataframe
        creation.

    Arguments:
        data: Two-dimensional data represented as a NumPy ndarray.
        schema: The DataFrame schema as Schema, dict of {name: type}, or a sequence of str.
        native_namespace: The native library to use for DataFrame creation.

    Returns:
        A new DataFrame.

    Examples:
        >>> import numpy as np
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> arr = np.array([[5, 2, 1], [1, 4, 3]])
        >>> schema = {"c": nw.Int16(), "d": nw.Float32(), "e": nw.Int8()}
        >>> nw.from_numpy(arr, schema=schema, native_namespace=pa)
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  pyarrow.Table   |
        |  c: int16        |
        |  d: float        |
        |  e: int8         |
        |  ----            |
        |  c: [[5,1]]      |
        |  d: [[2,4]]      |
        |  e: [[1,3]]      |
        └──────────────────┘
    """
    return _from_numpy_impl(data, schema, native_namespace=native_namespace)


def _from_numpy_impl(
    data: _2DArray,
    schema: Mapping[str, DType] | Schema | Sequence[str] | None = None,
    *,
    native_namespace: ModuleType,
) -> DataFrame[Any]:
    from narwhals.schema import Schema

    if not is_numpy_array_2d(data):
        msg = "`from_numpy` only accepts 2D numpy arrays"
        raise ValueError(msg)
    implementation = Implementation.from_native_namespace(native_namespace)

    if implementation is Implementation.POLARS:
        if isinstance(schema, (Mapping, Schema)):
            schema_pl: pl.Schema | Sequence[str] | None = Schema(schema).to_polars()
        elif is_sequence_but_not_str(schema) or schema is None:
            schema_pl = schema
        else:
            msg = (
                "`schema` is expected to be one of the following types: "
                "Mapping[str, DType] | Schema | Sequence[str]. "
                f"Got {type(schema)}."
            )
            raise TypeError(msg)
        native_frame = native_namespace.from_numpy(data, schema=schema_pl)

    elif implementation.is_pandas_like():
        if isinstance(schema, (Mapping, Schema)):
            from narwhals._pandas_like.utils import get_dtype_backend

            it: Iterable[DTypeBackend] = (
                get_dtype_backend(native_type, implementation)
                for native_type in schema.values()
            )
            native_frame = native_namespace.DataFrame(data, columns=schema.keys()).astype(
                Schema(schema).to_pandas(it)
            )
        elif is_sequence_but_not_str(schema):
            native_frame = native_namespace.DataFrame(data, columns=list(schema))
        elif schema is None:
            native_frame = native_namespace.DataFrame(
                data, columns=[f"column_{x}" for x in range(data.shape[1])]
            )
        else:
            msg = (
                "`schema` is expected to be one of the following types: "
                "Mapping[str, DType] | Schema | Sequence[str]. "
                f"Got {type(schema)}."
            )
            raise TypeError(msg)

    elif implementation is Implementation.PYARROW:
        pa_arrays = [native_namespace.array(val) for val in data.T]
        if isinstance(schema, (Mapping, Schema)):
            schema_pa = Schema(schema).to_arrow()
            native_frame = native_namespace.Table.from_arrays(pa_arrays, schema=schema_pa)
        elif is_sequence_but_not_str(schema):
            native_frame = native_namespace.Table.from_arrays(
                pa_arrays, names=list(schema)
            )
        elif schema is None:
            native_frame = native_namespace.Table.from_arrays(
                pa_arrays, names=[f"column_{x}" for x in range(data.shape[1])]
            )
        else:
            msg = (
                "`schema` is expected to be one of the following types: "
                "Mapping[str, DType] | Schema | Sequence[str]. "
                f"Got {type(schema)}."
            )
            raise TypeError(msg)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `from_numpy` function in the top-level namespace.
            native_frame = native_namespace.from_numpy(data, schema=schema)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `from_numpy` function."
            raise AttributeError(msg) from e
    return from_native(native_frame, eager_only=True)


def from_arrow(
    native_frame: ArrowStreamExportable, *, native_namespace: ModuleType
) -> DataFrame[Any]:
    """Construct a DataFrame from an object which supports the PyCapsule Interface.

    Arguments:
        native_frame: Object which implements `__arrow_c_stream__`.
        native_namespace: The native library to use for DataFrame creation.

    Returns:
        A new DataFrame.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pd.DataFrame({"a": [1, 2], "b": [4.2, 5.1]})
        >>> nw.from_arrow(df_native, native_namespace=pl)
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  shape: (2, 2)   |
        |  ┌─────┬─────┐   |
        |  │ a   ┆ b   │   |
        |  │ --- ┆ --- │   |
        |  │ i64 ┆ f64 │   |
        |  ╞═════╪═════╡   |
        |  │ 1   ┆ 4.2 │   |
        |  │ 2   ┆ 5.1 │   |
        |  └─────┴─────┘   |
        └──────────────────┘
    """
    if not hasattr(native_frame, "__arrow_c_stream__"):
        msg = f"Given object of type {type(native_frame)} does not support PyCapsule interface"
        raise TypeError(msg)
    implementation = Implementation.from_native_namespace(native_namespace)

    if implementation.is_polars() and parse_version(native_namespace) >= (1, 3):
        native_frame = native_namespace.DataFrame(native_frame)
    elif implementation in {
        Implementation.PANDAS,
        Implementation.MODIN,
        Implementation.CUDF,
        Implementation.POLARS,
    }:
        # These don't (yet?) support the PyCapsule Interface for import
        # so we go via PyArrow
        try:
            import pyarrow as pa  # ignore-banned-import
        except ModuleNotFoundError as exc:  # pragma: no cover
            msg = f"PyArrow>=14.0.0 is required for `from_arrow` for object of type {native_namespace}"
            raise ModuleNotFoundError(msg) from exc
        if parse_version(pa) < (14, 0):  # pragma: no cover
            msg = f"PyArrow>=14.0.0 is required for `from_arrow` for object of type {native_namespace}"
            raise ModuleNotFoundError(msg) from None

        tbl = pa.table(native_frame)
        if implementation is Implementation.PANDAS:
            native_frame = tbl.to_pandas()
        elif implementation is Implementation.MODIN:  # pragma: no cover
            from modin.pandas.utils import from_arrow

            native_frame = from_arrow(tbl)
        elif implementation is Implementation.CUDF:  # pragma: no cover
            native_frame = native_namespace.DataFrame.from_arrow(tbl)
        elif implementation is Implementation.POLARS:  # pragma: no cover
            native_frame = native_namespace.from_arrow(tbl)
        else:  # pragma: no cover
            msg = "congratulations, you entered unrecheable code - please report a bug"
            raise AssertionError(msg)
    elif implementation is Implementation.PYARROW:
        native_frame = native_namespace.table(native_frame)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement PyCapsule support
            native_frame = native_namespace.DataFrame(native_frame)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `DataFrame` class which accepts object which supports PyCapsule Interface."
            raise AttributeError(msg) from e
    return from_native(native_frame, eager_only=True)


def _get_sys_info() -> dict[str, str]:
    """System information.

    Returns system and Python version information

    Copied from sklearn

    Returns:
        Dictionary with system info.
    """
    python = sys.version.replace("\n", " ")

    blob = (
        ("python", python),
        ("executable", sys.executable),
        ("machine", platform.platform()),
    )

    return dict(blob)


def _get_deps_info() -> dict[str, str]:
    """Overview of the installed version of main dependencies.

    This function does not import the modules to collect the version numbers
    but instead relies on standard Python package metadata.

    Returns version information on relevant Python libraries

    This function and show_versions were copied from sklearn and adapted

    Returns:
        Mapping from dependency to version.
    """
    from importlib.metadata import PackageNotFoundError
    from importlib.metadata import version

    from narwhals import __version__

    deps = ("pandas", "polars", "cudf", "modin", "pyarrow", "numpy")
    deps_info = {"narwhals": __version__}

    for modname in deps:
        try:
            deps_info[modname] = version(modname)
        except PackageNotFoundError:  # noqa: PERF203
            deps_info[modname] = ""
    return deps_info


def show_versions() -> None:
    """Print useful debugging information.

    Examples:
        >>> from narwhals import show_versions
        >>> show_versions()  # doctest: +SKIP
    """
    sys_info = _get_sys_info()
    deps_info = _get_deps_info()

    print("\nSystem:")  # noqa: T201
    for k, stat in sys_info.items():
        print(f"{k:>10}: {stat}")  # noqa: T201

    print("\nPython dependencies:")  # noqa: T201
    for k, stat in deps_info.items():
        print(f"{k:>13}: {stat}")  # noqa: T201


def get_level(
    obj: DataFrame[Any] | LazyFrame[Any] | Series[IntoSeriesT],
) -> Literal["full", "lazy", "interchange"]:
    """Level of support Narwhals has for current object.

    Arguments:
        obj: Dataframe or Series.

    Returns:
        This can be one of:

            - 'full': full Narwhals API support
            - 'lazy': only lazy operations are supported. This excludes anything
              which involves iterating over rows in Python.
            - 'interchange': only metadata operations are supported (`df.schema`)
    """
    return obj._level


def read_csv(
    source: str,
    *,
    backend: ModuleType | Implementation | str | None = None,
    native_namespace: ModuleType | None = None,
    **kwargs: Any,
) -> DataFrame[Any]:
    """Read a CSV file into a DataFrame.

    Arguments:
        source: Path to a file.
        backend: The eager backend for DataFrame creation.
            `backend` can be specified in various ways:

            - As `Implementation.<BACKEND>` with `BACKEND` being `PANDAS`, `PYARROW`,
                `POLARS`, `MODIN` or `CUDF`.
            - As a string: `"pandas"`, `"pyarrow"`, `"polars"`, `"modin"` or `"cudf"`.
            - Directly as a module `pandas`, `pyarrow`, `polars`, `modin` or `cudf`.
        native_namespace: The native library to use for DataFrame creation.

            **Deprecated** (v1.27.2):
                Please use `backend` instead. Note that `native_namespace` is still available
                (and won't emit a deprecation warning) if you use `narwhals.stable.v1`,
                see [perfect backwards compatibility policy](../backcompat.md/).
        kwargs: Extra keyword arguments which are passed to the native CSV reader.
            For example, you could use
            `nw.read_csv('file.csv', backend='pandas', engine='pyarrow')`.

    Returns:
        DataFrame.

    Examples:
        >>> import narwhals as nw
        >>> nw.read_csv("file.csv", backend="pandas")  # doctest:+SKIP
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |        a   b     |
        |     0  1   4     |
        |     1  2   5     |
        └──────────────────┘
    """
    backend = validate_native_namespace_and_backend(
        backend, native_namespace, emit_deprecation_warning=True
    )
    if backend is None:  # pragma: no cover
        msg = "`backend` must be specified in `read_csv`."
        raise ValueError(msg)
    return _read_csv_impl(source, backend=backend, **kwargs)


def _read_csv_impl(
    source: str, *, backend: ModuleType | Implementation | str, **kwargs: Any
) -> DataFrame[Any]:
    eager_backend = Implementation.from_backend(backend)
    native_namespace = eager_backend.to_native_namespace()
    if eager_backend in {
        Implementation.POLARS,
        Implementation.PANDAS,
        Implementation.MODIN,
        Implementation.CUDF,
    }:
        native_frame = native_namespace.read_csv(source, **kwargs)
    elif eager_backend is Implementation.PYARROW:
        from pyarrow import csv  # ignore-banned-import

        native_frame = csv.read_csv(source, **kwargs)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `read_csv` function in the top-level namespace.
            native_frame = native_namespace.read_csv(source=source, **kwargs)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `read_csv` function."
            raise AttributeError(msg) from e
    return from_native(native_frame, eager_only=True)


def scan_csv(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
) -> LazyFrame[Any]:
    """Lazily read from a CSV file.

    For the libraries that do not support lazy dataframes, the function reads
    a csv file eagerly and then converts the resulting dataframe to a lazyframe.

    Arguments:
        source: Path to a file.
        native_namespace: The native library to use for DataFrame creation.
        kwargs: Extra keyword arguments which are passed to the native CSV reader.
            For example, you could use
            `nw.scan_csv('file.csv', native_namespace=pd, engine='pyarrow')`.

    Returns:
        LazyFrame.

    Examples:
        >>> import duckdb
        >>> import narwhals as nw
        >>>
        >>> nw.scan_csv("file.csv", native_namespace=duckdb).to_native()  # doctest:+SKIP
        ┌─────────┬───────┐
        │    a    │   b   │
        │ varchar │ int32 │
        ├─────────┼───────┤
        │ x       │     1 │
        │ y       │     2 │
        │ z       │     3 │
        └─────────┴───────┘
    """
    return _scan_csv_impl(source, native_namespace=native_namespace, **kwargs)


def _scan_csv_impl(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
) -> LazyFrame[Any]:
    implementation = Implementation.from_native_namespace(native_namespace)
    if implementation is Implementation.POLARS:
        native_frame = native_namespace.scan_csv(source, **kwargs)
    elif implementation in {
        Implementation.PANDAS,
        Implementation.MODIN,
        Implementation.CUDF,
        Implementation.DASK,
        Implementation.DUCKDB,
    }:
        native_frame = native_namespace.read_csv(source, **kwargs)
    elif implementation is Implementation.PYARROW:
        from pyarrow import csv  # ignore-banned-import

        native_frame = csv.read_csv(source, **kwargs)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `scan_csv` function in the top-level namespace.
            native_frame = native_namespace.scan_csv(source=source, **kwargs)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `scan_csv` function."
            raise AttributeError(msg) from e
    return from_native(native_frame).lazy()


def read_parquet(
    source: str,
    *,
    native_namespace: ModuleType,
    **kwargs: Any,
) -> DataFrame[Any]:
    """Read into a DataFrame from a parquet file.

    Arguments:
        source: Path to a file.
        native_namespace: The native library to use for DataFrame creation.
        kwargs: Extra keyword arguments which are passed to the native parquet reader.
            For example, you could use
            `nw.read_parquet('file.parquet', native_namespace=pd, engine='pyarrow')`.

    Returns:
        DataFrame.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> nw.read_parquet("file.parquet", native_namespace=pa)  # doctest:+SKIP
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |pyarrow.Table     |
        |a: int64          |
        |c: double         |
        |----              |
        |a: [[1,2]]        |
        |c: [[0.2,0.1]]    |
        └──────────────────┘
    """
    return _read_parquet_impl(source, native_namespace=native_namespace, **kwargs)


def _read_parquet_impl(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
) -> DataFrame[Any]:
    implementation = Implementation.from_native_namespace(native_namespace)
    if implementation in {
        Implementation.POLARS,
        Implementation.PANDAS,
        Implementation.MODIN,
        Implementation.CUDF,
        Implementation.DUCKDB,
    }:
        native_frame = native_namespace.read_parquet(source, **kwargs)
    elif implementation is Implementation.PYARROW:
        import pyarrow.parquet as pq  # ignore-banned-import

        native_frame = pq.read_table(source, **kwargs)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `read_parquet` function in the top-level namespace.
            native_frame = native_namespace.read_parquet(source=source, **kwargs)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `read_parquet` function."
            raise AttributeError(msg) from e
    return from_native(native_frame, eager_only=True)


def scan_parquet(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
) -> LazyFrame[Any]:
    """Lazily read from a parquet file.

    For the libraries that do not support lazy dataframes, the function reads
    a parquet file eagerly and then converts the resulting dataframe to a lazyframe.

    Arguments:
        source: Path to a file.
        native_namespace: The native library to use for DataFrame creation.
        kwargs: Extra keyword arguments which are passed to the native parquet reader.
            For example, you could use
            `nw.scan_parquet('file.parquet', native_namespace=pd, engine='pyarrow')`.

    Returns:
        LazyFrame.

    Examples:
        >>> import dask.dataframe as dd
        >>> import narwhals as nw
        >>>
        >>> nw.scan_parquet(
        ...     "file.parquet", native_namespace=dd
        ... ).collect()  # doctest:+SKIP
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |        a   b     |
        |     0  1   4     |
        |     1  2   5     |
        └──────────────────┘
    """
    return _scan_parquet_impl(source, native_namespace=native_namespace, **kwargs)


def _scan_parquet_impl(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
) -> LazyFrame[Any]:
    implementation = Implementation.from_native_namespace(native_namespace)
    if implementation is Implementation.POLARS:
        native_frame = native_namespace.scan_parquet(source, **kwargs)
    elif implementation in {
        Implementation.PANDAS,
        Implementation.MODIN,
        Implementation.CUDF,
        Implementation.DASK,
        Implementation.DUCKDB,
    }:
        native_frame = native_namespace.read_parquet(source, **kwargs)
    elif implementation is Implementation.PYARROW:
        import pyarrow.parquet as pq  # ignore-banned-import

        native_frame = pq.read_table(source, **kwargs)
    else:  # pragma: no cover
        try:
            # implementation is UNKNOWN, Narwhals extension using this feature should
            # implement `scan_parquet` function in the top-level namespace.
            native_frame = native_namespace.scan_parquet(source=source, **kwargs)
        except AttributeError as e:
            msg = "Unknown namespace is expected to implement `scan_parquet` function."
            raise AttributeError(msg) from e
    return from_native(native_frame).lazy()


def col(*names: str | Iterable[str]) -> Expr:
    """Creates an expression that references one or more columns by their name(s).

    Arguments:
        names: Name(s) of the columns to use.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [1, 2], "b": [3, 4], "c": ["x", "z"]})
        >>> nw.from_native(df_native).select(nw.col("a", "b") * nw.col("b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  shape: (2, 2)   |
        |  ┌─────┬─────┐   |
        |  │ a   ┆ b   │   |
        |  │ --- ┆ --- │   |
        |  │ i64 ┆ i64 │   |
        |  ╞═════╪═════╡   |
        |  │ 3   ┆ 9   │   |
        |  │ 8   ┆ 16  │   |
        |  └─────┴─────┘   |
        └──────────────────┘
    """

    def func(plx: Any) -> Any:
        return plx.col(*flatten(names))

    return Expr(func, ExprMetadata.selector())


def exclude(*names: str | Iterable[str]) -> Expr:
    """Creates an expression that excludes columns by their name(s).

    Arguments:
        names: Name(s) of the columns to exclude.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [1, 2], "b": [3, 4], "c": ["x", "z"]})
        >>> nw.from_native(df_native).select(nw.exclude("c", "a"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  shape: (2, 1)   |
        |  ┌─────┐         |
        |  │ b   │         |
        |  │ --- │         |
        |  │ i64 │         |
        |  ╞═════╡         |
        |  │ 3   │         |
        |  │ 4   │         |
        |  └─────┘         |
        └──────────────────┘
    """
    exclude_names = frozenset(flatten(names))

    def func(plx: Any) -> Any:
        return plx.exclude(exclude_names)

    return Expr(func, ExprMetadata.selector())


def nth(*indices: int | Sequence[int]) -> Expr:
    """Creates an expression that references one or more columns by their index(es).

    Notes:
        `nth` is not supported for Polars version<1.0.0. Please use
        [`narwhals.col`][] instead.

    Arguments:
        indices: One or more indices representing the columns to retrieve.

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> df_native = pa.table({"a": [1, 2], "b": [3, 4], "c": [0.123, 3.14]})
        >>> nw.from_native(df_native).select(nw.nth(0, 2) * 2)
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |pyarrow.Table     |
        |a: int64          |
        |c: double         |
        |----              |
        |a: [[2,4]]        |
        |c: [[0.246,6.28]] |
        └──────────────────┘
    """

    def func(plx: Any) -> Any:
        return plx.nth(*flatten(indices))

    return Expr(func, ExprMetadata.selector())


# Add underscore so it doesn't conflict with builtin `all`
def all_() -> Expr:
    """Instantiate an expression representing all columns.

    Returns:
        A new expression.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> df_native = pd.DataFrame({"a": [1, 2], "b": [3.14, 0.123]})
        >>> nw.from_native(df_native).select(nw.all() * 2)
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |      a      b    |
        |   0  2  6.280    |
        |   1  4  0.246    |
        └──────────────────┘
    """
    return Expr(lambda plx: plx.all(), ExprMetadata.selector())


# Add underscore so it doesn't conflict with builtin `len`
def len_() -> Expr:
    """Return the number of rows.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [1, 2], "b": [5, None]})
        >>> nw.from_native(df_native).select(nw.len())
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  shape: (1, 1)   |
        |  ┌─────┐         |
        |  │ len │         |
        |  │ --- │         |
        |  │ u32 │         |
        |  ╞═════╡         |
        |  │ 2   │         |
        |  └─────┘         |
        └──────────────────┘
    """

    def func(plx: Any) -> Any:
        return plx.len()

    return Expr(func, ExprMetadata(ExprKind.AGGREGATION, n_open_windows=0))


def sum(*columns: str) -> Expr:
    """Sum all values.

    Note:
        Syntactic sugar for ``nw.col(columns).sum()``

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function

    Returns:
        A new expression.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> df_native = pd.DataFrame({"a": [1, 2], "b": [-1.4, 6.2]})
        >>> nw.from_native(df_native).select(nw.sum("a", "b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |       a    b     |
        |    0  3  4.8     |
        └──────────────────┘
    """
    return col(*columns).sum()


def mean(*columns: str) -> Expr:
    """Get the mean value.

    Note:
        Syntactic sugar for ``nw.col(columns).mean()``

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> df_native = pa.table({"a": [1, 8, 3], "b": [3.14, 6.28, 42.1]})
        >>> nw.from_native(df_native).select(nw.mean("a", "b"))
        ┌─────────────────────────┐
        |   Narwhals DataFrame    |
        |-------------------------|
        |pyarrow.Table            |
        |a: double                |
        |b: double                |
        |----                     |
        |a: [[4]]                 |
        |b: [[17.173333333333336]]|
        └─────────────────────────┘
    """
    return col(*columns).mean()


def median(*columns: str) -> Expr:
    """Get the median value.

    Notes:
        - Syntactic sugar for ``nw.col(columns).median()``
        - Results might slightly differ across backends due to differences in the
            underlying algorithms used to compute the median.

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [4, 5, 2]})
        >>> nw.from_native(df_native).select(nw.median("a"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  shape: (1, 1)   |
        |  ┌─────┐         |
        |  │ a   │         |
        |  │ --- │         |
        |  │ f64 │         |
        |  ╞═════╡         |
        |  │ 4.0 │         |
        |  └─────┘         |
        └──────────────────┘
    """
    return col(*columns).median()


def min(*columns: str) -> Expr:
    """Return the minimum value.

    Note:
       Syntactic sugar for ``nw.col(columns).min()``.

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function.

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> df_native = pa.table({"a": [1, 2], "b": [5, 10]})
        >>> nw.from_native(df_native).select(nw.min("a", "b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |  pyarrow.Table   |
        |  a: int64        |
        |  b: int64        |
        |  ----            |
        |  a: [[1]]        |
        |  b: [[5]]        |
        └──────────────────┘
    """
    return col(*columns).min()


def max(*columns: str) -> Expr:
    """Return the maximum value.

    Note:
       Syntactic sugar for ``nw.col(columns).max()``.

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function.

    Returns:
        A new expression.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> df_native = pd.DataFrame({"a": [1, 2], "b": [5, 10]})
        >>> nw.from_native(df_native).select(nw.max("a", "b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |        a   b     |
        |     0  2  10     |
        └──────────────────┘
    """
    return col(*columns).max()


def sum_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Sum all values horizontally across columns.

    Warning:
        Unlike Polars, we support horizontal sum over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [1, 2, 3], "b": [5, 10, None]})
        >>> nw.from_native(df_native).with_columns(sum=nw.sum_horizontal("a", "b"))
        ┌────────────────────┐
        | Narwhals DataFrame |
        |--------------------|
        |shape: (3, 3)       |
        |┌─────┬──────┬─────┐|
        |│ a   ┆ b    ┆ sum │|
        |│ --- ┆ ---  ┆ --- │|
        |│ i64 ┆ i64  ┆ i64 │|
        |╞═════╪══════╪═════╡|
        |│ 1   ┆ 5    ┆ 6   │|
        |│ 2   ┆ 10   ┆ 12  │|
        |│ 3   ┆ null ┆ 3   │|
        |└─────┴──────┴─────┘|
        └────────────────────┘
    """
    if not exprs:
        msg = "At least one expression must be passed to `sum_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.sum_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


def min_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Get the minimum value horizontally across columns.

    Notes:
        We support `min_horizontal` over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> df_native = pa.table({"a": [1, 8, 3], "b": [4, 5, None]})
        >>> nw.from_native(df_native).with_columns(h_min=nw.min_horizontal("a", "b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        | pyarrow.Table    |
        | a: int64         |
        | b: int64         |
        | h_min: int64     |
        | ----             |
        | a: [[1,8,3]]     |
        | b: [[4,5,null]]  |
        | h_min: [[1,5,3]] |
        └──────────────────┘
    """
    if not exprs:
        msg = "At least one expression must be passed to `min_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.min_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


def max_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Get the maximum value horizontally across columns.

    Notes:
        We support `max_horizontal` over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> df_native = pl.DataFrame({"a": [1, 8, 3], "b": [4, 5, None]})
        >>> nw.from_native(df_native).with_columns(h_max=nw.max_horizontal("a", "b"))
        ┌──────────────────────┐
        |  Narwhals DataFrame  |
        |----------------------|
        |shape: (3, 3)         |
        |┌─────┬──────┬───────┐|
        |│ a   ┆ b    ┆ h_max │|
        |│ --- ┆ ---  ┆ ---   │|
        |│ i64 ┆ i64  ┆ i64   │|
        |╞═════╪══════╪═══════╡|
        |│ 1   ┆ 4    ┆ 4     │|
        |│ 8   ┆ 5    ┆ 8     │|
        |│ 3   ┆ null ┆ 3     │|
        |└─────┴──────┴───────┘|
        └──────────────────────┘
    """
    if not exprs:
        msg = "At least one expression must be passed to `max_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.max_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


class When:
    def __init__(self: Self, *predicates: IntoExpr | Iterable[IntoExpr]) -> None:
        self._predicate = all_horizontal(*flatten(predicates))
        check_expressions_preserve_length(self._predicate, function_name="when")

    def then(self: Self, value: IntoExpr | Any) -> Then:
        return Then(
            lambda plx: apply_n_ary_operation(
                plx,
                lambda *args: plx.when(args[0]).then(args[1]),
                self._predicate,
                value,
                str_as_lit=False,
            ),
            combine_metadata(self._predicate, value, str_as_lit=False),
        )


class Then(Expr):
    def otherwise(self: Self, value: IntoExpr | Any) -> Expr:
        kind = infer_kind(value, str_as_lit=False)

        def func(plx: CompliantNamespace[Any, Any]) -> CompliantExpr[Any, Any]:
            compliant_expr = self._to_compliant_expr(plx)
            compliant_value = extract_compliant(plx, value, str_as_lit=False)
            if is_scalar_like(kind) and is_compliant_expr(compliant_value):
                compliant_value = compliant_value.broadcast(kind)
            return compliant_expr.otherwise(compliant_value)  # type: ignore[attr-defined, no-any-return]

        return Expr(
            func,
            combine_metadata(self, value, str_as_lit=False),
        )


def when(*predicates: IntoExpr | Iterable[IntoExpr]) -> When:
    """Start a `when-then-otherwise` expression.

    Expression similar to an `if-else` statement in Python. Always initiated by a
    `pl.when(<condition>).then(<value if condition>)`, and optionally followed by a
    `.otherwise(<value if condition is false>)` can be appended at the end. If not
    appended, and the condition is not `True`, `None` will be returned.

    !!! info

        Chaining multiple `.when(<condition>).then(<value>)` statements is currently
        not supported.
        See [Narwhals#668](https://github.com/narwhals-dev/narwhals/issues/668).

    Arguments:
        predicates: Condition(s) that must be met in order to apply the subsequent
            statement. Accepts one or more boolean expressions, which are implicitly
            combined with `&`. String input is parsed as a column name.

    Returns:
        A "when" object, which `.then` can be called on.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> data = {"a": [1, 2, 3], "b": [5, 10, 15]}
        >>> df_native = pd.DataFrame(data)
        >>> nw.from_native(df_native).with_columns(
        ...     nw.when(nw.col("a") < 3).then(5).otherwise(6).alias("a_when")
        ... )
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |    a   b  a_when |
        | 0  1   5       5 |
        | 1  2  10       5 |
        | 2  3  15       6 |
        └──────────────────┘
    """
    return When(*predicates)


def all_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    r"""Compute the bitwise AND horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> data = {
        ...     "a": [False, False, True, True, False, None],
        ...     "b": [False, True, True, None, None, None],
        ... }
        >>> df_native = pa.table(data)
        >>> nw.from_native(df_native).select("a", "b", all=nw.all_horizontal("a", "b"))
        ┌─────────────────────────────────────────┐
        |           Narwhals DataFrame            |
        |-----------------------------------------|
        |pyarrow.Table                            |
        |a: bool                                  |
        |b: bool                                  |
        |all: bool                                |
        |----                                     |
        |a: [[false,false,true,true,false,null]]  |
        |b: [[false,true,true,null,null,null]]    |
        |all: [[false,false,true,null,false,null]]|
        └─────────────────────────────────────────┘

    """
    if not exprs:
        msg = "At least one expression must be passed to `all_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.all_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


def lit(value: Any, dtype: DType | type[DType] | None = None) -> Expr:
    """Return an expression representing a literal value.

    Arguments:
        value: The value to use as literal.
        dtype: The data type of the literal value. If not provided, the data type will
            be inferred.

    Returns:
        A new expression.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> df_native = pd.DataFrame({"a": [1, 2]})
        >>> nw.from_native(df_native).with_columns(nw.lit(3))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |     a  literal   |
        |  0  1        3   |
        |  1  2        3   |
        └──────────────────┘
    """
    if is_numpy_array(value):
        msg = (
            "numpy arrays are not supported as literal values. "
            "Consider using `with_columns` to create a new column from the array."
        )
        raise ValueError(msg)

    if isinstance(value, (list, tuple)):
        msg = f"Nested datatypes are not supported yet. Got {value}"
        raise NotImplementedError(msg)

    return Expr(
        lambda plx: plx.lit(value, dtype),
        ExprMetadata(ExprKind.LITERAL, n_open_windows=0),
    )


def any_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    r"""Compute the bitwise OR horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import polars as pl
        >>> import narwhals as nw
        >>>
        >>> data = {
        ...     "a": [False, False, True, True, False, None],
        ...     "b": [False, True, True, None, None, None],
        ... }
        >>> df_native = pl.DataFrame(data)
        >>> nw.from_native(df_native).select("a", "b", any=nw.any_horizontal("a", "b"))
        ┌─────────────────────────┐
        |   Narwhals DataFrame    |
        |-------------------------|
        |shape: (6, 3)            |
        |┌───────┬───────┬───────┐|
        |│ a     ┆ b     ┆ any   │|
        |│ ---   ┆ ---   ┆ ---   │|
        |│ bool  ┆ bool  ┆ bool  │|
        |╞═══════╪═══════╪═══════╡|
        |│ false ┆ false ┆ false │|
        |│ false ┆ true  ┆ true  │|
        |│ true  ┆ true  ┆ true  │|
        |│ true  ┆ null  ┆ true  │|
        |│ false ┆ null  ┆ null  │|
        |│ null  ┆ null  ┆ null  │|
        |└───────┴───────┴───────┘|
        └─────────────────────────┘
    """
    if not exprs:
        msg = "At least one expression must be passed to `any_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.any_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


def mean_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Compute the mean of all values horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.

    Examples:
        >>> import pyarrow as pa
        >>> import narwhals as nw
        >>>
        >>> data = {
        ...     "a": [1, 8, 3],
        ...     "b": [4, 5, None],
        ...     "c": ["x", "y", "z"],
        ... }
        >>> df_native = pa.table(data)

        We define a dataframe-agnostic function that computes the horizontal mean of "a"
        and "b" columns:

        >>> nw.from_native(df_native).select(nw.mean_horizontal("a", "b"))
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        | pyarrow.Table    |
        | a: double        |
        | ----             |
        | a: [[2.5,6.5,3]] |
        └──────────────────┘
    """
    if not exprs:
        msg = "At least one expression must be passed to `mean_horizontal`"
        raise ValueError(msg)
    flat_exprs = flatten(exprs)
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx, plx.mean_horizontal, *flat_exprs, str_as_lit=False
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )


def concat_str(
    exprs: IntoExpr | Iterable[IntoExpr],
    *more_exprs: IntoExpr,
    separator: str = "",
    ignore_nulls: bool = False,
) -> Expr:
    r"""Horizontally concatenate columns into a single string column.

    Arguments:
        exprs: Columns to concatenate into a single string column. Accepts expression
            input. Strings are parsed as column names, other non-expression inputs are
            parsed as literals. Non-`String` columns are cast to `String`.
        *more_exprs: Additional columns to concatenate into a single string column,
            specified as positional arguments.
        separator: String that will be used to separate the values of each column.
        ignore_nulls: Ignore null values (default is `False`).
            If set to `False`, null values will be propagated and if the row contains any
            null values, the output is null.

    Returns:
        A new expression.

    Examples:
        >>> import pandas as pd
        >>> import narwhals as nw
        >>>
        >>> data = {
        ...     "a": [1, 2, 3],
        ...     "b": ["dogs", "cats", None],
        ...     "c": ["play", "swim", "walk"],
        ... }
        >>> df_native = pd.DataFrame(data)
        >>> (
        ...     nw.from_native(df_native).select(
        ...         nw.concat_str(
        ...             [
        ...                 nw.col("a") * 2,
        ...                 nw.col("b"),
        ...                 nw.col("c"),
        ...             ],
        ...             separator=" ",
        ...         ).alias("full_sentence")
        ...     )
        ... )
        ┌──────────────────┐
        |Narwhals DataFrame|
        |------------------|
        |   full_sentence  |
        | 0   2 dogs play  |
        | 1   4 cats swim  |
        | 2          None  |
        └──────────────────┘
    """
    flat_exprs = flatten([*flatten([exprs]), *more_exprs])
    return Expr(
        lambda plx: apply_n_ary_operation(
            plx,
            lambda *args: plx.concat_str(
                *args, separator=separator, ignore_nulls=ignore_nulls
            ),
            *flat_exprs,
            str_as_lit=False,
        ),
        combine_metadata(*flat_exprs, str_as_lit=False),
    )
