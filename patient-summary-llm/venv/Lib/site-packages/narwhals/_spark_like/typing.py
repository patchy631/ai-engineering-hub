from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Protocol
from typing import Sequence

if TYPE_CHECKING:
    from pyspark.sql import Column

    class WindowFunction(Protocol):
        def __call__(
            self, _input: Column, partition_by: Sequence[str], order_by: Sequence[str]
        ) -> Column: ...
