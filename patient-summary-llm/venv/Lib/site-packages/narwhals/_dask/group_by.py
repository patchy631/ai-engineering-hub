from __future__ import annotations

import re
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Sequence

import dask.dataframe as dd

from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._expression_parsing import is_elementary_expression

try:
    import dask.dataframe.dask_expr as dx
except ModuleNotFoundError:  # pragma: no cover
    import dask_expr as dx

if TYPE_CHECKING:
    import pandas as pd
    from pandas.core.groupby import SeriesGroupBy as _PandasSeriesGroupBy
    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from narwhals._dask.dataframe import DaskLazyFrame
    from narwhals._dask.expr import DaskExpr

    PandasSeriesGroupBy: TypeAlias = _PandasSeriesGroupBy[Any, Any]
    _AggFn: TypeAlias = Callable[..., Any]
    Aggregation: TypeAlias = "str | _AggFn"

    from dask_expr._groupby import GroupBy as _DaskGroupBy
else:
    _DaskGroupBy = dx._groupby.GroupBy


def n_unique() -> dd.Aggregation:
    def chunk(s: PandasSeriesGroupBy) -> pd.Series[Any]:
        return s.nunique(dropna=False)

    def agg(s0: PandasSeriesGroupBy) -> pd.Series[Any]:
        return s0.sum()

    return dd.Aggregation(name="nunique", chunk=chunk, agg=agg)


def var(ddof: int) -> _AggFn:
    return partial(_DaskGroupBy.var, ddof=ddof)


def std(ddof: int) -> _AggFn:
    return partial(_DaskGroupBy.std, ddof=ddof)


POLARS_TO_DASK_AGGREGATIONS: Mapping[str, Aggregation] = {
    "sum": "sum",
    "mean": "mean",
    "median": "median",
    "max": "max",
    "min": "min",
    "std": std,
    "var": var,
    "len": "size",
    "n_unique": n_unique,
    "count": "count",
}


class DaskLazyGroupBy:
    def __init__(
        self: Self, df: DaskLazyFrame, keys: list[str], *, drop_null_keys: bool
    ) -> None:
        self._df: DaskLazyFrame = df
        self._keys = keys
        self._grouped = self._df._native_frame.groupby(
            list(self._keys),
            dropna=drop_null_keys,
            observed=True,
        )

    def agg(
        self: Self,
        *exprs: DaskExpr,
    ) -> DaskLazyFrame:
        return agg_dask(
            self._df,
            self._grouped,
            exprs,
            self._keys,
            self._from_native_frame,
        )

    def _from_native_frame(self: Self, df: dd.DataFrame) -> DaskLazyFrame:
        from narwhals._dask.dataframe import DaskLazyFrame

        return DaskLazyFrame(
            df,
            backend_version=self._df._backend_version,
            version=self._df._version,
        )


def agg_dask(
    df: DaskLazyFrame,
    grouped: Any,
    exprs: Sequence[DaskExpr],
    keys: list[str],
    from_dataframe: Callable[[Any], DaskLazyFrame],
) -> DaskLazyFrame:
    """This should be the fastpath, but cuDF is too far behind to use it.

    - https://github.com/rapidsai/cudf/issues/15118
    - https://github.com/rapidsai/cudf/issues/15084
    """
    if not exprs:
        # No aggregation provided
        return df.simple_select(*keys).unique(subset=keys)

    all_simple_aggs = True
    for expr in exprs:
        if not (
            is_elementary_expression(expr)
            and re.sub(r"(\w+->)", "", expr._function_name) in POLARS_TO_DASK_AGGREGATIONS
        ):
            all_simple_aggs = False
            break

    if all_simple_aggs:
        simple_aggregations: dict[str, tuple[str, Aggregation]] = {}
        for expr in exprs:
            output_names, aliases = evaluate_output_names_and_aliases(expr, df, keys)
            if expr._depth == 0:
                # e.g. agg(nw.len()) # noqa: ERA001
                function_name = POLARS_TO_DASK_AGGREGATIONS.get(
                    expr._function_name, expr._function_name
                )
                simple_aggregations.update(
                    dict.fromkeys(aliases, (keys[0], function_name))
                )
                continue

            # e.g. agg(nw.mean('a')) # noqa: ERA001
            function_name = re.sub(r"(\w+->)", "", expr._function_name)
            agg_function = POLARS_TO_DASK_AGGREGATIONS.get(function_name, function_name)
            # deal with n_unique case in a "lazy" mode to not depend on dask globally
            agg_function = (
                agg_function(**expr._call_kwargs)
                if callable(agg_function)
                else agg_function
            )

            simple_aggregations.update(
                {
                    alias: (output_name, agg_function)
                    for alias, output_name in zip(aliases, output_names)
                }
            )
        result_simple = grouped.agg(**simple_aggregations)
        return from_dataframe(result_simple.reset_index())

    msg = (
        "Non-trivial complex aggregation found.\n\n"
        "Hint: you were probably trying to apply a non-elementary aggregation with a "
        "dask dataframe.\n"
        "Please rewrite your query such that group-by aggregations "
        "are elementary. For example, instead of:\n\n"
        "    df.group_by('a').agg(nw.col('b').round(2).mean())\n\n"
        "use:\n\n"
        "    df.with_columns(nw.col('b').round(2)).group_by('a').agg(nw.col('b').mean())\n\n"
    )
    raise ValueError(msg)
