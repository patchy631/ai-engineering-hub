from __future__ import annotations

from typing import TYPE_CHECKING

import pyarrow.compute as pc

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.series import ArrowSeries


class ArrowSeriesStructNamespace:
    def __init__(self: Self, series: ArrowSeries) -> None:
        self._compliant_series: ArrowSeries = series

    def field(self: Self, name: str) -> ArrowSeries:
        return self._compliant_series._from_native_series(
            pc.struct_field(self._compliant_series._native_series, name),
        ).alias(name)
