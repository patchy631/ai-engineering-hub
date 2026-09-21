from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Literal
from typing import Sequence
from typing import cast
from typing import overload

import numpy as np

from narwhals._expression_parsing import evaluate_into_exprs
from narwhals._pandas_like.series import PANDAS_TO_NUMPY_DTYPE_MISSING
from narwhals._pandas_like.series import PandasLikeSeries
from narwhals._pandas_like.utils import align_series_full_broadcast
from narwhals._pandas_like.utils import check_column_names_are_unique
from narwhals._pandas_like.utils import convert_str_slice_to_int_slice
from narwhals._pandas_like.utils import create_compliant_series
from narwhals._pandas_like.utils import extract_dataframe_comparand
from narwhals._pandas_like.utils import horizontal_concat
from narwhals._pandas_like.utils import native_to_narwhals_dtype
from narwhals._pandas_like.utils import object_native_to_narwhals_dtype
from narwhals._pandas_like.utils import pivot_table
from narwhals._pandas_like.utils import rename
from narwhals._pandas_like.utils import select_columns_by_name
from narwhals.dependencies import is_numpy_array_1d
from narwhals.exceptions import InvalidOperationError
from narwhals.utils import Implementation
from narwhals.utils import check_column_exists
from narwhals.utils import generate_temporary_column_name
from narwhals.utils import import_dtypes_module
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

    from narwhals._pandas_like.expr import PandasLikeExpr
    from narwhals._pandas_like.group_by import PandasLikeGroupBy
    from narwhals._pandas_like.namespace import PandasLikeNamespace
    from narwhals.dtypes import DType
    from narwhals.typing import SizeUnit
    from narwhals.typing import _1DArray
    from narwhals.typing import _2DArray
    from narwhals.utils import Version

from narwhals.typing import CompliantDataFrame
from narwhals.typing import CompliantLazyFrame

CLASSICAL_NUMPY_DTYPES: frozenset[np.dtype[Any]] = frozenset(
    [
        np.dtype("float64"),
        np.dtype("float32"),
        np.dtype("int64"),
        np.dtype("int32"),
        np.dtype("int16"),
        np.dtype("int8"),
        np.dtype("uint64"),
        np.dtype("uint32"),
        np.dtype("uint16"),
        np.dtype("uint8"),
        np.dtype("bool"),
        np.dtype("datetime64[s]"),
        np.dtype("datetime64[ms]"),
        np.dtype("datetime64[us]"),
        np.dtype("datetime64[ns]"),
        np.dtype("timedelta64[s]"),
        np.dtype("timedelta64[ms]"),
        np.dtype("timedelta64[us]"),
        np.dtype("timedelta64[ns]"),
        np.dtype("object"),
    ]
)


class PandasLikeDataFrame(CompliantDataFrame["PandasLikeSeries"], CompliantLazyFrame):
    # --- not in the spec ---
    def __init__(
        self: Self,
        native_dataframe: Any,
        *,
        implementation: Implementation,
        backend_version: tuple[int, ...],
        version: Version,
        validate_column_names: bool,
    ) -> None:
        self._native_frame = native_dataframe
        self._implementation = implementation
        self._backend_version = backend_version
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)
        if validate_column_names:
            check_column_names_are_unique(native_dataframe.columns)

    def __narwhals_dataframe__(self: Self) -> Self:
        return self

    def __narwhals_lazyframe__(self: Self) -> Self:
        return self

    def __narwhals_namespace__(self: Self) -> PandasLikeNamespace:
        from narwhals._pandas_like.namespace import PandasLikeNamespace

        return PandasLikeNamespace(
            self._implementation, self._backend_version, version=self._version
        )

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation in {
            Implementation.PANDAS,
            Implementation.MODIN,
            Implementation.CUDF,
        }:
            return self._implementation.to_native_namespace()

        msg = f"Expected pandas/modin/cudf, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def __len__(self: Self) -> int:
        return len(self._native_frame)

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=version,
            validate_column_names=False,
        )

    def _from_native_frame(
        self: Self, df: Any, *, validate_column_names: bool = True
    ) -> Self:
        return self.__class__(
            df,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=validate_column_names,
        )

    def get_column(self: Self, name: str) -> PandasLikeSeries:
        return PandasLikeSeries(
            self._native_frame[name],
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )

    def __array__(self: Self, dtype: Any = None, *, copy: bool | None = None) -> _2DArray:
        return self.to_numpy(dtype=dtype, copy=copy)

    @overload
    def __getitem__(  # type: ignore[overload-overlap]
        self: Self,
        item: str | tuple[slice | Sequence[int] | _1DArray, int | str],
    ) -> PandasLikeSeries: ...

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
    ) -> PandasLikeSeries | Self:
        if isinstance(item, tuple):
            item = tuple(list(i) if is_sequence_but_not_str(i) else i for i in item)  # pyright: ignore[reportAssignmentType]

        if isinstance(item, str):
            return PandasLikeSeries(
                self._native_frame[item],
                implementation=self._implementation,
                backend_version=self._backend_version,
                version=self._version,
            )

        elif (
            isinstance(item, tuple)
            and len(item) == 2
            and is_sequence_but_not_str(item[1])
        ):
            if len(item[1]) == 0:
                # Return empty dataframe
                return self._from_native_frame(
                    self._native_frame.__class__(), validate_column_names=False
                )
            if all(isinstance(x, int) for x in item[1]):  # type: ignore[var-annotated]
                return self._from_native_frame(
                    self._native_frame.iloc[item], validate_column_names=False
                )
            if all(isinstance(x, str) for x in item[1]):  # type: ignore[var-annotated]
                indexer = (
                    item[0],
                    self._native_frame.columns.get_indexer(item[1]),
                )
                return self._from_native_frame(
                    self._native_frame.iloc[indexer], validate_column_names=False
                )
            msg = (
                f"Expected sequence str or int, got: {type(item[1])}"  # pragma: no cover
            )
            raise TypeError(msg)  # pragma: no cover

        elif isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], slice):
            columns = self._native_frame.columns
            if item[1] == slice(None):
                return self._from_native_frame(
                    self._native_frame.iloc[item[0], :], validate_column_names=False
                )
            if isinstance(item[1].start, str) or isinstance(item[1].stop, str):
                start, stop, step = convert_str_slice_to_int_slice(item[1], columns)
                return self._from_native_frame(
                    self._native_frame.iloc[item[0], slice(start, stop, step)],
                    validate_column_names=False,
                )
            if isinstance(item[1].start, int) or isinstance(item[1].stop, int):
                return self._from_native_frame(
                    self._native_frame.iloc[
                        item[0], slice(item[1].start, item[1].stop, item[1].step)
                    ],
                    validate_column_names=False,
                )
            msg = f"Expected slice of integers or strings, got: {type(item[1])}"  # pragma: no cover
            raise TypeError(msg)  # pragma: no cover

        elif isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[1], str):
                index = (item[0], self._native_frame.columns.get_loc(item[1]))
                native_series = self._native_frame.iloc[index]
            elif isinstance(item[1], int):
                native_series = self._native_frame.iloc[item]
            else:  # pragma: no cover
                msg = f"Expected str or int, got: {type(item[1])}"
                raise TypeError(msg)

            return PandasLikeSeries(
                native_series,
                implementation=self._implementation,
                backend_version=self._backend_version,
                version=self._version,
            )

        elif is_sequence_but_not_str(item) or is_numpy_array_1d(item):
            if all(isinstance(x, str) for x in item) and len(item) > 0:
                return self._from_native_frame(
                    select_columns_by_name(
                        self._native_frame,
                        cast("list[str] | _1DArray", item),
                        self._backend_version,
                        self._implementation,
                    ),
                    validate_column_names=False,
                )
            return self._from_native_frame(
                self._native_frame.iloc[item], validate_column_names=False
            )

        elif isinstance(item, slice):
            if isinstance(item.start, str) or isinstance(item.stop, str):
                start, stop, step = convert_str_slice_to_int_slice(
                    item, self._native_frame.columns
                )
                return self._from_native_frame(
                    self._native_frame.iloc[:, slice(start, stop, step)],
                    validate_column_names=False,
                )
            return self._from_native_frame(
                self._native_frame.iloc[item], validate_column_names=False
            )

        else:  # pragma: no cover
            msg = f"Expected str or slice, got: {type(item)}"
            raise TypeError(msg)

    # --- properties ---
    @property
    def columns(self: Self) -> list[str]:
        return self._native_frame.columns.tolist()

    @overload
    def rows(
        self: Self,
        *,
        named: Literal[True],
    ) -> list[dict[str, Any]]: ...

    @overload
    def rows(
        self: Self,
        *,
        named: Literal[False],
    ) -> list[tuple[Any, ...]]: ...

    @overload
    def rows(
        self: Self,
        *,
        named: bool,
    ) -> list[tuple[Any, ...]] | list[dict[str, Any]]: ...

    def rows(self: Self, *, named: bool) -> list[tuple[Any, ...]] | list[dict[str, Any]]:
        if not named:
            # cuDF does not support itertuples. But it does support to_dict!
            if self._implementation is Implementation.CUDF:
                # Extract the row values from the named rows
                return [tuple(row.values()) for row in self.rows(named=True)]

            return list(self._native_frame.itertuples(index=False, name=None))

        return self._native_frame.to_dict(orient="records")

    def iter_columns(self) -> Iterator[PandasLikeSeries]:
        for _name, series in self._native_frame.items():  # noqa: PERF102
            yield PandasLikeSeries(
                series,
                implementation=self._implementation,
                backend_version=self._backend_version,
                version=self._version,
            )

    _iter_columns = iter_columns

    def iter_rows(
        self: Self,
        *,
        named: bool,
        buffer_size: int,
    ) -> Iterator[list[tuple[Any, ...]]] | Iterator[list[dict[str, Any]]]:
        # The param ``buffer_size`` is only here for compatibility with the Polars API
        # and has no effect on the output.
        if not named:
            yield from self._native_frame.itertuples(index=False, name=None)
        else:
            col_names = self._native_frame.columns
            yield from (
                dict(zip(col_names, row))
                for row in self._native_frame.itertuples(index=False)
            )  # type: ignore[misc]

    @property
    def schema(self: Self) -> dict[str, DType]:
        native_dtypes = self._native_frame.dtypes
        return {
            col: native_to_narwhals_dtype(
                native_dtypes[col], self._version, self._implementation
            )
            if native_dtypes[col] != "object"
            else object_native_to_narwhals_dtype(
                self._native_frame[col], self._version, self._implementation
            )
            for col in self._native_frame.columns
        }

    def collect_schema(self: Self) -> dict[str, DType]:
        return self.schema

    # --- reshape ---
    def simple_select(self: Self, *column_names: str) -> Self:
        return self._from_native_frame(
            select_columns_by_name(
                self._native_frame,
                list(column_names),
                self._backend_version,
                self._implementation,
            ),
            validate_column_names=False,
        )

    def aggregate(
        self: PandasLikeDataFrame, *exprs: PandasLikeExpr
    ) -> PandasLikeDataFrame:
        return self.select(*exprs)

    def select(self: PandasLikeDataFrame, *exprs: PandasLikeExpr) -> PandasLikeDataFrame:
        new_series = evaluate_into_exprs(self, *exprs)
        if not new_series:
            # return empty dataframe, like Polars does
            return self._from_native_frame(
                self._native_frame.__class__(), validate_column_names=False
            )
        new_series = align_series_full_broadcast(*new_series)
        df = horizontal_concat(
            [s._native_series for s in new_series],
            implementation=self._implementation,
            backend_version=self._backend_version,
        )
        return self._from_native_frame(df, validate_column_names=True)

    def drop_nulls(
        self: PandasLikeDataFrame, subset: list[str] | None
    ) -> PandasLikeDataFrame:
        if subset is None:
            return self._from_native_frame(
                self._native_frame.dropna(axis=0), validate_column_names=False
            )
        plx = self.__narwhals_namespace__()
        return self.filter(~plx.any_horizontal(plx.col(*subset).is_null()))

    def estimated_size(self: Self, unit: SizeUnit) -> int | float:
        sz = self._native_frame.memory_usage(deep=True).sum()
        return scale_bytes(sz, unit=unit)

    def with_row_index(self: Self, name: str) -> Self:
        row_index = create_compliant_series(
            range(len(self._native_frame)),
            index=self._native_frame.index,
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        ).alias(name)
        return self._from_native_frame(
            horizontal_concat(
                [row_index._native_series, self._native_frame],
                implementation=self._implementation,
                backend_version=self._backend_version,
            )
        )

    def row(self: Self, row: int) -> tuple[Any, ...]:
        return tuple(x for x in self._native_frame.iloc[row])

    def filter(
        self: PandasLikeDataFrame, predicate: PandasLikeExpr | list[bool]
    ) -> PandasLikeDataFrame:
        if isinstance(predicate, list):
            mask_native: pd.Series[Any] | list[bool] = predicate
        else:
            # `[0]` is safe as the predicate's expression only returns a single column
            mask = evaluate_into_exprs(self, predicate)[0]
            mask_native = extract_dataframe_comparand(self._native_frame.index, mask)

        return self._from_native_frame(
            self._native_frame.loc[mask_native], validate_column_names=False
        )

    def with_columns(
        self: PandasLikeDataFrame, *exprs: PandasLikeExpr
    ) -> PandasLikeDataFrame:
        index = self._native_frame.index
        new_columns = evaluate_into_exprs(self, *exprs)
        if not new_columns and len(self) == 0:
            return self

        new_column_name_to_new_column_map = {s.name: s for s in new_columns}
        to_concat = []
        # Make sure to preserve column order
        for name in self._native_frame.columns:
            if name in new_column_name_to_new_column_map:
                to_concat.append(
                    extract_dataframe_comparand(
                        index, new_column_name_to_new_column_map.pop(name)
                    )
                )
            else:
                to_concat.append(self._native_frame[name])
        to_concat.extend(
            extract_dataframe_comparand(index, new_column_name_to_new_column_map[s])
            for s in new_column_name_to_new_column_map
        )

        df = horizontal_concat(
            to_concat,
            implementation=self._implementation,
            backend_version=self._backend_version,
        )
        return self._from_native_frame(df, validate_column_names=False)

    def rename(self: Self, mapping: dict[str, str]) -> Self:
        return self._from_native_frame(
            rename(
                self._native_frame,
                columns=mapping,
                implementation=self._implementation,
                backend_version=self._backend_version,
            )
        )

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        to_drop = parse_columns_to_drop(
            compliant_frame=self, columns=columns, strict=strict
        )
        return self._from_native_frame(
            self._native_frame.drop(columns=to_drop), validate_column_names=False
        )

    # --- transform ---
    def sort(
        self: Self,
        *by: str,
        descending: bool | Sequence[bool],
        nulls_last: bool,
    ) -> Self:
        df = self._native_frame
        if isinstance(descending, bool):
            ascending: bool | list[bool] = not descending
        else:
            ascending = [not d for d in descending]
        na_position = "last" if nulls_last else "first"
        return self._from_native_frame(
            df.sort_values(list(by), ascending=ascending, na_position=na_position),
            validate_column_names=False,
        )

    # --- convert ---
    def collect(
        self: Self,
        backend: Implementation | None,
        **kwargs: Any,
    ) -> CompliantDataFrame[Any]:
        if backend is None:
            return PandasLikeDataFrame(
                self._native_frame,
                implementation=self._implementation,
                backend_version=self._backend_version,
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.PANDAS:
            import pandas as pd  # ignore-banned-import

            return PandasLikeDataFrame(
                self.to_pandas(),
                implementation=Implementation.PANDAS,
                backend_version=parse_version(pd),
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.PYARROW:
            import pyarrow as pa  # ignore-banned-import

            from narwhals._arrow.dataframe import ArrowDataFrame

            return ArrowDataFrame(
                native_dataframe=self.to_arrow(),
                backend_version=parse_version(pa),
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.POLARS:
            import polars as pl  # ignore-banned-import

            from narwhals._polars.dataframe import PolarsDataFrame

            return PolarsDataFrame(
                df=self.to_polars(),
                backend_version=parse_version(pl),
                version=self._version,
            )

        msg = f"Unsupported `backend` value: {backend}"  # pragma: no cover
        raise ValueError(msg)  # pragma: no cover

    # --- actions ---
    def group_by(self: Self, *keys: str, drop_null_keys: bool) -> PandasLikeGroupBy:
        from narwhals._pandas_like.group_by import PandasLikeGroupBy

        return PandasLikeGroupBy(
            self,
            list(keys),
            drop_null_keys=drop_null_keys,
        )

    def join(
        self: Self,
        other: Self,
        *,
        how: Literal["left", "inner", "cross", "anti", "semi"],
        left_on: list[str] | None,
        right_on: list[str] | None,
        suffix: str,
    ) -> Self:
        if how == "cross":
            if (
                self._implementation is Implementation.MODIN
                or self._implementation is Implementation.CUDF
            ) or (
                self._implementation is Implementation.PANDAS
                and self._backend_version < (1, 4)
            ):
                key_token = generate_temporary_column_name(
                    n_bytes=8, columns=[*self.columns, *other.columns]
                )

                return self._from_native_frame(
                    self._native_frame.assign(**{key_token: 0})
                    .merge(
                        other._native_frame.assign(**{key_token: 0}),
                        how="inner",
                        left_on=key_token,
                        right_on=key_token,
                        suffixes=("", suffix),
                    )
                    .drop(columns=key_token),
                )
            else:
                return self._from_native_frame(
                    self._native_frame.merge(
                        other._native_frame,
                        how="cross",
                        suffixes=("", suffix),
                    ),
                )

        if how == "anti":
            if self._implementation is Implementation.CUDF:
                return self._from_native_frame(
                    self._native_frame.merge(
                        other._native_frame,
                        how="leftanti",
                        left_on=left_on,
                        right_on=right_on,
                    )
                )
            else:
                indicator_token = generate_temporary_column_name(
                    n_bytes=8, columns=[*self.columns, *other.columns]
                )
                if right_on is None:  # pragma: no cover
                    msg = "`right_on` cannot be `None` in anti-join"
                    raise TypeError(msg)

                # rename to avoid creating extra columns in join
                other_native = rename(
                    select_columns_by_name(
                        other._native_frame,
                        right_on,
                        self._backend_version,
                        self._implementation,
                    ),
                    columns=dict(zip(right_on, left_on)),  # type: ignore[arg-type]
                    implementation=self._implementation,
                    backend_version=self._backend_version,
                ).drop_duplicates()
                return self._from_native_frame(
                    self._native_frame.merge(
                        other_native,
                        how="outer",
                        indicator=indicator_token,
                        left_on=left_on,
                        right_on=left_on,
                    )
                    .loc[lambda t: t[indicator_token] == "left_only"]
                    .drop(columns=indicator_token)
                )

        if how == "semi":
            if right_on is None:  # pragma: no cover
                msg = "`right_on` cannot be `None` in semi-join"
                raise TypeError(msg)
            # rename to avoid creating extra columns in join
            other_native = (
                rename(
                    select_columns_by_name(
                        other._native_frame,
                        right_on,
                        self._backend_version,
                        self._implementation,
                    ),
                    columns=dict(zip(right_on, left_on)),  # type: ignore[arg-type]
                    implementation=self._implementation,
                    backend_version=self._backend_version,
                ).drop_duplicates()  # avoids potential rows duplication from inner join
            )
            return self._from_native_frame(
                self._native_frame.merge(
                    other_native,
                    how="inner",
                    left_on=left_on,
                    right_on=left_on,
                )
            )

        if how == "left":
            other_native = other._native_frame
            result_native = self._native_frame.merge(
                other_native,
                how="left",
                left_on=left_on,
                right_on=right_on,
                suffixes=("", suffix),
            )
            extra = []
            for left_key, right_key in zip(left_on, right_on):  # type: ignore[arg-type]
                if right_key != left_key and right_key not in self.columns:
                    extra.append(right_key)
                elif right_key != left_key:
                    extra.append(f"{right_key}{suffix}")
            return self._from_native_frame(result_native.drop(columns=extra))

        return self._from_native_frame(
            self._native_frame.merge(
                other._native_frame,
                left_on=left_on,
                right_on=right_on,
                how=how,
                suffixes=("", suffix),
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
        plx = self.__native_namespace__()
        return self._from_native_frame(
            plx.merge_asof(
                self._native_frame,
                other._native_frame,
                left_on=left_on,
                right_on=right_on,
                left_by=by_left,
                right_by=by_right,
                direction=strategy,
                suffixes=("", suffix),
            ),
        )

    # --- partial reduction ---

    def head(self: Self, n: int) -> Self:
        return self._from_native_frame(
            self._native_frame.head(n), validate_column_names=False
        )

    def tail(self: Self, n: int) -> Self:
        return self._from_native_frame(
            self._native_frame.tail(n), validate_column_names=False
        )

    def unique(
        self: Self,
        subset: list[str] | None,
        *,
        keep: Literal["any", "first", "last", "none"],
        maintain_order: bool | None = None,
    ) -> Self:
        # The param `maintain_order` is only here for compatibility with the Polars API
        # and has no effect on the output.
        mapped_keep = {"none": False, "any": "first"}.get(keep, keep)
        check_column_exists(self.columns, subset)
        return self._from_native_frame(
            self._native_frame.drop_duplicates(subset=subset, keep=mapped_keep),
            validate_column_names=False,
        )

    # --- lazy-only ---
    def lazy(self: Self, *, backend: Implementation | None = None) -> CompliantLazyFrame:
        from narwhals.utils import parse_version

        pandas_df = self.to_pandas()
        if backend is None:
            return self
        elif backend is Implementation.DUCKDB:
            import duckdb  # ignore-banned-import

            from narwhals._duckdb.dataframe import DuckDBLazyFrame

            return DuckDBLazyFrame(
                df=duckdb.table("pandas_df"),
                backend_version=parse_version(duckdb),
                version=self._version,
                validate_column_names=False,
            )
        elif backend is Implementation.POLARS:
            import polars as pl  # ignore-banned-import

            from narwhals._polars.dataframe import PolarsLazyFrame

            return PolarsLazyFrame(
                df=pl.from_pandas(pandas_df).lazy(),
                backend_version=parse_version(pl),
                version=self._version,
            )
        elif backend is Implementation.DASK:
            import dask  # ignore-banned-import
            import dask.dataframe as dd  # ignore-banned-import

            from narwhals._dask.dataframe import DaskLazyFrame

            return DaskLazyFrame(
                native_dataframe=dd.from_pandas(pandas_df),
                backend_version=parse_version(dask),
                version=self._version,
                validate_column_names=False,
            )
        raise AssertionError  # pragma: no cover

    @property
    def shape(self: Self) -> tuple[int, int]:
        return self._native_frame.shape

    def to_dict(self: Self, *, as_series: bool) -> dict[str, Any]:
        if as_series:
            return {
                col: PandasLikeSeries(
                    self._native_frame[col],
                    implementation=self._implementation,
                    backend_version=self._backend_version,
                    version=self._version,
                )
                for col in self.columns
            }
        return self._native_frame.to_dict(orient="list")

    def to_numpy(self: Self, dtype: Any = None, *, copy: bool | None = None) -> _2DArray:
        native_dtypes = self._native_frame.dtypes

        if copy is None:
            # pandas default differs from Polars, but cuDF default is True
            copy = self._implementation is Implementation.CUDF

        if native_dtypes.isin(CLASSICAL_NUMPY_DTYPES).all():
            # Fast path, no conversions necessary.
            if dtype is not None:
                return self._native_frame.to_numpy(dtype=dtype, copy=copy)
            return self._native_frame.to_numpy(copy=copy)

        dtypes = import_dtypes_module(self._version)

        to_convert = [
            key
            for key, val in self.schema.items()
            if val == dtypes.Datetime and val.time_zone is not None  # type: ignore[attr-defined]
        ]
        if to_convert:
            df = self.with_columns(
                self.__narwhals_namespace__()
                .col(*to_convert)
                .dt.convert_time_zone("UTC")
                .dt.replace_time_zone(None)
            )._native_frame
        else:
            df = self._native_frame

        if dtype is not None:
            return df.to_numpy(dtype=dtype, copy=copy)

        # pandas return `object` dtype for nullable dtypes if dtype=None,
        # so we cast each Series to numpy and let numpy find a common dtype.
        # If there aren't any dtypes where `to_numpy()` is "broken" (i.e. it
        # returns Object) then we just call `to_numpy()` on the DataFrame.
        for col_dtype in native_dtypes:
            if str(col_dtype) in PANDAS_TO_NUMPY_DTYPE_MISSING:
                import numpy as np

                arr: Any = np.hstack(
                    [
                        self[col].to_numpy(copy=copy, dtype=None)[:, None]
                        for col in self.columns
                    ]
                )
                return arr
        return df.to_numpy(copy=copy)

    def to_pandas(self: Self) -> pd.DataFrame:
        if self._implementation is Implementation.PANDAS:
            return self._native_frame
        elif self._implementation is Implementation.CUDF:  # pragma: no cover
            return self._native_frame.to_pandas()
        elif self._implementation is Implementation.MODIN:
            return self._native_frame._to_pandas()
        msg = f"Unknown implementation: {self._implementation}"  # pragma: no cover
        raise AssertionError(msg)

    def to_polars(self: Self) -> pl.DataFrame:
        import polars as pl  # ignore-banned-import

        if self._implementation is Implementation.PANDAS:
            return pl.from_pandas(self._native_frame)
        elif self._implementation is Implementation.CUDF:  # pragma: no cover
            return pl.from_pandas(self._native_frame.to_pandas())
        elif self._implementation is Implementation.MODIN:
            return pl.from_pandas(self._native_frame._to_pandas())
        msg = f"Unknown implementation: {self._implementation}"  # pragma: no cover
        raise AssertionError(msg)

    def write_parquet(self: Self, file: str | Path | BytesIO) -> None:
        self._native_frame.to_parquet(file)

    @overload
    def write_csv(self: Self, file: None) -> str: ...

    @overload
    def write_csv(self: Self, file: str | Path | BytesIO) -> None: ...

    def write_csv(self: Self, file: str | Path | BytesIO | None) -> str | None:
        return self._native_frame.to_csv(file, index=False)

    # --- descriptive ---
    def is_unique(self: Self) -> PandasLikeSeries:
        return PandasLikeSeries(
            ~self._native_frame.duplicated(keep=False),
            implementation=self._implementation,
            backend_version=self._backend_version,
            version=self._version,
        )

    def item(self: Self, row: int | None, column: int | str | None) -> Any:
        if row is None and column is None:
            if self.shape != (1, 1):
                msg = (
                    "can only call `.item()` if the dataframe is of shape (1, 1),"
                    " or if explicit row/col values are provided;"
                    f" frame has shape {self.shape!r}"
                )
                raise ValueError(msg)
            return self._native_frame.iloc[0, 0]

        elif row is None or column is None:
            msg = "cannot call `.item()` with only one of `row` or `column`"
            raise ValueError(msg)

        _col = self.columns.index(column) if isinstance(column, str) else column
        return self._native_frame.iloc[row, _col]

    def clone(self: Self) -> Self:
        return self._from_native_frame(
            self._native_frame.copy(), validate_column_names=False
        )

    def gather_every(self: Self, n: int, offset: int) -> Self:
        return self._from_native_frame(
            self._native_frame.iloc[offset::n], validate_column_names=False
        )

    def pivot(
        self: Self,
        on: list[str],
        *,
        index: list[str] | None,
        values: list[str] | None,
        aggregate_function: Any | None,
        sort_columns: bool,
        separator: str,
    ) -> Self:
        if self._implementation is Implementation.PANDAS and (
            self._backend_version < (1, 1)
        ):  # pragma: no cover
            msg = "pivot is only supported for pandas>=1.1"
            raise NotImplementedError(msg)
        if self._implementation is Implementation.MODIN:
            msg = "pivot is not supported for Modin backend due to https://github.com/modin-project/modin/issues/7409."
            raise NotImplementedError(msg)
        from itertools import product

        frame = self._native_frame

        if index is None:
            index = [c for c in self.columns if c not in {*on, *values}]  # type: ignore[misc]

        if values is None:
            values = [c for c in self.columns if c not in {*on, *index}]

        if aggregate_function is None:
            result = frame.pivot(columns=on, index=index, values=values)
        elif aggregate_function == "len":
            result = (
                frame.groupby([*on, *index])
                .agg(dict.fromkeys(values, "size"))
                .reset_index()
                .pivot(columns=on, index=index, values=values)
            )
        else:
            result = pivot_table(
                df=self,
                values=values,
                index=index,
                columns=on,
                aggregate_function=aggregate_function,
            )

        # Put columns in the right order
        if sort_columns and self._implementation is Implementation.CUDF:
            uniques = {
                col: sorted(self._native_frame[col].unique().to_arrow().to_pylist())
                for col in on
            }
        elif sort_columns:
            uniques = {
                col: sorted(self._native_frame[col].unique().tolist()) for col in on
            }
        elif self._implementation is Implementation.CUDF:
            uniques = {
                col: self._native_frame[col].unique().to_arrow().to_pylist() for col in on
            }
        else:
            uniques = {col: self._native_frame[col].unique().tolist() for col in on}
        ordered_cols = list(product(values, *uniques.values()))
        result = result.loc[:, ordered_cols]
        columns = result.columns.tolist()

        n_on = len(on)
        if n_on == 1:
            new_columns = [
                separator.join(col).strip() if len(values) > 1 else col[-1]
                for col in columns
            ]
        else:
            new_columns = [
                separator.join([col[0], '{"' + '","'.join(col[-n_on:]) + '"}'])
                if len(values) > 1
                else '{"' + '","'.join(col[-n_on:]) + '"}'
                for col in columns
            ]
        result.columns = new_columns
        result.columns.names = [""]  # type: ignore[attr-defined]
        return self._from_native_frame(result.reset_index())

    def to_arrow(self: Self) -> Any:
        if self._implementation is Implementation.CUDF:
            return self._native_frame.to_arrow(preserve_index=False)

        import pyarrow as pa  # ignore-banned-import()

        return pa.Table.from_pandas(self._native_frame)

    def sample(
        self: Self,
        n: int | None,
        *,
        fraction: float | None,
        with_replacement: bool,
        seed: int | None,
    ) -> Self:
        return self._from_native_frame(
            self._native_frame.sample(
                n=n, frac=fraction, replace=with_replacement, random_state=seed
            ),
            validate_column_names=False,
        )

    def unpivot(
        self: Self,
        on: list[str] | None,
        index: list[str] | None,
        variable_name: str,
        value_name: str,
    ) -> Self:
        return self._from_native_frame(
            self._native_frame.melt(
                id_vars=index,
                value_vars=on,
                var_name=variable_name,
                value_name=value_name,
            )
        )

    def explode(self: Self, columns: list[str]) -> Self:
        dtypes = import_dtypes_module(self._version)

        schema = self.collect_schema()
        for col_to_explode in columns:
            dtype = schema[col_to_explode]

            if dtype != dtypes.List:
                msg = (
                    f"`explode` operation not supported for dtype `{dtype}`, "
                    "expected List type"
                )
                raise InvalidOperationError(msg)

        if len(columns) == 1:
            return self._from_native_frame(
                self._native_frame.explode(columns[0]), validate_column_names=False
            )
        else:
            native_frame = self._native_frame
            anchor_series = native_frame[columns[0]].list.len()

            if not all(
                (native_frame[col_name].list.len() == anchor_series).all()
                for col_name in columns[1:]
            ):
                from narwhals.exceptions import ShapeError

                msg = "exploded columns must have matching element counts"
                raise ShapeError(msg)

            original_columns = self.columns
            other_columns = [c for c in original_columns if c not in columns]

            exploded_frame = native_frame[[*other_columns, columns[0]]].explode(
                columns[0]
            )
            exploded_series = [
                native_frame[col_name].explode().to_frame() for col_name in columns[1:]
            ]

            plx = self.__native_namespace__()
            return self._from_native_frame(
                plx.concat([exploded_frame, *exploded_series], axis=1)[original_columns],
                validate_column_names=False,
            )
