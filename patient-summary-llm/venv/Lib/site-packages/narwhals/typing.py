from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Iterator
from typing import Literal
from typing import Mapping
from typing import Protocol
from typing import Sequence
from typing import TypeVar
from typing import Union

from narwhals.utils import deprecated
from narwhals.utils import unstable

if not TYPE_CHECKING:
    if sys.version_info >= (3, 9):
        from typing import Protocol as Protocol38
    else:
        from typing import Generic as Protocol38
else:
    # TODO @dangotbanned: Remove after dropping `3.8` (#2084)
    # - https://github.com/narwhals-dev/narwhals/pull/2064#discussion_r1965921386
    from typing import Protocol as Protocol38

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Iterable
    from typing import Mapping
    from typing import Sized

    import numpy as np
    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from narwhals import dtypes
    from narwhals._expression_parsing import ExprKind
    from narwhals._selectors import CompliantSelectorNamespace
    from narwhals.dataframe import DataFrame
    from narwhals.dataframe import LazyFrame
    from narwhals.dtypes import DType
    from narwhals.expr import Expr
    from narwhals.series import Series
    from narwhals.utils import Implementation
    from narwhals.utils import Version

    # All dataframes supported by Narwhals have a
    # `columns` property. Their similarities don't extend
    # _that_ much further unfortunately...
    class NativeFrame(Protocol):
        @property
        def columns(self) -> Any: ...

        def join(self, *args: Any, **kwargs: Any) -> Any: ...

    class NativeSeries(Sized, Iterable[Any], Protocol):
        def filter(self, *args: Any, **kwargs: Any) -> Any: ...

    class DataFrameLike(Protocol):
        def __dataframe__(self, *args: Any, **kwargs: Any) -> Any: ...


class CompliantSeries(Protocol):
    @property
    def dtype(self) -> DType: ...
    @property
    def name(self) -> str: ...
    @property
    def native(self) -> Any: ...
    def __narwhals_series__(self) -> CompliantSeries: ...
    def alias(self, name: str) -> Self: ...
    def _from_native_series(self, series: Any) -> Self: ...


CompliantSeriesT_co = TypeVar(
    "CompliantSeriesT_co", bound=CompliantSeries, covariant=True
)


class CompliantDataFrame(Protocol[CompliantSeriesT_co]):
    def __narwhals_dataframe__(self) -> Self: ...
    def __narwhals_namespace__(self) -> Any: ...
    def simple_select(
        self, *column_names: str
    ) -> Self: ...  # `select` where all args are column names.
    def aggregate(self, *exprs: Any) -> Self:
        ...  # `select` where all args are aggregations or literals
        # (so, no broadcasting is necessary).

    @property
    def columns(self) -> Sequence[str]: ...
    @property
    def schema(self) -> Mapping[str, DType]: ...
    def get_column(self, name: str) -> CompliantSeriesT_co: ...
    def iter_columns(self) -> Iterator[CompliantSeriesT_co]: ...


class CompliantLazyFrame(Protocol):
    def __narwhals_lazyframe__(self) -> Self: ...
    def __narwhals_namespace__(self) -> Any: ...
    def simple_select(
        self, *column_names: str
    ) -> Self: ...  # `select` where all args are column names.
    def aggregate(self, *exprs: Any) -> Self:
        ...  # `select` where all args are aggregations or literals
        # (so, no broadcasting is necessary).

    @property
    def columns(self) -> Sequence[str]: ...
    @property
    def schema(self) -> Mapping[str, DType]: ...
    def _iter_columns(self) -> Iterator[Any]: ...


CompliantFrameT = TypeVar(
    "CompliantFrameT", bound="CompliantDataFrame[Any] | CompliantLazyFrame"
)


class CompliantExpr(Protocol38[CompliantFrameT, CompliantSeriesT_co]):
    _implementation: Implementation
    _backend_version: tuple[int, ...]
    _version: Version
    _evaluate_output_names: Callable[[CompliantFrameT], Sequence[str]]
    _alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None
    _depth: int
    _function_name: str

    def __call__(self, df: CompliantFrameT) -> Sequence[CompliantSeriesT_co]: ...
    def __narwhals_expr__(self) -> None: ...
    def __narwhals_namespace__(
        self,
    ) -> CompliantNamespace[CompliantFrameT, CompliantSeriesT_co]: ...
    def is_null(self) -> Self: ...
    def abs(self) -> Self: ...
    def all(self) -> Self: ...
    def any(self) -> Self: ...
    def alias(self, name: str) -> Self: ...
    def cast(self, dtype: DType | type[DType]) -> Self: ...
    def count(self) -> Self: ...
    def min(self) -> Self: ...
    def max(self) -> Self: ...
    def arg_min(self) -> Self: ...
    def arg_max(self) -> Self: ...
    def arg_true(self) -> Self: ...
    def mean(self) -> Self: ...
    def sum(self) -> Self: ...
    def median(self) -> Self: ...
    def skew(self) -> Self: ...
    def std(self, *, ddof: int) -> Self: ...
    def var(self, *, ddof: int) -> Self: ...
    def n_unique(self) -> Self: ...
    def null_count(self) -> Self: ...
    def drop_nulls(self) -> Self: ...
    def fill_null(
        self,
        value: Any | None,
        strategy: Literal["forward", "backward"] | None,
        limit: int | None,
    ) -> Self: ...
    def diff(self) -> Self: ...
    def unique(self) -> Self: ...
    def len(self) -> Self: ...
    def round(self, decimals: int) -> Self: ...
    def mode(self) -> Self: ...
    def head(self, n: int) -> Self: ...
    def tail(self, n: int) -> Self: ...
    def shift(self, n: int) -> Self: ...
    def is_finite(self) -> Self: ...
    def is_nan(self) -> Self: ...
    def is_unique(self) -> Self: ...
    def is_first_distinct(self) -> Self: ...
    def is_last_distinct(self) -> Self: ...
    def cum_sum(self, *, reverse: bool) -> Self: ...
    def cum_count(self, *, reverse: bool) -> Self: ...
    def cum_min(self, *, reverse: bool) -> Self: ...
    def cum_max(self, *, reverse: bool) -> Self: ...
    def cum_prod(self, *, reverse: bool) -> Self: ...
    def is_in(self, other: Any) -> Self: ...
    def sort(self, *, descending: bool, nulls_last: bool) -> Self: ...
    def rank(
        self,
        method: Literal["average", "min", "max", "dense", "ordinal"],
        *,
        descending: bool,
    ) -> Self: ...
    def replace_strict(
        self,
        old: Sequence[Any] | Mapping[Any, Any],
        new: Sequence[Any],
        *,
        return_dtype: DType | type[DType] | None,
    ) -> Self: ...
    def over(
        self: Self, keys: Sequence[str], kind: ExprKind, order_by: Sequence[str] | None
    ) -> Self: ...
    def sample(
        self,
        n: int | None,
        *,
        fraction: float | None,
        with_replacement: bool,
        seed: int | None,
    ) -> Self: ...
    def quantile(
        self,
        quantile: float,
        interpolation: Literal["nearest", "higher", "lower", "midpoint", "linear"],
    ) -> Self: ...
    def map_batches(
        self,
        function: Callable[[CompliantSeries], CompliantExpr[Any, Any]],
        return_dtype: DType | type[DType] | None,
    ) -> Self: ...

    @property
    def str(self) -> Any: ...
    @property
    def name(self) -> Any: ...
    @property
    def dt(self) -> Any: ...
    @property
    def cat(self) -> Any: ...
    @property
    def list(self) -> Any: ...
    @property
    def struct(self) -> Any: ...

    @unstable
    def ewm_mean(
        self,
        *,
        com: float | None,
        span: float | None,
        half_life: float | None,
        alpha: float | None,
        adjust: bool,
        min_samples: int,
        ignore_nulls: bool,
    ) -> Self: ...

    @unstable
    def rolling_sum(
        self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self: ...

    @unstable
    def rolling_mean(
        self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self: ...

    @unstable
    def rolling_var(
        self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self: ...

    @unstable
    def rolling_std(
        self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self: ...

    @deprecated("Since `1.22.0`")
    def gather_every(self, n: int, offset: int) -> Self: ...
    def __and__(self, other: Any) -> Self: ...
    def __or__(self, other: Any) -> Self: ...
    def __add__(self, other: Any) -> Self: ...
    def __sub__(self, other: Any) -> Self: ...
    def __mul__(self, other: Any) -> Self: ...
    def __floordiv__(self, other: Any) -> Self: ...
    def __truediv__(self, other: Any) -> Self: ...
    def __mod__(self, other: Any) -> Self: ...
    def __pow__(self, other: Any) -> Self: ...
    def __gt__(self, other: Any) -> Self: ...
    def __ge__(self, other: Any) -> Self: ...
    def __lt__(self, other: Any) -> Self: ...
    def __le__(self, other: Any) -> Self: ...
    def __invert__(self) -> Self: ...
    def broadcast(
        self, kind: Literal[ExprKind.AGGREGATION, ExprKind.LITERAL]
    ) -> Self: ...


class CompliantNamespace(Protocol[CompliantFrameT, CompliantSeriesT_co]):
    def col(
        self, *column_names: str
    ) -> CompliantExpr[CompliantFrameT, CompliantSeriesT_co]: ...
    def lit(
        self, value: Any, dtype: DType | None
    ) -> CompliantExpr[CompliantFrameT, CompliantSeriesT_co]: ...
    @property
    def selectors(self) -> CompliantSelectorNamespace[Any, Any]: ...


class SupportsNativeNamespace(Protocol):
    def __native_namespace__(self) -> ModuleType: ...


IntoCompliantExpr: TypeAlias = (
    "CompliantExpr[CompliantFrameT, CompliantSeriesT_co] | CompliantSeriesT_co"
)

IntoExpr: TypeAlias = Union["Expr", str, "Series[Any]"]
"""Anything which can be converted to an expression.

Use this to mean "either a Narwhals expression, or something which can be converted
into one". For example, `exprs` in `DataFrame.select` is typed to accept `IntoExpr`,
as it can either accept a `nw.Expr` (e.g. `df.select(nw.col('a'))`) or a string
which will be interpreted as a `nw.Expr`, e.g. `df.select('a')`.
"""

IntoDataFrame: TypeAlias = Union["NativeFrame", "DataFrame[Any]", "DataFrameLike"]
"""Anything which can be converted to a Narwhals DataFrame.

Use this if your function accepts a narwhalifiable object but doesn't care about its backend.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoDataFrame
    >>> def agnostic_shape(df_native: IntoDataFrame) -> tuple[int, int]:
    ...     df = nw.from_native(df_native, eager_only=True)
    ...     return df.shape
"""

IntoFrame: TypeAlias = Union[
    "NativeFrame", "DataFrame[Any]", "LazyFrame[Any]", "DataFrameLike"
]
"""Anything which can be converted to a Narwhals DataFrame or LazyFrame.

Use this if your function can accept an object which can be converted to either
`nw.DataFrame` or `nw.LazyFrame` and it doesn't care about its backend.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoFrame
    >>> def agnostic_columns(df_native: IntoFrame) -> list[str]:
    ...     df = nw.from_native(df_native)
    ...     return df.collect_schema().names()
"""

Frame: TypeAlias = Union["DataFrame[Any]", "LazyFrame[Any]"]
"""Narwhals DataFrame or Narwhals LazyFrame.

Use this if your function can work with either and your function doesn't care
about its backend.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import Frame
    >>> @nw.narwhalify
    ... def agnostic_columns(df: Frame) -> list[str]:
    ...     return df.columns
"""

IntoSeries: TypeAlias = Union["Series[Any]", "NativeSeries"]
"""Anything which can be converted to a Narwhals Series.

Use this if your function can accept an object which can be converted to `nw.Series`
and it doesn't care about its backend.

Examples:
    >>> from typing import Any
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoSeries
    >>> def agnostic_to_list(s_native: IntoSeries) -> list[Any]:
    ...     s = nw.from_native(s_native)
    ...     return s.to_list()
"""

IntoFrameT = TypeVar("IntoFrameT", bound="IntoFrame")
"""TypeVar bound to object convertible to Narwhals DataFrame or Narwhals LazyFrame.

Use this if your function accepts an object which is convertible to `nw.DataFrame`
or `nw.LazyFrame` and returns an object of the same type.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoFrameT
    >>> def agnostic_func(df_native: IntoFrameT) -> IntoFrameT:
    ...     df = nw.from_native(df_native)
    ...     return df.with_columns(c=nw.col("a") + 1).to_native()
"""

IntoDataFrameT = TypeVar("IntoDataFrameT", bound="IntoDataFrame")
"""TypeVar bound to object convertible to Narwhals DataFrame.

Use this if your function accepts an object which can be converted to `nw.DataFrame`
and returns an object of the same class.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoDataFrameT
    >>> def agnostic_func(df_native: IntoDataFrameT) -> IntoDataFrameT:
    ...     df = nw.from_native(df_native, eager_only=True)
    ...     return df.with_columns(c=df["a"] + 1).to_native()
"""

FrameT = TypeVar("FrameT", bound="Frame")
"""TypeVar bound to Narwhals DataFrame or Narwhals LazyFrame.

Use this if your function accepts either `nw.DataFrame` or `nw.LazyFrame` and returns
an object of the same kind.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import FrameT
    >>> @nw.narwhalify
    ... def agnostic_func(df: FrameT) -> FrameT:
    ...     return df.with_columns(c=nw.col("a") + 1)
"""

DataFrameT = TypeVar("DataFrameT", bound="DataFrame[Any]")
"""TypeVar bound to Narwhals DataFrame.

Use this if your function can accept a Narwhals DataFrame and returns a Narwhals
DataFrame backed by the same backend.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import DataFrameT
    >>> @nw.narwhalify
    >>> def func(df: DataFrameT) -> DataFrameT:
    ...     return df.with_columns(c=df["a"] + 1)
"""

IntoSeriesT = TypeVar("IntoSeriesT", bound="IntoSeries")
"""TypeVar bound to object convertible to Narwhals Series.

Use this if your function accepts an object which can be converted to `nw.Series`
and returns an object of the same class.

Examples:
    >>> import narwhals as nw
    >>> from narwhals.typing import IntoSeriesT
    >>> def agnostic_abs(s_native: IntoSeriesT) -> IntoSeriesT:
    ...     s = nw.from_native(s_native, series_only=True)
    ...     return s.abs().to_native()
"""

DTypeBackend: TypeAlias = 'Literal["pyarrow", "numpy_nullable"] | None'
SizeUnit: TypeAlias = Literal[
    "b",
    "kb",
    "mb",
    "gb",
    "tb",
    "bytes",
    "kilobytes",
    "megabytes",
    "gigabytes",
    "terabytes",
]

TimeUnit: TypeAlias = Literal["ns", "us", "ms", "s"]

_ShapeT = TypeVar("_ShapeT", bound="tuple[int, ...]")
_NDArray: TypeAlias = "np.ndarray[_ShapeT, Any]"
_1DArray: TypeAlias = "_NDArray[tuple[int]]"  # noqa: PYI042, PYI047
_2DArray: TypeAlias = "_NDArray[tuple[int, int]]"  # noqa: PYI042, PYI047
_AnyDArray: TypeAlias = "_NDArray[tuple[int, ...]]"  # noqa: PYI047


class DTypes:
    Decimal: type[dtypes.Decimal]
    Int128: type[dtypes.Int128]
    Int64: type[dtypes.Int64]
    Int32: type[dtypes.Int32]
    Int16: type[dtypes.Int16]
    Int8: type[dtypes.Int8]
    UInt128: type[dtypes.UInt128]
    UInt64: type[dtypes.UInt64]
    UInt32: type[dtypes.UInt32]
    UInt16: type[dtypes.UInt16]
    UInt8: type[dtypes.UInt8]
    Float64: type[dtypes.Float64]
    Float32: type[dtypes.Float32]
    String: type[dtypes.String]
    Boolean: type[dtypes.Boolean]
    Object: type[dtypes.Object]
    Categorical: type[dtypes.Categorical]
    Enum: type[dtypes.Enum]
    Datetime: type[dtypes.Datetime]
    Duration: type[dtypes.Duration]
    Date: type[dtypes.Date]
    Field: type[dtypes.Field]
    Struct: type[dtypes.Struct]
    List: type[dtypes.List]
    Array: type[dtypes.Array]
    Unknown: type[dtypes.Unknown]


__all__ = [
    "CompliantDataFrame",
    "CompliantLazyFrame",
    "CompliantSeries",
    "DataFrameT",
    "Frame",
    "FrameT",
    "IntoDataFrame",
    "IntoDataFrameT",
    "IntoExpr",
    "IntoFrame",
    "IntoFrameT",
    "IntoSeries",
    "IntoSeriesT",
]
