from __future__ import annotations

import warnings
from importlib import import_module
from typing import TYPE_CHECKING
from typing import Any
from typing import Iterator
from typing import Literal
from typing import Sequence
from typing import cast

from narwhals._spark_like.utils import evaluate_exprs
from narwhals._spark_like.utils import native_to_narwhals_dtype
from narwhals.exceptions import InvalidOperationError
from narwhals.typing import CompliantDataFrame
from narwhals.typing import CompliantLazyFrame
from narwhals.utils import Implementation
from narwhals.utils import check_column_exists
from narwhals.utils import find_stacklevel
from narwhals.utils import import_dtypes_module
from narwhals.utils import parse_columns_to_drop
from narwhals.utils import parse_version
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from types import ModuleType

    import pyarrow as pa
    from pyspark.sql import Column
    from pyspark.sql import DataFrame
    from pyspark.sql import Window
    from pyspark.sql.session import SparkSession
    from sqlframe.base.dataframe import BaseDataFrame as _SQLFrameDataFrame
    from typing_extensions import Self
    from typing_extensions import TypeAlias

    from narwhals._spark_like.expr import SparkLikeExpr
    from narwhals._spark_like.group_by import SparkLikeLazyGroupBy
    from narwhals._spark_like.namespace import SparkLikeNamespace
    from narwhals.dtypes import DType
    from narwhals.utils import Version

    SQLFrameDataFrame: TypeAlias = _SQLFrameDataFrame[Any, Any, Any, Any, Any]
    _NativeDataFrame: TypeAlias = "DataFrame | SQLFrameDataFrame"

Incomplete: TypeAlias = Any  # pragma: no cover
"""Marker for working code that fails type checking."""


class SparkLikeLazyFrame(CompliantLazyFrame):
    def __init__(
        self: Self,
        native_dataframe: _NativeDataFrame,
        *,
        backend_version: tuple[int, ...],
        version: Version,
        implementation: Implementation,
        # Unused, just for compatibility. We only validate when collecting.
        validate_column_names: bool = False,
    ) -> None:
        self._native_frame = native_dataframe
        self._backend_version = backend_version
        self._implementation = implementation
        self._version = version
        self._cached_schema: dict[str, DType] | None = None
        validate_backend_version(self._implementation, self._backend_version)

    @property
    def _F(self: Self):  # type: ignore[no-untyped-def] # noqa: ANN202, N802
        if TYPE_CHECKING:
            from pyspark.sql import functions

            return functions
        if self._implementation is Implementation.SQLFRAME:
            from sqlframe.base.session import _BaseSession

            return import_module(
                f"sqlframe.{_BaseSession().execution_dialect_name}.functions"
            )

        from pyspark.sql import functions

        return functions

    @property
    def _native_dtypes(self: Self):  # type: ignore[no-untyped-def] # noqa: ANN202
        if TYPE_CHECKING:
            from pyspark.sql import types

            return types

        if self._implementation is Implementation.SQLFRAME:
            from sqlframe.base.session import _BaseSession

            return import_module(
                f"sqlframe.{_BaseSession().execution_dialect_name}.types"
            )

        from pyspark.sql import types

        return types

    @property
    def _Window(self: Self) -> type[Window]:  # noqa: N802
        if self._implementation is Implementation.SQLFRAME:
            from sqlframe.base.session import _BaseSession

            _window = import_module(
                f"sqlframe.{_BaseSession().execution_dialect_name}.window"
            )
            return _window.Window

        from pyspark.sql import Window

        return Window

    @property
    def _session(self: Self) -> SparkSession:
        if self._implementation is Implementation.SQLFRAME:
            return cast("SQLFrameDataFrame", self._native_frame).session

        return cast("DataFrame", self._native_frame).sparkSession

    def __native_namespace__(self: Self) -> ModuleType:  # pragma: no cover
        return self._implementation.to_native_namespace()

    def __narwhals_namespace__(self: Self) -> SparkLikeNamespace:
        from narwhals._spark_like.namespace import SparkLikeNamespace

        return SparkLikeNamespace(
            backend_version=self._backend_version,
            version=self._version,
            implementation=self._implementation,
        )

    def __narwhals_lazyframe__(self: Self) -> Self:
        return self

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_frame,
            backend_version=self._backend_version,
            version=version,
            implementation=self._implementation,
        )

    def _from_native_frame(self: Self, df: DataFrame) -> Self:
        return self.__class__(
            df,
            backend_version=self._backend_version,
            version=self._version,
            implementation=self._implementation,
        )

    def _collect_to_arrow(self) -> pa.Table:
        if self._implementation is Implementation.PYSPARK and self._backend_version < (
            4,
        ):
            import pyarrow as pa  # ignore-banned-import

            native_frame = cast("DataFrame", self._native_frame)
            try:
                return pa.Table.from_batches(native_frame._collect_as_arrow())
            except ValueError as exc:
                if "at least one RecordBatch" in str(exc):
                    # Empty dataframe
                    from narwhals._arrow.utils import narwhals_to_native_dtype

                    data: dict[str, list[Any]] = {}
                    schema: list[tuple[str, pa.DataType]] = []
                    current_schema = self.collect_schema()
                    for key, value in current_schema.items():
                        data[key] = []
                        try:
                            native_dtype = narwhals_to_native_dtype(value, self._version)
                        except Exception as exc:  # noqa: BLE001
                            native_spark_dtype = native_frame.schema[key].dataType
                            # If we can't convert the type, just set it to `pa.null`, and warn.
                            # Avoid the warning if we're starting from PySpark's void type.
                            # We can avoid the check when we introduce `nw.Null` dtype.
                            if not isinstance(
                                native_spark_dtype, self._native_dtypes.NullType
                            ):
                                warnings.warn(
                                    f"Could not convert dtype {native_spark_dtype} to PyArrow dtype, {exc!r}",
                                    stacklevel=find_stacklevel(),
                                )
                            schema.append((key, pa.null()))
                        else:
                            schema.append((key, native_dtype))
                    return pa.Table.from_pydict(data, schema=pa.schema(schema))
                else:  # pragma: no cover
                    raise
        else:
            # NOTE: See https://github.com/narwhals-dev/narwhals/pull/2051#discussion_r1969224309
            to_arrow: Incomplete = self._native_frame.toArrow
            return to_arrow()

    def _iter_columns(self) -> Iterator[Column]:
        for col in self.columns:
            yield self._F.col(col)

    @property
    def columns(self: Self) -> list[str]:
        return list(self.schema)

    def collect(
        self: Self,
        backend: ModuleType | Implementation | str | None,
        **kwargs: Any,
    ) -> CompliantDataFrame[Any]:
        if backend is Implementation.PANDAS:
            import pandas as pd  # ignore-banned-import

            from narwhals._pandas_like.dataframe import PandasLikeDataFrame

            return PandasLikeDataFrame(
                native_dataframe=self._native_frame.toPandas(),
                implementation=Implementation.PANDAS,
                backend_version=parse_version(pd),
                version=self._version,
                validate_column_names=True,
            )

        elif backend is None or backend is Implementation.PYARROW:
            import pyarrow as pa  # ignore-banned-import

            from narwhals._arrow.dataframe import ArrowDataFrame

            return ArrowDataFrame(
                self._collect_to_arrow(),
                backend_version=parse_version(pa),
                version=self._version,
                validate_column_names=True,
            )

        elif backend is Implementation.POLARS:
            import polars as pl  # ignore-banned-import
            import pyarrow as pa  # ignore-banned-import

            from narwhals._polars.dataframe import PolarsDataFrame

            return PolarsDataFrame(
                df=pl.from_arrow(self._collect_to_arrow()),  # type: ignore[arg-type]
                backend_version=parse_version(pl),
                version=self._version,
            )

        msg = f"Unsupported `backend` value: {backend}"  # pragma: no cover
        raise ValueError(msg)  # pragma: no cover

    def simple_select(self: Self, *column_names: str) -> Self:
        return self._from_native_frame(self._native_frame.select(*column_names))

    def aggregate(
        self: Self,
        *exprs: SparkLikeExpr,
    ) -> Self:
        new_columns = evaluate_exprs(self, *exprs)

        new_columns_list = [col.alias(col_name) for col_name, col in new_columns]
        return self._from_native_frame(self._native_frame.agg(*new_columns_list))

    def select(
        self: Self,
        *exprs: SparkLikeExpr,
    ) -> Self:
        new_columns = evaluate_exprs(self, *exprs)

        if not new_columns:
            # return empty dataframe, like Polars does
            schema = self._native_dtypes.StructType([])
            spark_df = self._session.createDataFrame([], schema)
            return self._from_native_frame(spark_df)

        new_columns_list = [col.alias(col_name) for (col_name, col) in new_columns]
        return self._from_native_frame(self._native_frame.select(*new_columns_list))

    def with_columns(self: Self, *exprs: SparkLikeExpr) -> Self:
        new_columns = evaluate_exprs(self, *exprs)
        return self._from_native_frame(self._native_frame.withColumns(dict(new_columns)))

    def filter(self: Self, predicate: SparkLikeExpr) -> Self:
        # `[0]` is safe as the predicate's expression only returns a single column
        condition = predicate._call(self)[0]
        spark_df = self._native_frame.where(condition)
        return self._from_native_frame(spark_df)

    @property
    def schema(self: Self) -> dict[str, DType]:
        if self._cached_schema is None:
            self._cached_schema = {
                field.name: native_to_narwhals_dtype(
                    dtype=field.dataType,
                    version=self._version,
                    # NOTE: Unclear if this is an unsafe hash (https://github.com/narwhals-dev/narwhals/pull/2051#discussion_r1970074662)
                    spark_types=self._native_dtypes,  # pyright: ignore[reportArgumentType]
                )
                for field in self._native_frame.schema
            }
        return self._cached_schema

    def collect_schema(self: Self) -> dict[str, DType]:
        return self.schema

    def drop(self: Self, columns: list[str], strict: bool) -> Self:  # noqa: FBT001
        columns_to_drop = parse_columns_to_drop(
            compliant_frame=self, columns=columns, strict=strict
        )
        return self._from_native_frame(self._native_frame.drop(*columns_to_drop))

    def head(self: Self, n: int) -> Self:
        return self._from_native_frame(self._native_frame.limit(num=n))

    def group_by(self: Self, *keys: str, drop_null_keys: bool) -> SparkLikeLazyGroupBy:
        from narwhals._spark_like.group_by import SparkLikeLazyGroupBy

        return SparkLikeLazyGroupBy(
            compliant_frame=self, keys=list(keys), drop_null_keys=drop_null_keys
        )

    def sort(
        self: Self,
        *by: str,
        descending: bool | Sequence[bool],
        nulls_last: bool,
    ) -> Self:
        if isinstance(descending, bool):
            descending = [descending] * len(by)

        if nulls_last:
            sort_funcs = (
                self._F.desc_nulls_last if d else self._F.asc_nulls_last
                for d in descending
            )
        else:
            sort_funcs = (
                self._F.desc_nulls_first if d else self._F.asc_nulls_first
                for d in descending
            )

        sort_cols = [sort_f(col) for col, sort_f in zip(by, sort_funcs)]
        return self._from_native_frame(self._native_frame.sort(*sort_cols))

    def drop_nulls(self: Self, subset: list[str] | None) -> Self:
        return self._from_native_frame(self._native_frame.dropna(subset=subset))

    def rename(self: Self, mapping: dict[str, str]) -> Self:
        rename_mapping = {
            colname: mapping.get(colname, colname) for colname in self.columns
        }
        return self._from_native_frame(
            self._native_frame.select(
                [self._F.col(old).alias(new) for old, new in rename_mapping.items()]
            )
        )

    def unique(
        self: Self,
        subset: list[str] | None,
        *,
        keep: Literal["any", "none"],
    ) -> Self:
        if keep != "any":
            msg = "`LazyFrame.unique` with PySpark backend only supports `keep='any'`."
            raise ValueError(msg)
        check_column_exists(self.columns, subset)
        return self._from_native_frame(self._native_frame.dropDuplicates(subset=subset))

    def join(
        self: Self,
        other: Self,
        how: Literal["inner", "left", "cross", "semi", "anti"],
        left_on: list[str] | None,
        right_on: list[str] | None,
        suffix: str,
    ) -> Self:
        self_native = self._native_frame
        other_native = other._native_frame

        left_columns = self.columns
        right_columns = other.columns

        # create a mapping for columns on other
        # `right_on` columns will be renamed as `left_on`
        # the remaining columns will be either added the suffix or left unchanged.
        rename_mapping = {
            **dict(zip(right_on or [], left_on or [])),
            **{
                colname: f"{colname}{suffix}" if colname in left_columns else colname
                for colname in list(set(right_columns).difference(set(right_on or [])))
            },
        }
        other_native = other_native.select(
            [self._F.col(old).alias(new) for old, new in rename_mapping.items()]
        )

        # If how in {"semi", "anti"}, then resulting columns are same as left columns
        # Otherwise, we add the right columns with the new mapping, while keeping the
        # original order of right_columns.
        col_order = left_columns

        if how in {"inner", "left", "cross"}:
            col_order.extend(
                [
                    rename_mapping[colname]
                    for colname in right_columns
                    if colname not in (right_on or [])
                ]
            )
        return self._from_native_frame(
            self_native.join(other_native, on=left_on, how=how).select(col_order)
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

        native_frame = self._native_frame
        column_names = self.columns

        if len(columns) != 1:
            msg = (
                "Exploding on multiple columns is not supported with SparkLike backend since "
                "we cannot guarantee that the exploded columns have matching element counts."
            )
            raise NotImplementedError(msg)

        if self._implementation.is_pyspark():
            return self._from_native_frame(
                native_frame.select(
                    *[
                        self._F.col(col_name).alias(col_name)
                        if col_name != columns[0]
                        else self._F.explode_outer(col_name).alias(col_name)
                        for col_name in column_names
                    ]
                ),
            )
        elif self._implementation.is_sqlframe():
            # Not every sqlframe dialect supports `explode_outer` function
            # (see https://github.com/eakmanrq/sqlframe/blob/3cb899c515b101ff4c197d84b34fae490d0ed257/sqlframe/base/functions.py#L2288-L2289)
            # therefore we simply explode the array column which will ignore nulls and
            # zero sized arrays, and append these specific condition with nulls (to
            # match polars behavior).

            def null_condition(col_name: str) -> Column:
                return self._F.isnull(col_name) | (self._F.array_size(col_name) == 0)

            return self._from_native_frame(
                native_frame.select(
                    *[
                        self._F.col(col_name).alias(col_name)
                        if col_name != columns[0]
                        else self._F.explode(col_name).alias(col_name)
                        for col_name in column_names
                    ]
                ).union(
                    native_frame.filter(null_condition(columns[0])).select(
                        *[
                            self._F.col(col_name).alias(col_name)
                            if col_name != columns[0]
                            else self._F.lit(None).alias(col_name)
                            for col_name in column_names
                        ]
                    )
                ),
            )
        else:  # pragma: no cover
            msg = "Unreachable code, please report an issue at https://github.com/narwhals-dev/narwhals/issues"
            raise AssertionError(msg)

    def unpivot(
        self: Self,
        on: list[str] | None,
        index: list[str] | None,
        variable_name: str,
        value_name: str,
    ) -> Self:
        if self._implementation.is_sqlframe():
            if variable_name == "":
                msg = "`variable_name` cannot be empty string for sqlframe backend."
                raise NotImplementedError(msg)

            if value_name == "":
                msg = "`value_name` cannot be empty string for sqlframe backend."
                raise NotImplementedError(msg)

        ids = tuple(self.columns) if index is None else tuple(index)
        values = (
            tuple(set(self.columns).difference(set(ids))) if on is None else tuple(on)
        )
        unpivoted_native_frame = self._native_frame.unpivot(
            ids=ids,
            values=values,
            variableColumnName=variable_name,
            valueColumnName=value_name,
        )
        if index is None:
            unpivoted_native_frame = unpivoted_native_frame.drop(*ids)
        return self._from_native_frame(unpivoted_native_frame)
