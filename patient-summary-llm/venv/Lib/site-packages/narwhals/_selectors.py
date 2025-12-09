"""Almost entirely complete, generic `selectors` implementation."""

from __future__ import annotations

import re
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Collection
from typing import Iterable
from typing import Iterator
from typing import Sequence
from typing import TypeVar
from typing import overload

from narwhals.typing import CompliantExpr
from narwhals.utils import _parse_time_unit_and_time_zone
from narwhals.utils import dtype_matches_time_unit_and_time_zone
from narwhals.utils import get_column_names
from narwhals.utils import import_dtypes_module
from narwhals.utils import is_compliant_dataframe
from narwhals.utils import is_tracks_depth

if not TYPE_CHECKING:  # pragma: no cover
    # TODO @dangotbanned: Remove after dropping `3.8` (#2084)
    # - https://github.com/narwhals-dev/narwhals/pull/2064#discussion_r1965921386
    import sys

    if sys.version_info >= (3, 9):
        from typing import Protocol
    else:
        from typing import Generic

        Protocol = Generic
else:  # pragma: no cover
    from typing import Protocol

if TYPE_CHECKING:
    from datetime import timezone

    from typing_extensions import Self
    from typing_extensions import TypeAlias
    from typing_extensions import TypeIs

    from narwhals.dtypes import DType
    from narwhals.typing import CompliantDataFrame
    from narwhals.typing import CompliantLazyFrame
    from narwhals.typing import CompliantSeries
    from narwhals.typing import TimeUnit
    from narwhals.utils import Implementation
    from narwhals.utils import Version


SeriesT = TypeVar("SeriesT", bound="CompliantSeries")
FrameT = TypeVar("FrameT", bound="CompliantDataFrame[Any] | CompliantLazyFrame")
DataFrameT = TypeVar("DataFrameT", bound="CompliantDataFrame[Any]")
LazyFrameT = TypeVar("LazyFrameT", bound="CompliantLazyFrame")
SelectorOrExpr: TypeAlias = (
    "CompliantSelector[FrameT, SeriesT] | CompliantExpr[FrameT, SeriesT]"
)
EvalSeries: TypeAlias = Callable[[FrameT], Sequence[SeriesT]]
EvalNames: TypeAlias = Callable[[FrameT], Sequence[str]]


class CompliantSelectorNamespace(Protocol[FrameT, SeriesT]):
    _implementation: Implementation
    _backend_version: tuple[int, ...]
    _version: Version

    def _selector(
        self,
        call: EvalSeries[FrameT, SeriesT],
        evaluate_output_names: EvalNames[FrameT],
        /,
    ) -> CompliantSelector[FrameT, SeriesT]: ...

    def _iter_columns(self, df: FrameT, /) -> Iterator[SeriesT]: ...

    def _iter_schema(self, df: FrameT, /) -> Iterator[tuple[str, DType]]:
        for ser in self._iter_columns(df):
            yield ser.name, ser.dtype

    def _iter_columns_dtypes(self, df: FrameT, /) -> Iterator[tuple[SeriesT, DType]]:
        # NOTE: Defined to be overridden for lazy
        # - Their `SeriesT` is a **native** object
        #   - `.dtype` won't return a `nw.DType` (or maybe anything) for lazy backends
        #   - See (https://github.com/narwhals-dev/narwhals/issues/2044)
        for ser in self._iter_columns(df):
            yield ser, ser.dtype

    def _iter_columns_names(self, df: FrameT, /) -> Iterator[tuple[SeriesT, str]]:
        yield from zip(self._iter_columns(df), df.columns)

    def _is_dtype(
        self: CompliantSelectorNamespace[FrameT, SeriesT], dtype: type[DType], /
    ) -> CompliantSelector[FrameT, SeriesT]:
        def series(df: FrameT) -> Sequence[SeriesT]:
            return [
                ser for ser, tp in self._iter_columns_dtypes(df) if isinstance(tp, dtype)
            ]

        def names(df: FrameT) -> Sequence[str]:
            return [name for name, tp in self._iter_schema(df) if isinstance(tp, dtype)]

        return self._selector(series, names)

    def by_dtype(
        self: Self, dtypes: Collection[DType | type[DType]]
    ) -> CompliantSelector[FrameT, SeriesT]:
        def series(df: FrameT) -> Sequence[SeriesT]:
            return [ser for ser, tp in self._iter_columns_dtypes(df) if tp in dtypes]

        def names(df: FrameT) -> Sequence[str]:
            return [name for name, tp in self._iter_schema(df) if tp in dtypes]

        return self._selector(series, names)

    def matches(self: Self, pattern: str) -> CompliantSelector[FrameT, SeriesT]:
        p = re.compile(pattern)

        def series(df: FrameT) -> Sequence[SeriesT]:
            if is_compliant_dataframe(df) and not self._implementation.is_duckdb():
                return [df.get_column(col) for col in df.columns if p.search(col)]

            return [ser for ser, name in self._iter_columns_names(df) if p.search(name)]

        def names(df: FrameT) -> Sequence[str]:
            return [col for col in df.columns if p.search(col)]

        return self._selector(series, names)

    def numeric(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        def series(df: FrameT) -> Sequence[SeriesT]:
            return [ser for ser, tp in self._iter_columns_dtypes(df) if tp.is_numeric()]

        def names(df: FrameT) -> Sequence[str]:
            return [name for name, tp in self._iter_schema(df) if tp.is_numeric()]

        return self._selector(series, names)

    def categorical(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        return self._is_dtype(import_dtypes_module(self._version).Categorical)

    def string(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        return self._is_dtype(import_dtypes_module(self._version).String)

    def boolean(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        return self._is_dtype(import_dtypes_module(self._version).Boolean)

    def all(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        def series(df: FrameT) -> Sequence[SeriesT]:
            return list(self._iter_columns(df))

        return self._selector(series, get_column_names)

    def datetime(
        self: Self,
        time_unit: TimeUnit | Iterable[TimeUnit] | None,
        time_zone: str | timezone | Iterable[str | timezone | None] | None,
    ) -> CompliantSelector[FrameT, SeriesT]:
        time_units, time_zones = _parse_time_unit_and_time_zone(time_unit, time_zone)
        matches = partial(
            dtype_matches_time_unit_and_time_zone,
            dtypes=import_dtypes_module(version=self._version),
            time_units=time_units,
            time_zones=time_zones,
        )

        def series(df: FrameT) -> Sequence[SeriesT]:
            return [ser for ser, tp in self._iter_columns_dtypes(df) if matches(tp)]

        def names(df: FrameT) -> Sequence[str]:
            return [name for name, tp in self._iter_schema(df) if matches(tp)]

        return self._selector(series, names)


class EagerSelectorNamespace(
    CompliantSelectorNamespace[DataFrameT, SeriesT], Protocol[DataFrameT, SeriesT]
):
    def _iter_columns(self, df: DataFrameT, /) -> Iterator[SeriesT]:
        yield from df.iter_columns()


class LazySelectorNamespace(
    CompliantSelectorNamespace[LazyFrameT, SeriesT], Protocol[LazyFrameT, SeriesT]
):
    def _iter_schema(self, df: LazyFrameT) -> Iterator[tuple[str, DType]]:
        yield from df.schema.items()

    def _iter_columns(self, df: LazyFrameT) -> Iterator[SeriesT]:
        yield from df._iter_columns()

    def _iter_columns_dtypes(self, df: LazyFrameT, /) -> Iterator[tuple[SeriesT, DType]]:
        yield from zip(self._iter_columns(df), df.schema.values())


class CompliantSelector(CompliantExpr[FrameT, SeriesT], Protocol[FrameT, SeriesT]):
    @property
    def selectors(self) -> CompliantSelectorNamespace[FrameT, SeriesT]:
        return self.__narwhals_namespace__().selectors

    def _to_expr(self: Self) -> CompliantExpr[FrameT, SeriesT]: ...

    def _is_selector(
        self: Self, other: Self | CompliantExpr[FrameT, SeriesT]
    ) -> TypeIs[CompliantSelector[FrameT, SeriesT]]:
        return isinstance(other, type(self))

    @overload
    def __sub__(self: Self, other: Self) -> Self: ...
    @overload
    def __sub__(
        self: Self, other: CompliantExpr[FrameT, SeriesT]
    ) -> CompliantExpr[FrameT, SeriesT]: ...
    def __sub__(
        self: Self, other: SelectorOrExpr[FrameT, SeriesT]
    ) -> SelectorOrExpr[FrameT, SeriesT]:
        if self._is_selector(other):

            def series(df: FrameT) -> Sequence[SeriesT]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [
                    x for x, name in zip(self(df), lhs_names) if name not in rhs_names
                ]

            def names(df: FrameT) -> Sequence[str]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [x for x in lhs_names if x not in rhs_names]

            return self.selectors._selector(series, names)
        else:
            return self._to_expr() - other

    @overload
    def __or__(self: Self, other: Self) -> Self: ...
    @overload
    def __or__(
        self: Self, other: CompliantExpr[FrameT, SeriesT]
    ) -> CompliantExpr[FrameT, SeriesT]: ...
    def __or__(
        self: Self, other: SelectorOrExpr[FrameT, SeriesT]
    ) -> SelectorOrExpr[FrameT, SeriesT]:
        if self._is_selector(other):

            def names(df: FrameT) -> Sequence[SeriesT]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [
                    *(x for x, name in zip(self(df), lhs_names) if name not in rhs_names),
                    *other(df),
                ]

            def series(df: FrameT) -> Sequence[str]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [*(x for x in lhs_names if x not in rhs_names), *rhs_names]

            return self.selectors._selector(names, series)
        else:
            return self._to_expr() | other

    @overload
    def __and__(self: Self, other: Self) -> Self: ...
    @overload
    def __and__(
        self: Self, other: CompliantExpr[FrameT, SeriesT]
    ) -> CompliantExpr[FrameT, SeriesT]: ...
    def __and__(
        self: Self, other: SelectorOrExpr[FrameT, SeriesT]
    ) -> SelectorOrExpr[FrameT, SeriesT]:
        if self._is_selector(other):

            def series(df: FrameT) -> Sequence[SeriesT]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [x for x, name in zip(self(df), lhs_names) if name in rhs_names]

            def names(df: FrameT) -> Sequence[str]:
                lhs_names, rhs_names = _eval_lhs_rhs(df, self, other)
                return [x for x in lhs_names if x in rhs_names]

            return self.selectors._selector(series, names)
        else:
            return self._to_expr() & other

    def __invert__(self: Self) -> CompliantSelector[FrameT, SeriesT]:
        return self.selectors.all() - self  # type: ignore[no-any-return]

    def __repr__(self: Self) -> str:  # pragma: no cover
        s = f"depth={self._depth}, " if is_tracks_depth(self._implementation) else ""
        return f"{type(self).__name__}({s}function_name={self._function_name})"


def _eval_lhs_rhs(
    df: CompliantDataFrame[Any] | CompliantLazyFrame,
    lhs: CompliantExpr[Any, Any],
    rhs: CompliantExpr[Any, Any],
) -> tuple[Sequence[str], Sequence[str]]:
    return lhs._evaluate_output_names(df), rhs._evaluate_output_names(df)
