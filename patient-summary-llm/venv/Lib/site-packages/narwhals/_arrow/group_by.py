from __future__ import annotations

import collections
import re
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import cast

import pyarrow as pa
import pyarrow.compute as pc

from narwhals._arrow.utils import extract_py_scalar
from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._expression_parsing import is_elementary_expression
from narwhals.utils import generate_temporary_column_name

if TYPE_CHECKING:
    from typing_extensions import Self

    from narwhals._arrow.dataframe import ArrowDataFrame
    from narwhals._arrow.expr import ArrowExpr
    from narwhals._arrow.typing import Incomplete

POLARS_TO_ARROW_AGGREGATIONS = {
    "sum": "sum",
    "mean": "mean",
    "median": "approximate_median",
    "max": "max",
    "min": "min",
    "std": "stddev",
    "var": "variance",
    "len": "count",
    "n_unique": "count_distinct",
    "count": "count",
}


class ArrowGroupBy:
    def __init__(
        self: Self, df: ArrowDataFrame, keys: list[str], *, drop_null_keys: bool
    ) -> None:
        if drop_null_keys:
            self._df = df.drop_nulls(keys)
        else:
            self._df = df
        self._keys = keys.copy()
        self._grouped = pa.TableGroupBy(self._df._native_frame, self._keys)

    def agg(self: Self, *exprs: ArrowExpr) -> ArrowDataFrame:
        all_simple_aggs = True
        for expr in exprs:
            if not (
                is_elementary_expression(expr)
                and re.sub(r"(\w+->)", "", expr._function_name)
                in POLARS_TO_ARROW_AGGREGATIONS
            ):
                all_simple_aggs = False
                break

        if not all_simple_aggs:
            msg = (
                "Non-trivial complex aggregation found.\n\n"
                "Hint: you were probably trying to apply a non-elementary aggregation with a "
                "pyarrow table.\n"
                "Please rewrite your query such that group-by aggregations "
                "are elementary. For example, instead of:\n\n"
                "    df.group_by('a').agg(nw.col('b').round(2).mean())\n\n"
                "use:\n\n"
                "    df.with_columns(nw.col('b').round(2)).group_by('a').agg(nw.col('b').mean())\n\n"
            )
            raise ValueError(msg)

        aggs: list[tuple[str, str, Any]] = []
        expected_pyarrow_column_names: list[str] = self._keys.copy()
        new_column_names: list[str] = self._keys.copy()

        for expr in exprs:
            output_names, aliases = evaluate_output_names_and_aliases(
                expr, self._df, self._keys
            )

            if expr._depth == 0:
                # e.g. agg(nw.len()) # noqa: ERA001
                if expr._function_name != "len":  # pragma: no cover
                    msg = "Safety assertion failed, please report a bug to https://github.com/narwhals-dev/narwhals/issues"
                    raise AssertionError(msg)

                new_column_names.append(aliases[0])
                expected_pyarrow_column_names.append(f"{self._keys[0]}_count")
                aggs.append((self._keys[0], "count", pc.CountOptions(mode="all")))

                continue

            function_name = re.sub(r"(\w+->)", "", expr._function_name)
            if function_name in {"std", "var"}:
                option: Any = pc.VarianceOptions(ddof=expr._call_kwargs["ddof"])
            elif function_name in {"len", "n_unique"}:
                option = pc.CountOptions(mode="all")
            elif function_name == "count":
                option = pc.CountOptions(mode="only_valid")
            else:
                option = None

            function_name = POLARS_TO_ARROW_AGGREGATIONS[function_name]

            new_column_names.extend(aliases)
            expected_pyarrow_column_names.extend(
                [f"{output_name}_{function_name}" for output_name in output_names]
            )
            aggs.extend(
                [(output_name, function_name, option) for output_name in output_names]
            )

        result_simple = self._grouped.aggregate(aggs)

        # Rename columns, being very careful
        expected_old_names_indices: dict[str, list[int]] = collections.defaultdict(list)
        for idx, item in enumerate(expected_pyarrow_column_names):
            expected_old_names_indices[item].append(idx)
        if not (
            set(result_simple.column_names) == set(expected_pyarrow_column_names)
            and len(result_simple.column_names) == len(expected_pyarrow_column_names)
        ):  # pragma: no cover
            msg = (
                f"Safety assertion failed, expected {expected_pyarrow_column_names} "
                f"got {result_simple.column_names}, "
                "please report a bug at https://github.com/narwhals-dev/narwhals/issues"
            )
            raise AssertionError(msg)
        index_map: list[int] = [
            expected_old_names_indices[item].pop(0) for item in result_simple.column_names
        ]
        new_column_names = [new_column_names[i] for i in index_map]
        result_simple = result_simple.rename_columns(new_column_names)
        if self._df._backend_version < (12, 0, 0):
            columns = result_simple.column_names
            result_simple = result_simple.select(
                [*self._keys, *[col for col in columns if col not in self._keys]]
            )
        return self._df._from_native_frame(result_simple)

    def __iter__(self: Self) -> Iterator[tuple[Any, ArrowDataFrame]]:
        col_token = generate_temporary_column_name(n_bytes=8, columns=self._df.columns)
        null_token: str = "__null_token_value__"  # noqa: S105

        table = self._df._native_frame
        # NOTE: stubs fail in multiple places for `ChunkedArray`
        it = cast(
            "Iterator[pa.StringArray]",
            (table[key].cast(pa.string()) for key in self._keys),
        )
        # NOTE: stubs indicate `separator` must also be a `ChunkedArray`
        # Reality: `str` is fine
        concat_str: Incomplete = pc.binary_join_element_wise
        key_values = concat_str(
            *it, "", null_handling="replace", null_replacement=null_token
        )
        table = table.add_column(i=0, field_=col_token, column=key_values)
        for v in pc.unique(key_values):
            t = self._df._from_native_frame(
                table.filter(pc.equal(table[col_token], v)).drop([col_token])
            )
            row = t.simple_select(*self._keys).row(0)
            yield tuple(extract_py_scalar(el) for el in row), t
