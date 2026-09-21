from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Literal
from typing import Sequence
from typing import cast
from typing import overload

import pyarrow as pa
import pyarrow.compute as pc

from narwhals._arrow.utils import align_series_full_broadcast
from narwhals._arrow.utils import convert_str_slice_to_int_slice
from narwhals._arrow.utils import extract_dataframe_comparand
from narwhals._arrow.utils import native_to_narwhals_dtype
from narwhals._arrow.utils import select_rows
from narwhals._expression_parsing import ExprKind
from narwhals._expression_parsing import evaluate_into_exprs
from narwhals.dependencies import is_numpy_array_1d
from narwhals.utils import Implementation
from narwhals.utils import Version
from narwhals.utils import check_column_exists
from narwhals.utils import check_column_names_are_unique
from narwhals.utils import generate_temporary_column_name
from narwhals.utils import is_sequence_but_not_str
from narwhals.utils import parse_columns_to_drop
from narwhals.utils import parse_version
from narwhals.utils import scale_bytes
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from io import BytesIO
    from pathlib import Path
    from types import ModuleType

    import pandas as pd
    import polars as pl
    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from narwhals._arrow.expr import ArrowExpr
    from narwhals._arrow.group_by import ArrowGroupBy
    from narwhals._arrow.namespace import ArrowNamespace
    from narwhals._arrow.series import ArrowSeries
    from narwhals._arrow.typing import ArrowChunkedArray
    from narwhals._arrow.typing import Indices  # type: ignore[attr-defined]
    from narwhals._arrow.typing import Mask  # type: ignore[attr-defined]
    from narwhals._arrow.typing import Order  # type: ignore[attr-defined]
    from narwhals.dtypes import DType
    from narwhals.typing import SizeUnit
    from narwhals.typing import _1DArray
    from narwhals.typing import _2DArray
    from narwhals.utils import Version

    JoinType: TypeAlias = Literal[
        "left semi",
        "right semi",
        "left anti",
        "right anti",
        "inner",
        "left outer",
        "right outer",
        "full outer",
    ]
    PromoteOptions: TypeAlias = Literal["none", "default", "permissive"]

from narwhals.typing import CompliantDataFrame
from narwhals.typing import CompliantLazyFrame


class ArrowDataFrame(CompliantDataFrame["ArrowSeries"], CompliantLazyFrame):
    # --- not in the spec ---
    def __init__(
        self: Self,
        native_dataframe: pa.Table,
        *,
        backend_version: tuple[int, ...],
        version: Version,
        validate_column_names: bool,
    ) -> None:
        if validate_column_names:
            check_column_names_are_unique(native_dataframe.column_names)
        self._native_frame = native_dataframe
        self._implementation = Implementation.PYARROW
        self._backend_version = backend_version
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)

    def __narwhals_namespace__(self: Self) -> ArrowNamespace:
        from narwhals._arrow.namespace import ArrowNamespace

        return ArrowNamespace(
            backend_version=self._backend_version, version=self._version
        )

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.PYARROW:
            return self._implementation.to_native_namespace()

        msg = f"Expected pyarrow, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def __narwhals_dataframe__(self: Self) -> Self:
        return self

    def __narwhals_lazyframe__(self: Self) -> Self:
        return self

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame,
            backend_version=self._backend_version,
            version=version,
            validate_column_names=False,
        )

    def _from_native_frame(
        self: Self, df: pa.Table, *, validate_column_names: bool = True
    ) -> Self:
        return self.__class__(
            df,
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=validate_column_names,
        )

    @property
    def shape(self: Self) -> tuple[int, int]:
        return self._native_frame.shape

    def __len__(self: Self) -> int:
        return len(self._native_frame)

    def row(self: Self, index: int) -> tuple[Any, ...]:
        return tuple(col[index] for col in self._native_frame.itercolumns())

    @overload
    def rows(self: Self, *, named: Literal[True]) -> list[dict[str, Any]]: ...

    @overload
    def rows(self: Self, *, named: Literal[False]) -> list[tuple[Any, ...]]: ...

    @overload
    def rows(
        self: Self, *, named: bool
    ) -> list[tuple[Any, ...]] | list[dict[str, Any]]: ...

    def rows(self: Self, *, named: bool) -> list[tuple[Any, ...]] | list[dict[str, Any]]:
        if not named:
            return list(self.iter_rows(named=False, buffer_size=512))  # type: ignore[return-value]
        return self._native_frame.to_pylist()

    def iter_columns(self) -> Iterator[ArrowSeries]:
        from narwhals._arrow.series import ArrowSeries

        for name, series in zip(self.columns, self._native_frame.itercolumns()):
            yield ArrowSeries(
                series,
                name=name,
                backend_version=self._backend_version,
                version=self._version,
            )

    _iter_columns = iter_columns

    def iter_rows(
        self: Self, *, named: bool, buffer_size: int
    ) -> Iterator[tuple[Any, ...]] | Iterator[dict[str, Any]]:
        df = self._native_frame
        num_rows = df.num_rows

        if not named:
            for i in range(0, num_rows, buffer_size):
                rows = df[i : i + buffer_size].to_pydict().values()
                yield from zip(*rows)
        else:
            for i in range(0, num_rows, buffer_size):
                yield from df[i : i + buffer_size].to_pylist()

    def get_column(self: Self, name: str) -> ArrowSeries:
        from narwhals._arrow.series import ArrowSeries

        if not isinstance(name, str):
            msg = f"Expected str, got: {type(name)}"
            raise TypeError(msg)

        return ArrowSeries(
            self._native_frame[name],
            name=name,
            backend_version=self._backend_version,
            version=self._version,
        )

    def __array__(self: Self, dtype: Any, *, copy: bool | None) -> _2DArray:
        return self._native_frame.__array__(dtype, copy=copy)

    @overload
    def __getitem__(  # type: ignore[overload-overlap, unused-ignore]
        self: Self, item: str | tuple[slice | Sequence[int] | _1DArray, int | str]
    ) -> ArrowSeries: ...
    @overload
    def __getitem__(
        self: Self,
        item: (
            int
            | slice
            | Sequence[int]
            | Sequence[str]
            | _1DArray
            | tuple[
                slice | Sequence[int] | _1DArray, slice | Sequence[int] | Sequence[str]
            ]
        ),
    ) -> Self: ...
    def __getitem__(
        self: Self,
        item: (
            str
            | int
            | slice
            | Sequence[int]
            | Sequence[str]
            | _1DArray
            | tuple[slice | Sequence[int] | _1DArray, int | str]
            | tuple[
                slice | Sequence[int] | _1DArray, slice | Sequence[int] | Sequence[str]
            ]
        ),
    ) -> ArrowSeries | Self:
        if isinstance(item, tuple):
            item = tuple(list(i) if is_sequence_but_not_str(i) else i for i in item)  # pyright: ignore[reportAssignmentType]

        if isinstance(item, str):
            from narwhals._arrow.series import ArrowSeries

            return ArrowSeries(
                self._native_frame[item],
                name=item,
                backend_version=self._backend_version,
                version=self._version,
            )
        elif (
            isinstance(item, tuple)
            and len(item) == 2
            and is_sequence_but_not_str(item[1])
            and not isinstance(item[0], str)
        ):
            if len(item[1]) == 0:
                # Return empty dataframe
                return self._from_native_frame(self._native_frame.slice(0, 0).select([]))
            selected_rows = select_rows(self._native_frame, item[0])
            return self._from_native_frame(selected_rows.select(cast("Indices", item[1])))

        elif isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[1], slice):
                columns = self.columns
                indices = cast("Indices", item[0])
                if item[1] == slice(None):
                    if isinstance(item[0], Sequence) and len(item[0]) == 0:
                        return self._from_native_frame(self._native_frame.slice(0, 0))
                    return self._from_native_frame(self._native_frame.take(indices))
                if isinstance(item[1].start, str) or isinstance(item[1].stop, str):
                    start, stop, step = convert_str_slice_to_int_slice(item[1], columns)
                    return self._from_native_frame(
                        self._native_frame.take(indices).select(columns[start:stop:step])
                    )
                if isinstance(item[1].start, int) or isinstance(item[1].stop, int):
                    return self._from_native_frame(
                        self._native_frame.take(indices).select(
                            columns[item[1].start : item[1].stop : item[1].step]
                        )
                    )
                msg = f"Expected slice of integers or strings, got: {type(item[1])}"  # pragma: no cover
                raise TypeError(msg)  # pragma: no cover
            from narwhals._arrow.series import ArrowSeries

            # PyArrow columns are always strings
            col_name = (
                item[1]
                if isinstance(item[1], str)
                else self.columns[cast("int", item[1])]
            )
            if isinstance(item[0], str):  # pragma: no cover
                msg = "Can not slice with tuple with the first element as a str"
                raise TypeError(msg)
            if (isinstance(item[0], slice)) and (item[0] == slice(None)):
                return ArrowSeries(
                    self._native_frame[col_name],
                    name=col_name,
                    backend_version=self._backend_version,
                    version=self._version,
                )
            selected_rows = select_rows(self._native_frame, item[0])
            return ArrowSeries(
                selected_rows[col_name],
                name=col_name,
                backend_version=self._backend_version,
                version=self._version,
            )

        elif isinstance(item, slice):
            if item.step is not None and item.step != 1:
                msg = "Slicing with step is not supported on PyArrow tables"
                raise NotImplementedError(msg)
            columns = self.columns
            if isinstance(item.start, str) or isinstance(item.stop, str):
                start, stop, step = convert_str_slice_to_int_slice(item, columns)
                return self._from_native_frame(
                    self._native_frame.select(columns[start:stop:step])
                )
            start = item.start or 0
            stop = item.stop if item.stop is not None else len(self._native_frame)
            return self._from_native_frame(self._native_frame.slice(start, stop - start))

        elif isinstance(item, Sequence) or is_numpy_array_1d(item):
            if (
                isinstance(item, Sequence)
                and all(isinstance(x, str) for x in item)
                and len(item) > 0
            ):
                return self._from_native_frame(
                    self._native_frame.select(cast("Indices", item))
                )
            if isinstance(item, Sequence) and len(item) == 0:
                return self._from_native_frame(self._native_frame.slice(0, 0))
            return self._from_native_frame(self._native_frame.take(cast("Indices", item)))

        else:  # pragma: no cover
            msg = f"Expected str or slice, got: {type(item)}"
            raise TypeError(msg)

    @property
    def schema(self: Self) -> dict[str, DType]:
        schema = self._native_frame.schema
        return {
            name: native_to_narwhals_dtype(dtype, self._version)
            for name, dtype in zip(schema.names, schema.types)
        }

    def collect_schema(self: Self) -> dict[str, DType]:
        return self.schema

    def estimated_size(self: Self, unit: SizeUnit) -> int | float:
        sz = self._native_frame.nbytes
        return scale_bytes(sz, unit)

    @property
    def columns(self: Self) -> list[str]:
        return self._native_frame.schema.names

    def simple_select(self, *column_names: str) -> Self:
        return self._from_native_frame(
            self._native_frame.select(list(column_names)), validate_column_names=False
        )

    def aggregate(self: ArrowDataFrame, *exprs: ArrowExpr) -> ArrowDataFrame:
        return self.select(*exprs)

    def select(self: ArrowDataFrame, *exprs: ArrowExpr) -> ArrowDataFrame:
        new_series = evaluate_into_exprs(self, *exprs)
        if not new_series:
            # return empty dataframe, like Polars does
            return self._from_native_frame(
                self._native_frame.__class__.from_arrays([]), validate_column_names=False
            )
        names = [s.name for s in new_series]
        reshaped = align_series_full_broadcast(*new_series)
        df = pa.Table.from_arrays([s._native_series for s in reshaped], names=names)
        return self._from_native_frame(df, validate_column_names=True)

    def with_columns(self: ArrowDataFrame, *exprs: ArrowExpr) -> ArrowDataFrame:
        native_frame = self._native_frame
        new_columns = evaluate_into_exprs(self, *exprs)

        length = len(self)
        columns = self.columns

        for col_value in new_columns:
            col_name = col_value.name

            column = extract_dataframe_comparand(
                length=length, other=col_value, backend_version=self._backend_version
            )
            native_frame = (
                native_frame.set_column(
                    columns.index(col_name),
                    field_=col_name,
                    column=column,  # type: ignore[arg-type]
                )
                if col_name in columns
                else native_frame.append_column(field_=col_name, column=column)
            )

        return self._from_native_frame(native_frame, validate_column_names=False)

    def group_by(self: Self, *keys: str, drop_null_keys: bool) -> ArrowGroupBy:
        from narwhals._arrow.group_by import ArrowGroupBy

        return ArrowGroupBy(self, list(keys), drop_null_keys=drop_null_keys)

    def join(
        self: Self,
        other: Self,
        *,
        how: Literal["left", "inner", "cross", "anti", "semi"],
        left_on: Sequence[str] | None,
        right_on: Sequence[str] | None,
        suffix: str,
    ) -> Self:
        how_to_join_map: dict[str, JoinType] = {
            "anti": "left anti",
            "semi": "left semi",
            "inner": "inner",
            "left": "left outer",
        }

        if how == "cross":
            plx = self.__narwhals_namespace__()
            key_token = generate_temporary_column_name(
                n_bytes=8, columns=[*self.columns, *other.columns]
            )

            return self._from_native_frame(
                self.with_columns(
                    plx.lit(0, None).alias(key_token).broadcast(ExprKind.LITERAL)
                )
                ._native_frame.join(
                    other.with_columns(
                        plx.lit(0, None).alias(key_token).broadcast(ExprKind.LITERAL)
                    )._native_frame,
                    keys=key_token,
                    right_keys=key_token,
                    join_type="inner",
                    right_suffix=suffix,
                )
                .drop([key_token]),
            )

        return self._from_native_frame(
            self._native_frame.join(
                other._native_frame,
                keys=left_on or [],  # type: ignore[arg-type]
                right_keys=right_on,  # type: ignore[arg-type]
                join_type=how_to_join_map[how],
                right_suffix=suffix,
            ),
        )

    def join_asof(
        self: Self,
        other: Self,
        *,
        left_on: str | None,
        right_on: str | None,
        by_left: list[str] | None,
        by_right: list[str] | None,
        strategy: Literal["backward", "forward", "nearest"],
        suffix: str,
    ) -> Self:
        msg = "join_asof is not yet supported on PyArrow tables"  # pragma: no cover
        raise NotImplementedError(msg)

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        to_drop = parse_columns_to_drop(
            compliant_frame=self, columns=columns, strict=strict
        )
        return self._from_native_frame(
            self._native_frame.drop(to_drop), validate_column_names=False
        )

    def drop_nulls(self: ArrowDataFrame, subset: list[str] | None) -> ArrowDataFrame:
        if subset is None:
            return self._from_native_frame(
                self._native_frame.drop_null(), validate_column_names=False
            )
        plx = self.__narwhals_namespace__()
        return self.filter(~plx.any_horizontal(plx.col(*subset).is_null()))

    def sort(
        self: Self,
        *by: str,
        descending: bool | Sequence[bool],
        nulls_last: bool,
    ) -> Self:
        df = self._native_frame

        if isinstance(descending, bool):
            order: Order = "descending" if descending else "ascending"
            sorting: list[tuple[str, Order]] = [(key, order) for key in by]
        else:
            sorting = [
                (key, "descending" if is_descending else "ascending")
                for key, is_descending in zip(by, descending)
            ]

        null_placement = "at_end" if nulls_last else "at_start"

        return self._from_native_frame(
            df.sort_by(sorting, null_placement=null_placement),
            validate_column_names=False,
        )

    def to_pandas(self: Self) -> pd.DataFrame:
        return self._native_frame.to_pandas()

    def to_polars(self: Self) -> pl.DataFrame:
        import polars as pl  # ignore-banned-import

        return pl.from_arrow(self._native_frame)  # type: ignore[return-value]

    def to_numpy(self: Self) -> _2DArray:
        import numpy as np  # ignore-banned-import

        arr: Any = np.column_stack([col.to_numpy() for col in self._native_frame.columns])
        return arr

    @overload
    def to_dict(self: Self, *, as_series: Literal[True]) -> dict[str, ArrowSeries]: ...

    @overload
    def to_dict(self: Self, *, as_series: Literal[False]) -> dict[str, list[Any]]: ...

    def to_dict(
        self: Self, *, as_series: bool
    ) -> dict[str, ArrowSeries] | dict[str, list[Any]]:
        df = self._native_frame

        names_and_values = zip(df.column_names, df.columns)
        if as_series:
            from narwhals._arrow.series import ArrowSeries

            return {
                name: ArrowSeries(
                    col,
                    name=name,
                    backend_version=self._backend_version,
                    version=self._version,
                )
                for name, col in names_and_values
            }
        else:
            return {name: col.to_pylist() for name, col in names_and_values}

    def with_row_index(self: Self, name: str) -> Self:
        df = self._native_frame
        cols = self.columns

        row_indices = pa.array(range(df.num_rows))
        return self._from_native_frame(
            df.append_column(name, row_indices).select([name, *cols])
        )

    def filter(
        self: ArrowDataFrame, predicate: ArrowExpr | list[bool | None]
    ) -> ArrowDataFrame:
        if isinstance(predicate, list):
            mask_native: Mask | ArrowChunkedArray = predicate
        else:
            # `[0]` is safe as the predicate's expression only returns a single column
            mask_native = evaluate_into_exprs(self, predicate)[0]._native_series
        return self._from_native_frame(
            self._native_frame.filter(mask_native),  # pyright: ignore[reportArgumentType]
            validate_column_names=False,
        )

    def head(self: Self, n: int) -> Self:
        df = self._native_frame
        if n >= 0:
            return self._from_native_frame(df.slice(0, n), validate_column_names=False)
        else:
            num_rows = df.num_rows
            return self._from_native_frame(
                df.slice(0, max(0, num_rows + n)), validate_column_names=False
            )

    def tail(self: Self, n: int) -> Self:
        df = self._native_frame
        if n >= 0:
            num_rows = df.num_rows
            return self._from_native_frame(
                df.slice(max(0, num_rows - n)), validate_column_names=False
            )
        else:
            return self._from_native_frame(df.slice(abs(n)), validate_column_names=False)

    def lazy(self: Self, *, backend: Implementation | None = None) -> CompliantLazyFrame:
        from narwhals.utils import parse_version

        if backend is None:
            return self
        elif backend is Implementation.DUCKDB:
            import duckdb  # ignore-banned-import

            from narwhals._duckdb.dataframe import DuckDBLazyFrame

            df = self._native_frame  # noqa: F841
            return DuckDBLazyFrame(
                df=duckdb.table("df"),
                backend_version=parse_version(duckdb),
                version=self._version,
                validate_column_names=False,
            )
        elif backend is Implementation.POLARS:
            import polars as pl  # ignore-banned-import

            from narwhals._polars.dataframe import PolarsLazyFrame

            return PolarsLazyFrame(
                df=pl.from_arrow(self._native_frame).lazy(),  # type: ignore[union-attr]
                backend_version=parse_version(pl),
                version=self._version,
            )
        elif backend is Implementation.DASK:
            import dask  # ignore-banned-import
            import dask.dataframe as dd  # ignore-banned-import

            from narwhals._dask.dataframe import DaskLazyFrame

            return DaskLazyFrame(
                native_dataframe=dd.from_pandas(self._native_frame.to_pandas()),
                backend_version=parse_version(dask),
                version=self._version,
                validate_column_names=False,
            )
        raise AssertionError  # pragma: no cover

    def collect(
        self: Self,
        backend: Implementation | None,
        **kwargs: Any,
    ) -> CompliantDataFrame[Any]:
        if backend is Implementation.PYARROW or backend is None:
            from narwhals._arrow.dataframe import ArrowDataFrame

            return ArrowDataFrame(
                native_dataframe=self._native_frame,
                backend_version=self._backend_version,
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.PANDAS:
            import pandas as pd  # ignore-banned-import

            from narwhals._pandas_like.dataframe import PandasLikeDataFrame

            return PandasLikeDataFrame(
                native_dataframe=self._native_frame.to_pandas(),
                implementation=Implementation.PANDAS,
                backend_version=parse_version(pd),
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.POLARS:
            import polars as pl  # ignore-banned-import

            from narwhals._polars.dataframe import PolarsDataFrame

            return PolarsDataFrame(
                df=pl.from_arrow(self._native_frame),  # type: ignore[arg-type]
                backend_version=parse_version(pl),
                version=self._version,
            )

        msg = f"Unsupported `backend` value: {backend}"  # pragma: no cover
        raise AssertionError(msg)  # pragma: no cover

    def clone(self: Self) -> Self:
        msg = "clone is not yet supported on PyArrow tables"
        raise NotImplementedError(msg)

    def item(self: Self, row: int | None, column: int | str | None) -> Any:
        from narwhals._arrow.series import maybe_extract_py_scalar

        if row is None and column is None:
            if self.shape != (1, 1):
                msg = (
                    "can only call `.item()` if the dataframe is of shape (1, 1),"
                    " or if explicit row/col values are provided;"
                    f" frame has shape {self.shape!r}"
                )
                raise ValueError(msg)
            return maybe_extract_py_scalar(
                self._native_frame[0][0], return_py_scalar=True
            )

        elif row is None or column is None:
            msg = "cannot call `.item()` with only one of `row` or `column`"
            raise ValueError(msg)

        _col = self.columns.index(column) if isinstance(column, str) else column
        return maybe_extract_py_scalar(
            self._native_frame[_col][row], return_py_scalar=True
        )

    def rename(self: Self, mapping: dict[str, str]) -> Self:
        df = self._native_frame
        new_cols = [mapping.get(c, c) for c in df.column_names]
        return self._from_native_frame(df.rename_columns(new_cols))

    def write_parquet(self: Self, file: str | Path | BytesIO) -> None:
        import pyarrow.parquet as pp

        pp.write_table(self._native_frame, file)

    @overload
    def write_csv(self: Self, file: None) -> str: ...

    @overload
    def write_csv(self: Self, file: str | Path | BytesIO) -> None: ...

    def write_csv(self: Self, file: str | Path | BytesIO | None) -> str | None:
        import pyarrow.csv as pa_csv

        pa_table = self._native_frame
        if file is None:
            csv_buffer = pa.BufferOutputStream()
            pa_csv.write_csv(pa_table, csv_buffer)
            return csv_buffer.getvalue().to_pybytes().decode()
        pa_csv.write_csv(pa_table, file)
        return None

    def is_unique(self: Self) -> ArrowSeries:
        from narwhals._arrow.series import ArrowSeries

        col_token = generate_temporary_column_name(n_bytes=8, columns=self.columns)
        row_index = pa.array(range(len(self)))
        keep_idx = (
            self._native_frame.append_column(col_token, row_index)
            .group_by(self.columns)
            .aggregate([(col_token, "min"), (col_token, "max")])
        )
        return ArrowSeries(
            pa.chunked_array(
                pc.and_(
                    pc.is_in(row_index, keep_idx[f"{col_token}_min"]),
                    pc.is_in(row_index, keep_idx[f"{col_token}_max"]),
                )
            ),
            name="",
            backend_version=self._backend_version,
            version=self._version,
        )

    def unique(
        self: ArrowDataFrame,
        subset: list[str] | None,
        *,
        keep: Literal["any", "first", "last", "none"],
        maintain_order: bool | None = None,
    ) -> ArrowDataFrame:
        # The param `maintain_order` is only here for compatibility with the Polars API
        # and has no effect on the output.
        import numpy as np  # ignore-banned-import

        df = self._native_frame
        check_column_exists(self.columns, subset)
        subset = subset or self.columns

        if keep in {"any", "first", "last"}:
            agg_func_map = {"any": "min", "first": "min", "last": "max"}

            agg_func = agg_func_map[keep]
            col_token = generate_temporary_column_name(n_bytes=8, columns=self.columns)
            keep_idx_native = (
                df.append_column(col_token, pa.array(np.arange(len(self))))
                .group_by(subset)
                .aggregate([(col_token, agg_func)])
                .column(f"{col_token}_{agg_func}")
            )
            indices = cast("Indices", keep_idx_native)
            return self._from_native_frame(df.take(indices), validate_column_names=False)

        keep_idx = self.simple_select(*subset).is_unique()
        plx = self.__narwhals_namespace__()
        return self.filter(plx._create_expr_from_series(keep_idx))

    def gather_every(self: Self, n: int, offset: int) -> Self:
        return self._from_native_frame(
            self._native_frame[offset::n], validate_column_names=False
        )

    def to_arrow(self: Self) -> pa.Table:
        return self._native_frame

    def sample(
        self: Self,
        n: int | None,
        *,
        fraction: float | None,
        with_replacement: bool,
        seed: int | None,
    ) -> Self:
        import numpy as np  # ignore-banned-import

        frame = self._native_frame
        num_rows = len(self)
        if n is None and fraction is not None:
            n = int(num_rows * fraction)

        rng = np.random.default_rng(seed=seed)
        idx = np.arange(0, num_rows)
        mask = rng.choice(idx, size=n, replace=with_replacement)

        return self._from_native_frame(pc.take(frame, mask), validate_column_names=False)  # type: ignore[call-overload, unused-ignore]

    def unpivot(
        self: Self,
        on: list[str] | None,
        index: list[str] | None,
        variable_name: str,
        value_name: str,
    ) -> Self:
        native_frame = self._native_frame
        n_rows = len(self)

        index_: list[str] = [] if index is None else index
        on_: list[str] = (
            [c for c in self.columns if c not in index_] if on is None else on
        )
        concat = (
            partial(pa.concat_tables, promote_options="permissive")
            if self._backend_version >= (14, 0, 0)
            else pa.concat_tables
        )
        names = [*index_, variable_name, value_name]
        return self._from_native_frame(
            concat(
                [
                    pa.Table.from_arrays(
                        [
                            *(native_frame.column(idx_col) for idx_col in index_),
                            cast(
                                "ArrowChunkedArray",
                                pa.array([on_col] * n_rows, pa.string()),
                            ),
                            native_frame.column(on_col),
                        ],
                        names=names,
                    )
                    for on_col in on_
                ]
            )
        )
        # TODO(Unassigned): Even with promote_options="permissive", pyarrow does not
        # upcast numeric to non-numeric (e.g. string) datatypes
