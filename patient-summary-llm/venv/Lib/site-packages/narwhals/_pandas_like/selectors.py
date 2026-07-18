from __future__ import annotations

from typing import TYPE_CHECKING

from narwhals._pandas_like.dataframe import PandasLikeDataFrame
from narwhals._pandas_like.expr import PandasLikeExpr
from narwhals._pandas_like.series import PandasLikeSeries
from narwhals._selectors import CompliantSelector
from narwhals._selectors import EagerSelectorNamespace

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.series import PandasLikeSeries
    from narwhals._selectors import EvalNames
    from narwhals._selectors import EvalSeries
    from narwhals.utils import _FullContext


class PandasSelectorNamespace(
    EagerSelectorNamespace["PandasLikeDataFrame", "PandasLikeSeries"]
):
    def _selector(
        self,
        call: EvalSeries[PandasLikeDataFrame, PandasLikeSeries],
        evaluate_output_names: EvalNames[PandasLikeDataFrame],
        /,
    ) -> PandasSelector:
        return PandasSelector(
            call,
            depth=0,
            function_name="selector",
            evaluate_output_names=evaluate_output_names,
            alias_output_names=None,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )

    def __init__(self: Self, context: _FullContext, /) -> None:
        self._implementation = context._implementation
        self._backend_version = context._backend_version
        self._version = context._version


class PandasSelector(  # type: ignore[misc]
    CompliantSelector["PandasLikeDataFrame", "PandasLikeSeries"], PandasLikeExpr
):
    def _to_expr(self: Self) -> PandasLikeExpr:
        return PandasLikeExpr(
            self._call,
            depth=self._depth,
            function_name=self._function_name,
            evaluate_output_names=self._evaluate_output_names,
            alias_output_names=self._alias_output_names,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )
