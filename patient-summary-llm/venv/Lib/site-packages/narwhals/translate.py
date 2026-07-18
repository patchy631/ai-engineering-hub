from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from decimal import Decimal
from functools import wraps
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Literal
from typing import TypeVar
from typing import overload

from narwhals.dependencies import get_cudf
from narwhals.dependencies import get_cupy
from narwhals.dependencies import get_dask
from narwhals.dependencies import get_dask_expr
from narwhals.dependencies import get_modin
from narwhals.dependencies import get_numpy
from narwhals.dependencies import get_pandas
from narwhals.dependencies import get_polars
from narwhals.dependencies import get_pyarrow
from narwhals.dependencies import get_pyspark
from narwhals.dependencies import is_cudf_dataframe
from narwhals.dependencies import is_cudf_series
from narwhals.dependencies import is_dask_dataframe
from narwhals.dependencies import is_duckdb_relation
from narwhals.dependencies import is_ibis_table
from narwhals.dependencies import is_modin_dataframe
from narwhals.dependencies import is_modin_series
from narwhals.dependencies import is_pandas_dataframe
from narwhals.dependencies import is_pandas_series
from narwhals.dependencies import is_polars_dataframe
from narwhals.dependencies import is_polars_lazyframe
from narwhals.dependencies import is_polars_series
from narwhals.dependencies import is_pyarrow_chunked_array
from narwhals.dependencies import is_pyarrow_table
from narwhals.dependencies import is_pyspark_dataframe
from narwhals.dependencies import is_sqlframe_dataframe
from narwhals.utils import Version

if TYPE_CHECKING:
    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame
    from narwhals.series import Series
    from narwhals.typing import IntoDataFrameT
    from narwhals.typing import IntoFrame
    from narwhals.typing import IntoFrameT
    from narwhals.typing import IntoSeries
    from narwhals.typing import IntoSeriesT

T = TypeVar("T")

NON_TEMPORAL_SCALAR_TYPES = (
    bool,
    bytes,
    str,
    int,
    float,
    complex,
    Decimal,
)


@overload
def to_native(
    narwhals_object: DataFrame[IntoDataFrameT], *, pass_through: Literal[False] = ...
) -> IntoDataFrameT: ...
@overload
def to_native(
    narwhals_object: LazyFrame[IntoFrameT], *, pass_through: Literal[False] = ...
) -> IntoFrameT: ...
@overload
def to_native(
    narwhals_object: Series[IntoSeriesT], *, pass_through: Literal[False] = ...
) -> IntoSeriesT: ...
@overload
def to_native(narwhals_object: Any, *, pass_through: bool) -> Any: ...


def to_native(
    narwhals_object: DataFrame[IntoDataFrameT]
    | LazyFrame[IntoFrameT]
    | Series[IntoSeriesT],
    *,
    strict: bool | None = None,
    pass_through: bool | None = None,
) -> IntoDataFrameT | IntoFrameT | IntoSeriesT | Any:
    """Convert Narwhals object to native one.

    Arguments:
        narwhals_object: Narwhals object.
        strict: Determine what happens if `narwhals_object` isn't a Narwhals class:

            - `True` (default): raise an error
            - `False`: pass object through as-is

            **Deprecated** (v1.13.0):
                Please use `pass_through` instead. Note that `strict` is still available
                (and won't emit a deprecation warning) if you use `narwhals.stable.v1`,
                see [perfect backwards compatibility policy](../backcompat.md/).
        pass_through: Determine what happens if `narwhals_object` isn't a Narwhals class:

            - `False` (default): raise an error
            - `True`: pass object through as-is

    Returns:
        Object of class that user started with.
    """
    from narwhals.dataframe import BaseFrame
    from narwhals.series import Series
    from narwhals.utils import validate_strict_and_pass_though

    pass_through = validate_strict_and_pass_though(
        strict, pass_through, pass_through_default=False, emit_deprecation_warning=True
    )

    if isinstance(narwhals_object, BaseFrame):
        return narwhals_object._compliant_frame._native_frame
    if isinstance(narwhals_object, Series):
        return narwhals_object._compliant_series._native_series

    if not pass_through:
        msg = f"Expected Narwhals object, got {type(narwhals_object)}."
        raise TypeError(msg)
    return narwhals_object


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeries,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoFrameT | IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoFrame | IntoSeries,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[Any] | LazyFrame[Any] | Series[Any]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT]: ...


# All params passed in as variables
@overload
def from_native(
    native_object: Any,
    *,
    pass_through: bool,
    eager_only: bool,
    series_only: bool,
    allow_series: bool | None,
) -> Any: ...


def from_native(
    native_object: IntoFrameT | IntoSeriesT | IntoFrame | IntoSeries | T,
    *,
    strict: bool | None = None,
    pass_through: bool | None = None,
    eager_only: bool = False,
    series_only: bool = False,
    allow_series: bool | None = None,
) -> LazyFrame[IntoFrameT] | DataFrame[IntoFrameT] | Series[IntoSeriesT] | T:
    """Convert `native_object` to Narwhals Dataframe, Lazyframe, or Series.

    Arguments:
        native_object: Raw object from user.
            Depending on the other arguments, input object can be:

            - a Dataframe / Lazyframe / Series supported by Narwhals (pandas, Polars, PyArrow, ...)
            - an object which implements `__narwhals_dataframe__`, `__narwhals_lazyframe__`,
              or `__narwhals_series__`
        strict: Determine what happens if the object can't be converted to Narwhals:

            - `True` or `None` (default): raise an error
            - `False`: pass object through as-is

            **Deprecated** (v1.13.0):
                Please use `pass_through` instead. Note that `strict` is still available
                (and won't emit a deprecation warning) if you use `narwhals.stable.v1`,
                see [perfect backwards compatibility policy](../backcompat.md/).
        pass_through: Determine what happens if the object can't be converted to Narwhals:

            - `False` or `None` (default): raise an error
            - `True`: pass object through as-is
        eager_only: Whether to only allow eager objects:

            - `False` (default): don't require `native_object` to be eager
            - `True`: only convert to Narwhals if `native_object` is eager
        series_only: Whether to only allow Series:

            - `False` (default): don't require `native_object` to be a Series
            - `True`: only convert to Narwhals if `native_object` is a Series
        allow_series: Whether to allow Series (default is only Dataframe / Lazyframe):

            - `False` or `None` (default): don't convert to Narwhals if `native_object` is a Series
            - `True`: allow `native_object` to be a Series

    Returns:
        DataFrame, LazyFrame, Series, or original object, depending
            on which combination of parameters was passed.
    """
    from narwhals.utils import validate_strict_and_pass_though

    pass_through = validate_strict_and_pass_though(
        strict, pass_through, pass_through_default=False, emit_deprecation_warning=True
    )

    return _from_native_impl(  # type: ignore[no-any-return]
        native_object,
        pass_through=pass_through,
        eager_only=eager_only,
        eager_or_interchange_only=False,
        series_only=series_only,
        allow_series=allow_series,
        version=Version.MAIN,
    )


def _from_native_impl(  # noqa: PLR0915
    native_object: Any,
    *,
    pass_through: bool = False,
    eager_only: bool = False,
    # Interchange-level was removed after v1
    eager_or_interchange_only: bool = False,
    series_only: bool = False,
    allow_series: bool | None = None,
    version: Version,
) -> Any:
    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame
    from narwhals.series import Series
    from narwhals.utils import Implementation
    from narwhals.utils import _supports_dataframe_interchange
    from narwhals.utils import is_compliant_dataframe
    from narwhals.utils import is_compliant_lazyframe
    from narwhals.utils import is_compliant_series
    from narwhals.utils import parse_version

    # Early returns
    if isinstance(native_object, (DataFrame, LazyFrame)) and not series_only:
        return native_object
    if isinstance(native_object, Series) and (series_only or allow_series):
        return native_object

    if series_only:
        if allow_series is False:
            msg = "Invalid parameter combination: `series_only=True` and `allow_series=False`"
            raise ValueError(msg)
        allow_series = True
    if eager_only and eager_or_interchange_only:
        msg = "Invalid parameter combination: `eager_only=True` and `eager_or_interchange_only=True`"
        raise ValueError(msg)

    # Extensions
    if is_compliant_dataframe(native_object):
        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with dataframe"
                raise TypeError(msg)
            return native_object
        return DataFrame(
            native_object.__narwhals_dataframe__(),
            level="full",
        )
    elif is_compliant_lazyframe(native_object):
        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with lazyframe"
                raise TypeError(msg)
            return native_object
        if eager_only or eager_or_interchange_only:
            if not pass_through:
                msg = "Cannot only use `eager_only` or `eager_or_interchange_only` with lazyframe"
                raise TypeError(msg)
            return native_object
        return LazyFrame(
            native_object.__narwhals_lazyframe__(),
            level="full",
        )
    elif is_compliant_series(native_object):
        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        return Series(
            native_object.__narwhals_series__(),
            level="full",
        )

    # Polars
    elif is_polars_dataframe(native_object):
        from narwhals._polars.dataframe import PolarsDataFrame

        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with polars.DataFrame"
                raise TypeError(msg)
            return native_object
        pl = get_polars()
        return DataFrame(
            PolarsDataFrame(
                native_object, backend_version=parse_version(pl), version=version
            ),
            level="full",
        )
    elif is_polars_lazyframe(native_object):
        from narwhals._polars.dataframe import PolarsLazyFrame

        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with polars.LazyFrame"
                raise TypeError(msg)
            return native_object
        if eager_only or eager_or_interchange_only:
            if not pass_through:
                msg = "Cannot only use `eager_only` or `eager_or_interchange_only` with polars.LazyFrame"
                raise TypeError(msg)
            return native_object
        pl = get_polars()
        return LazyFrame(
            PolarsLazyFrame(
                native_object, backend_version=parse_version(pl), version=version
            ),
            level="lazy",
        )
    elif is_polars_series(native_object):
        from narwhals._polars.series import PolarsSeries

        pl = get_polars()
        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        return Series(
            PolarsSeries(
                native_object, backend_version=parse_version(pl), version=version
            ),
            level="full",
        )

    # pandas
    elif is_pandas_dataframe(native_object):
        from narwhals._pandas_like.dataframe import PandasLikeDataFrame

        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with dataframe"
                raise TypeError(msg)
            return native_object
        pd = get_pandas()
        return DataFrame(
            PandasLikeDataFrame(
                native_object,
                backend_version=parse_version(pd),
                implementation=Implementation.PANDAS,
                version=version,
                validate_column_names=True,
            ),
            level="full",
        )
    elif is_pandas_series(native_object):
        from narwhals._pandas_like.series import PandasLikeSeries

        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        pd = get_pandas()
        return Series(
            PandasLikeSeries(
                native_object,
                implementation=Implementation.PANDAS,
                backend_version=parse_version(pd),
                version=version,
            ),
            level="full",
        )

    # Modin
    elif is_modin_dataframe(native_object):  # pragma: no cover
        from narwhals._pandas_like.dataframe import PandasLikeDataFrame

        mpd = get_modin()
        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with modin.DataFrame"
                raise TypeError(msg)
            return native_object
        return DataFrame(
            PandasLikeDataFrame(
                native_object,
                implementation=Implementation.MODIN,
                backend_version=parse_version(mpd),
                version=version,
                validate_column_names=True,
            ),
            level="full",
        )
    elif is_modin_series(native_object):  # pragma: no cover
        from narwhals._pandas_like.series import PandasLikeSeries

        mpd = get_modin()
        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        return Series(
            PandasLikeSeries(
                native_object,
                implementation=Implementation.MODIN,
                backend_version=parse_version(mpd),
                version=version,
            ),
            level="full",
        )

    # cuDF
    elif is_cudf_dataframe(native_object):  # pragma: no cover
        from narwhals._pandas_like.dataframe import PandasLikeDataFrame

        cudf = get_cudf()
        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with cudf.DataFrame"
                raise TypeError(msg)
            return native_object
        return DataFrame(
            PandasLikeDataFrame(
                native_object,
                implementation=Implementation.CUDF,
                backend_version=parse_version(cudf),
                version=version,
                validate_column_names=True,
            ),
            level="full",
        )
    elif is_cudf_series(native_object):  # pragma: no cover
        from narwhals._pandas_like.series import PandasLikeSeries

        cudf = get_cudf()
        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        return Series(
            PandasLikeSeries(
                native_object,
                implementation=Implementation.CUDF,
                backend_version=parse_version(cudf),
                version=version,
            ),
            level="full",
        )

    # PyArrow
    elif is_pyarrow_table(native_object):
        from narwhals._arrow.dataframe import ArrowDataFrame

        pa = get_pyarrow()
        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with arrow table"
                raise TypeError(msg)
            return native_object
        return DataFrame(
            ArrowDataFrame(
                native_object,
                backend_version=parse_version(pa),
                version=version,
                validate_column_names=True,
            ),
            level="full",
        )
    elif is_pyarrow_chunked_array(native_object):
        from narwhals._arrow.series import ArrowSeries

        pa = get_pyarrow()
        if not allow_series:
            if not pass_through:
                msg = "Please set `allow_series=True` or `series_only=True`"
                raise TypeError(msg)
            return native_object
        return Series(
            ArrowSeries(
                native_object, backend_version=parse_version(pa), name="", version=version
            ),
            level="full",
        )

    # Dask
    elif is_dask_dataframe(native_object):
        from narwhals._dask.dataframe import DaskLazyFrame

        if series_only:
            if not pass_through:
                msg = "Cannot only use `series_only` with dask DataFrame"
                raise TypeError(msg)
            return native_object
        if eager_only or eager_or_interchange_only:
            if not pass_through:
                msg = "Cannot only use `eager_only` or `eager_or_interchange_only` with dask DataFrame"
                raise TypeError(msg)
            return native_object
        if (
            parse_version(get_dask()) <= (2024, 12, 1) and get_dask_expr() is None
        ):  # pragma: no cover
            msg = "Please install dask-expr"
            raise ImportError(msg)
        return LazyFrame(
            DaskLazyFrame(
                native_object,
                backend_version=parse_version(get_dask()),
                version=version,
                validate_column_names=True,
            ),
            level="lazy",
        )

    # DuckDB
    elif is_duckdb_relation(native_object):
        from narwhals._duckdb.dataframe import DuckDBLazyFrame

        if eager_only or series_only:  # pragma: no cover
            if not pass_through:
                msg = (
                    "Cannot only use `series_only=True` or `eager_only=False` "
                    "with DuckDBPyRelation"
                )
            else:
                return native_object
            raise TypeError(msg)
        import duckdb  # ignore-banned-import

        backend_version = parse_version(duckdb)
        if version is Version.V1:
            return DataFrame(
                DuckDBLazyFrame(
                    native_object,
                    backend_version=backend_version,
                    version=version,
                    validate_column_names=True,
                ),
                level="interchange",
            )
        return LazyFrame(
            DuckDBLazyFrame(
                native_object,
                backend_version=backend_version,
                version=version,
                validate_column_names=True,
            ),
            level="lazy",
        )

    # Ibis
    elif is_ibis_table(native_object):  # pragma: no cover
        from narwhals._ibis.dataframe import IbisLazyFrame

        if eager_only or series_only:
            if not pass_through:
                msg = (
                    "Cannot only use `series_only=True` or `eager_only=False` "
                    "with Ibis table"
                )
                raise TypeError(msg)
            return native_object
        import ibis  # ignore-banned-import

        backend_version = parse_version(ibis)
        if version is Version.V1:
            return DataFrame(
                IbisLazyFrame(
                    native_object, backend_version=backend_version, version=version
                ),
                level="interchange",
            )
        return LazyFrame(
            IbisLazyFrame(
                native_object, backend_version=backend_version, version=version
            ),
            level="lazy",
        )

    # PySpark
    elif is_pyspark_dataframe(native_object):  # pragma: no cover
        from narwhals._spark_like.dataframe import SparkLikeLazyFrame

        if series_only:
            msg = "Cannot only use `series_only` with pyspark DataFrame"
            raise TypeError(msg)
        if eager_only or eager_or_interchange_only:
            msg = "Cannot only use `eager_only` or `eager_or_interchange_only` with pyspark DataFrame"
            raise TypeError(msg)
        return LazyFrame(
            SparkLikeLazyFrame(
                native_object,
                backend_version=parse_version(get_pyspark()),
                version=version,
                implementation=Implementation.PYSPARK,
                validate_column_names=True,
            ),
            level="lazy",
        )

    elif is_sqlframe_dataframe(native_object):  # pragma: no cover
        from narwhals._spark_like.dataframe import SparkLikeLazyFrame

        if series_only:
            msg = "Cannot only use `series_only` with SQLFrame DataFrame"
            raise TypeError(msg)
        if eager_only or eager_or_interchange_only:
            msg = "Cannot only use `eager_only` or `eager_or_interchange_only` with SQLFrame DataFrame"
            raise TypeError(msg)
        import sqlframe._version

        backend_version = parse_version(sqlframe._version)
        return LazyFrame(
            SparkLikeLazyFrame(
                native_object,
                backend_version=backend_version,
                version=version,
                implementation=Implementation.SQLFRAME,
                validate_column_names=True,
            ),
            level="lazy",
        )

    # Interchange protocol
    elif _supports_dataframe_interchange(native_object):
        from narwhals._interchange.dataframe import InterchangeFrame

        if eager_only or series_only:
            if not pass_through:
                msg = (
                    "Cannot only use `series_only=True` or `eager_only=False` "
                    "with object which only implements __dataframe__"
                )
                raise TypeError(msg)
            return native_object
        return DataFrame(
            InterchangeFrame(native_object, version=version),
            level="interchange",
        )

    elif not pass_through:
        msg = f"Expected pandas-like dataframe, Polars dataframe, or Polars lazyframe, got: {type(native_object)}"
        raise TypeError(msg)
    return native_object


def get_native_namespace(
    *obj: DataFrame[Any] | LazyFrame[Any] | Series[Any] | IntoFrame | IntoSeries,
) -> Any:
    """Get native namespace from object.

    Arguments:
        obj: Dataframe, Lazyframe, or Series. Multiple objects can be
            passed positionally, in which case they must all have the
            same native namespace (else an error is raised).

    Returns:
        Native module.

    Examples:
        >>> import polars as pl
        >>> import pandas as pd
        >>> import narwhals as nw
        >>> df = nw.from_native(pd.DataFrame({"a": [1, 2, 3]}))
        >>> nw.get_native_namespace(df)
        <module 'pandas'...>
        >>> df = nw.from_native(pl.DataFrame({"a": [1, 2, 3]}))
        >>> nw.get_native_namespace(df)
        <module 'polars'...>
    """
    if not obj:
        msg = "At least one object must be passed to `get_native_namespace`."
        raise ValueError(msg)
    result = {_get_native_namespace_single_obj(x) for x in obj}
    if len(result) != 1:
        msg = f"Found objects with different native namespaces: {result}."
        raise ValueError(msg)
    return result.pop()


def _get_native_namespace_single_obj(
    obj: DataFrame[Any] | LazyFrame[Any] | Series[Any] | IntoFrame | IntoSeries,
) -> Any:
    from narwhals.utils import has_native_namespace

    if has_native_namespace(obj):
        return obj.__native_namespace__()
    if is_pandas_dataframe(obj) or is_pandas_series(obj):
        return get_pandas()
    if is_modin_dataframe(obj) or is_modin_series(obj):  # pragma: no cover
        return get_modin()
    if is_pyarrow_table(obj) or is_pyarrow_chunked_array(obj):
        return get_pyarrow()
    if is_cudf_dataframe(obj) or is_cudf_series(obj):  # pragma: no cover
        return get_cudf()
    if is_dask_dataframe(obj):  # pragma: no cover
        return get_dask()
    if is_polars_dataframe(obj) or is_polars_lazyframe(obj) or is_polars_series(obj):
        return get_polars()
    msg = f"Could not get native namespace from object of type: {type(obj)}"
    raise TypeError(msg)


def narwhalify(
    func: Callable[..., Any] | None = None,
    *,
    strict: bool | None = None,
    pass_through: bool | None = None,
    eager_only: bool = False,
    series_only: bool = False,
    allow_series: bool | None = True,
) -> Callable[..., Any]:
    """Decorate function so it becomes dataframe-agnostic.

    This will try to convert any dataframe/series-like object into the Narwhals
    respective DataFrame/Series, while leaving the other parameters as they are.
    Similarly, if the output of the function is a Narwhals DataFrame or Series, it will be
    converted back to the original dataframe/series type, while if the output is another
    type it will be left as is.
    By setting `pass_through=False`, then every input and every output will be required to be a
    dataframe/series-like object.

    Arguments:
        func: Function to wrap in a `from_native`-`to_native` block.
        strict: **Deprecated** (v1.13.0):
            Please use `pass_through` instead. Note that `strict` is still available
            (and won't emit a deprecation warning) if you use `narwhals.stable.v1`,
            see [perfect backwards compatibility policy](../backcompat.md/).

            Determine what happens if the object can't be converted to Narwhals:

            - `True` or `None` (default): raise an error
            - `False`: pass object through as-is
        pass_through: Determine what happens if the object can't be converted to Narwhals:

            - `False` or `None` (default): raise an error
            - `True`: pass object through as-is
        eager_only: Whether to only allow eager objects:

            - `False` (default): don't require `native_object` to be eager
            - `True`: only convert to Narwhals if `native_object` is eager
        series_only: Whether to only allow Series:

            - `False` (default): don't require `native_object` to be a Series
            - `True`: only convert to Narwhals if `native_object` is a Series
        allow_series: Whether to allow Series (default is only Dataframe / Lazyframe):

            - `False` or `None`: don't convert to Narwhals if `native_object` is a Series
            - `True` (default): allow `native_object` to be a Series

    Returns:
        Decorated function.

    Examples:
        Instead of writing

        >>> import narwhals as nw
        >>> def agnostic_group_by_sum(df):
        ...     df = nw.from_native(df, pass_through=True)
        ...     df = df.group_by("a").agg(nw.col("b").sum())
        ...     return nw.to_native(df)

        you can just write

        >>> @nw.narwhalify
        ... def agnostic_group_by_sum(df):
        ...     return df.group_by("a").agg(nw.col("b").sum())
    """
    from narwhals.utils import validate_strict_and_pass_though

    pass_through = validate_strict_and_pass_though(
        strict, pass_through, pass_through_default=True, emit_deprecation_warning=True
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            args = [
                from_native(
                    arg,
                    pass_through=pass_through,
                    eager_only=eager_only,
                    series_only=series_only,
                    allow_series=allow_series,
                )
                for arg in args
            ]  # type: ignore[assignment]

            kwargs = {
                name: from_native(
                    value,
                    pass_through=pass_through,
                    eager_only=eager_only,
                    series_only=series_only,
                    allow_series=allow_series,
                )
                for name, value in kwargs.items()
            }

            backends = {
                b()
                for v in (*args, *kwargs.values())
                if (b := getattr(v, "__native_namespace__", None))
            }

            if len(backends) > 1:
                msg = "Found multiple backends. Make sure that all dataframe/series inputs come from the same backend."
                raise ValueError(msg)

            result = func(*args, **kwargs)

            return to_native(result, pass_through=pass_through)

        return wrapper

    if func is None:
        return decorator
    else:
        # If func is not None, it means the decorator is used without arguments
        return decorator(func)


def to_py_scalar(scalar_like: Any) -> Any:
    """If a scalar is not Python native, converts it to Python native.

    Arguments:
        scalar_like: Scalar-like value.

    Returns:
        Python scalar.

    Raises:
        ValueError: If the object is not convertible to a scalar.

    Examples:
        >>> import narwhals as nw
        >>> import pandas as pd
        >>> df = nw.from_native(pd.DataFrame({"a": [1, 2, 3]}))
        >>> nw.to_py_scalar(df["a"].item(0))
        1
        >>> import pyarrow as pa
        >>> df = nw.from_native(pa.table({"a": [1, 2, 3]}))
        >>> nw.to_py_scalar(df["a"].item(0))
        1
        >>> nw.to_py_scalar(1)
        1
    """
    if scalar_like is None:
        return None
    if isinstance(scalar_like, NON_TEMPORAL_SCALAR_TYPES):
        return scalar_like

    np = get_numpy()
    if (
        np
        and isinstance(scalar_like, np.datetime64)
        and scalar_like.dtype == "datetime64[ns]"
    ):
        return datetime(1970, 1, 1) + timedelta(microseconds=scalar_like.item() // 1000)

    if np and np.isscalar(scalar_like) and hasattr(scalar_like, "item"):
        return scalar_like.item()

    pd = get_pandas()
    if pd and isinstance(scalar_like, pd.Timestamp):
        return scalar_like.to_pydatetime()
    if pd and isinstance(scalar_like, pd.Timedelta):
        return scalar_like.to_pytimedelta()
    if pd and pd.api.types.is_scalar(scalar_like):
        try:
            is_na = pd.isna(scalar_like)
        except Exception:  # pragma: no cover  # noqa: BLE001, S110
            pass
        else:
            if is_na:
                return None

    # pd.Timestamp and pd.Timedelta subclass datetime and timedelta,
    # so we need to check this separately
    if isinstance(scalar_like, (datetime, timedelta)):
        return scalar_like

    pa = get_pyarrow()
    if pa and isinstance(scalar_like, pa.Scalar):
        return scalar_like.as_py()

    cupy = get_cupy()
    if (  # pragma: no cover
        cupy and isinstance(scalar_like, cupy.ndarray) and scalar_like.size == 1
    ):
        return scalar_like.item()

    msg = (
        f"Expected object convertible to a scalar, found {type(scalar_like)}. "
        "Please report a bug to https://github.com/narwhals-dev/narwhals/issues"
    )
    raise ValueError(msg)


__all__ = [
    "get_native_namespace",
    "narwhalify",
    "to_native",
    "to_py_scalar",
]
