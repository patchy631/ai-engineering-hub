from __future__ import annotations  # pragma: no cover

from typing import TYPE_CHECKING  # pragma: no cover
from typing import Union  # pragma: no cover

if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

    from narwhals._polars.expr import PolarsExpr
    from narwhals._polars.series import PolarsSeries

    IntoPolarsExpr: TypeAlias = Union[PolarsExpr, PolarsSeries]
