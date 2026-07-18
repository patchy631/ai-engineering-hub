from __future__ import annotations

from typing import TYPE_CHECKING

import pyarrow as pa
import pyarrow.compute as pc

from narwhals._arrow.utils import ArrowSeriesNamespace

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.series import ArrowSeries


class ArrowSeriesListNamespace(ArrowSeriesNamespace):
    def len(self: Self) -> ArrowSeries:
        return self.from_native(pc.list_value_length(self.native).cast(pa.uint32()))
