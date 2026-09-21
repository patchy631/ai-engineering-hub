from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Literal
from typing import Sequence
from typing import overload

import polars as pl

from narwhals._polars.namespace import PolarsNamespace
from narwhals._polars.utils import catch_polars_exception
from narwhals._polars.utils import convert_str_slice_to_int_slice
from narwhals._polars.utils import extract_args_kwargs
from narwhals._polars.utils import native_to_narwhals_dtype
from narwhals.exceptions import ColumnNotFoundError
from narwhals.utils import Implementation
from narwhals.utils import is_sequence_but_not_str
from narwhals.utils import parse_columns_to_drop
from narwhals.utils import parse_version
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from types import ModuleType
    from typing import TypeVar

    from typing_extensions import Self

    from narwhals._polars.group_by import PolarsGroupBy
    from narwhals._polars.group_by import PolarsLazyGroupBy
    from narwhals._polars.series import PolarsSeries
    from narwhals.dtypes import DType
    from narwhals.typing import CompliantDataFrame
    from narwhals.typing import CompliantLazyFrame
    from narwhals.typing import _2DArray
    from narwhals.utils import Version

    T = TypeVar("T")


class PolarsDataFrame:
    def __init__(
        self: Self,
        df: pl.DataFrame,
        *,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._native_frame = df
        self._backend_version = backend_version
        self._implementation = Implementation.POLARS
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)

    def __repr__(self: Self) -> str:  # pragma: no cover
        return "PolarsDataFrame"

    def __narwhals_dataframe__(self: Self) -> Self:
        return self

    def __narwhals_namespace__(self: Self) -> PolarsNamespace:
        return PolarsNamespace(
            backend_version=self._backend_version, version=self._version
        )

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.POLARS:
            return self._implementation.to_native_namespace()

        msg = f"Expected polars, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame, backend_version=self._backend_version, version=version
        )

    def _from_native_frame(self: Self, df: pl.DataFrame) -> Self:
        return self.__class__(
            df, backend_version=self._backend_version, version=self._version
        )

    @overload
    def _from_native_object(self: Self, obj: pl.Series) -> PolarsSeries: ...

    @overload
    def _from_native_object(self: Self, obj: pl.DataFrame) -> Self: ...

    @overload
    def _from_native_object(self: Self, obj: T) -> T: ...

    def _from_native_object(
        self: Self, obj: pl.Series | pl.DataFrame | T
    ) -> Self | PolarsSeries | T:
        if isinstance(obj, pl.Series):
            from narwhals._polars.series import PolarsSeries

            return PolarsSeries(
                obj, backend_version=self._backend_version, version=self._version
            )
        if isinstance(obj, pl.DataFrame):
            return self._from_native_frame(obj)
        # scalar
        return obj

    def __len__(self) -> int:
        return len(self._native_frame)

    def head(self, n: int) -> Self:
        return self._from_native_frame(self._native_frame.head(n))

    def tail(self, n: int) -> Self:
        return self._from_native_frame(self._native_frame.tail(n))

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            try:
                return self._from_native_object(
                    getattr(self._native_frame, attr)(*args, **kwargs)
                )
            except pl.exceptions.ColumnNotFoundError as e:  # pragma: no cover
                msg = f"{e!s}\n\nHint: Did you mean one of these columns: {self.columns}?"
                raise ColumnNotFoundError(msg) from e
            except Exception as e:  # noqa: BLE001
                raise catch_polars_exception(e, self._backend_version) from None

        return func

    def __array__(
        self: Self, dtype: Any | None = None, *, copy: bool | None = None
    ) -> _2DArray:
        if self._backend_version < (0, 20, 28) and copy is not None:
            msg = "`copy` in `__array__` is only supported for Polars>=0.20.28"
            raise NotImplementedError(msg)
        if self._backend_version < (0, 20, 28):
            return self._native_frame.__array__(dtype)
        return self._native_frame.__array__(dtype)

    def collect_schema(self: Self) -> dict[str, DType]:
        if self._backend_version < (1,):
            return {
                name: native_to_narwhals_dtype(
                    dtype, self._version, self._backend_version
                )
                for name, dtype in self._native_frame.schema.items()
            }
        else:
            collected_schema = self._native_frame.collect_schema()
            return {
                name: native_to_narwhals_dtype(
                    dtype, self._version, self._backend_version
                )
                for name, dtype in collected_schema.items()
            }

    @property
    def shape(self: Self) -> tuple[int, int]:
        return self._native_frame.shape

    def __getitem__(self: Self, item: Any) -> Any:
        if self._backend_version > (0, 20, 30):
            return self._from_native_object(self._native_frame.__getitem__(item))
        else:  # pragma: no cover
            # TODO(marco): we can delete this branch after Polars==0.20.30 becomes the minimum
            # Polars version we support
            if isinstance(item, tuple):
                item = tuple(list(i) if is_sequence_but_not_str(i) else i for i in item)

            columns = self.columns
            if isinstance(item, tuple) and len(item) == 2 and isinstance(item[1], slice):
                if item[1] == slice(None):
                    if isinstance(item[0], Sequence) and not len(item[0]):
                        return self._from_native_frame(self._native_frame[0:0])
                    return self._from_native_frame(
                        self._native_frame.__getitem__(item[0])
                    )
                if isinstance(item[1].start, str) or isinstance(item[1].stop, str):
                    start, stop, step = convert_str_slice_to_int_slice(item[1], columns)
                    return self._from_native_frame(
                        self._native_frame.select(columns[start:stop:step]).__getitem__(
                            item[0]
                        )
                    )
                if isinstance(item[1].start, int) or isinstance(item[1].stop, int):
                    return self._from_native_frame(
                        self._native_frame.select(
                            columns[item[1].start : item[1].stop : item[1].step]
                        ).__getitem__(item[0])
                    )
                msg = f"Expected slice of integers or strings, got: {type(item[1])}"  # pragma: no cover
                raise TypeError(msg)  # pragma: no cover

            if (
                isinstance(item, tuple)
                and (len(item) == 2)
                and is_sequence_but_not_str(item[1])
                and (len(item[1]) == 0)
            ):
                result = self._native_frame.select(item[1])
            elif isinstance(item, slice) and (
                isinstance(item.start, str) or isinstance(item.stop, str)
            ):
                start, stop, step = convert_str_slice_to_int_slice(item, columns)
                return self._from_native_frame(
                    self._native_frame.select(columns[start:stop:step])
                )
            elif is_sequence_but_not_str(item) and (len(item) == 0):
                result = self._native_frame.slice(0, 0)
            else:
                result = self._native_frame.__getitem__(item)
            if isinstance(result, pl.Series):
                from narwhals._polars.series import PolarsSeries

                return PolarsSeries(
                    result, backend_version=self._backend_version, version=self._version
                )
            return self._from_native_object(result)

    def simple_select(self, *column_names: str) -> Self:
        return self._from_native_frame(self._native_frame.select(*column_names))

    def aggregate(self: Self, *exprs: Any) -> Self:
        return self.select(*exprs)  # type: ignore[no-any-return]

    def get_column(self: Self, name: str) -> PolarsSeries:
        from narwhals._polars.series import PolarsSeries

        return PolarsSeries(
            self._native_frame.get_column(name),
            backend_version=self._backend_version,
            version=self._version,
        )

    def iter_columns(self) -> Iterator[PolarsSeries]:
        from narwhals._polars.series import PolarsSeries

        for series in self._native_frame.iter_columns():
            yield PolarsSeries(
                series, backend_version=self._backend_version, version=self._version
            )

    @property
    def columns(self: Self) -> list[str]:
        return self._native_frame.columns

    @property
    def schema(self: Self) -> dict[str, DType]:
        schema = self._native_frame.schema
        return {
            name: native_to_narwhals_dtype(dtype, self._version, self._backend_version)
            for name, dtype in schema.items()
        }

    def lazy(self: Self, *, backend: Implementation | None = None) -> CompliantLazyFrame:
        from narwhals.utils import parse_version

        if backend is None or backend is Implementation.POLARS:
            from narwhals._polars.dataframe import PolarsLazyFrame

            return PolarsLazyFrame(
                self._native_frame.lazy(),
                backend_version=self._backend_version,
                version=self._version,
            )
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

    @overload
    def to_dict(self: Self, *, as_series: Literal[True]) -> dict[str, PolarsSeries]: ...

    @overload
    def to_dict(self: Self, *, as_series: Literal[False]) -> dict[str, list[Any]]: ...

    def to_dict(
        self: Self, *, as_series: bool
    ) -> dict[str, PolarsSeries] | dict[str, list[Any]]:
        df = self._native_frame

        if as_series:
            from narwhals._polars.series import PolarsSeries

            return {
                name: PolarsSeries(
                    col, backend_version=self._backend_version, version=self._version
                )
                for name, col in df.to_dict(as_series=True).items()
            }
        else:
            return df.to_dict(as_series=False)

    def group_by(self: Self, *by: str, drop_null_keys: bool) -> PolarsGroupBy:
        from narwhals._polars.group_by import PolarsGroupBy

        return PolarsGroupBy(self, list(by), drop_null_keys=drop_null_keys)

    def with_row_index(self: Self, name: str) -> Self:
        if self._backend_version < (0, 20, 4):
            return self._from_native_frame(self._native_frame.with_row_count(name))
        return self._from_native_frame(self._native_frame.with_row_index(name))

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        to_drop = parse_columns_to_drop(
            compliant_frame=self, columns=columns, strict=strict
        )
        return self._from_native_frame(self._native_frame.drop(to_drop))

    def unpivot(
        self: Self,
        on: list[str] | None,
        index: list[str] | None,
        variable_name: str,
        value_name: str,
    ) -> Self:
        if self._backend_version < (1, 0, 0):
            return self._from_native_frame(
                self._native_frame.melt(
                    id_vars=index,
                    value_vars=on,
                    variable_name=variable_name,
                    value_name=value_name,
                )
            )
        return self._from_native_frame(
            self._native_frame.unpivot(
                on=on, index=index, variable_name=variable_name, value_name=value_name
            )
        )

    def pivot(
        self: Self,
        on: list[str],
        *,
        index: list[str] | None,
        values: list[str] | None,
        aggregate_function: Literal[
            "min", "max", "first", "last", "sum", "mean", "median", "len"
        ]
        | None,
        sort_columns: bool,
        separator: str,
    ) -> Self:
        if self._backend_version < (1, 0, 0):  # pragma: no cover
            msg = "`pivot` is only supported for Polars>=1.0.0"
            raise NotImplementedError(msg)
        try:
            result = self._native_frame.pivot(
                on,
                index=index,
                values=values,
                aggregate_function=aggregate_function,
                sort_columns=sort_columns,
                separator=separator,
            )
        except Exception as e:  # noqa: BLE001
            raise catch_polars_exception(e, self._backend_version) from None
        return self._from_native_object(result)

    def to_polars(self: Self) -> pl.DataFrame:
        return self._native_frame


class PolarsLazyFrame:
    def __init__(
        self: Self,
        df: pl.LazyFrame,
        *,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._native_frame = df
        self._backend_version = backend_version
        self._implementation = Implementation.POLARS
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)

    def __repr__(self: Self) -> str:  # pragma: no cover
        return "PolarsLazyFrame"

    def __narwhals_lazyframe__(self: Self) -> Self:
        return self

    def __narwhals_namespace__(self: Self) -> PolarsNamespace:
        return PolarsNamespace(
            backend_version=self._backend_version, version=self._version
        )

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.POLARS:
            return self._implementation.to_native_namespace()

        msg = f"Expected polars, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def _from_native_frame(self: Self, df: pl.LazyFrame) -> Self:
        return self.__class__(
            df, backend_version=self._backend_version, version=self._version
        )

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame, backend_version=self._backend_version, version=version
        )

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            try:
                return self._from_native_frame(
                    getattr(self._native_frame, attr)(*args, **kwargs)
                )
            except pl.exceptions.ColumnNotFoundError as e:  # pragma: no cover
                raise ColumnNotFoundError(str(e)) from e

        return func

    def _iter_columns(self) -> Iterator[PolarsSeries]:  # pragma: no cover
        yield from self.collect(self._implementation).iter_columns()

    @property
    def columns(self: Self) -> list[str]:
        return self._native_frame.columns

    @property
    def schema(self: Self) -> dict[str, DType]:
        schema = self._native_frame.schema
        return {
            name: native_to_narwhals_dtype(dtype, self._version, self._backend_version)
            for name, dtype in schema.items()
        }

    def collect_schema(self: Self) -> dict[str, DType]:
        if self._backend_version < (1,):
            return {
                name: native_to_narwhals_dtype(
                    dtype, self._version, self._backend_version
                )
                for name, dtype in self._native_frame.schema.items()
            }
        else:
            try:
                collected_schema = self._native_frame.collect_schema()
            except Exception as e:  # noqa: BLE001
                raise catch_polars_exception(e, self._backend_version) from None
            return {
                name: native_to_narwhals_dtype(
                    dtype, self._version, self._backend_version
                )
                for name, dtype in collected_schema.items()
            }

    def collect(
        self: Self,
        backend: Implementation | None,
        **kwargs: Any,
    ) -> CompliantDataFrame[Any]:
        try:
            result = self._native_frame.collect(**kwargs)
        except Exception as e:  # noqa: BLE001
            raise catch_polars_exception(e, self._backend_version) from None

        if backend is None or backend is Implementation.POLARS:
            from narwhals._polars.dataframe import PolarsDataFrame

            return PolarsDataFrame(
                result,
                backend_version=self._backend_version,
                version=self._version,
            )

        if backend is Implementation.PANDAS:
            import pandas as pd  # ignore-banned-import

            from narwhals._pandas_like.dataframe import PandasLikeDataFrame

            return PandasLikeDataFrame(
                result.to_pandas(),
                implementation=Implementation.PANDAS,
                backend_version=parse_version(pd),
                version=self._version,
                validate_column_names=False,
            )

        if backend is Implementation.PYARROW:
            import pyarrow as pa  # ignore-banned-import

            from narwhals._arrow.dataframe import ArrowDataFrame

            return ArrowDataFrame(
                result.to_arrow(),
                backend_version=parse_version(pa),
                version=self._version,
                validate_column_names=False,
            )

        msg = f"Unsupported `backend` value: {backend}"  # pragma: no cover
        raise ValueError(msg)  # pragma: no cover

    def group_by(self: Self, *by: str, drop_null_keys: bool) -> PolarsLazyGroupBy:
        from narwhals._polars.group_by import PolarsLazyGroupBy

        return PolarsLazyGroupBy(self, list(by), drop_null_keys=drop_null_keys)

    def with_row_index(self: Self, name: str) -> Self:
        if self._backend_version < (0, 20, 4):
            return self._from_native_frame(self._native_frame.with_row_count(name))
        return self._from_native_frame(self._native_frame.with_row_index(name))

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        if self._backend_version < (1, 0, 0):
            return self._from_native_frame(self._native_frame.drop(columns))
        return self._from_native_frame(self._native_frame.drop(columns, strict=strict))

    def unpivot(
        self: Self,
        on: list[str] | None,
        index: list[str] | None,
        variable_name: str,
        value_name: str,
    ) -> Self:
        if self._backend_version < (1, 0, 0):
            return self._from_native_frame(
                self._native_frame.melt(
                    id_vars=index,
                    value_vars=on,
                    variable_name=variable_name,
                    value_name=value_name,
                )
            )
        return self._from_native_frame(
            self._native_frame.unpivot(
                on=on, index=index, variable_name=variable_name, value_name=value_name
            )
        )

    def simple_select(self, *column_names: str) -> Self:
        return self._from_native_frame(self._native_frame.select(*column_names))

    def aggregate(self: Self, *exprs: Any) -> Self:
        return self.select(*exprs)  # type: ignore[no-any-return]
