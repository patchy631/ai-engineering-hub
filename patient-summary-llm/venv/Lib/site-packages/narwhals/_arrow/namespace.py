from __future__ import annotations

import operator
from functools import partial
from functools import reduce
from itertools import chain
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Container
from typing import Iterable
from typing import Literal
from typing import Sequence

import pyarrow as pa
import pyarrow.compute as pc

from narwhals._arrow.dataframe import ArrowDataFrame
from narwhals._arrow.expr import ArrowExpr
from narwhals._arrow.selectors import ArrowSelectorNamespace
from narwhals._arrow.series import ArrowSeries
from narwhals._arrow.utils import align_series_full_broadcast
from narwhals._arrow.utils import diagonal_concat
from narwhals._arrow.utils import extract_dataframe_comparand
from narwhals._arrow.utils import horizontal_concat
from narwhals._arrow.utils import nulls_like
from narwhals._arrow.utils import vertical_concat
from narwhals._expression_parsing import combine_alias_output_names
from narwhals._expression_parsing import combine_evaluate_output_names
from narwhals.typing import CompliantNamespace
from narwhals.utils import Implementation
from narwhals.utils import exclude_column_names
from narwhals.utils import get_column_names
from narwhals.utils import import_dtypes_module
from narwhals.utils import passthrough_column_names

if TYPE_CHECKING:
    from typing import Callable

    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from narwhals._arrow.typing import Incomplete
    from narwhals._arrow.typing import IntoArrowExpr
    from narwhals.dtypes import DType
    from narwhals.utils import Version

    _Scalar: TypeAlias = Any


class ArrowNamespace(CompliantNamespace[ArrowDataFrame, ArrowSeries]):
    def _create_expr_from_callable(
        self: Self,
        func: Callable[[ArrowDataFrame], Sequence[ArrowSeries]],
        *,
        depth: int,
        function_name: str,
        evaluate_output_names: Callable[[ArrowDataFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        call_kwargs: dict[str, Any] | None = None,
    ) -> ArrowExpr:
        from narwhals._arrow.expr import ArrowExpr

        return ArrowExpr(
            func,
            depth=depth,
            function_name=function_name,
            evaluate_output_names=evaluate_output_names,
            alias_output_names=alias_output_names,
            backend_version=self._backend_version,
            version=self._version,
            call_kwargs=call_kwargs,
        )

    def _create_expr_from_series(self: Self, series: ArrowSeries) -> ArrowExpr:
        from narwhals._arrow.expr import ArrowExpr

        return ArrowExpr(
            lambda _df: [series],
            depth=0,
            function_name="series",
            evaluate_output_names=lambda _df: [series.name],
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )

    def _create_series_from_scalar(
        self: Self, value: Any, *, reference_series: ArrowSeries
    ) -> ArrowSeries:
        from narwhals._arrow.series import ArrowSeries

        if self._backend_version < (13,) and hasattr(value, "as_py"):
            value = value.as_py()
        return ArrowSeries._from_iterable(
            [value],
            name=reference_series.name,
            backend_version=self._backend_version,
            version=self._version,
        )

    def _create_compliant_series(self: Self, value: Any) -> ArrowSeries:
        from narwhals._arrow.series import ArrowSeries

        return ArrowSeries(
            native_series=pa.chunked_array([value]),
            name="",
            backend_version=self._backend_version,
            version=self._version,
        )

    # --- not in spec ---
    def __init__(
        self: Self, *, backend_version: tuple[int, ...], version: Version
    ) -> None:
        self._backend_version = backend_version
        self._implementation = Implementation.PYARROW
        self._version = version

    # --- selection ---
    def col(self: Self, *column_names: str) -> ArrowExpr:
        from narwhals._arrow.expr import ArrowExpr

        return ArrowExpr.from_column_names(
            passthrough_column_names(column_names),
            function_name="col",
            backend_version=self._backend_version,
            version=self._version,
        )

    def exclude(self: Self, excluded_names: Container[str]) -> ArrowExpr:
        return ArrowExpr.from_column_names(
            partial(exclude_column_names, names=excluded_names),
            function_name="exclude",
            backend_version=self._backend_version,
            version=self._version,
        )

    def nth(self: Self, *column_indices: int) -> ArrowExpr:
        from narwhals._arrow.expr import ArrowExpr

        return ArrowExpr.from_column_indices(
            *column_indices, backend_version=self._backend_version, version=self._version
        )

    def len(self: Self) -> ArrowExpr:
        # coverage bug? this is definitely hit
        return ArrowExpr(  # pragma: no cover
            lambda df: [
                ArrowSeries._from_iterable(
                    [len(df._native_frame)],
                    name="len",
                    backend_version=self._backend_version,
                    version=self._version,
                )
            ],
            depth=0,
            function_name="len",
            evaluate_output_names=lambda _df: ["len"],
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )

    def all(self: Self) -> ArrowExpr:
        return ArrowExpr.from_column_names(
            get_column_names,
            function_name="all",
            backend_version=self._backend_version,
            version=self._version,
        )

    def lit(self: Self, value: Any, dtype: DType | None) -> ArrowExpr:
        def _lit_arrow_series(_: ArrowDataFrame) -> ArrowSeries:
            arrow_series = ArrowSeries._from_iterable(
                data=[value],
                name="literal",
                backend_version=self._backend_version,
                version=self._version,
            )
            if dtype:
                return arrow_series.cast(dtype)
            return arrow_series

        return ArrowExpr(
            lambda df: [_lit_arrow_series(df)],
            depth=0,
            function_name="lit",
            evaluate_output_names=lambda _df: ["literal"],
            alias_output_names=None,
            backend_version=self._backend_version,
            version=self._version,
        )

    def all_horizontal(self: Self, *exprs: ArrowExpr) -> ArrowExpr:
        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            series = chain.from_iterable(expr(df) for expr in exprs)
            return [reduce(operator.and_, align_series_full_broadcast(*series))]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="all_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def any_horizontal(self: Self, *exprs: ArrowExpr) -> ArrowExpr:
        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            series = chain.from_iterable(expr(df) for expr in exprs)
            return [reduce(operator.or_, align_series_full_broadcast(*series))]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="any_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def sum_horizontal(self: Self, *exprs: ArrowExpr) -> ArrowExpr:
        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            it = chain.from_iterable(expr(df) for expr in exprs)
            series = (s.fill_null(0, strategy=None, limit=None) for s in it)
            return [reduce(operator.add, align_series_full_broadcast(*series))]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="sum_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def mean_horizontal(self: Self, *exprs: ArrowExpr) -> IntoArrowExpr:
        dtypes = import_dtypes_module(self._version)

        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            expr_results = list(chain.from_iterable(expr(df) for expr in exprs))
            series = align_series_full_broadcast(
                *(s.fill_null(0, strategy=None, limit=None) for s in expr_results)
            )
            non_na = align_series_full_broadcast(
                *(1 - s.is_null().cast(dtypes.Int64()) for s in expr_results)
            )
            return [reduce(operator.add, series) / reduce(operator.add, non_na)]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="mean_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def min_horizontal(self: Self, *exprs: ArrowExpr) -> ArrowExpr:
        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            init_series, *series = list(chain.from_iterable(expr(df) for expr in exprs))
            init_series, *series = align_series_full_broadcast(init_series, *series)
            # NOTE: Stubs copy the wrong signature https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L963
            min_element_wise: Incomplete = pc.min_element_wise
            native_series = reduce(
                min_element_wise,
                [s._native_series for s in series],
                init_series._native_series,
            )
            return [
                ArrowSeries(
                    native_series,
                    name=init_series.name,
                    backend_version=self._backend_version,
                    version=self._version,
                )
            ]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="min_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def max_horizontal(self: Self, *exprs: ArrowExpr) -> ArrowExpr:
        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            init_series, *series = list(chain.from_iterable(expr(df) for expr in exprs))
            init_series, *series = align_series_full_broadcast(init_series, *series)
            # NOTE: stubs are missing `ChunkedArray` support
            # https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L948-L954
            max_element_wise: Incomplete = pc.max_element_wise
            native_series = reduce(
                max_element_wise,
                [s._native_series for s in series],
                init_series._native_series,
            )
            return [
                ArrowSeries(
                    native_series,
                    name=init_series.name,
                    backend_version=self._backend_version,
                    version=self._version,
                )
            ]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="max_horizontal",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )

    def concat(
        self: Self,
        items: Iterable[ArrowDataFrame],
        *,
        how: Literal["horizontal", "vertical", "diagonal"],
    ) -> ArrowDataFrame:
        dfs = [item._native_frame for item in items]

        if not dfs:
            msg = "No dataframes to concatenate"  # pragma: no cover
            raise AssertionError(msg)

        if how == "horizontal":
            result_table = horizontal_concat(dfs)
        elif how == "vertical":
            result_table = vertical_concat(dfs)
        elif how == "diagonal":
            result_table = diagonal_concat(dfs, self._backend_version)
        else:
            raise NotImplementedError

        return ArrowDataFrame(
            result_table,
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=True,
        )

    @property
    def selectors(self: Self) -> ArrowSelectorNamespace:
        return ArrowSelectorNamespace(self)

    def when(self: Self, predicate: ArrowExpr) -> ArrowWhen:
        return ArrowWhen(predicate, self._backend_version, version=self._version)

    def concat_str(
        self: Self,
        *exprs: ArrowExpr,
        separator: str,
        ignore_nulls: bool,
    ) -> ArrowExpr:
        dtypes = import_dtypes_module(self._version)

        def func(df: ArrowDataFrame) -> list[ArrowSeries]:
            compliant_series_list = align_series_full_broadcast(
                *(chain.from_iterable(expr.cast(dtypes.String())(df) for expr in exprs))
            )
            null_handling: Literal["skip", "emit_null"] = (
                "skip" if ignore_nulls else "emit_null"
            )
            it = (s._native_series for s in compliant_series_list)
            # NOTE: stubs indicate `separator` must also be a `ChunkedArray`
            # Reality: `str` is fine
            concat_str: Incomplete = pc.binary_join_element_wise
            return [
                ArrowSeries(
                    native_series=concat_str(*it, separator, null_handling=null_handling),
                    name=compliant_series_list[0].name,
                    backend_version=self._backend_version,
                    version=self._version,
                )
            ]

        return self._create_expr_from_callable(
            func=func,
            depth=max(x._depth for x in exprs) + 1,
            function_name="concat_str",
            evaluate_output_names=combine_evaluate_output_names(*exprs),
            alias_output_names=combine_alias_output_names(*exprs),
        )


class ArrowWhen:
    def __init__(
        self: Self,
        condition: ArrowExpr,
        backend_version: tuple[int, ...],
        then_value: ArrowExpr | _Scalar = None,
        otherwise_value: ArrowExpr | _Scalar = None,
        *,
        version: Version,
    ) -> None:
        self._backend_version = backend_version
        self._condition: ArrowExpr = condition
        self._then_value: ArrowExpr | _Scalar = then_value
        self._otherwise_value: ArrowExpr | _Scalar = otherwise_value
        self._version = version

    def __call__(self: Self, df: ArrowDataFrame) -> Sequence[ArrowSeries]:
        plx = df.__narwhals_namespace__()
        condition = self._condition(df)[0]
        condition_native = condition._native_series

        if isinstance(self._then_value, ArrowExpr):
            value_series = self._then_value(df)[0]
        else:
            value_series = plx._create_series_from_scalar(
                self._then_value, reference_series=condition.alias("literal")
            )
            value_series._broadcast = True
        value_series_native = extract_dataframe_comparand(
            len(df), value_series, self._backend_version
        )

        if self._otherwise_value is None:
            otherwise_null = nulls_like(len(condition_native), value_series)
            return [
                value_series._from_native_series(
                    pc.if_else(condition_native, value_series_native, otherwise_null)
                )
            ]
        if isinstance(self._otherwise_value, ArrowExpr):
            otherwise_series = self._otherwise_value(df)[0]
        else:
            native_result = pc.if_else(
                condition_native, value_series_native, self._otherwise_value
            )
            return [value_series._from_native_series(native_result)]

        otherwise_series_native = extract_dataframe_comparand(
            len(df), otherwise_series, self._backend_version
        )
        return [
            value_series._from_native_series(
                pc.if_else(condition_native, value_series_native, otherwise_series_native)
            )
        ]

    def then(self: Self, value: ArrowExpr | ArrowSeries | _Scalar) -> ArrowThen:
        self._then_value = value

        return ArrowThen(
            self,
            depth=0,
            function_name="whenthen",
            evaluate_output_names=getattr(
                value, "_evaluate_output_names", lambda _df: ["literal"]
            ),
            alias_output_names=getattr(value, "_alias_output_names", None),
            backend_version=self._backend_version,
            version=self._version,
        )


class ArrowThen(ArrowExpr):
    def __init__(
        self: Self,
        call: ArrowWhen,
        *,
        depth: int,
        function_name: str,
        evaluate_output_names: Callable[[ArrowDataFrame], Sequence[str]],
        alias_output_names: Callable[[Sequence[str]], Sequence[str]] | None,
        backend_version: tuple[int, ...],
        version: Version,
        call_kwargs: dict[str, Any] | None = None,
    ) -> None:
        self._backend_version = backend_version
        self._version = version
        self._call: ArrowWhen = call
        self._depth = depth
        self._function_name = function_name
        self._evaluate_output_names = evaluate_output_names
        self._alias_output_names = alias_output_names
        self._call_kwargs = call_kwargs or {}

    def otherwise(self: Self, value: ArrowExpr | ArrowSeries | _Scalar) -> ArrowExpr:
        self._call._otherwise_value = value
        self._function_name = "whenotherwise"
        return self
