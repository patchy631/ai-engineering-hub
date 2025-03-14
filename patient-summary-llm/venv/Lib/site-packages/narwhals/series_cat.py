from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Generic
from typing import TypeVar

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals.series import Series

SeriesT = TypeVar("SeriesT", bound="Series[Any]")


class SeriesCatNamespace(Generic[SeriesT]):
    def __init__(self: Self, series: SeriesT) -> None:
        self._narwhals_series = series

    def get_categories(self: Self) -> SeriesT:
        """Get unique categories from column.

        Returns:
            A new Series containing the unique categories.

        Examples:
            >>> import pandas as pd
            >>> import narwhals as nw
            >>> s_native = pd.Series(["apple", "mango", "mango"], dtype="category")
            >>> s = nw.from_native(s_native, series_only=True)
            >>> s.cat.get_categories().to_native()
            0    apple
            1    mango
            dtype: object
        """
        return self._narwhals_series._from_compliant_series(
            self._narwhals_series._compliant_series.cat.get_categories()
        )
