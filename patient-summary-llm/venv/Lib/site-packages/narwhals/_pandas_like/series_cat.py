from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.series import PandasLikeSeries


class PandasLikeSeriesCatNamespace:
    def __init__(self: Self, series: PandasLikeSeries) -> None:
        self._compliant_series = series

    def get_categories(self: Self) -> PandasLikeSeries:
        s = self._compliant_series._native_series
        return self._compliant_series._from_native_series(
            s.__class__(s.cat.categories, name=s.name)
        )
