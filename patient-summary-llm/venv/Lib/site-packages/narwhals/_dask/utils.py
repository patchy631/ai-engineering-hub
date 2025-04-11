from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Sequence

from narwhals._expression_parsing import evaluate_output_names_and_aliases
from narwhals._pandas_like.utils import select_columns_by_name
from narwhals.dependencies import get_pandas
from narwhals.dependencies import get_pyarrow
from narwhals.utils import Implementation
from narwhals.utils import import_dtypes_module
from narwhals.utils import isinstance_or_issubclass
from narwhals.utils import parse_version

try:
    import dask.dataframe.dask_expr as dx
except ModuleNotFoundError:  # pragma: no cover
    import dask_expr as dx

if TYPE_CHECKING:
    import dask.dataframe as dd

    from narwhals._dask.dataframe import DaskLazyFrame
    from narwhals._dask.expr import DaskExpr
    from narwhals.dtypes import DType
    from narwhals.utils import Version


def maybe_evaluate_expr(df: DaskLazyFrame, obj: DaskExpr | object) -> dx.Series | object:
    from narwhals._dask.expr import DaskExpr

    if isinstance(obj, DaskExpr):
        results = obj._call(df)
        if len(results) != 1:
            msg = "Multi-output expressions (e.g. `nw.all()` or `nw.col('a', 'b')`) not supported in this context"
            raise AssertionError(msg)
        return results[0]
    return obj


def evaluate_exprs(df: DaskLazyFrame, /, *exprs: DaskExpr) -> list[tuple[str, dx.Series]]:
    native_results: list[tuple[str, dx.Series]] = []
    for expr in exprs:
        native_series_list = expr._call(df)
        _, aliases = evaluate_output_names_and_aliases(expr, df, [])
        if len(aliases) != len(native_series_list):  # pragma: no cover
            msg = f"Internal error: got aliases {aliases}, but only got {len(native_series_list)} results"
            raise AssertionError(msg)
        native_results.extend(zip(aliases, native_series_list))
    return native_results


def align_series_full_broadcast(
    df: DaskLazyFrame, *series: dx.Series | object
) -> Sequence[dx.Series]:
    return [
        s if isinstance(s, dx.Series) else df._native_frame.assign(_tmp=s)["_tmp"]
        for s in series
    ]  # pyright: ignore[reportReturnType]


def add_row_index(
    frame: dd.DataFrame,
    name: str,
    backend_version: tuple[int, ...],
    implementation: Implementation,
) -> dd.DataFrame:
    original_cols = frame.columns
    frame = frame.assign(**{name: 1})
    return select_columns_by_name(
        frame.assign(**{name: frame[name].cumsum(method="blelloch") - 1}),
        [name, *original_cols],
        backend_version,
        implementation,
    )


def validate_comparand(lhs: dx.Series, rhs: dx.Series) -> None:
    try:
        import dask.dataframe.dask_expr as dx
    except ModuleNotFoundError:  # pragma: no cover
        import dask_expr as dx

    if not dx.expr.are_co_aligned(lhs._expr, rhs._expr):  # pragma: no cover
        # are_co_aligned is a method which cheaply checks if two Dask expressions
        # have the same index, and therefore don't require index alignment.
        # If someone only operates on a Dask DataFrame via expressions, then this
        # should always be the case: expression outputs (by definition) all come from the
        # same input dataframe, and Dask Series does not have any operations which
        # change the index. Nonetheless, we perform this safety check anyway.

        # However, we still need to carefully vet which methods we support for Dask, to
        # avoid issues where `are_co_aligned` doesn't do what we want it to do:
        # https://github.com/dask/dask-expr/issues/1112.
        msg = "Objects are not co-aligned, so this operation is not supported for Dask backend"
        raise RuntimeError(msg)


def narwhals_to_native_dtype(dtype: DType | type[DType], version: Version) -> Any:
    dtypes = import_dtypes_module(version)
    if isinstance_or_issubclass(dtype, dtypes.Float64):
        return "float64"
    if isinstance_or_issubclass(dtype, dtypes.Float32):
        return "float32"
    if isinstance_or_issubclass(dtype, dtypes.Int64):
        return "int64"
    if isinstance_or_issubclass(dtype, dtypes.Int32):
        return "int32"
    if isinstance_or_issubclass(dtype, dtypes.Int16):
        return "int16"
    if isinstance_or_issubclass(dtype, dtypes.Int8):
        return "int8"
    if isinstance_or_issubclass(dtype, dtypes.UInt64):
        return "uint64"
    if isinstance_or_issubclass(dtype, dtypes.UInt32):
        return "uint32"
    if isinstance_or_issubclass(dtype, dtypes.UInt16):
        return "uint16"
    if isinstance_or_issubclass(dtype, dtypes.UInt8):
        return "uint8"
    if isinstance_or_issubclass(dtype, dtypes.String):
        if (pd := get_pandas()) is not None and parse_version(pd) >= (2, 0, 0):
            if get_pyarrow() is not None:
                return "string[pyarrow]"
            return "string[python]"  # pragma: no cover
        return "object"  # pragma: no cover
    if isinstance_or_issubclass(dtype, dtypes.Boolean):
        return "bool"
    if isinstance_or_issubclass(dtype, dtypes.Categorical):
        return "category"
    if isinstance_or_issubclass(dtype, dtypes.Datetime):
        return "datetime64[us]"
    if isinstance_or_issubclass(dtype, dtypes.Date):
        return "date32[day][pyarrow]"
    if isinstance_or_issubclass(dtype, dtypes.Duration):
        return "timedelta64[ns]"
    if isinstance_or_issubclass(dtype, dtypes.List):  # pragma: no cover
        msg = "Converting to List dtype is not supported yet"
        return NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, dtypes.Struct):  # pragma: no cover
        msg = "Converting to Struct dtype is not supported yet"
        return NotImplementedError(msg)
    if isinstance_or_issubclass(dtype, dtypes.Array):  # pragma: no cover
        msg = "Converting to Array dtype is not supported yet"
        return NotImplementedError(msg)

    msg = f"Unknown dtype: {dtype}"  # pragma: no cover
    raise AssertionError(msg)


def name_preserving_sum(s1: dx.Series, s2: dx.Series) -> dx.Series:
    return (s1 + s2).rename(s1.name)  # pyright: ignore[reportOperatorIssue]


def name_preserving_div(s1: dx.Series, s2: dx.Series) -> dx.Series:
    return (s1 / s2).rename(s1.name)  # pyright: ignore[reportOperatorIssue]
