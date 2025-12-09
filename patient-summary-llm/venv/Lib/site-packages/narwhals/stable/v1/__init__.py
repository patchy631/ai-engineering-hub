from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Iterable
from typing import Literal
from typing import Sequence
from typing import overload
from warnings import warn

import narwhals as nw
from narwhals import dependencies
from narwhals import exceptions
from narwhals import selectors
from narwhals._expression_parsing import ExprKind
from narwhals.dataframe import DataFrame as NwDataFrame
from narwhals.dataframe import LazyFrame as NwLazyFrame
from narwhals.dependencies import get_polars
from narwhals.exceptions import InvalidIntoExprError
from narwhals.expr import Expr as NwExpr
from narwhals.functions import Then as NwThen
from narwhals.functions import When as NwWhen
from narwhals.functions import _from_dict_impl
from narwhals.functions import _from_numpy_impl
from narwhals.functions import _new_series_impl
from narwhals.functions import _read_csv_impl
from narwhals.functions import _read_parquet_impl
from narwhals.functions import _scan_csv_impl
from narwhals.functions import _scan_parquet_impl
from narwhals.functions import from_arrow as nw_from_arrow
from narwhals.functions import get_level
from narwhals.functions import show_versions
from narwhals.functions import when as nw_when
from narwhals.schema import Schema as NwSchema
from narwhals.series import Series as NwSeries
from narwhals.stable.v1 import dtypes
from narwhals.stable.v1.dtypes import Array
from narwhals.stable.v1.dtypes import Boolean
from narwhals.stable.v1.dtypes import Categorical
from narwhals.stable.v1.dtypes import Date
from narwhals.stable.v1.dtypes import Datetime
from narwhals.stable.v1.dtypes import Decimal
from narwhals.stable.v1.dtypes import Duration
from narwhals.stable.v1.dtypes import Enum
from narwhals.stable.v1.dtypes import Field
from narwhals.stable.v1.dtypes import Float32
from narwhals.stable.v1.dtypes import Float64
from narwhals.stable.v1.dtypes import Int8
from narwhals.stable.v1.dtypes import Int16
from narwhals.stable.v1.dtypes import Int32
from narwhals.stable.v1.dtypes import Int64
from narwhals.stable.v1.dtypes import Int128
from narwhals.stable.v1.dtypes import List
from narwhals.stable.v1.dtypes import Object
from narwhals.stable.v1.dtypes import String
from narwhals.stable.v1.dtypes import Struct
from narwhals.stable.v1.dtypes import UInt8
from narwhals.stable.v1.dtypes import UInt16
from narwhals.stable.v1.dtypes import UInt32
from narwhals.stable.v1.dtypes import UInt64
from narwhals.stable.v1.dtypes import UInt128
from narwhals.stable.v1.dtypes import Unknown
from narwhals.translate import _from_native_impl
from narwhals.translate import get_native_namespace
from narwhals.translate import to_py_scalar
from narwhals.typing import IntoDataFrameT
from narwhals.typing import IntoFrameT
from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import find_stacklevel
from narwhals.utils import generate_temporary_column_name
from narwhals.utils import is_ordered_categorical
from narwhals.utils import maybe_align_index
from narwhals.utils import maybe_convert_dtypes
from narwhals.utils import maybe_get_index
from narwhals.utils import maybe_reset_index
from narwhals.utils import maybe_set_index
from narwhals.utils import validate_native_namespace_and_backend
from narwhals.utils import validate_strict_and_pass_though

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Mapping

    from typing_extensions import Self
    from typing_extensions import TypeVar

    from narwhals.dtypes import DType
    from narwhals.functions import ArrowStreamExportable
    from narwhals.typing import IntoExpr
    from narwhals.typing import IntoFrame
    from narwhals.typing import IntoSeries
    from narwhals.typing import _1DArray
    from narwhals.typing import _2DArray

    IntoSeriesT = TypeVar("IntoSeriesT", bound="IntoSeries", default=Any)
    T = TypeVar("T", default=Any)
else:
    from typing import TypeVar

    IntoSeriesT = TypeVar("IntoSeriesT", bound="IntoSeries")
    T = TypeVar("T")


class DataFrame(NwDataFrame[IntoDataFrameT]):
    """Narwhals DataFrame, backed by a native eager dataframe.

    !!! warning
        This class is not meant to be instantiated directly - instead:

        - If the native object is a eager dataframe from one of the supported
            backend (e.g. pandas.DataFrame, polars.DataFrame, pyarrow.Table),
            you can use [`narwhals.from_native`][]:
            ```py
            narwhals.from_native(native_dataframe)
            narwhals.from_native(native_dataframe, eager_only=True)
            ```

        - If the object is a dictionary of column names and generic sequences mapping
            (e.g. `dict[str, list]`), you can create a DataFrame via
            [`narwhals.from_dict`][]:
            ```py
            narwhals.from_dict(
                data={"a": [1, 2, 3]},
                native_namespace=narwhals.get_native_namespace(another_object),
            )
            ```
    """

    # We need to override any method which don't return Self so that type
    # annotations are correct.

    @property
    def _series(self: Self) -> type[Series[Any]]:
        return Series

    @property
    def _lazyframe(self: Self) -> type[LazyFrame[Any]]:
        return LazyFrame

    @overload
    def __getitem__(  # type: ignore[overload-overlap]
        self: Self,
        item: str | tuple[slice | Sequence[int] | _1DArray, int | str],
    ) -> Series[Any]: ...
    @overload
    def __getitem__(
        self: Self,
        item: (
            int
            | slice
            | _1DArray
            | Sequence[int]
            | Sequence[str]
            | tuple[
                slice | Sequence[int] | _1DArray, slice | Sequence[int] | Sequence[str]
            ]
        ),
    ) -> Self: ...

    def __getitem__(self: Self, item: Any) -> Any:
        return super().__getitem__(item)

    def lazy(
        self: Self,
        backend: ModuleType | Implementation | str | None = None,
    ) -> LazyFrame[Any]:
        """Restrict available API methods to lazy-only ones.

        If `backend` is specified, then a conversion between different backends
        might be triggered.

        If a library does not support lazy execution and `backend` is not specified,
        then this is will only restrict the API to lazy-only operations. This is useful
        if you want to ensure that you write dataframe-agnostic code which all has
        the possibility of running entirely lazily.

        Arguments:
            backend: Which lazy backend collect to. This will be the underlying
                backend for the resulting Narwhals LazyFrame. If not specified, and the
                given library does not support lazy execution, then this will restrict
                the API to lazy-only operations.

                `backend` can be specified in various ways:

                - As `Implementation.<BACKEND>` with `BACKEND` being `DASK`, `DUCKDB`
                    or `POLARS`.
                - As a string: `"dask"`, `"duckdb"` or `"polars"`
                - Directly as a module `dask.dataframe`, `duckdb` or `polars`.

        Returns:
            A new LazyFrame.
        """
        return super().lazy(backend=backend)  # type: ignore[return-value]

    # Not sure what mypy is complaining about, probably some fancy
    # thing that I need to understand category theory for
    @overload  # type: ignore[override]
    def to_dict(
        self: Self, *, as_series: Literal[True] = ...
    ) -> dict[str, Series[Any]]: ...
    @overload
    def to_dict(self: Self, *, as_series: Literal[False]) -> dict[str, list[Any]]: ...
    @overload
    def to_dict(
        self: Self, *, as_series: bool
    ) -> dict[str, Series[Any]] | dict[str, list[Any]]: ...
    def to_dict(
        self: Self, *, as_series: bool = True
    ) -> dict[str, Series[Any]] | dict[str, list[Any]]:
        """Convert DataFrame to a dictionary mapping column name to values.

        Arguments:
            as_series: If set to true ``True``, then the values are Narwhals Series,
                    otherwise the values are Any.

        Returns:
            A mapping from column name to values / Series.
        """
        return super().to_dict(as_series=as_series)  # type: ignore[return-value]

    def is_duplicated(self: Self) -> Series[Any]:
        r"""Get a mask of all duplicated rows in this DataFrame.

        Returns:
            A new Series.
        """
        return super().is_duplicated()  # type: ignore[return-value]

    def is_unique(self: Self) -> Series[Any]:
        r"""Get a mask of all unique rows in this DataFrame.

        Returns:
            A new Series.
        """
        return super().is_unique()  # type: ignore[return-value]

    def _l1_norm(self: Self) -> Self:
        """Private, just used to test the stable API.

        Returns:
            A new DataFrame.
        """
        return self.select(all()._l1_norm())


class LazyFrame(NwLazyFrame[IntoFrameT]):
    """Narwhals LazyFrame, backed by a native lazyframe.

    !!! warning
        This class is not meant to be instantiated directly - instead use
        [`narwhals.from_native`][] with a native
        object that is a lazy dataframe from one of the supported
        backend (e.g. polars.LazyFrame, dask_expr._collection.DataFrame):
        ```py
        narwhals.from_native(native_lazyframe)
        ```
    """

    @property
    def _dataframe(self: Self) -> type[DataFrame[Any]]:
        return DataFrame

    def _extract_compliant(self: Self, arg: Any) -> Any:
        # After v1, we raise when passing order-dependent or length-changing
        # expressions to LazyFrame
        from narwhals.dataframe import BaseFrame
        from narwhals.expr import Expr
        from narwhals.series import Series

        if isinstance(arg, BaseFrame):
            return arg._compliant_frame
        if isinstance(arg, Series):  # pragma: no cover
            msg = "Mixing Series with LazyFrame is not supported."
            raise TypeError(msg)
        if isinstance(arg, Expr):
            # After stable.v1, we raise for order-dependent exprs or filtrations
            return arg._to_compliant_expr(self.__narwhals_namespace__())
        if isinstance(arg, str):
            plx = self.__narwhals_namespace__()
            return plx.col(arg)
        if get_polars() is not None and "polars" in str(type(arg)):  # pragma: no cover
            msg = (
                f"Expected Narwhals object, got: {type(arg)}.\n\n"
                "Perhaps you:\n"
                "- Forgot a `nw.from_native` somewhere?\n"
                "- Used `pl.col` instead of `nw.col`?"
            )
            raise TypeError(msg)
        raise InvalidIntoExprError.from_invalid_type(type(arg))

    def collect(
        self: Self,
        backend: ModuleType | Implementation | str | None = None,
        **kwargs: Any,
    ) -> DataFrame[Any]:
        r"""Materialize this LazyFrame into a DataFrame.

        As each underlying lazyframe has different arguments to set when materializing
        the lazyframe into a dataframe, we allow to pass them as kwargs (see examples
        below for how to generalize the specification).

        Arguments:
            backend: specifies which eager backend collect to. This will be the underlying
                backend for the resulting Narwhals DataFrame. If None, then the following
                default conversions will be applied:

                - `polars.LazyFrame` -> `polars.DataFrame`
                - `dask.DataFrame` -> `pandas.DataFrame`
                - `duckdb.PyRelation` -> `pyarrow.Table`
                - `pyspark.DataFrame` -> `pyarrow.Table`

                `backend` can be specified in various ways:

                - As `Implementation.<BACKEND>` with `BACKEND` being `PANDAS`, `PYARROW`
                    or `POLARS`.
                - As a string: `"pandas"`, `"pyarrow"` or `"polars"`
                - Directly as a module `pandas`, `pyarrow` or `polars`.
            kwargs: backend specific kwargs to pass along. To know more please check the
                backend specific documentation:

                - [polars.LazyFrame.collect](https://docs.pola.rs/api/python/dev/reference/lazyframe/api/polars.LazyFrame.collect.html)
                - [dask.dataframe.DataFrame.compute](https://docs.dask.org/en/stable/generated/dask.dataframe.DataFrame.compute.html)

        Returns:
            DataFrame
        """
        return super().collect(backend=backend, **kwargs)  # type: ignore[return-value]

    def _l1_norm(self: Self) -> Self:
        """Private, just used to test the stable API.

        Returns:
            A new lazyframe.
        """
        return self.select(all()._l1_norm())

    def tail(self, n: int = 5) -> Self:  # pragma: no cover
        r"""Get the last `n` rows.

        Arguments:
            n: Number of rows to return.

        Returns:
            A subset of the LazyFrame of shape (n, n_columns).
        """
        return super().tail(n)

    def gather_every(self: Self, n: int, offset: int = 0) -> Self:
        r"""Take every nth row in the DataFrame and return as a new DataFrame.

        Arguments:
            n: Gather every *n*-th row.
            offset: Starting index.

        Returns:
            The LazyFrame containing only the selected rows.
        """
        return self._from_compliant_dataframe(
            self._compliant_frame.gather_every(n=n, offset=offset)
        )


class Series(NwSeries[IntoSeriesT]):
    """Narwhals Series, backed by a native series.

    !!! warning
        This class is not meant to be instantiated directly - instead:

        - If the native object is a series from one of the supported backend (e.g.
            pandas.Series, polars.Series, pyarrow.ChunkedArray), you can use
            [`narwhals.from_native`][]:
            ```py
            narwhals.from_native(native_series, allow_series=True)
            narwhals.from_native(native_series, series_only=True)
            ```

        - If the object is a generic sequence (e.g. a list or a tuple of values), you can
            create a series via [`narwhals.new_series`][]:
            ```py
            narwhals.new_series(
                name=name,
                values=values,
                native_namespace=narwhals.get_native_namespace(another_object),
            )
            ```
    """

    # We need to override any method which don't return Self so that type
    # annotations are correct.

    @property
    def _dataframe(self: Self) -> type[DataFrame[Any]]:
        return DataFrame

    def to_frame(self: Self) -> DataFrame[Any]:
        """Convert to dataframe.

        Returns:
            A DataFrame containing this Series as a single column.
        """
        return super().to_frame()  # type: ignore[return-value]

    def value_counts(
        self: Self,
        *,
        sort: bool = False,
        parallel: bool = False,
        name: str | None = None,
        normalize: bool = False,
    ) -> DataFrame[Any]:
        r"""Count the occurrences of unique values.

        Arguments:
            sort: Sort the output by count in descending order. If set to False (default),
                the order of the output is random.
            parallel: Execute the computation in parallel. Used for Polars only.
            name: Give the resulting count column a specific name; if `normalize` is True
                defaults to "proportion", otherwise defaults to "count".
            normalize: If true gives relative frequencies of the unique values

        Returns:
            A DataFrame with two columns:
            - The original values as first column
            - Either count or proportion as second column, depending on normalize parameter.
        """
        return super().value_counts(  # type: ignore[return-value]
            sort=sort, parallel=parallel, name=name, normalize=normalize
        )

    def ewm_mean(
        self: Self,
        *,
        com: float | None = None,
        span: float | None = None,
        half_life: float | None = None,
        alpha: float | None = None,
        adjust: bool = True,
        min_samples: int = 1,
        ignore_nulls: bool = False,
    ) -> Self:
        r"""Compute exponentially-weighted moving average.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        Arguments:
            com: Specify decay in terms of center of mass, $\gamma$, with <br> $\alpha = \frac{1}{1+\gamma}\forall\gamma\geq0$
            span: Specify decay in terms of span, $\theta$, with <br> $\alpha = \frac{2}{\theta + 1} \forall \theta \geq 1$
            half_life: Specify decay in terms of half-life, $\tau$, with <br> $\alpha = 1 - \exp \left\{ \frac{ -\ln(2) }{ \tau } \right\} \forall \tau > 0$
            alpha: Specify smoothing factor alpha directly, $0 < \alpha \leq 1$.
            adjust: Divide by decaying adjustment factor in beginning periods to account for imbalance in relative weightings

                - When `adjust=True` (the default) the EW function is calculated
                  using weights $w_i = (1 - \alpha)^i$
                - When `adjust=False` the EW function is calculated recursively by
                  $$
                  y_0=x_0
                  $$
                  $$
                  y_t = (1 - \alpha)y_{t - 1} + \alpha x_t
                  $$
            min_samples: Minimum number of observations in window required to have a value (otherwise result is null).
            ignore_nulls: Ignore missing values when calculating weights.

                - When `ignore_nulls=False` (default), weights are based on absolute
                  positions.
                  For example, the weights of $x_0$ and $x_2$ used in
                  calculating the final weighted average of $[x_0, None, x_2]$ are
                  $(1-\alpha)^2$ and $1$ if `adjust=True`, and
                  $(1-\alpha)^2$ and $\alpha$ if `adjust=False`.
                - When `ignore_nulls=True`, weights are based
                  on relative positions. For example, the weights of
                  $x_0$ and $x_2$ used in calculating the final weighted
                  average of $[x_0, None, x_2]$ are
                  $1-\alpha$ and $1$ if `adjust=True`,
                  and $1-\alpha$ and $\alpha$ if `adjust=False`.

        Returns:
            Series
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.ewm_mean` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().ewm_mean(
            com=com,
            span=span,
            half_life=half_life,
            alpha=alpha,
            adjust=adjust,
            min_samples=min_samples,
            ignore_nulls=ignore_nulls,
        )

    def rolling_sum(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
    ) -> Self:
        """Apply a rolling sum (moving sum) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their sum.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`
            center: Set the labels at the center of the window.

        Returns:
            A new series.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.rolling_sum` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_sum(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
        )

    def rolling_mean(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
    ) -> Self:
        """Apply a rolling mean (moving mean) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their mean.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`
            center: Set the labels at the center of the window.

        Returns:
            A new series.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.rolling_mean` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_mean(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
        )

    def rolling_var(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
        ddof: int = 1,
    ) -> Self:
        """Apply a rolling variance (moving variance) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their variance.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`.
            center: Set the labels at the center of the window.
            ddof: Delta Degrees of Freedom; the divisor for a length N window is N - ddof.

        Returns:
            A new series.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.rolling_var` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_var(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
            ddof=ddof,
        )

    def rolling_std(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
        ddof: int = 1,
    ) -> Self:
        """Apply a rolling standard deviation (moving standard deviation) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their standard deviation.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`.
            center: Set the labels at the center of the window.
            ddof: Delta Degrees of Freedom; the divisor for a length N window is N - ddof.

        Returns:
            A new series.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.rolling_std` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_std(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
            ddof=ddof,
        )

    def hist(
        self: Self,
        bins: list[float | int] | None = None,
        *,
        bin_count: int | None = None,
        include_breakpoint: bool = True,
    ) -> DataFrame[Any]:
        """Bin values into buckets and count their occurrences.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        Arguments:
            bins: A monotonically increasing sequence of values.
            bin_count: If no bins provided, this will be used to determine the distance of the bins.
            include_breakpoint: Include a column that shows the intervals as categories.

        Returns:
            A new DataFrame containing the counts of values that occur within each passed bin.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Series.hist` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().hist(  # type: ignore[return-value]
            bins=bins,
            bin_count=bin_count,
            include_breakpoint=include_breakpoint,
        )


class Expr(NwExpr):
    def _l1_norm(self: Self) -> Self:
        return super()._taxicab_norm()

    def ewm_mean(
        self: Self,
        *,
        com: float | None = None,
        span: float | None = None,
        half_life: float | None = None,
        alpha: float | None = None,
        adjust: bool = True,
        min_samples: int = 1,
        ignore_nulls: bool = False,
    ) -> Self:
        r"""Compute exponentially-weighted moving average.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        Arguments:
            com: Specify decay in terms of center of mass, $\gamma$, with <br> $\alpha = \frac{1}{1+\gamma}\forall\gamma\geq0$
            span: Specify decay in terms of span, $\theta$, with <br> $\alpha = \frac{2}{\theta + 1} \forall \theta \geq 1$
            half_life: Specify decay in terms of half-life, $\tau$, with <br> $\alpha = 1 - \exp \left\{ \frac{ -\ln(2) }{ \tau } \right\} \forall \tau > 0$
            alpha: Specify smoothing factor alpha directly, $0 < \alpha \leq 1$.
            adjust: Divide by decaying adjustment factor in beginning periods to account for imbalance in relative weightings

                - When `adjust=True` (the default) the EW function is calculated
                  using weights $w_i = (1 - \alpha)^i$
                - When `adjust=False` the EW function is calculated recursively by
                  $$
                  y_0=x_0
                  $$
                  $$
                  y_t = (1 - \alpha)y_{t - 1} + \alpha x_t
                  $$
            min_samples: Minimum number of observations in window required to have a value, (otherwise result is null).
            ignore_nulls: Ignore missing values when calculating weights.

                - When `ignore_nulls=False` (default), weights are based on absolute
                  positions.
                  For example, the weights of $x_0$ and $x_2$ used in
                  calculating the final weighted average of $[x_0, None, x_2]$ are
                  $(1-\alpha)^2$ and $1$ if `adjust=True`, and
                  $(1-\alpha)^2$ and $\alpha$ if `adjust=False`.
                - When `ignore_nulls=True`, weights are based
                  on relative positions. For example, the weights of
                  $x_0$ and $x_2$ used in calculating the final weighted
                  average of $[x_0, None, x_2]$ are
                  $1-\alpha$ and $1$ if `adjust=True`,
                  and $1-\alpha$ and $\alpha$ if `adjust=False`.

        Returns:
            Expr
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Expr.ewm_mean` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().ewm_mean(
            com=com,
            span=span,
            half_life=half_life,
            alpha=alpha,
            adjust=adjust,
            min_samples=min_samples,
            ignore_nulls=ignore_nulls,
        )

    def rolling_sum(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
    ) -> Self:
        """Apply a rolling sum (moving sum) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their sum.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`
            center: Set the labels at the center of the window.

        Returns:
            A new expression.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Expr.rolling_sum` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_sum(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
        )

    def rolling_mean(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
    ) -> Self:
        """Apply a rolling mean (moving mean) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their mean.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`
            center: Set the labels at the center of the window.

        Returns:
            A new expression.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Expr.rolling_mean` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_mean(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
        )

    def rolling_var(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
        ddof: int = 1,
    ) -> Self:
        """Apply a rolling variance (moving variance) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their variance.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`.
            center: Set the labels at the center of the window.
            ddof: Delta Degrees of Freedom; the divisor for a length N window is N - ddof.

        Returns:
            A new expression.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Expr.rolling_var` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_var(
            window_size=window_size, min_samples=min_samples, center=center, ddof=ddof
        )

    def rolling_std(
        self: Self,
        window_size: int,
        *,
        min_samples: int | None = None,
        center: bool = False,
        ddof: int = 1,
    ) -> Self:
        """Apply a rolling standard deviation (moving standard deviation) over the values.

        !!! warning
            This functionality is considered **unstable**. It may be changed at any point
            without it being considered a breaking change.

        A window of length `window_size` will traverse the values. The resulting values
        will be aggregated to their standard deviation.

        The window at a given row will include the row itself and the `window_size - 1`
        elements before it.

        Arguments:
            window_size: The length of the window in number of elements. It must be a
                strictly positive integer.
            min_samples: The number of values in the window that should be non-null before
                computing a result. If set to `None` (default), it will be set equal to
                `window_size`. If provided, it must be a strictly positive integer, and
                less than or equal to `window_size`
            center: Set the labels at the center of the window.
            ddof: Delta Degrees of Freedom; the divisor for a length N window is N - ddof.

        Returns:
            A new expression.
        """
        from narwhals.exceptions import NarwhalsUnstableWarning
        from narwhals.utils import find_stacklevel

        msg = (
            "`Expr.rolling_std` is being called from the stable API although considered "
            "an unstable feature."
        )
        warn(message=msg, category=NarwhalsUnstableWarning, stacklevel=find_stacklevel())
        return super().rolling_std(
            window_size=window_size,
            min_samples=min_samples,
            center=center,
            ddof=ddof,
        )

    def head(self: Self, n: int = 10) -> Self:
        r"""Get the first `n` rows.

        Arguments:
            n: Number of rows to return.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).head(n),
            self._metadata.with_kind_and_extra_open_window(ExprKind.FILTRATION),
        )

    def tail(self: Self, n: int = 10) -> Self:
        r"""Get the last `n` rows.

        Arguments:
            n: Number of rows to return.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).tail(n),
            self._metadata.with_kind_and_extra_open_window(ExprKind.FILTRATION),
        )

    def gather_every(self: Self, n: int, offset: int = 0) -> Self:
        r"""Take every nth value in the Series and return as new Series.

        Arguments:
            n: Gather every *n*-th row.
            offset: Starting index.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).gather_every(n=n, offset=offset),
            self._metadata.with_kind_and_extra_open_window(ExprKind.FILTRATION),
        )

    def unique(self: Self, *, maintain_order: bool | None = None) -> Self:
        """Return unique values of this expression.

        Arguments:
            maintain_order: Keep the same order as the original expression.
                This is deprecated and will be removed in a future version,
                but will still be kept around in `narwhals.stable.v1`.

        Returns:
            A new expression.
        """
        if maintain_order is not None:
            msg = (
                "`maintain_order` has no effect and is only kept around for backwards-compatibility. "
                "You can safely remove this argument."
            )
            warn(message=msg, category=UserWarning, stacklevel=find_stacklevel())
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).unique(),
            self._metadata.with_kind(ExprKind.FILTRATION),
        )

    def sort(self: Self, *, descending: bool = False, nulls_last: bool = False) -> Self:
        """Sort this column. Place null values first.

        Arguments:
            descending: Sort in descending order.
            nulls_last: Place null values last instead of first.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).sort(
                descending=descending, nulls_last=nulls_last
            ),
            self._metadata.with_extra_open_window(),
        )

    def arg_true(self: Self) -> Self:
        """Find elements where boolean expression is True.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).arg_true(),
            self._metadata.with_kind_and_extra_open_window(ExprKind.FILTRATION),
        )

    def sample(
        self: Self,
        n: int | None = None,
        *,
        fraction: float | None = None,
        with_replacement: bool = False,
        seed: int | None = None,
    ) -> Self:
        """Sample randomly from this expression.

        !!! warning
            `Expr.sample` is deprecated and will be removed in a future version.
            Hint: instead of `df.select(nw.col('a').sample())`, use
            `df.select(nw.col('a')).sample()` instead.
            Note: this will remain available in `narwhals.stable.v1`.
            See [stable api](../backcompat.md/) for more information.

        Arguments:
            n: Number of items to return. Cannot be used with fraction.
            fraction: Fraction of items to return. Cannot be used with n.
            with_replacement: Allow values to be sampled more than once.
            seed: Seed for the random number generator. If set to None (default), a random
                seed is generated for each sample operation.

        Returns:
            A new expression.
        """
        return self.__class__(
            lambda plx: self._to_compliant_expr(plx).sample(
                n, fraction=fraction, with_replacement=with_replacement, seed=seed
            ),
            self._metadata.with_kind(ExprKind.FILTRATION),
        )


class Schema(NwSchema):
    """Ordered mapping of column names to their data type.

    Arguments:
        schema: Mapping[str, DType] | Iterable[tuple[str, DType]] | None
            The schema definition given by column names and their associated.
            *instantiated* Narwhals data type. Accepts a mapping or an iterable of tuples.
    """

    _version = Version.V1


@overload
def _stableify(obj: NwDataFrame[IntoFrameT]) -> DataFrame[IntoFrameT]: ...
@overload
def _stableify(obj: NwLazyFrame[IntoFrameT]) -> LazyFrame[IntoFrameT]: ...
@overload
def _stableify(obj: NwSeries[IntoSeriesT]) -> Series[IntoSeriesT]: ...
@overload
def _stableify(obj: NwExpr) -> Expr: ...
@overload
def _stableify(obj: Any) -> Any: ...


def _stableify(
    obj: NwDataFrame[IntoFrameT]
    | NwLazyFrame[IntoFrameT]
    | NwSeries[IntoSeriesT]
    | NwExpr
    | Any,
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT] | Series[IntoSeriesT] | Expr | Any:
    if isinstance(obj, NwDataFrame):
        return DataFrame(
            obj._compliant_frame._change_version(Version.V1),
            level=obj._level,
        )
    if isinstance(obj, NwLazyFrame):
        return LazyFrame(
            obj._compliant_frame._change_version(Version.V1),
            level=obj._level,
        )
    if isinstance(obj, NwSeries):
        return Series(
            obj._compliant_series._change_version(Version.V1),
            level=obj._level,
        )
    if isinstance(obj, NwExpr):
        return Expr(obj._to_compliant_expr, obj._metadata)
    return obj


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeriesT,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeriesT,
    *,
    strict: Literal[False],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    strict: Literal[False],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    strict: Literal[False],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoFrameT | IntoSeriesT,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoFrameT,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    strict: Literal[False],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    strict: Literal[True] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    strict: Literal[True] = ...,
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoFrame | IntoSeries,
    *,
    strict: Literal[True] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[Any] | LazyFrame[Any] | Series[Any]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    strict: Literal[True] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoFrameT,
    *,
    strict: Literal[True] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeries,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT | IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoDataFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    pass_through: Literal[True],
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoFrameT | IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT] | Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoFrameT,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoFrameT] | LazyFrame[IntoFrameT]: ...


@overload
def from_native(
    native_object: T,
    *,
    pass_through: Literal[True],
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> T: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[True],
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoDataFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[True],
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: None = ...,
) -> DataFrame[IntoDataFrameT]: ...


@overload
def from_native(
    native_object: IntoFrame | IntoSeries,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[False] = ...,
    allow_series: Literal[True],
) -> DataFrame[Any] | LazyFrame[Any] | Series[Any]: ...


@overload
def from_native(
    native_object: IntoSeriesT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
    series_only: Literal[True],
    allow_series: None = ...,
) -> Series[IntoSeriesT]: ...


@overload
def from_native(
    native_object: IntoFrameT,
    *,
    pass_through: Literal[False] = ...,
    eager_only: Literal[False] = ...,
    eager_or_interchange_only: Literal[False] = ...,
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
    eager_or_interchange_only: bool = False,
    series_only: bool,
    allow_series: bool | None,
) -> Any: ...


def from_native(
    native_object: IntoFrameT | IntoFrame | IntoSeriesT | IntoSeries | T,
    *,
    strict: bool | None = None,
    pass_through: bool | None = None,
    eager_only: bool = False,
    eager_or_interchange_only: bool = False,
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
        eager_or_interchange_only: Whether to only allow eager objects or objects which
            have interchange-level support in Narwhals:

            - `False` (default): don't require `native_object` to either be eager or to
              have interchange-level support in Narwhals
            - `True`: only convert to Narwhals if `native_object` is eager or has
              interchange-level support in Narwhals

            See [interchange-only support](../extending.md/#interchange-only-support)
            for more details.
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
    # Early returns
    if isinstance(native_object, (DataFrame, LazyFrame)) and not series_only:
        return native_object
    if isinstance(native_object, Series) and (series_only or allow_series):
        return native_object

    pass_through = validate_strict_and_pass_though(
        strict, pass_through, pass_through_default=False, emit_deprecation_warning=False
    )

    result = _from_native_impl(
        native_object,
        pass_through=pass_through,
        eager_only=eager_only,
        eager_or_interchange_only=eager_or_interchange_only,
        series_only=series_only,
        allow_series=allow_series,
        version=Version.V1,
    )
    return _stableify(result)  # type: ignore[no-any-return]


@overload
def to_native(
    narwhals_object: DataFrame[IntoDataFrameT], *, strict: Literal[True] = ...
) -> IntoDataFrameT: ...
@overload
def to_native(
    narwhals_object: LazyFrame[IntoFrameT], *, strict: Literal[True] = ...
) -> IntoFrameT: ...
@overload
def to_native(
    narwhals_object: Series[IntoSeriesT], *, strict: Literal[True] = ...
) -> IntoSeriesT: ...
@overload
def to_native(narwhals_object: Any, *, strict: bool) -> Any: ...
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
) -> IntoFrameT | IntoSeriesT | Any:
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
        strict, pass_through, pass_through_default=False, emit_deprecation_warning=False
    )

    if isinstance(narwhals_object, BaseFrame):
        return narwhals_object._compliant_frame._native_frame
    if isinstance(narwhals_object, Series):
        return narwhals_object._compliant_series._native_series

    if not pass_through:
        msg = f"Expected Narwhals object, got {type(narwhals_object)}."
        raise TypeError(msg)
    return narwhals_object


def narwhalify(
    func: Callable[..., Any] | None = None,
    *,
    strict: bool | None = None,
    pass_through: bool | None = None,
    eager_only: bool = False,
    eager_or_interchange_only: bool = False,
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
        eager_or_interchange_only: Whether to only allow eager objects or objects which
            have interchange-level support in Narwhals:

            - `False` (default): don't require `native_object` to either be eager or to
              have interchange-level support in Narwhals
            - `True`: only convert to Narwhals if `native_object` is eager or has
              interchange-level support in Narwhals

            See [interchange-only support](../extending.md/#interchange-only-support)
            for more details.
        series_only: Whether to only allow Series:

            - `False` (default): don't require `native_object` to be a Series
            - `True`: only convert to Narwhals if `native_object` is a Series
        allow_series: Whether to allow Series (default is only Dataframe / Lazyframe):

            - `False` or `None`: don't convert to Narwhals if `native_object` is a Series
            - `True` (default): allow `native_object` to be a Series

    Returns:
        Decorated function.
    """
    pass_through = validate_strict_and_pass_though(
        strict, pass_through, pass_through_default=True, emit_deprecation_warning=False
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            args = [
                from_native(
                    arg,
                    pass_through=pass_through,
                    eager_only=eager_only,
                    eager_or_interchange_only=eager_or_interchange_only,
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
                    eager_or_interchange_only=eager_or_interchange_only,
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

            if backends.__len__() > 1:
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


def all() -> Expr:
    """Instantiate an expression representing all columns.

    Returns:
        A new expression.
    """
    return _stableify(nw.all())


def col(*names: str | Iterable[str]) -> Expr:
    """Creates an expression that references one or more columns by their name(s).

    Arguments:
        names: Name(s) of the columns to use.

    Returns:
        A new expression.
    """
    return _stableify(nw.col(*names))


def exclude(*names: str | Iterable[str]) -> Expr:
    """Creates an expression that excludes columns by their name(s).

    Arguments:
        names: Name(s) of the columns to exclude.

    Returns:
        A new expression.
    """
    return _stableify(nw.exclude(*names))


def nth(*indices: int | Sequence[int]) -> Expr:
    """Creates an expression that references one or more columns by their index(es).

    Notes:
        `nth` is not supported for Polars version<1.0.0. Please use
        [`narwhals.col`][] instead.

    Arguments:
        indices: One or more indices representing the columns to retrieve.

    Returns:
        A new expression.
    """
    return _stableify(nw.nth(*indices))


def len() -> Expr:
    """Return the number of rows.

    Returns:
        A new expression.
    """
    return _stableify(nw.len())


def lit(value: Any, dtype: DType | type[DType] | None = None) -> Expr:
    """Return an expression representing a literal value.

    Arguments:
        value: The value to use as literal.
        dtype: The data type of the literal value. If not provided, the data type will
            be inferred.

    Returns:
        A new expression.
    """
    return _stableify(nw.lit(value, dtype))


def min(*columns: str) -> Expr:
    """Return the minimum value.

    Note:
       Syntactic sugar for ``nw.col(columns).min()``.

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function.

    Returns:
        A new expression.
    """
    return _stableify(nw.min(*columns))


def max(*columns: str) -> Expr:
    """Return the maximum value.

    Note:
       Syntactic sugar for ``nw.col(columns).max()``.

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function.

    Returns:
        A new expression.
    """
    return _stableify(nw.max(*columns))


def mean(*columns: str) -> Expr:
    """Get the mean value.

    Note:
        Syntactic sugar for ``nw.col(columns).mean()``

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function

    Returns:
        A new expression.
    """
    return _stableify(nw.mean(*columns))


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
    """
    return _stableify(nw.median(*columns))


def sum(*columns: str) -> Expr:
    """Sum all values.

    Note:
        Syntactic sugar for ``nw.col(columns).sum()``

    Arguments:
        columns: Name(s) of the columns to use in the aggregation function

    Returns:
        A new expression.
    """
    return _stableify(nw.sum(*columns))


def sum_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Sum all values horizontally across columns.

    Warning:
        Unlike Polars, we support horizontal sum over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.sum_horizontal(*exprs))


def all_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    r"""Compute the bitwise AND horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.all_horizontal(*exprs))


def any_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    r"""Compute the bitwise OR horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.any_horizontal(*exprs))


def mean_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Compute the mean of all values horizontally across columns.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.mean_horizontal(*exprs))


def min_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Get the minimum value horizontally across columns.

    Notes:
        We support `min_horizontal` over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.min_horizontal(*exprs))


def max_horizontal(*exprs: IntoExpr | Iterable[IntoExpr]) -> Expr:
    """Get the maximum value horizontally across columns.

    Notes:
        We support `max_horizontal` over numeric columns only.

    Arguments:
        exprs: Name(s) of the columns to use in the aggregation function. Accepts
            expression input.

    Returns:
        A new expression.
    """
    return _stableify(nw.max_horizontal(*exprs))


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
    """
    return _stableify(nw.concat(items, how=how))


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
    """
    return _stableify(
        nw.concat_str(exprs, *more_exprs, separator=separator, ignore_nulls=ignore_nulls)
    )


class When(NwWhen):
    @classmethod
    def from_when(cls: type, when: NwWhen) -> When:
        return cls(when._predicate)  # type: ignore[no-any-return]

    def then(self: Self, value: Any) -> Then:
        return Then.from_then(super().then(value))


class Then(NwThen, Expr):
    @classmethod
    def from_then(cls: type, then: NwThen) -> Then:
        return cls(  # type: ignore[no-any-return]
            then._to_compliant_expr, then._metadata
        )

    def otherwise(self: Self, value: Any) -> Expr:
        return _stableify(super().otherwise(value))


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
    """
    return When.from_when(nw_when(*predicates))


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
    """
    return _stableify(  # type: ignore[no-any-return]
        _new_series_impl(
            name,
            values,
            dtype,
            native_namespace=native_namespace,
            version=Version.V1,
        )
    )


def from_arrow(
    native_frame: ArrowStreamExportable, *, native_namespace: ModuleType
) -> DataFrame[Any]:
    """Construct a DataFrame from an object which supports the PyCapsule Interface.

    Arguments:
        native_frame: Object which implements `__arrow_c_stream__`.
        native_namespace: The native library to use for DataFrame creation.

    Returns:
        A new DataFrame.
    """
    return _stableify(  # type: ignore[no-any-return]
        nw_from_arrow(native_frame, native_namespace=native_namespace)
    )


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
    """
    backend = validate_native_namespace_and_backend(
        backend, native_namespace, emit_deprecation_warning=False
    )
    return _stableify(  # type: ignore[no-any-return]
        _from_dict_impl(data, schema, backend=backend)
    )


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
    """
    return _stableify(_from_numpy_impl(data, schema, native_namespace=native_namespace))  # type: ignore[no-any-return]


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
    """
    backend = validate_native_namespace_and_backend(
        backend, native_namespace, emit_deprecation_warning=True
    )
    if backend is None:  # pragma: no cover
        raise AssertionError
    return _stableify(  # type: ignore[no-any-return]
        _read_csv_impl(source, backend=backend, **kwargs)
    )


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
    """
    return _stableify(  # type: ignore[no-any-return]
        _scan_csv_impl(source, native_namespace=native_namespace, **kwargs)
    )


def read_parquet(
    source: str, *, native_namespace: ModuleType, **kwargs: Any
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
    """
    return _stableify(  # type: ignore[no-any-return]
        _read_parquet_impl(source, native_namespace=native_namespace, **kwargs)
    )


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
    """
    return _stableify(  # type: ignore[no-any-return]
        _scan_parquet_impl(source, native_namespace=native_namespace, **kwargs)
    )


__all__ = [
    "Array",
    "Boolean",
    "Categorical",
    "DataFrame",
    "Date",
    "Datetime",
    "Decimal",
    "Duration",
    "Enum",
    "Expr",
    "Field",
    "Float32",
    "Float64",
    "Implementation",
    "Int8",
    "Int16",
    "Int32",
    "Int64",
    "Int128",
    "LazyFrame",
    "List",
    "Object",
    "Schema",
    "Series",
    "String",
    "Struct",
    "UInt8",
    "UInt16",
    "UInt32",
    "UInt64",
    "UInt128",
    "Unknown",
    "all",
    "all_horizontal",
    "any_horizontal",
    "col",
    "concat",
    "concat_str",
    "dependencies",
    "dtypes",
    "exceptions",
    "exclude",
    "from_arrow",
    "from_dict",
    "from_native",
    "from_numpy",
    "generate_temporary_column_name",
    "get_level",
    "get_native_namespace",
    "is_ordered_categorical",
    "len",
    "lit",
    "max",
    "max_horizontal",
    "maybe_align_index",
    "maybe_convert_dtypes",
    "maybe_get_index",
    "maybe_reset_index",
    "maybe_set_index",
    "mean",
    "mean_horizontal",
    "median",
    "min",
    "min_horizontal",
    "narwhalify",
    "new_series",
    "nth",
    "read_csv",
    "read_parquet",
    "scan_csv",
    "scan_parquet",
    "selectors",
    "show_versions",
    "sum",
    "sum_horizontal",
    "to_native",
    "to_py_scalar",
    "when",
]
