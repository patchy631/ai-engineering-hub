from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Iterator
from typing import cast

from narwhals._polars.utils import extract_native

if TYPE_CHECKING:
    from polars.dataframe.group_by import GroupBy as NativeGroupBy
    from polars.lazyframe.group_by import LazyGroupBy as NativeLazyGroupBy
    from typing_extensions import Self

    from narwhals._polars.dataframe import PolarsDataFrame
    from narwhals._polars.dataframe import PolarsLazyFrame
    from narwhals._polars.expr import PolarsExpr


class PolarsGroupBy:
    def __init__(
        self: Self, df: PolarsDataFrame, keys: list[str], *, drop_null_keys: bool
    ) -> None:
        self._compliant_frame: PolarsDataFrame = df
        self.keys: list[str] = keys
        df = df.drop_nulls(keys) if drop_null_keys else df
        self._grouped: NativeGroupBy = df._native_frame.group_by(keys)

    def agg(self: Self, *aggs: PolarsExpr) -> PolarsDataFrame:
        from_native = self._compliant_frame._from_native_frame
        return from_native(self._grouped.agg(extract_native(arg) for arg in aggs))

    def __iter__(self: Self) -> Iterator[tuple[tuple[str, ...], PolarsDataFrame]]:
        for key, df in self._grouped:
            yield tuple(cast("str", key)), self._compliant_frame._from_native_frame(df)


class PolarsLazyGroupBy:
    def __init__(
        self: Self, df: PolarsLazyFrame, keys: list[str], *, drop_null_keys: bool
    ) -> None:
        self._compliant_frame: PolarsLazyFrame = df
        self.keys: list[str] = keys
        df = df.drop_nulls(keys) if drop_null_keys else df
        self._grouped: NativeLazyGroupBy = df._native_frame.group_by(keys)

    def agg(self: Self, *aggs: PolarsExpr) -> PolarsLazyFrame:
        from_native = self._compliant_frame._from_native_frame
        return from_native(self._grouped.agg(extract_native(arg) for arg in aggs))
