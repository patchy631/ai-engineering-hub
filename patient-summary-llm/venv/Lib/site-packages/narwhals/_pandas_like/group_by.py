from __future__ import annotations

import collections
import re
import warnings
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator

from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._expression_parsing import is_elementary_expression
from narwhals._pandas_like.utils import horizontal_concat
from narwhals._pandas_like.utils import native_series_from_iterable
from narwhals._pandas_like.utils import select_columns_by_name
from narwhals._pandas_like.utils import set_columns
from narwhals.utils import Implementation
from narwhals.utils import find_stacklevel

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._pandas_like.dataframe import PandasLikeDataFrame
    from narwhals._pandas_like.expr import PandasLikeExpr

AGGREGATIONS_TO_PANDAS_EQUIVALENT = {
    "sum": "sum",
    "mean": "mean",
    "median": "median",
    "max": "max",
    "min": "min",
    "std": "std",
    "var": "var",
    "len": "size",
    "n_unique": "nunique",
    "count": "count",
}


class PandasLikeGroupBy:
    def __init__(
        self: Self, df: PandasLikeDataFrame, keys: list[str], *, drop_null_keys: bool
    ) -> None:
        self._df = df
        self._keys = keys
        # Drop index to avoid potential collisions:
        # https://github.com/narwhals-dev/narwhals/issues/1907.
        if set(df._native_frame.index.names).intersection(df.columns):
            native_frame = df._native_frame.reset_index(drop=True)
        else:
            native_frame = df._native_frame
        if (
            self._df._implementation is Implementation.PANDAS
            and self._df._backend_version < (1, 1)
        ):  # pragma: no cover
            if (
                not drop_null_keys
                and self._df.simple_select(*self._keys)._native_frame.isna().any().any()
            ):
                msg = "Grouping by null values is not supported in pandas < 1.1.0"
                raise NotImplementedError(msg)
            self._grouped = native_frame.groupby(
                list(self._keys),
                sort=False,
                as_index=True,
                observed=True,
            )
        else:
            self._grouped = native_frame.groupby(
                list(self._keys),
                sort=False,
                as_index=True,
                dropna=drop_null_keys,
                observed=True,
            )

    def agg(self: Self, *exprs: PandasLikeExpr) -> PandasLikeDataFrame:  # noqa: PLR0915
        implementation = self._df._implementation
        backend_version = self._df._backend_version
        new_names: list[str] = self._keys.copy()

        all_aggs_are_simple = True
        for expr in exprs:
            _, aliases = evaluate_output_names_and_aliases(expr, self._df, self._keys)
            new_names.extend(aliases)

            if not (
                is_elementary_expression(expr)
                and re.sub(r"(\w+->)", "", expr._function_name)
                in AGGREGATIONS_TO_PANDAS_EQUIVALENT
            ):
                all_aggs_are_simple = False

        # dict of {output_name: root_name} that we count n_unique on
        # We need to do this separately from the rest so that we
        # can pass the `dropna` kwargs.
        nunique_aggs: dict[str, str] = {}
        simple_aggs: dict[str, list[str]] = collections.defaultdict(list)
        simple_aggs_functions: set[str] = set()

        # ddof to (output_names, aliases) mapping
        std_aggs: dict[int, tuple[list[str], list[str]]] = collections.defaultdict(
            lambda: ([], [])
        )
        var_aggs: dict[int, tuple[list[str], list[str]]] = collections.defaultdict(
            lambda: ([], [])
        )

        expected_old_names: list[str] = []
        simple_agg_new_names: list[str] = []

        if all_aggs_are_simple:
            for expr in exprs:
                output_names, aliases = evaluate_output_names_and_aliases(
                    expr, self._df, self._keys
                )
                if expr._depth == 0:
                    # e.g. agg(nw.len()) # noqa: ERA001
                    function_name = AGGREGATIONS_TO_PANDAS_EQUIVALENT.get(
                        expr._function_name, expr._function_name
                    )
                    simple_aggs_functions.add(function_name)

                    for alias in aliases:
                        expected_old_names.append(f"{self._keys[0]}_{function_name}")
                        simple_aggs[self._keys[0]].append(function_name)
                        simple_agg_new_names.append(alias)
                    continue

                # e.g. agg(nw.mean('a')) # noqa: ERA001
                function_name = re.sub(r"(\w+->)", "", expr._function_name)
                function_name = AGGREGATIONS_TO_PANDAS_EQUIVALENT.get(
                    function_name, function_name
                )

                is_n_unique = function_name == "nunique"
                is_std = function_name == "std"
                is_var = function_name == "var"
                for output_name, alias in zip(output_names, aliases):
                    if is_n_unique:
                        nunique_aggs[alias] = output_name
                    elif is_std and (ddof := expr._call_kwargs["ddof"]) != 1:
                        std_aggs[ddof][0].append(output_name)
                        std_aggs[ddof][1].append(alias)
                    elif is_var and (ddof := expr._call_kwargs["ddof"]) != 1:
                        var_aggs[ddof][0].append(output_name)
                        var_aggs[ddof][1].append(alias)
                    else:
                        expected_old_names.append(f"{output_name}_{function_name}")
                        simple_aggs[output_name].append(function_name)
                        simple_agg_new_names.append(alias)
                        simple_aggs_functions.add(function_name)

            result_aggs = []

            if simple_aggs:
                # Fast path for single aggregation such as `df.groupby(...).mean()`
                if (
                    len(simple_aggs_functions) == 1
                    and (agg_method := simple_aggs_functions.pop()) != "size"
                    and len(simple_aggs) > 1
                ):
                    result_simple_aggs = getattr(
                        self._grouped[list(simple_aggs.keys())], agg_method
                    )()
                    result_simple_aggs.columns = [
                        f"{a}_{agg_method}" for a in result_simple_aggs.columns
                    ]
                else:
                    result_simple_aggs = self._grouped.agg(simple_aggs)
                    result_simple_aggs.columns = [
                        f"{a}_{b}" for a, b in result_simple_aggs.columns
                    ]
                if not (
                    set(result_simple_aggs.columns) == set(expected_old_names)
                    and len(result_simple_aggs.columns) == len(expected_old_names)
                ):  # pragma: no cover
                    msg = (
                        f"Safety assertion failed, expected {expected_old_names} "
                        f"got {result_simple_aggs.columns}, "
                        "please report a bug at https://github.com/narwhals-dev/narwhals/issues"
                    )
                    raise AssertionError(msg)

                # Rename columns, being very careful
                expected_old_names_indices: dict[str, list[int]] = (
                    collections.defaultdict(list)
                )
                for idx, item in enumerate(expected_old_names):
                    expected_old_names_indices[item].append(idx)
                index_map: list[int] = [
                    expected_old_names_indices[item].pop(0)
                    for item in result_simple_aggs.columns
                ]
                result_simple_aggs.columns = [simple_agg_new_names[i] for i in index_map]
                result_aggs.append(result_simple_aggs)

            if nunique_aggs:
                result_nunique_aggs = self._grouped[list(nunique_aggs.values())].nunique(
                    dropna=False
                )
                result_nunique_aggs.columns = list(nunique_aggs.keys())

                result_aggs.append(result_nunique_aggs)

            if std_aggs:
                result_aggs.extend(
                    [
                        set_columns(
                            self._grouped[std_output_names].std(ddof=ddof),
                            columns=std_aliases,
                            implementation=implementation,
                            backend_version=backend_version,
                        )
                        for ddof, (std_output_names, std_aliases) in std_aggs.items()
                    ]
                )
            if var_aggs:
                result_aggs.extend(
                    [
                        set_columns(
                            self._grouped[var_output_names].var(ddof=ddof),
                            columns=var_aliases,
                            implementation=implementation,
                            backend_version=backend_version,
                        )
                        for ddof, (var_output_names, var_aliases) in var_aggs.items()
                    ]
                )

            if result_aggs:
                output_names_counter = collections.Counter(
                    c for frame in result_aggs for c in frame
                )
                if any(v > 1 for v in output_names_counter.values()):
                    msg = ""
                    for key, value in output_names_counter.items():
                        if value > 1:
                            msg += f"\n- '{key}' {value} times"
                        else:  # pragma: no cover
                            pass
                    msg = f"Expected unique output names, got:{msg}"
                    raise ValueError(msg)
                result = horizontal_concat(
                    dfs=result_aggs,
                    implementation=implementation,
                    backend_version=backend_version,
                )
            else:
                # No aggregation provided
                result = self._df.__native_namespace__().DataFrame(
                    list(self._grouped.groups.keys()), columns=self._keys
                )
            # Keep inplace=True to avoid making a redundant copy.
            # This may need updating, depending on https://github.com/pandas-dev/pandas/pull/51466/files
            result.reset_index(inplace=True)  # noqa: PD002
            return self._df._from_native_frame(
                select_columns_by_name(result, new_names, backend_version, implementation)
            )

        if self._df._native_frame.empty:
            # Don't even attempt this, it's way too inconsistent across pandas versions.
            msg = (
                "No results for group-by aggregation.\n\n"
                "Hint: you were probably trying to apply a non-elementary aggregation with a "
                "pandas-like API.\n"
                "Please rewrite your query such that group-by aggregations "
                "are elementary. For example, instead of:\n\n"
                "    df.group_by('a').agg(nw.col('b').round(2).mean())\n\n"
                "use:\n\n"
                "    df.with_columns(nw.col('b').round(2)).group_by('a').agg(nw.col('b').mean())\n\n"
            )
            raise ValueError(msg)

        warnings.warn(
            "Found complex group-by expression, which can't be expressed efficiently with the "
            "pandas API. If you can, please rewrite your query such that group-by aggregations "
            "are simple (e.g. mean, std, min, max, ...). \n\n"
            "Please see: "
            "https://narwhals-dev.github.io/narwhals/pandas_like_concepts/improve_group_by_operation/",
            UserWarning,
            stacklevel=find_stacklevel(),
        )

        def func(df: Any) -> Any:
            out_group = []
            out_names = []
            for expr in exprs:
                results_keys = expr(self._df._from_native_frame(df))
                for result_keys in results_keys:
                    out_group.append(result_keys._native_series.iloc[0])
                    out_names.append(result_keys.name)
            return native_series_from_iterable(
                out_group,
                index=out_names,
                name="",
                implementation=implementation,
            )

        if implementation is Implementation.PANDAS and backend_version >= (2, 2):
            result_complex = self._grouped.apply(func, include_groups=False)
        else:  # pragma: no cover
            result_complex = self._grouped.apply(func)

        # Keep inplace=True to avoid making a redundant copy.
        # This may need updating, depending on https://github.com/pandas-dev/pandas/pull/51466/files
        result_complex.reset_index(inplace=True)  # noqa: PD002

        return self._df._from_native_frame(
            select_columns_by_name(
                result_complex, new_names, backend_version, implementation
            )
        )

    def __iter__(self: Self) -> Iterator[tuple[Any, PandasLikeDataFrame]]:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=".*a length 1 tuple will be returned",
                category=FutureWarning,
            )
            for key, group in self._grouped:
                yield (key, self._df._from_native_frame(group))
