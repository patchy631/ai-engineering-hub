from __future__ import annotations

import os
import re
from datetime import timezone
from enum import Enum
from enum import auto
from inspect import getattr_static
from secrets import token_hex
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Container
from typing import Iterable
from typing import Literal
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from typing import Union
from typing import cast
from typing import overload
from warnings import warn

from narwhals.dependencies import get_cudf
from narwhals.dependencies import get_dask_dataframe
from narwhals.dependencies import get_duckdb
from narwhals.dependencies import get_ibis
from narwhals.dependencies import get_modin
from narwhals.dependencies import get_pandas
from narwhals.dependencies import get_polars
from narwhals.dependencies import get_pyarrow
from narwhals.dependencies import get_pyspark_sql
from narwhals.dependencies import get_sqlframe
from narwhals.dependencies import is_cudf_series
from narwhals.dependencies import is_modin_series
from narwhals.dependencies import is_pandas_dataframe
from narwhals.dependencies import is_pandas_like_dataframe
from narwhals.dependencies import is_pandas_like_series
from narwhals.dependencies import is_pandas_series
from narwhals.dependencies import is_polars_series
from narwhals.dependencies import is_pyarrow_chunked_array
from narwhals.exceptions import ColumnNotFoundError
from narwhals.exceptions import DuplicateError
from narwhals.exceptions import InvalidOperationError

if TYPE_CHECKING:
    from types import ModuleType
    from typing import AbstractSet as Set

    import pandas as pd
    from typing_extensions import Self
    from typing_extensions import TypeAlias
    from typing_extensions import TypeIs

    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame
    from narwhals.dtypes import DType
    from narwhals.series import Series
    from narwhals.typing import CompliantDataFrame
    from narwhals.typing import CompliantExpr
    from narwhals.typing import CompliantFrameT
    from narwhals.typing import CompliantLazyFrame
    from narwhals.typing import CompliantSeries
    from narwhals.typing import DataFrameLike
    from narwhals.typing import DTypes
    from narwhals.typing import IntoSeriesT
    from narwhals.typing import SizeUnit
    from narwhals.typing import SupportsNativeNamespace
    from narwhals.typing import TimeUnit

    FrameOrSeriesT = TypeVar(
        "FrameOrSeriesT", bound=Union[LazyFrame[Any], DataFrame[Any], Series[Any]]
    )
    _T = TypeVar("_T")
    _T1 = TypeVar("_T1")
    _T2 = TypeVar("_T2")
    _T3 = TypeVar("_T3")
    _Fn = TypeVar("_Fn", bound="Callable[..., Any]")

    _TracksDepth: TypeAlias = "Literal[Implementation.DASK,Implementation.CUDF,Implementation.MODIN,Implementation.PANDAS,Implementation.PYSPARK]"

    class _SupportsVersion(Protocol):
        __version__: str

    class _SupportsGet(Protocol):  # noqa: PYI046
        def __get__(self, instance: Any, owner: Any | None = None, /) -> Any: ...

    class _StoresImplementation(Protocol):
        _implementation: Implementation
        """Implementation of native object (pandas, Polars, PyArrow, ...)."""

    class _StoresBackendVersion(Protocol):
        _backend_version: tuple[int, ...]
        """Version tuple for a native package."""

    class _StoresVersion(Protocol):
        _version: Version
        """Narwhals API version (V1 or MAIN)."""

    class _LimitedContext(_StoresBackendVersion, _StoresVersion, Protocol):
        """Provides 2 attributes.

        - `_backend_version`
        - `_version`
        """

    class _FullContext(_StoresImplementation, _LimitedContext, Protocol):  # noqa: PYI046
        """Provides 3 attributes.

        - `_implementation`
        - `_backend_version`
        - `_version`
        """

    class _StoresColumns(Protocol):
        @property
        def columns(self) -> Sequence[str]: ...


NativeT_co = TypeVar("NativeT_co", covariant=True)
CompliantT_co = TypeVar("CompliantT_co", covariant=True)
CompliantExprT_co = TypeVar(
    "CompliantExprT_co", bound="CompliantExpr[Any, Any]", covariant=True
)
CompliantSeriesT_co = TypeVar(
    "CompliantSeriesT_co", bound="CompliantSeries", covariant=True
)


class _StoresNative(Protocol[NativeT_co]):
    """Provides access to a native object.

    Native objects have types like:

    >>> from pandas import Series
    >>> from pyarrow import Table
    """

    @property
    def native(self) -> NativeT_co:
        """Return the native object."""
        ...


class _StoresCompliant(Protocol[CompliantT_co]):
    """Provides access to a compliant object.

    Compliant objects have types like:

    >>> from narwhals._pandas_like.series import PandasLikeSeries
    >>> from narwhals._arrow.dataframe import ArrowDataFrame
    """

    @property
    def compliant(self) -> CompliantT_co:
        """Return the compliant object."""
        ...


class _SeriesNamespace(  # type: ignore[misc]  # noqa: PYI046
    _StoresCompliant[CompliantSeriesT_co],
    _StoresNative[NativeT_co],
    Protocol[CompliantSeriesT_co, NativeT_co],
):
    _compliant_series: CompliantSeriesT_co

    @property
    def compliant(self) -> CompliantSeriesT_co:
        return self._compliant_series

    @property
    def native(self) -> NativeT_co:
        return self._compliant_series.native

    def from_native(self, series: Any, /) -> CompliantSeriesT_co:
        return self.compliant._from_native_series(series)


class _ExprNamespace(  # type: ignore[misc] # noqa: PYI046
    _StoresCompliant[CompliantExprT_co], Protocol[CompliantExprT_co]
):
    _compliant_expr: CompliantExprT_co

    @property
    def compliant(self) -> CompliantExprT_co:
        return self._compliant_expr


class Version(Enum):
    V1 = auto()
    MAIN = auto()


class Implementation(Enum):
    """Implementation of native object (pandas, Polars, PyArrow, ...)."""

    PANDAS = auto()
    """Pandas implementation."""
    MODIN = auto()
    """Modin implementation."""
    CUDF = auto()
    """cuDF implementation."""
    PYARROW = auto()
    """PyArrow implementation."""
    PYSPARK = auto()
    """PySpark implementation."""
    POLARS = auto()
    """Polars implementation."""
    DASK = auto()
    """Dask implementation."""
    DUCKDB = auto()
    """DuckDB implementation."""
    IBIS = auto()
    """Ibis implementation."""
    SQLFRAME = auto()
    """SQLFrame implementation."""

    UNKNOWN = auto()
    """Unknown implementation."""

    @classmethod
    def from_native_namespace(
        cls: type[Self], native_namespace: ModuleType
    ) -> Implementation:  # pragma: no cover
        """Instantiate Implementation object from a native namespace module.

        Arguments:
            native_namespace: Native namespace.

        Returns:
            Implementation.
        """
        mapping = {
            get_pandas(): Implementation.PANDAS,
            get_modin(): Implementation.MODIN,
            get_cudf(): Implementation.CUDF,
            get_pyarrow(): Implementation.PYARROW,
            get_pyspark_sql(): Implementation.PYSPARK,
            get_polars(): Implementation.POLARS,
            get_dask_dataframe(): Implementation.DASK,
            get_duckdb(): Implementation.DUCKDB,
            get_ibis(): Implementation.IBIS,
            get_sqlframe(): Implementation.SQLFRAME,
        }
        return mapping.get(native_namespace, Implementation.UNKNOWN)

    @classmethod
    def from_string(
        cls: type[Self], backend_name: str
    ) -> Implementation:  # pragma: no cover
        """Instantiate Implementation object from a native namespace module.

        Arguments:
            backend_name: Name of backend, expressed as string.

        Returns:
            Implementation.
        """
        mapping = {
            "pandas": Implementation.PANDAS,
            "modin": Implementation.MODIN,
            "cudf": Implementation.CUDF,
            "pyarrow": Implementation.PYARROW,
            "pyspark": Implementation.PYSPARK,
            "polars": Implementation.POLARS,
            "dask": Implementation.DASK,
            "duckdb": Implementation.DUCKDB,
            "ibis": Implementation.IBIS,
            "sqlframe": Implementation.SQLFRAME,
        }
        return mapping.get(backend_name, Implementation.UNKNOWN)

    @classmethod
    def from_backend(
        cls: type[Self], backend: str | Implementation | ModuleType
    ) -> Implementation:
        """Instantiate from native namespace module, string, or Implementation.

        Arguments:
            backend: Backend to instantiate Implementation from.

        Returns:
            Implementation.
        """
        return (
            cls.from_string(backend)
            if isinstance(backend, str)
            else backend
            if isinstance(backend, Implementation)
            else cls.from_native_namespace(backend)
        )

    def to_native_namespace(self: Self) -> ModuleType:
        """Return the native namespace module corresponding to Implementation.

        Returns:
            Native module.
        """
        if self is Implementation.PANDAS:
            import pandas as pd  # ignore-banned-import

            return pd
        if self is Implementation.MODIN:
            import modin.pandas

            return modin.pandas
        if self is Implementation.CUDF:  # pragma: no cover
            import cudf  # ignore-banned-import

            return cudf
        if self is Implementation.PYARROW:
            import pyarrow as pa  # ignore-banned-import

            return pa
        if self is Implementation.PYSPARK:  # pragma: no cover
            import pyspark.sql

            return pyspark.sql
        if self is Implementation.POLARS:
            import polars as pl  # ignore-banned-import

            return pl
        if self is Implementation.DASK:
            import dask.dataframe  # ignore-banned-import

            return dask.dataframe

        if self is Implementation.DUCKDB:
            import duckdb  # ignore-banned-import

            return duckdb

        if self is Implementation.SQLFRAME:
            import sqlframe  # ignore-banned-import

            return sqlframe

        msg = "Not supported Implementation"  # pragma: no cover
        raise AssertionError(msg)

    def is_pandas(self: Self) -> bool:
        """Return whether implementation is pandas.

        Returns:
            Boolean.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_pandas()
            True
        """
        return self is Implementation.PANDAS

    def is_pandas_like(self: Self) -> bool:
        """Return whether implementation is pandas, Modin, or cuDF.

        Returns:
            Boolean.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_pandas_like()
            True
        """
        return self in {
            Implementation.PANDAS,
            Implementation.MODIN,
            Implementation.CUDF,
        }

    def is_spark_like(self: Self) -> bool:
        """Return whether implementation is pyspark or sqlframe.

        Returns:
            Boolean.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> df_native = pd.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_spark_like()
            False
        """
        return self in {Implementation.PYSPARK, Implementation.SQLFRAME}

    def is_polars(self: Self) -> bool:
        """Return whether implementation is Polars.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_polars()
            True
        """
        return self is Implementation.POLARS

    def is_cudf(self: Self) -> bool:
        """Return whether implementation is cuDF.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_cudf()
            False
        """
        return self is Implementation.CUDF  # pragma: no cover

    def is_modin(self: Self) -> bool:
        """Return whether implementation is Modin.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_modin()
            False
        """
        return self is Implementation.MODIN  # pragma: no cover

    def is_pyspark(self: Self) -> bool:
        """Return whether implementation is PySpark.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_pyspark()
            False
        """
        return self is Implementation.PYSPARK  # pragma: no cover

    def is_pyarrow(self: Self) -> bool:
        """Return whether implementation is PyArrow.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_pyarrow()
            False
        """
        return self is Implementation.PYARROW  # pragma: no cover

    def is_dask(self: Self) -> bool:
        """Return whether implementation is Dask.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_dask()
            False
        """
        return self is Implementation.DASK  # pragma: no cover

    def is_duckdb(self: Self) -> bool:
        """Return whether implementation is DuckDB.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_duckdb()
            False
        """
        return self is Implementation.DUCKDB  # pragma: no cover

    def is_ibis(self: Self) -> bool:
        """Return whether implementation is Ibis.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_ibis()
            False
        """
        return self is Implementation.IBIS  # pragma: no cover

    def is_sqlframe(self: Self) -> bool:
        """Return whether implementation is SQLFrame.

        Returns:
            Boolean.

        Examples:
            >>> import polars as pl
            >>> import narwhals as nw
            >>> df_native = pl.DataFrame({"a": [1, 2, 3]})
            >>> df = nw.from_native(df_native)
            >>> df.implementation.is_sqlframe()
            False
        """
        return self is Implementation.SQLFRAME  # pragma: no cover


MIN_VERSIONS: dict[Implementation, tuple[int, ...]] = {
    Implementation.PANDAS: (0, 25, 3),
    Implementation.MODIN: (0, 25, 3),
    Implementation.CUDF: (24, 10),
    Implementation.PYARROW: (11,),
    Implementation.PYSPARK: (3, 5),
    Implementation.POLARS: (0, 20, 3),
    Implementation.DASK: (2024, 8),
    Implementation.DUCKDB: (1,),
    Implementation.IBIS: (6,),
    Implementation.SQLFRAME: (3, 22, 0),
}


def validate_backend_version(
    implementation: Implementation, backend_version: tuple[int, ...]
) -> None:
    if backend_version < (min_version := MIN_VERSIONS[implementation]):
        msg = f"Minimum version of {implementation} supported by Narwhals is {min_version}, found: {backend_version}"
        raise ValueError(msg)


def import_dtypes_module(version: Version) -> DTypes:
    if version is Version.V1:
        from narwhals.stable.v1 import dtypes
    elif version is Version.MAIN:
        from narwhals import dtypes  # type: ignore[no-redef]
    else:  # pragma: no cover
        msg = (
            "Congratulations, you have entered unreachable code.\n"
            "Please report an issue at https://github.com/narwhals-dev/narwhals/issues.\n"
            f"Version: {version}"
        )
        raise AssertionError(msg)
    return dtypes  # type: ignore[return-value]


def remove_prefix(text: str, prefix: str) -> str:  # pragma: no cover
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


def remove_suffix(text: str, suffix: str) -> str:  # pragma: no cover
    if text.endswith(suffix):
        return text[: -len(suffix)]
    return text  # pragma: no cover


def flatten(args: Any) -> list[Any]:
    return list(args[0] if (len(args) == 1 and _is_iterable(args[0])) else args)


def tupleify(arg: Any) -> Any:
    if not isinstance(arg, (list, tuple)):  # pragma: no cover
        return (arg,)
    return arg


def _is_iterable(arg: Any | Iterable[Any]) -> bool:
    from narwhals.series import Series

    if is_pandas_dataframe(arg) or is_pandas_series(arg):
        msg = f"Expected Narwhals class or scalar, got: {type(arg)}. Perhaps you forgot a `nw.from_native` somewhere?"
        raise TypeError(msg)
    if (pl := get_polars()) is not None and isinstance(
        arg, (pl.Series, pl.Expr, pl.DataFrame, pl.LazyFrame)
    ):
        msg = (
            f"Expected Narwhals class or scalar, got: {type(arg)}.\n\n"
            "Hint: Perhaps you\n"
            "- forgot a `nw.from_native` somewhere?\n"
            "- used `pl.col` instead of `nw.col`?"
        )
        raise TypeError(msg)

    return isinstance(arg, Iterable) and not isinstance(arg, (str, bytes, Series))


def parse_version(version: str | ModuleType | _SupportsVersion) -> tuple[int, ...]:
    """Simple version parser; split into a tuple of ints for comparison.

    Arguments:
        version: Version string, or object with one, to parse.

    Returns:
        Parsed version number.
    """
    # lifted from Polars
    # [marco]: Take care of DuckDB pre-releases which end with e.g. `-dev4108`
    # and pandas pre-releases which end with e.g. .dev0+618.gb552dc95c9
    version_str = version if isinstance(version, str) else version.__version__
    version_str = re.sub(r"(\D?dev.*$)", "", version_str)
    return tuple(int(re.sub(r"\D", "", v)) for v in version_str.split("."))


@overload
def isinstance_or_issubclass(
    obj_or_cls: type, cls_or_tuple: type[_T]
) -> TypeIs[type[_T]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: object | type, cls_or_tuple: type[_T]
) -> TypeIs[_T | type[_T]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: type, cls_or_tuple: tuple[type[_T1], type[_T2]]
) -> TypeIs[type[_T1 | _T2]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: object | type, cls_or_tuple: tuple[type[_T1], type[_T2]]
) -> TypeIs[_T1 | _T2 | type[_T1 | _T2]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: type, cls_or_tuple: tuple[type[_T1], type[_T2], type[_T3]]
) -> TypeIs[type[_T1 | _T2 | _T3]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: object | type, cls_or_tuple: tuple[type[_T1], type[_T2], type[_T3]]
) -> TypeIs[_T1 | _T2 | _T3 | type[_T1 | _T2 | _T3]]: ...


@overload
def isinstance_or_issubclass(
    obj_or_cls: Any, cls_or_tuple: tuple[type, ...]
) -> TypeIs[Any]: ...


def isinstance_or_issubclass(obj_or_cls: Any, cls_or_tuple: Any) -> bool:
    from narwhals.dtypes import DType

    if isinstance(obj_or_cls, DType):
        return isinstance(obj_or_cls, cls_or_tuple)
    return isinstance(obj_or_cls, cls_or_tuple) or (
        isinstance(obj_or_cls, type) and issubclass(obj_or_cls, cls_or_tuple)
    )


def validate_laziness(items: Iterable[Any]) -> None:
    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame

    if all(isinstance(item, DataFrame) for item in items) or (
        all(isinstance(item, LazyFrame) for item in items)
    ):
        return
    msg = f"The items to concatenate should either all be eager, or all lazy, got: {[type(item) for item in items]}"
    raise TypeError(msg)


def maybe_align_index(
    lhs: FrameOrSeriesT, rhs: Series[Any] | DataFrame[Any] | LazyFrame[Any]
) -> FrameOrSeriesT:
    """Align `lhs` to the Index of `rhs`, if they're both pandas-like.

    Arguments:
        lhs: Dataframe or Series.
        rhs: Dataframe or Series to align with.

    Returns:
        Same type as input.

    Notes:
        This is only really intended for backwards-compatibility purposes,
        for example if your library already aligns indices for users.
        If you're designing a new library, we highly encourage you to not
        rely on the Index.
        For non-pandas-like inputs, this only checks that `lhs` and `rhs`
        are the same length.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>> df_pd = pd.DataFrame({"a": [1, 2]}, index=[3, 4])
        >>> s_pd = pd.Series([6, 7], index=[4, 3])
        >>> df = nw.from_native(df_pd)
        >>> s = nw.from_native(s_pd, series_only=True)
        >>> nw.to_native(nw.maybe_align_index(df, s))
           a
        4  2
        3  1
    """
    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.series import PandasLikeSeries

    def _validate_index(index: Any) -> None:
        if not index.is_unique:
            msg = "given index doesn't have a unique index"
            raise ValueError(msg)

    lhs_any = cast("Any", lhs)
    rhs_any = cast("Any", rhs)
    if isinstance(
        getattr(lhs_any, "_compliant_frame", None), PandasLikeDataFrame
    ) and isinstance(getattr(rhs_any, "_compliant_frame", None), PandasLikeDataFrame):
        _validate_index(lhs_any._compliant_frame._native_frame.index)
        _validate_index(rhs_any._compliant_frame._native_frame.index)
        return lhs_any._from_compliant_dataframe(
            lhs_any._compliant_frame._from_native_frame(
                lhs_any._compliant_frame._native_frame.loc[
                    rhs_any._compliant_frame._native_frame.index
                ]
            )
        )
    if isinstance(
        getattr(lhs_any, "_compliant_frame", None), PandasLikeDataFrame
    ) and isinstance(getattr(rhs_any, "_compliant_series", None), PandasLikeSeries):
        _validate_index(lhs_any._compliant_frame._native_frame.index)
        _validate_index(rhs_any._compliant_series._native_series.index)
        return lhs_any._from_compliant_dataframe(
            lhs_any._compliant_frame._from_native_frame(
                lhs_any._compliant_frame._native_frame.loc[
                    rhs_any._compliant_series._native_series.index
                ]
            )
        )
    if isinstance(
        getattr(lhs_any, "_compliant_series", None), PandasLikeSeries
    ) and isinstance(getattr(rhs_any, "_compliant_frame", None), PandasLikeDataFrame):
        _validate_index(lhs_any._compliant_series._native_series.index)
        _validate_index(rhs_any._compliant_frame._native_frame.index)
        return lhs_any._from_compliant_series(
            lhs_any._compliant_series._from_native_series(
                lhs_any._compliant_series._native_series.loc[
                    rhs_any._compliant_frame._native_frame.index
                ]
            )
        )
    if isinstance(
        getattr(lhs_any, "_compliant_series", None), PandasLikeSeries
    ) and isinstance(getattr(rhs_any, "_compliant_series", None), PandasLikeSeries):
        _validate_index(lhs_any._compliant_series._native_series.index)
        _validate_index(rhs_any._compliant_series._native_series.index)
        return lhs_any._from_compliant_series(
            lhs_any._compliant_series._from_native_series(
                lhs_any._compliant_series._native_series.loc[
                    rhs_any._compliant_series._native_series.index
                ]
            )
        )
    if len(lhs_any) != len(rhs_any):
        msg = f"Expected `lhs` and `rhs` to have the same length, got {len(lhs_any)} and {len(rhs_any)}"
        raise ValueError(msg)
    return lhs


def maybe_get_index(obj: DataFrame[Any] | LazyFrame[Any] | Series[Any]) -> Any | None:
    """Get the index of a DataFrame or a Series, if it's pandas-like.

    Arguments:
        obj: Dataframe or Series.

    Returns:
        Same type as input.

    Notes:
        This is only really intended for backwards-compatibility purposes,
        for example if your library already aligns indices for users.
        If you're designing a new library, we highly encourage you to not
        rely on the Index.
        For non-pandas-like inputs, this returns `None`.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>> df_pd = pd.DataFrame({"a": [1, 2], "b": [4, 5]})
        >>> df = nw.from_native(df_pd)
        >>> nw.maybe_get_index(df)
        RangeIndex(start=0, stop=2, step=1)
        >>> series_pd = pd.Series([1, 2])
        >>> series = nw.from_native(series_pd, series_only=True)
        >>> nw.maybe_get_index(series)
        RangeIndex(start=0, stop=2, step=1)
    """
    obj_any = cast("Any", obj)
    native_obj = obj_any.to_native()
    if is_pandas_like_dataframe(native_obj) or is_pandas_like_series(native_obj):
        return native_obj.index
    return None


def maybe_set_index(
    obj: FrameOrSeriesT,
    column_names: str | list[str] | None = None,
    *,
    index: Series[IntoSeriesT] | list[Series[IntoSeriesT]] | None = None,
) -> FrameOrSeriesT:
    """Set the index of a DataFrame or a Series, if it's pandas-like.

    Arguments:
        obj: object for which maybe set the index (can be either a Narwhals `DataFrame`
            or `Series`).
        column_names: name or list of names of the columns to set as index.
            For dataframes, only one of `column_names` and `index` can be specified but
            not both. If `column_names` is passed and `df` is a Series, then a
            `ValueError` is raised.
        index: series or list of series to set as index.

    Returns:
        Same type as input.

    Raises:
        ValueError: If one of the following condition happens:

            - none of `column_names` and `index` are provided
            - both `column_names` and `index` are provided
            - `column_names` is provided and `df` is a Series

    Notes:
        This is only really intended for backwards-compatibility purposes, for example if
        your library already aligns indices for users.
        If you're designing a new library, we highly encourage you to not
        rely on the Index.

        For non-pandas-like inputs, this is a no-op.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>> df_pd = pd.DataFrame({"a": [1, 2], "b": [4, 5]})
        >>> df = nw.from_native(df_pd)
        >>> nw.to_native(nw.maybe_set_index(df, "b"))  # doctest: +NORMALIZE_WHITESPACE
           a
        b
        4  1
        5  2
    """
    from narwhals.translate import to_native

    df_any = cast("Any", obj)
    native_obj = df_any.to_native()

    if column_names is not None and index is not None:
        msg = "Only one of `column_names` or `index` should be provided"
        raise ValueError(msg)

    if not column_names and index is None:
        msg = "Either `column_names` or `index` should be provided"
        raise ValueError(msg)

    if index is not None:
        keys = (
            [to_native(idx, pass_through=True) for idx in index]
            if _is_iterable(index)
            else to_native(index, pass_through=True)
        )
    else:
        keys = column_names

    if is_pandas_like_dataframe(native_obj):
        return df_any._from_compliant_dataframe(
            df_any._compliant_frame._from_native_frame(native_obj.set_index(keys))
        )
    elif is_pandas_like_series(native_obj):
        from narwhals._pandas_like.utils import set_index

        if column_names:
            msg = "Cannot set index using column names on a Series"
            raise ValueError(msg)

        native_obj = set_index(
            native_obj,
            keys,
            implementation=obj._compliant_series._implementation,  # type: ignore[union-attr]
            backend_version=obj._compliant_series._backend_version,  # type: ignore[union-attr]
        )
        return df_any._from_compliant_series(
            df_any._compliant_series._from_native_series(native_obj)
        )
    else:
        return df_any


def maybe_reset_index(obj: FrameOrSeriesT) -> FrameOrSeriesT:
    """Reset the index to the default integer index of a DataFrame or a Series, if it's pandas-like.

    Arguments:
        obj: Dataframe or Series.

    Returns:
        Same type as input.

    Notes:
        This is only really intended for backwards-compatibility purposes,
        for example if your library already resets the index for users.
        If you're designing a new library, we highly encourage you to not
        rely on the Index.
        For non-pandas-like inputs, this is a no-op.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>> df_pd = pd.DataFrame({"a": [1, 2], "b": [4, 5]}, index=([6, 7]))
        >>> df = nw.from_native(df_pd)
        >>> nw.to_native(nw.maybe_reset_index(df))
           a  b
        0  1  4
        1  2  5
        >>> series_pd = pd.Series([1, 2])
        >>> series = nw.from_native(series_pd, series_only=True)
        >>> nw.maybe_get_index(series)
        RangeIndex(start=0, stop=2, step=1)
    """
    obj_any = cast("Any", obj)
    native_obj = obj_any.to_native()
    if is_pandas_like_dataframe(native_obj):
        native_namespace = obj_any.__native_namespace__()
        if _has_default_index(native_obj, native_namespace):
            return obj_any
        return obj_any._from_compliant_dataframe(
            obj_any._compliant_frame._from_native_frame(native_obj.reset_index(drop=True))
        )
    if is_pandas_like_series(native_obj):
        native_namespace = obj_any.__native_namespace__()
        if _has_default_index(native_obj, native_namespace):
            return obj_any
        return obj_any._from_compliant_series(
            obj_any._compliant_series._from_native_series(
                native_obj.reset_index(drop=True)
            )
        )
    return obj_any


def _is_range_index(obj: Any, native_namespace: Any) -> TypeIs[pd.RangeIndex]:
    return isinstance(obj, native_namespace.RangeIndex)


# NOTE: Remove ignore(s) after release w/ (https://github.com/pandas-dev/pandas-stubs/pull/1115)
def _has_default_index(
    native_frame_or_series: pd.Series[Any] | pd.DataFrame, native_namespace: Any
) -> bool:
    index = native_frame_or_series.index
    return (
        _is_range_index(index, native_namespace)
        and index.start == 0
        and index.stop == len(index)
        and index.step == 1
    )


def maybe_convert_dtypes(
    obj: FrameOrSeriesT, *args: bool, **kwargs: bool | str
) -> FrameOrSeriesT:
    """Convert columns or series to the best possible dtypes using dtypes supporting ``pd.NA``, if df is pandas-like.

    Arguments:
        obj: DataFrame or Series.
        *args: Additional arguments which gets passed through.
        **kwargs: Additional arguments which gets passed through.

    Returns:
        Same type as input.

    Notes:
        For non-pandas-like inputs, this is a no-op.
        Also, `args` and `kwargs` just get passed down to the underlying library as-is.

    Examples:
        >>> import pandas as pd
        >>> import polars as pl
        >>> import narwhals as nw
        >>> import numpy as np
        >>> df_pd = pd.DataFrame(
        ...     {
        ...         "a": pd.Series([1, 2, 3], dtype=np.dtype("int32")),
        ...         "b": pd.Series([True, False, np.nan], dtype=np.dtype("O")),
        ...     }
        ... )
        >>> df = nw.from_native(df_pd)
        >>> nw.to_native(
        ...     nw.maybe_convert_dtypes(df)
        ... ).dtypes  # doctest: +NORMALIZE_WHITESPACE
        a             Int32
        b           boolean
        dtype: object
    """
    obj_any = cast("Any", obj)
    native_obj = obj_any.to_native()
    if is_pandas_like_dataframe(native_obj):
        return obj_any._from_compliant_dataframe(
            obj_any._compliant_frame._from_native_frame(
                native_obj.convert_dtypes(*args, **kwargs)
            )
        )
    if is_pandas_like_series(native_obj):
        return obj_any._from_compliant_series(
            obj_any._compliant_series._from_native_series(
                native_obj.convert_dtypes(*args, **kwargs)
            )
        )
    return obj_any


def scale_bytes(sz: int, unit: SizeUnit) -> int | float:
    """Scale size in bytes to other size units (eg: "kb", "mb", "gb", "tb").

    Arguments:
        sz: original size in bytes
        unit: size unit to convert into

    Returns:
        Integer or float.
    """
    if unit in {"b", "bytes"}:
        return sz
    elif unit in {"kb", "kilobytes"}:
        return sz / 1024
    elif unit in {"mb", "megabytes"}:
        return sz / 1024**2
    elif unit in {"gb", "gigabytes"}:
        return sz / 1024**3
    elif unit in {"tb", "terabytes"}:
        return sz / 1024**4
    else:
        msg = f"`unit` must be one of {{'b', 'kb', 'mb', 'gb', 'tb'}}, got {unit!r}"
        raise ValueError(msg)


def is_ordered_categorical(series: Series[Any]) -> bool:
    """Return whether indices of categories are semantically meaningful.

    This is a convenience function to accessing what would otherwise be
    the `is_ordered` property from the DataFrame Interchange Protocol,
    see https://data-apis.org/dataframe-protocol/latest/API.html.

    - For Polars:
      - Enums are always ordered.
      - Categoricals are ordered if `dtype.ordering == "physical"`.
    - For pandas-like APIs:
      - Categoricals are ordered if `dtype.cat.ordered == True`.
    - For PyArrow table:
      - Categoricals are ordered if `dtype.type.ordered == True`.

    Arguments:
        series: Input Series.

    Returns:
        Whether the Series is an ordered categorical.

    Examples:
        >>> import narwhals as nw
        >>> import pandas as pd
        >>> import polars as pl
        >>> data = ["x", "y"]
        >>> s_pd = pd.Series(data, dtype=pd.CategoricalDtype(ordered=True))
        >>> s_pl = pl.Series(data, dtype=pl.Categorical(ordering="physical"))

        Let's define a library-agnostic function:

        >>> @nw.narwhalify
        ... def func(s):
        ...     return nw.is_ordered_categorical(s)

        Then, we can pass any supported library to `func`:

        >>> func(s_pd)
        True
        >>> func(s_pl)
        True
    """
    from narwhals._interchange.series import InterchangeSeries

    dtypes = import_dtypes_module(series._compliant_series._version)

    if (
        isinstance(series._compliant_series, InterchangeSeries)
        and series.dtype == dtypes.Categorical
    ):
        return series._compliant_series._native_series.describe_categorical["is_ordered"]
    if series.dtype == dtypes.Enum:
        return True
    if series.dtype != dtypes.Categorical:
        return False
    native_series = series.to_native()
    if is_polars_series(native_series):
        return native_series.dtype.ordering == "physical"  # type: ignore[attr-defined]
    if is_pandas_series(native_series):
        return bool(native_series.cat.ordered)
    if is_modin_series(native_series):  # pragma: no cover
        return native_series.cat.ordered
    if is_cudf_series(native_series):  # pragma: no cover
        return native_series.cat.ordered
    if is_pyarrow_chunked_array(native_series):
        from narwhals._arrow.utils import is_dictionary

        return is_dictionary(native_series.type) and native_series.type.ordered
    # If it doesn't match any of the above, let's just play it safe and return False.
    return False  # pragma: no cover


def generate_unique_token(n_bytes: int, columns: list[str]) -> str:  # pragma: no cover
    msg = (
        "Use `generate_temporary_column_name` instead. `generate_unique_token` is "
        "deprecated and it will be removed in future versions"
    )
    issue_deprecation_warning(msg, _version="1.13.0")
    return generate_temporary_column_name(n_bytes=n_bytes, columns=columns)


def generate_temporary_column_name(n_bytes: int, columns: list[str]) -> str:
    """Generates a unique column name that is not present in the given list of columns.

    It relies on [python secrets token_hex](https://docs.python.org/3/library/secrets.html#secrets.token_hex)
    function to return a string nbytes random bytes.

    Arguments:
        n_bytes: The number of bytes to generate for the token.
        columns: The list of columns to check for uniqueness.

    Returns:
        A unique token that is not present in the given list of columns.

    Raises:
        AssertionError: If a unique token cannot be generated after 100 attempts.

    Examples:
        >>> import narwhals as nw
        >>> columns = ["abc", "xyz"]
        >>> nw.generate_temporary_column_name(n_bytes=8, columns=columns) not in columns
        True
    """
    counter = 0
    while True:
        token = token_hex(n_bytes)
        if token not in columns:
            return token

        counter += 1
        if counter > 100:
            msg = (
                "Internal Error: Narwhals was not able to generate a column name with "
                f"{n_bytes=} and not in {columns}"
            )
            raise AssertionError(msg)


def parse_columns_to_drop(
    compliant_frame: Any,
    columns: Iterable[str],
    strict: bool,  # noqa: FBT001
) -> list[str]:
    cols = compliant_frame.columns
    to_drop = list(columns)
    if strict:
        missing_columns = [x for x in to_drop if x not in cols]
        if missing_columns:
            raise ColumnNotFoundError.from_missing_and_available_column_names(
                missing_columns=missing_columns, available_columns=cols
            )
    else:
        to_drop = list(set(cols).intersection(set(to_drop)))
    return to_drop


def is_sequence_but_not_str(sequence: Any | Sequence[_T]) -> TypeIs[Sequence[_T]]:
    return isinstance(sequence, Sequence) and not isinstance(sequence, str)


def find_stacklevel() -> int:
    """Find the first place in the stack that is not inside narwhals.

    Returns:
        Stacklevel.

    Taken from:
    https://github.com/pandas-dev/pandas/blob/ab89c53f48df67709a533b6a95ce3d911871a0a8/pandas/util/_exceptions.py#L30-L51
    """
    import inspect
    from pathlib import Path

    import narwhals as nw

    pkg_dir = str(Path(nw.__file__).parent)

    # https://stackoverflow.com/questions/17407119/python-inspect-stack-is-slow
    frame = inspect.currentframe()
    n = 0
    try:
        while frame:
            fname = inspect.getfile(frame)
            if fname.startswith(pkg_dir) or (
                (qualname := getattr(frame.f_code, "co_qualname", None))
                # ignore @singledispatch wrappers
                and qualname.startswith("singledispatch.")
            ):
                frame = frame.f_back
                n += 1
            else:  # pragma: no cover
                break
        else:  # pragma: no cover
            pass
    finally:
        # https://docs.python.org/3/library/inspect.html
        # > Though the cycle detector will catch these, destruction of the frames
        # > (and local variables) can be made deterministic by removing the cycle
        # > in a finally clause.
        del frame
    return n


def issue_deprecation_warning(message: str, _version: str) -> None:
    """Issue a deprecation warning.

    Arguments:
        message: The message associated with the warning.
        _version: Narwhals version when the warning was introduced. Just used for internal
            bookkeeping.
    """
    warn(message=message, category=DeprecationWarning, stacklevel=find_stacklevel())


def validate_strict_and_pass_though(
    strict: bool | None,  # noqa: FBT001
    pass_through: bool | None,  # noqa: FBT001
    *,
    pass_through_default: bool,
    emit_deprecation_warning: bool,
) -> bool:
    if strict is None and pass_through is None:
        pass_through = pass_through_default
    elif strict is not None and pass_through is None:
        if emit_deprecation_warning:
            msg = (
                "`strict` in `from_native` is deprecated, please use `pass_through` instead.\n\n"
                "Note: `strict` will remain available in `narwhals.stable.v1`.\n"
                "See https://narwhals-dev.github.io/narwhals/backcompat/ for more information.\n"
            )
            issue_deprecation_warning(msg, _version="1.13.0")
        pass_through = not strict
    elif strict is None and pass_through is not None:
        pass
    else:
        msg = "Cannot pass both `strict` and `pass_through`"
        raise ValueError(msg)
    return pass_through


def validate_native_namespace_and_backend(
    backend: ModuleType | Implementation | str | None = None,
    native_namespace: ModuleType | None = None,
    *,
    emit_deprecation_warning: bool,
) -> ModuleType | Implementation | str | None:
    if native_namespace is not None and backend is None:  # pragma: no cover
        if emit_deprecation_warning:
            msg = (
                "`native_namespace` is deprecated, please use `backend` instead.\n\n"
                "Note: `native_namespace` will remain available in `narwhals.stable.v1`.\n"
                "See https://narwhals-dev.github.io/narwhals/backcompat/ for more information.\n"
            )
            issue_deprecation_warning(msg, _version="1.25.1")
        backend = native_namespace
    elif native_namespace is not None and backend is not None:
        msg = "Can't pass both `native_namespace` and `backend`"
        raise ValueError(msg)
    return backend


def _validate_rolling_arguments(
    window_size: int, min_samples: int | None
) -> tuple[int, int]:
    if window_size < 1:
        msg = "window_size must be greater or equal than 1"
        raise ValueError(msg)

    if not isinstance(window_size, int):
        _type = window_size.__class__.__name__
        msg = (
            f"argument 'window_size': '{_type}' object cannot be "
            "interpreted as an integer"
        )
        raise TypeError(msg)

    if min_samples is not None:
        if min_samples < 1:
            msg = "min_samples must be greater or equal than 1"
            raise ValueError(msg)

        if not isinstance(min_samples, int):
            _type = min_samples.__class__.__name__
            msg = (
                f"argument 'min_samples': '{_type}' object cannot be "
                "interpreted as an integer"
            )
            raise TypeError(msg)
        if min_samples > window_size:
            msg = "`min_samples` must be less or equal than `window_size`"
            raise InvalidOperationError(msg)
    else:
        min_samples = window_size

    return window_size, min_samples


def generate_repr(header: str, native_repr: str) -> str:
    try:
        terminal_width = os.get_terminal_size().columns
    except OSError:
        terminal_width = int(os.getenv("COLUMNS", 80))  # noqa: PLW1508
    native_lines = native_repr.splitlines()
    max_native_width = max(len(line) for line in native_lines)

    if max_native_width + 2 <= terminal_width:
        length = max(max_native_width, len(header))
        output = f"┌{'─' * length}┐\n"
        header_extra = length - len(header)
        output += f"|{' ' * (header_extra // 2)}{header}{' ' * (header_extra // 2 + header_extra % 2)}|\n"
        output += f"|{'-' * (length)}|\n"
        start_extra = (length - max_native_width) // 2
        end_extra = (length - max_native_width) // 2 + (length - max_native_width) % 2
        for line in native_lines:
            output += f"|{' ' * (start_extra)}{line}{' ' * (end_extra + max_native_width - len(line))}|\n"
        output += f"└{'─' * length}┘"
        return output

    diff = 39 - len(header)
    return (
        f"┌{'─' * (39)}┐\n"
        f"|{' ' * (diff // 2)}{header}{' ' * (diff // 2 + diff % 2)}|\n"
        "| Use `.to_native` to see native output |\n└"
        f"{'─' * 39}┘"
    )


def check_column_exists(columns: list[str], subset: list[str] | None) -> None:
    if subset is not None and (missing := set(subset).difference(columns)):
        msg = f"Column(s) {sorted(missing)} not found in {columns}"
        raise ColumnNotFoundError(msg)


def check_column_names_are_unique(columns: list[str]) -> None:
    len_unique_columns = len(set(columns))
    if len(columns) != len_unique_columns:
        from collections import Counter

        counter = Counter(columns)
        duplicates = {k: v for k, v in counter.items() if v > 1}
        msg = "".join(f"\n- '{k}' {v} times" for k, v in duplicates.items())
        msg = f"Expected unique column names, got:{msg}"
        raise DuplicateError(msg)


def _parse_time_unit_and_time_zone(
    time_unit: TimeUnit | Iterable[TimeUnit] | None,
    time_zone: str | timezone | Iterable[str | timezone | None] | None,
) -> tuple[Set[TimeUnit], Set[str | None]]:
    time_units: Set[TimeUnit] = (
        {"ms", "us", "ns", "s"}
        if time_unit is None
        else {time_unit}
        if isinstance(time_unit, str)
        else set(time_unit)
    )
    time_zones: Set[str | None] = (
        {None}
        if time_zone is None
        else {str(time_zone)}
        if isinstance(time_zone, (str, timezone))
        else {str(tz) if tz is not None else None for tz in time_zone}
    )
    return time_units, time_zones


def dtype_matches_time_unit_and_time_zone(
    dtype: DType, dtypes: DTypes, time_units: Set[TimeUnit], time_zones: Set[str | None]
) -> bool:
    return (
        isinstance(dtype, dtypes.Datetime)
        and (dtype.time_unit in time_units)
        and (
            dtype.time_zone in time_zones
            or ("*" in time_zones and dtype.time_zone is not None)
        )
    )


def get_column_names(frame: _StoresColumns, /) -> Sequence[str]:
    return frame.columns


def exclude_column_names(frame: _StoresColumns, names: Container[str]) -> Sequence[str]:
    return [col_name for col_name in frame.columns if col_name not in names]


def passthrough_column_names(names: Sequence[str], /) -> Callable[[Any], Sequence[str]]:
    def fn(_frame: Any, /) -> Sequence[str]:
        return names

    return fn


def _hasattr_static(obj: Any, attr: str) -> bool:
    sentinel = object()
    return getattr_static(obj, attr, sentinel) is not sentinel


def is_compliant_dataframe(
    obj: CompliantDataFrame[CompliantSeriesT_co] | Any,
) -> TypeIs[CompliantDataFrame[CompliantSeriesT_co]]:
    return _hasattr_static(obj, "__narwhals_dataframe__")


def is_compliant_lazyframe(obj: Any) -> TypeIs[CompliantLazyFrame]:
    return _hasattr_static(obj, "__narwhals_lazyframe__")


def is_compliant_series(obj: Any) -> TypeIs[CompliantSeries]:
    return _hasattr_static(obj, "__narwhals_series__")


def is_compliant_expr(
    obj: CompliantExpr[CompliantFrameT, CompliantSeriesT_co] | Any,
) -> TypeIs[CompliantExpr[CompliantFrameT, CompliantSeriesT_co]]:
    return hasattr(obj, "__narwhals_expr__")


def has_native_namespace(obj: Any) -> TypeIs[SupportsNativeNamespace]:
    return hasattr(obj, "__native_namespace__")


def _supports_dataframe_interchange(obj: Any) -> TypeIs[DataFrameLike]:
    return hasattr(obj, "__dataframe__")


def is_tracks_depth(obj: Implementation, /) -> TypeIs[_TracksDepth]:  # pragma: no cover
    # Return `True` for implementations that utilize `CompliantExpr._depth`.
    return obj.is_pandas_like() or obj in {Implementation.PYARROW, Implementation.DASK}


# TODO @dangotbanned: Extend with runtime behavior for `v1.*`
# See `narwhals.exceptions.NarwhalsUnstableWarning`
def unstable(fn: _Fn, /) -> _Fn:
    """Visual-only marker for unstable functionality.

    Arguments:
        fn: Function to decorate.

    Returns:
        Decorated function (unchanged).

    Examples:
        >>> from narwhals.utils import unstable
        >>> @unstable
        ... def a_work_in_progress_feature(*args):
        ...     return args
        >>>
        >>> a_work_in_progress_feature.__name__
        'a_work_in_progress_feature'
        >>> a_work_in_progress_feature(1, 2, 3)
        (1, 2, 3)
    """
    return fn


class not_implemented:  # noqa: N801
    """Mark some functionality as unsupported.

    Arguments:
        alias: optional name used instead of the data model hook [`__set_name__`].

    Returns:
        An exception-raising [descriptor].

    Notes:
        - Attribute/method name *doesn't* need to be declared twice
        - Allows different behavior when looked up on the class vs instance
        - Allows us to use `isinstance(...)` instead of monkeypatching an attribute to the function

    Examples:
        >>> from narwhals.utils import not_implemented
        >>> class Thing:
        ...     def totally_ready(self) -> str:
        ...         return "I'm ready!"
        ...
        ...     not_ready_yet = not_implemented()
        >>>
        >>> thing = Thing()
        >>> thing.totally_ready()
        "I'm ready!"
        >>> thing.not_ready_yet()
        Traceback (most recent call last):
            ...
        NotImplementedError: 'not_ready_yet' is not implemented for: 'Thing'.
        ...
        >>> isinstance(Thing.not_ready_yet, not_implemented)
        True

    [`__set_name__`]: https://docs.python.org/3/reference/datamodel.html#object.__set_name__
    [descriptor]: https://docs.python.org/3/howto/descriptor.html
    """

    def __init__(self, alias: str | None = None, /) -> None:
        # NOTE: Don't like this
        # Trying to workaround `mypy` requiring `@property` everywhere
        self._alias: str | None = alias

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>: {self._name_owner}.{self._name}"

    def __set_name__(self, owner: type[_T], name: str) -> None:
        # https://docs.python.org/3/howto/descriptor.html#customized-names
        self._name_owner: str = owner.__name__
        self._name: str = self._alias or name

    def __get__(
        self, instance: _T | Literal["raise"] | None, owner: type[_T] | None = None, /
    ) -> Any:
        if instance is None:
            # NOTE: Branch for `cls._name`
            # We can check that to see if an instance of `type(self)` for
            # https://narwhals-dev.github.io/narwhals/api-completeness/expr/
            return self
        # NOTE: Prefer not exposing the actual class we're defining in
        # `_implementation` may not be available everywhere
        who = getattr(instance, "_implementation", self._name_owner)
        raise _not_implemented_error(self._name, who)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        # NOTE: Purely to duck-type as assignable to **any** instance method
        # Wouldn't be reachable through *regular* attribute access
        return self.__get__("raise")


def _not_implemented_error(what: str, who: str, /) -> NotImplementedError:
    msg = (
        f"{what!r} is not implemented for: {who!r}.\n\n"
        "If you would like to see this functionality in `narwhals`, "
        "please open an issue at: https://github.com/narwhals-dev/narwhals/issues"
    )
    return NotImplementedError(msg)


if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 13):
        # NOTE: avoids `mypy`
        #     error: Module "narwhals.utils" does not explicitly export attribute "deprecated"  [attr-defined]
        from warnings import deprecated as deprecated  # noqa: PLC0414
    else:
        from typing_extensions import deprecated as deprecated  # noqa: PLC0414
else:

    def deprecated(message: str, /) -> Callable[[_Fn], _Fn]:  # noqa: ARG001
        def wrapper(func: _Fn, /) -> _Fn:
            return func

        return wrapper
