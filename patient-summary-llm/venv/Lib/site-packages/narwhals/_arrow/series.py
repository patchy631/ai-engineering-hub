from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Iterable
from typing import Iterator
from typing import Literal
from typing import Sequence
from typing import cast
from typing import overload

import pyarrow as pa
import pyarrow.compute as pc

from narwhals._arrow.series_cat import ArrowSeriesCatNamespace
from narwhals._arrow.series_dt import ArrowSeriesDateTimeNamespace
from narwhals._arrow.series_list import ArrowSeriesListNamespace
from narwhals._arrow.series_str import ArrowSeriesStringNamespace
from narwhals._arrow.series_struct import ArrowSeriesStructNamespace
from narwhals._arrow.utils import cast_for_truediv
from narwhals._arrow.utils import chunked_array
from narwhals._arrow.utils import extract_native
from narwhals._arrow.utils import floordiv_compat
from narwhals._arrow.utils import lit
from narwhals._arrow.utils import narwhals_to_native_dtype
from narwhals._arrow.utils import native_to_narwhals_dtype
from narwhals._arrow.utils import nulls_like
from narwhals._arrow.utils import pad_series
from narwhals.exceptions import InvalidOperationError
from narwhals.typing import CompliantSeries
from narwhals.utils import Implementation
from narwhals.utils import _StoresNative
from narwhals.utils import generate_temporary_column_name
from narwhals.utils import import_dtypes_module
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from types import ModuleType

    import pandas as pd
    import polars as pl
    from typing_extensions import Self

    from narwhals._arrow.dataframe import ArrowDataFrame
    from narwhals._arrow.namespace import ArrowNamespace
    from narwhals._arrow.typing import ArrowArray
    from narwhals._arrow.typing import ArrowChunkedArray
    from narwhals._arrow.typing import Incomplete
    from narwhals._arrow.typing import Indices  # type: ignore[attr-defined]
    from narwhals._arrow.typing import NullPlacement
    from narwhals._arrow.typing import Order  # type: ignore[attr-defined]
    from narwhals._arrow.typing import TieBreaker
    from narwhals._arrow.typing import _AsPyType
    from narwhals._arrow.typing import _BasicDataType
    from narwhals.dtypes import DType
    from narwhals.typing import _1DArray
    from narwhals.typing import _2DArray
    from narwhals.utils import Version


# TODO @dangotbanned: move into `_arrow.utils`
# Lots of modules are importing inline
@overload
def maybe_extract_py_scalar(
    value: pa.Scalar[_BasicDataType[_AsPyType]],
    return_py_scalar: bool,  # noqa: FBT001
) -> _AsPyType: ...


@overload
def maybe_extract_py_scalar(
    value: pa.Scalar[pa.StructType],
    return_py_scalar: bool,  # noqa: FBT001
) -> list[dict[str, Any]]: ...


@overload
def maybe_extract_py_scalar(
    value: pa.Scalar[pa.ListType[_BasicDataType[_AsPyType]]],
    return_py_scalar: bool,  # noqa: FBT001
) -> list[_AsPyType]: ...


@overload
def maybe_extract_py_scalar(
    value: pa.Scalar[Any] | Any,
    return_py_scalar: bool,  # noqa: FBT001
) -> Any: ...


def maybe_extract_py_scalar(value: Any, return_py_scalar: bool) -> Any:  # noqa: FBT001
    if TYPE_CHECKING:
        return value.as_py()
    if return_py_scalar:
        return getattr(value, "as_py", lambda: value)()
    return value


class ArrowSeries(CompliantSeries, _StoresNative["ArrowChunkedArray"]):
    def __init__(
        self: Self,
        native_series: ArrowChunkedArray,
        *,
        name: str,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._name = name
        self._native_series: ArrowChunkedArray = native_series
        self._implementation = Implementation.PYARROW
        self._backend_version = backend_version
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)
        self._broadcast = False

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self.native,
            name=self._name,
            backend_version=self._backend_version,
            version=version,
        )

    def _from_native_series(
        self: Self,
        series: ArrowArray | ArrowChunkedArray,
    ) -> Self:
        return self.__class__(
            chunked_array(series),
            name=self._name,
            backend_version=self._backend_version,
            version=self._version,
        )

    @classmethod
    def _from_iterable(
        cls: type[Self],
        data: Iterable[Any],
        name: str,
        *,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> Self:
        return cls(
            chunked_array([data]),
            name=name,
            backend_version=backend_version,
            version=version,
        )

    def __narwhals_namespace__(self: Self) -> ArrowNamespace:
        from narwhals._arrow.namespace import ArrowNamespace

        return ArrowNamespace(
            backend_version=self._backend_version, version=self._version
        )

    def __len__(self: Self) -> int:
        return len(self.native)

    def __eq__(self: Self, other: object) -> Self:  # type: ignore[override]
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.equal(ser, other))  # type: ignore[arg-type]

    def __ne__(self: Self, other: object) -> Self:  # type: ignore[override]
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.not_equal(ser, other))  # type: ignore[arg-type]

    def __ge__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.greater_equal(ser, other))

    def __gt__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.greater(ser, other))

    def __le__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.less_equal(ser, other))

    def __lt__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.less(ser, other))

    def __and__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.and_kleene(ser, other))  # type: ignore[arg-type]

    def __rand__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.and_kleene(other, ser))  # type: ignore[arg-type]

    def __or__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.or_kleene(ser, other))  # type: ignore[arg-type]

    def __ror__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.or_kleene(other, ser))  # type: ignore[arg-type]

    def __add__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.add(ser, other))

    def __radd__(self: Self, other: Any) -> Self:
        return self + other

    def __sub__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.subtract(ser, other))

    def __rsub__(self: Self, other: Any) -> Self:
        return (self - other) * (-1)

    def __mul__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.multiply(ser, other))

    def __rmul__(self: Self, other: Any) -> Self:
        return self * other

    def __pow__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.power(ser, other))

    def __rpow__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(pc.power(other, ser))

    def __floordiv__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(floordiv_compat(ser, other))

    def __rfloordiv__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        return self._from_native_series(floordiv_compat(other, ser))

    def __truediv__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        if not isinstance(other, (pa.Array, pa.ChunkedArray)):
            # scalar
            other = lit(other)
        return self._from_native_series(pc.divide(*cast_for_truediv(ser, other)))

    def __rtruediv__(self: Self, other: Any) -> Self:
        ser, other = extract_native(self, other)
        if not isinstance(other, (pa.Array, pa.ChunkedArray)):
            # scalar
            other = lit(other) if not isinstance(other, pa.Scalar) else other
        return self._from_native_series(pc.divide(*cast_for_truediv(other, ser)))  # pyright: ignore[reportArgumentType]

    def __mod__(self: Self, other: Any) -> Self:
        floor_div = (self // other)._native_series
        ser, other = extract_native(self, other)
        res = pc.subtract(ser, pc.multiply(floor_div, other))
        return self._from_native_series(res)

    def __rmod__(self: Self, other: Any) -> Self:
        floor_div = (other // self)._native_series
        ser, other = extract_native(self, other)
        res = pc.subtract(other, pc.multiply(floor_div, ser))
        return self._from_native_series(res)

    def __invert__(self: Self) -> Self:
        return self._from_native_series(pc.invert(self.native))  # type: ignore[call-overload]

    @property
    def _type(self: Self) -> pa.DataType:
        return self.native.type

    @property
    def native(self) -> ArrowChunkedArray:
        return self._native_series

    def len(self: Self, *, _return_py_scalar: bool = True) -> int:
        return maybe_extract_py_scalar(len(self.native), _return_py_scalar)

    def filter(self: Self, predicate: ArrowSeries | list[bool | None]) -> Self:
        if not (
            isinstance(predicate, list) and all(isinstance(x, bool) for x in predicate)
        ):
            _, other_native = extract_native(self, predicate)
        else:
            other_native = predicate
        return self._from_native_series(self.native.filter(other_native))  # pyright: ignore[reportArgumentType]

    def mean(self: Self, *, _return_py_scalar: bool = True) -> float:
        # NOTE: stub overly strict https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L274-L307
        # docs say numeric https://arrow.apache.org/docs/python/generated/pyarrow.compute.mean.html
        mean: Incomplete = pc.mean
        return maybe_extract_py_scalar(mean(self.native), _return_py_scalar)

    def median(self: Self, *, _return_py_scalar: bool = True) -> float:
        from narwhals.exceptions import InvalidOperationError

        if not self.dtype.is_numeric():
            msg = "`median` operation not supported for non-numeric input type."
            raise InvalidOperationError(msg)

        return maybe_extract_py_scalar(
            pc.approximate_median(self.native), _return_py_scalar
        )

    def min(self: Self, *, _return_py_scalar: bool = True) -> Any:
        return maybe_extract_py_scalar(pc.min(self.native), _return_py_scalar)

    def max(self: Self, *, _return_py_scalar: bool = True) -> Any:
        return maybe_extract_py_scalar(pc.max(self.native), _return_py_scalar)

    def arg_min(self: Self, *, _return_py_scalar: bool = True) -> int:
        index_min = pc.index(self.native, pc.min(self.native))
        return maybe_extract_py_scalar(index_min, _return_py_scalar)

    def arg_max(self: Self, *, _return_py_scalar: bool = True) -> int:
        index_max = pc.index(self.native, pc.max(self.native))
        return maybe_extract_py_scalar(index_max, _return_py_scalar)

    def sum(self: Self, *, _return_py_scalar: bool = True) -> float:
        return maybe_extract_py_scalar(
            pc.sum(self.native, min_count=0), _return_py_scalar
        )

    def drop_nulls(self: Self) -> Self:
        return self._from_native_series(self.native.drop_null())

    def shift(self: Self, n: int) -> Self:
        if n > 0:
            arrays = [nulls_like(n, self), *self.native[:-n].chunks]
        elif n < 0:
            arrays = [*self.native[-n:].chunks, nulls_like(-n, self)]
        else:
            return self._from_native_series(self.native)
        return self._from_native_series(pa.concat_arrays(arrays))

    def std(self: Self, ddof: int, *, _return_py_scalar: bool = True) -> float:
        return maybe_extract_py_scalar(
            pc.stddev(self.native, ddof=ddof), _return_py_scalar
        )

    def var(self: Self, ddof: int, *, _return_py_scalar: bool = True) -> float:
        return maybe_extract_py_scalar(
            pc.variance(self.native, ddof=ddof), _return_py_scalar
        )

    def skew(self: Self, *, _return_py_scalar: bool = True) -> float | None:
        # NOTE: stub issue with `pc.subtract`, `pc.mean` and `pa.ChunkedArray`
        ser_not_null: Incomplete = self.native.drop_null()
        if len(ser_not_null) == 0:
            return None
        elif len(ser_not_null) == 1:
            return float("nan")
        elif len(ser_not_null) == 2:
            return 0.0
        else:
            m = cast(
                "pc.NumericArray[Any]", pc.subtract(ser_not_null, pc.mean(ser_not_null))
            )
            m2 = pc.mean(pc.power(m, lit(2)))
            m3 = pc.mean(pc.power(m, lit(3)))
            biased_population_skewness = pc.divide(m3, pc.power(m2, lit(1.5)))
            return maybe_extract_py_scalar(biased_population_skewness, _return_py_scalar)

    def count(self: Self, *, _return_py_scalar: bool = True) -> int:
        return maybe_extract_py_scalar(pc.count(self.native), _return_py_scalar)

    def n_unique(self: Self, *, _return_py_scalar: bool = True) -> int:
        return maybe_extract_py_scalar(
            pc.count(self.native.unique(), mode="all"), _return_py_scalar
        )

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.PYARROW:
            return self._implementation.to_native_namespace()

        msg = f"Expected pyarrow, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    @property
    def name(self: Self) -> str:
        return self._name

    def __narwhals_series__(self: Self) -> Self:
        return self

    @overload
    def __getitem__(self: Self, idx: int) -> Any: ...

    @overload
    def __getitem__(
        self: Self, idx: slice | Sequence[int] | ArrowChunkedArray
    ) -> Self: ...

    def __getitem__(
        self: Self, idx: int | slice | Sequence[int] | ArrowChunkedArray
    ) -> Any | Self:
        if isinstance(idx, int):
            return maybe_extract_py_scalar(self.native[idx], return_py_scalar=True)
        if isinstance(idx, (Sequence, pa.ChunkedArray)):
            return self._from_native_series(self.native.take(cast("Indices", idx)))
        return self._from_native_series(self.native[idx])

    def scatter(self: Self, indices: int | Sequence[int], values: Any) -> Self:
        import numpy as np  # ignore-banned-import

        if isinstance(indices, int):
            indices_native = pa.array([indices])
            values_native = pa.array([values])
        else:
            # TODO(unassigned): we may also want to let `indices` be a Series.
            # https://github.com/narwhals-dev/narwhals/issues/2155
            indices_native = pa.array(indices)
            if isinstance(values, self.__class__):
                values_native = values.native.combine_chunks()
            else:
                values_native = pa.array(values)

        sorting_indices = pc.sort_indices(indices_native)  # type: ignore[call-overload]
        indices_native = pc.take(indices_native, sorting_indices)
        values_native = pc.take(values_native, sorting_indices)

        mask: _1DArray = np.zeros(self.len(), dtype=bool)
        mask[indices_native] = True
        result = pc.replace_with_mask(
            self.native,
            cast("list[bool]", mask),
            values_native.take(cast("Indices", indices_native)),
        )
        return self._from_native_series(result)

    def to_list(self: Self) -> list[Any]:
        return self.native.to_pylist()

    def __array__(self: Self, dtype: Any = None, *, copy: bool | None = None) -> _1DArray:
        return self.native.__array__(dtype=dtype, copy=copy)

    def to_numpy(self: Self) -> _1DArray:
        return self.native.to_numpy()

    def alias(self: Self, name: str) -> Self:
        return self.__class__(
            self.native,
            name=name,
            backend_version=self._backend_version,
            version=self._version,
        )

    @property
    def dtype(self: Self) -> DType:
        return native_to_narwhals_dtype(self.native.type, self._version)

    def abs(self: Self) -> Self:
        return self._from_native_series(pc.abs(self.native))

    def cum_sum(self: Self, *, reverse: bool) -> Self:
        # NOTE: stub only permits `NumericArray`
        # https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L140
        cum_sum: Incomplete = pc.cumulative_sum
        result = (
            cum_sum(self.native, skip_nulls=True)
            if not reverse
            else cum_sum(self.native[::-1], skip_nulls=True)[::-1]
        )
        return self._from_native_series(result)

    def round(self: Self, decimals: int) -> Self:
        # NOTE: stub only permits `NumericArray`
        # https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L140
        pc_round: Incomplete = pc.round
        return self._from_native_series(
            pc_round(self.native, decimals, round_mode="half_towards_infinity")
        )

    def diff(self: Self) -> Self:
        # NOTE: stub only permits `ChunkedArray[TemporalScalar]`
        # (https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L145-L148)
        diff: Incomplete = pc.pairwise_diff
        return self._from_native_series(diff(self.native.combine_chunks()))

    def any(self: Self, *, _return_py_scalar: bool = True) -> bool:
        # NOTE: stub restricts to `BooleanArray`, should be based on truthiness
        # Copies `pc.all`
        pc_any: Incomplete = pc.any
        return maybe_extract_py_scalar(
            pc_any(self.native, min_count=0), _return_py_scalar
        )

    def all(self: Self, *, _return_py_scalar: bool = True) -> bool:
        # NOTE: stub restricts to `BooleanArray`, should be based on truthiness
        pc_all: Incomplete = pc.all
        return maybe_extract_py_scalar(
            pc_all(self.native, min_count=0), _return_py_scalar
        )

    def is_between(
        self: Self,
        lower_bound: Any,
        upper_bound: Any,
        closed: Literal["left", "right", "none", "both"],
    ) -> Self:
        _, lower_bound = extract_native(self, lower_bound)
        _, upper_bound = extract_native(self, upper_bound)
        if closed == "left":
            ge = pc.greater_equal(self.native, lower_bound)
            lt = pc.less(self.native, upper_bound)
            res = pc.and_kleene(ge, lt)
        elif closed == "right":
            gt = pc.greater(self.native, lower_bound)
            le = pc.less_equal(self.native, upper_bound)
            res = pc.and_kleene(gt, le)
        elif closed == "none":
            gt = pc.greater(self.native, lower_bound)
            lt = pc.less(self.native, upper_bound)
            res = pc.and_kleene(gt, lt)
        elif closed == "both":
            ge = pc.greater_equal(self.native, lower_bound)
            le = pc.less_equal(self.native, upper_bound)
            res = pc.and_kleene(ge, le)
        else:  # pragma: no cover
            raise AssertionError
        return self._from_native_series(res)

    def is_null(self: Self) -> Self:
        return self._from_native_series(self.native.is_null())

    def is_nan(self: Self) -> Self:
        return self._from_native_series(pc.is_nan(self.native))

    def cast(self: Self, dtype: DType | type[DType]) -> Self:
        data_type = narwhals_to_native_dtype(dtype, self._version)
        return self._from_native_series(pc.cast(self.native, data_type))

    def null_count(self: Self, *, _return_py_scalar: bool = True) -> int:
        return maybe_extract_py_scalar(self.native.null_count, _return_py_scalar)

    def head(self: Self, n: int) -> Self:
        if n >= 0:
            return self._from_native_series(self.native.slice(0, n))
        else:
            num_rows = len(self)
            return self._from_native_series(self.native.slice(0, max(0, num_rows + n)))

    def tail(self: Self, n: int) -> Self:
        if n >= 0:
            num_rows = len(self)
            return self._from_native_series(self.native.slice(max(0, num_rows - n)))
        else:
            return self._from_native_series(self.native.slice(abs(n)))

    def is_in(self: Self, other: Any) -> Self:
        if isinstance(other, pa.ChunkedArray):
            value_set: ArrowChunkedArray | ArrowArray = other
        else:
            value_set = pa.array(other)
        return self._from_native_series(pc.is_in(self.native, value_set=value_set))

    def arg_true(self: Self) -> Self:
        import numpy as np  # ignore-banned-import

        res = np.flatnonzero(self.native)
        return self._from_iterable(
            res,
            name=self.name,
            backend_version=self._backend_version,
            version=self._version,
        )

    def item(self: Self, index: int | None = None) -> Any:
        if index is None:
            if len(self) != 1:
                msg = (
                    "can only call '.item()' if the Series is of length 1,"
                    f" or an explicit index is provided (Series is of length {len(self)})"
                )
                raise ValueError(msg)
            return maybe_extract_py_scalar(self.native[0], return_py_scalar=True)
        return maybe_extract_py_scalar(self.native[index], return_py_scalar=True)

    def value_counts(
        self: Self,
        *,
        sort: bool,
        parallel: bool,
        name: str | None,
        normalize: bool,
    ) -> ArrowDataFrame:
        """Parallel is unused, exists for compatibility."""
        from narwhals._arrow.dataframe import ArrowDataFrame

        index_name_ = "index" if self._name is None else self._name
        value_name_ = name or ("proportion" if normalize else "count")

        val_counts = pc.value_counts(self.native)
        values = val_counts.field("values")
        counts = cast("ArrowChunkedArray", val_counts.field("counts"))

        if normalize:
            arrays = [values, pc.divide(*cast_for_truediv(counts, pc.sum(counts)))]
        else:
            arrays = [values, counts]

        val_count = pa.Table.from_arrays(arrays, names=[index_name_, value_name_])

        if sort:
            val_count = val_count.sort_by([(value_name_, "descending")])

        return ArrowDataFrame(
            val_count,
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=True,
        )

    def zip_with(self: Self, mask: Self, other: Self) -> Self:
        cond = mask.native.combine_chunks()
        return self._from_native_series(pc.if_else(cond, self.native, other.native))

    def sample(
        self: Self,
        n: int | None,
        *,
        fraction: float | None,
        with_replacement: bool,
        seed: int | None,
    ) -> Self:
        import numpy as np  # ignore-banned-import

        num_rows = len(self)
        if n is None and fraction is not None:
            n = int(num_rows * fraction)

        rng = np.random.default_rng(seed=seed)
        idx = np.arange(0, num_rows)
        mask = rng.choice(idx, size=n, replace=with_replacement)
        return self._from_native_series(self.native.take(mask))  # pyright: ignore[reportArgumentType]

    def fill_null(
        self: Self,
        value: Any | None,
        strategy: Literal["forward", "backward"] | None,
        limit: int | None,
    ) -> Self:
        import numpy as np  # ignore-banned-import

        def fill_aux(
            arr: ArrowArray | ArrowChunkedArray,
            limit: int,
            direction: Literal["forward", "backward"] | None = None,
        ) -> ArrowArray:
            # this algorithm first finds the indices of the valid values to fill all the null value positions
            # then it calculates the distance of each new index and the original index
            # if the distance is equal to or less than the limit and the original value is null, it is replaced
            valid_mask = pc.is_valid(arr)
            indices = pa.array(np.arange(len(arr)), type=pa.int64())
            if direction == "forward":
                valid_index = np.maximum.accumulate(np.where(valid_mask, indices, -1))
                distance = indices - valid_index
            else:
                valid_index = np.minimum.accumulate(
                    np.where(valid_mask[::-1], indices[::-1], len(arr))
                )[::-1]
                distance = valid_index - indices
            return pc.if_else(
                pc.and_(pc.is_null(arr), pc.less_equal(distance, lit(limit))),
                arr.take(valid_index),
                arr,
            )

        if value is not None:
            _, value = extract_native(self, value)
            series = pc.fill_null(self.native, value)  # type: ignore[attr-defined]
        elif limit is None:
            fill_func = (
                pc.fill_null_forward if strategy == "forward" else pc.fill_null_backward
            )
            series = fill_func(self.native)
        else:
            series = fill_aux(self.native, limit, strategy)
        return self._from_native_series(series)

    def to_frame(self: Self) -> ArrowDataFrame:
        from narwhals._arrow.dataframe import ArrowDataFrame

        df = pa.Table.from_arrays([self.native], names=[self.name])
        return ArrowDataFrame(
            df,
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=False,
        )

    def to_pandas(self: Self) -> pd.Series[Any]:
        import pandas as pd  # ignore-banned-import()

        return pd.Series(self.native, name=self.name)  # pyright: ignore[reportArgumentType, reportCallIssue]

    def to_polars(self: Self) -> pl.Series:
        import polars as pl  # ignore-banned-import

        return pl.from_arrow(self.native)  # type: ignore[return-value]

    def is_unique(self: Self) -> Self:
        return self.to_frame().is_unique().alias(self.name)  # type: ignore[return-value]

    def is_first_distinct(self: Self) -> Self:
        import numpy as np  # ignore-banned-import

        row_number = pa.array(np.arange(len(self)))
        col_token = generate_temporary_column_name(n_bytes=8, columns=[self.name])
        first_distinct_index = (
            pa.Table.from_arrays([self.native], names=[self.name])
            .append_column(col_token, row_number)
            .group_by(self.name)
            .aggregate([(col_token, "min")])
            .column(f"{col_token}_min")
        )

        return self._from_native_series(pc.is_in(row_number, first_distinct_index))

    def is_last_distinct(self: Self) -> Self:
        import numpy as np  # ignore-banned-import

        row_number = pa.array(np.arange(len(self)))
        col_token = generate_temporary_column_name(n_bytes=8, columns=[self.name])
        last_distinct_index = (
            pa.Table.from_arrays([self.native], names=[self.name])
            .append_column(col_token, row_number)
            .group_by(self.name)
            .aggregate([(col_token, "max")])
            .column(f"{col_token}_max")
        )

        return self._from_native_series(pc.is_in(row_number, last_distinct_index))

    def is_sorted(self: Self, *, descending: bool) -> bool:
        if not isinstance(descending, bool):
            msg = f"argument 'descending' should be boolean, found {type(descending)}"
            raise TypeError(msg)
        if descending:
            result = pc.all(pc.greater_equal(self.native[:-1], self.native[1:]))
        else:
            result = pc.all(pc.less_equal(self.native[:-1], self.native[1:]))
        return maybe_extract_py_scalar(result, return_py_scalar=True)

    def unique(self: Self, *, maintain_order: bool) -> Self:
        # TODO(marco): `pc.unique` seems to always maintain order, is that guaranteed?
        return self._from_native_series(self.native.unique())

    def replace_strict(
        self: Self, old: Sequence[Any], new: Sequence[Any], *, return_dtype: DType | None
    ) -> Self:
        # https://stackoverflow.com/a/79111029/4451315
        idxs = pc.index_in(self.native, pa.array(old))
        result_native = pc.take(pa.array(new), idxs)
        if return_dtype is not None:
            result_native.cast(narwhals_to_native_dtype(return_dtype, self._version))
        result = self._from_native_series(result_native)
        if result.is_null().sum() != self.is_null().sum():
            msg = (
                "replace_strict did not replace all non-null values.\n\n"
                "The following did not get replaced: "
                f"{self.filter(~self.is_null() & result.is_null()).unique(maintain_order=False).to_list()}"
            )
            raise ValueError(msg)
        return result

    def sort(self: Self, *, descending: bool, nulls_last: bool) -> Self:
        order: Order = "descending" if descending else "ascending"
        null_placement: NullPlacement = "at_end" if nulls_last else "at_start"
        sorted_indices = pc.array_sort_indices(
            self.native, order=order, null_placement=null_placement
        )
        return self._from_native_series(self.native.take(sorted_indices))

    def to_dummies(self: Self, *, separator: str, drop_first: bool) -> ArrowDataFrame:
        import numpy as np  # ignore-banned-import

        from narwhals._arrow.dataframe import ArrowDataFrame

        name = self._name
        # NOTE: stub is missing attributes (https://arrow.apache.org/docs/python/generated/pyarrow.DictionaryArray.html)
        da: Incomplete = self.native.combine_chunks().dictionary_encode("encode")

        columns: _2DArray = np.zeros((len(da.dictionary), len(da)), np.int8)
        columns[da.indices, np.arange(len(da))] = 1
        null_col_pa, null_col_pl = f"{name}{separator}None", f"{name}{separator}null"
        cols = [
            {null_col_pa: null_col_pl}.get(
                f"{name}{separator}{v}", f"{name}{separator}{v}"
            )
            for v in da.dictionary
        ]

        output_order = (
            [
                null_col_pl,
                *sorted([c for c in cols if c != null_col_pl])[int(drop_first) :],
            ]
            if null_col_pl in cols
            else sorted(cols)[int(drop_first) :]
        )
        return ArrowDataFrame(
            pa.Table.from_arrays(columns, names=cols),
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=True,
        ).simple_select(*output_order)

    def quantile(
        self: Self,
        quantile: float,
        interpolation: Literal["nearest", "higher", "lower", "midpoint", "linear"],
        *,
        _return_py_scalar: bool = True,
    ) -> float:
        return maybe_extract_py_scalar(
            pc.quantile(self.native, q=quantile, interpolation=interpolation)[0],
            _return_py_scalar,
        )

    def gather_every(self: Self, n: int, offset: int = 0) -> Self:
        return self._from_native_series(self.native[offset::n])

    def clip(
        self: Self, lower_bound: Self | Any | None, upper_bound: Self | Any | None
    ) -> Self:
        _, lower_bound = extract_native(self, lower_bound)
        _, upper_bound = extract_native(self, upper_bound)
        # NOTE: stubs are missing `ChunkedArray` support
        # https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L948-L954
        max_element_wise: Incomplete = pc.max_element_wise
        arr = max_element_wise(self.native, lower_bound)
        arr = cast("ArrowChunkedArray", pc.min_element_wise(arr, upper_bound))

        return self._from_native_series(arr)

    def to_arrow(self: Self) -> ArrowArray:
        return self.native.combine_chunks()

    def mode(self: Self) -> Self:
        plx = self.__narwhals_namespace__()
        col_token = generate_temporary_column_name(n_bytes=8, columns=[self.name])
        return self.value_counts(  # type: ignore[return-value]
            name=col_token,
            normalize=False,
            sort=False,
            parallel=False,  # parallel is unused
        ).filter(plx.col(col_token) == plx.col(col_token).max())[self.name]

    def is_finite(self: Self) -> Self:
        return self._from_native_series(pc.is_finite(self.native))

    def cum_count(self: Self, *, reverse: bool) -> Self:
        dtypes = import_dtypes_module(self._version)
        return (~self.is_null()).cast(dtypes.UInt32()).cum_sum(reverse=reverse)

    def cum_min(self: Self, *, reverse: bool) -> Self:
        if self._backend_version < (13, 0, 0):
            msg = "cum_min method is not supported for pyarrow < 13.0.0"
            raise NotImplementedError(msg)

        native_series = cast("Any", self.native)

        result = (
            pc.cumulative_min(native_series, skip_nulls=True)
            if not reverse
            else pc.cumulative_min(native_series[::-1], skip_nulls=True)[::-1]
        )
        return self._from_native_series(result)

    def cum_max(self: Self, *, reverse: bool) -> Self:
        if self._backend_version < (13, 0, 0):
            msg = "cum_max method is not supported for pyarrow < 13.0.0"
            raise NotImplementedError(msg)

        native_series = cast("Any", self.native)

        result = (
            pc.cumulative_max(native_series, skip_nulls=True)
            if not reverse
            else pc.cumulative_max(native_series[::-1], skip_nulls=True)[::-1]
        )
        return self._from_native_series(result)

    def cum_prod(self: Self, *, reverse: bool) -> Self:
        if self._backend_version < (13, 0, 0):
            msg = "cum_max method is not supported for pyarrow < 13.0.0"
            raise NotImplementedError(msg)

        native_series = cast("Any", self.native)

        result = (
            pc.cumulative_prod(native_series, skip_nulls=True)
            if not reverse
            else pc.cumulative_prod(native_series[::-1], skip_nulls=True)[::-1]
        )
        return self._from_native_series(result)

    def rolling_sum(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self:
        min_samples = min_samples if min_samples is not None else window_size
        padded_series, offset = pad_series(self, window_size=window_size, center=center)

        cum_sum = padded_series.cum_sum(reverse=False).fill_null(
            value=None, strategy="forward", limit=None
        )
        rolling_sum = (
            cum_sum
            - cum_sum.shift(window_size).fill_null(value=0, strategy=None, limit=None)
            if window_size != 0
            else cum_sum
        )

        valid_count = padded_series.cum_count(reverse=False)
        count_in_window = valid_count - valid_count.shift(window_size).fill_null(
            value=0, strategy=None, limit=None
        )

        result = self._from_native_series(
            pc.if_else(
                (count_in_window >= min_samples)._native_series,
                rolling_sum._native_series,
                None,
            )
        )
        return result[offset:]

    def rolling_mean(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self:
        min_samples = min_samples if min_samples is not None else window_size
        padded_series, offset = pad_series(self, window_size=window_size, center=center)

        cum_sum = padded_series.cum_sum(reverse=False).fill_null(
            value=None, strategy="forward", limit=None
        )
        rolling_sum = (
            cum_sum
            - cum_sum.shift(window_size).fill_null(value=0, strategy=None, limit=None)
            if window_size != 0
            else cum_sum
        )

        valid_count = padded_series.cum_count(reverse=False)
        count_in_window = valid_count - valid_count.shift(window_size).fill_null(
            value=0, strategy=None, limit=None
        )

        result = (
            self._from_native_series(
                pc.if_else(
                    (count_in_window >= min_samples)._native_series,
                    rolling_sum._native_series,
                    None,
                )
            )
            / count_in_window
        )
        return result[offset:]

    def rolling_var(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        min_samples = min_samples if min_samples is not None else window_size
        padded_series, offset = pad_series(self, window_size=window_size, center=center)

        cum_sum = padded_series.cum_sum(reverse=False).fill_null(
            value=None, strategy="forward", limit=None
        )
        rolling_sum = (
            cum_sum
            - cum_sum.shift(window_size).fill_null(value=0, strategy=None, limit=None)
            if window_size != 0
            else cum_sum
        )

        cum_sum_sq = (
            pow(padded_series, 2)
            .cum_sum(reverse=False)
            .fill_null(value=None, strategy="forward", limit=None)
        )
        rolling_sum_sq = (
            cum_sum_sq
            - cum_sum_sq.shift(window_size).fill_null(value=0, strategy=None, limit=None)
            if window_size != 0
            else cum_sum_sq
        )

        valid_count = padded_series.cum_count(reverse=False)
        count_in_window = valid_count - valid_count.shift(window_size).fill_null(
            value=0, strategy=None, limit=None
        )
        # NOTE: stubs are missing `ChunkedArray` support
        # https://github.com/zen-xu/pyarrow-stubs/blob/d97063876720e6a5edda7eb15f4efe07c31b8296/pyarrow-stubs/compute.pyi#L948-L954
        max_element_wise: Incomplete = pc.max_element_wise

        result = self._from_native_series(
            pc.if_else(
                (count_in_window >= min_samples)._native_series,
                (rolling_sum_sq - (rolling_sum**2 / count_in_window))._native_series,
                None,
            )
        ) / self._from_native_series(
            max_element_wise((count_in_window - ddof)._native_series, 0)
        )

        return result[offset:]

    def rolling_std(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        return (
            self.rolling_var(
                window_size=window_size, min_samples=min_samples, center=center, ddof=ddof
            )
            ** 0.5
        )

    def rank(
        self: Self,
        method: Literal["average", "min", "max", "dense", "ordinal"],
        *,
        descending: bool,
    ) -> Self:
        if method == "average":
            msg = (
                "`rank` with `method='average' is not supported for pyarrow backend. "
                "The available methods are {'min', 'max', 'dense', 'ordinal'}."
            )
            raise ValueError(msg)

        # ignore-banned-import

        sort_keys: Order = "descending" if descending else "ascending"
        tiebreaker: TieBreaker = "first" if method == "ordinal" else method

        native_series: ArrowChunkedArray | ArrowArray
        if self._backend_version < (14, 0, 0):  # pragma: no cover
            native_series = self.native.combine_chunks()
        else:
            native_series = self.native

        null_mask = pc.is_null(native_series)

        rank = pc.rank(native_series, sort_keys=sort_keys, tiebreaker=tiebreaker)

        result = pc.if_else(null_mask, lit(None, native_series.type), rank)
        return self._from_native_series(result)

    def hist(  # noqa: PLR0915
        self: Self,
        bins: list[float | int] | None,
        *,
        bin_count: int | None,
        include_breakpoint: bool,
    ) -> ArrowDataFrame:
        if self._backend_version < (13,):
            msg = f"`Series.hist` requires PyArrow>=13.0.0, found PyArrow version: {self._backend_version}"
            raise NotImplementedError(msg)
        import numpy as np  # ignore-banned-import

        from narwhals._arrow.dataframe import ArrowDataFrame

        def _hist_from_bin_count(bin_count: int):  # type: ignore[no-untyped-def] # noqa: ANN202
            d = pc.min_max(self.native)
            lower, upper = d["min"], d["max"]
            pa_float = pa.type_for_alias("float")
            if lower == upper:
                range_ = lit(1.0)
                mid = lit(0.5)
                width = pc.divide(range_, lit(bin_count))
                lower = pc.subtract(lower, mid)
                upper = pc.add(upper, mid)
            else:
                range_ = pc.subtract(upper, lower)
                width = pc.divide(pc.cast(range_, pa_float), lit(float(bin_count)))

            bin_proportions = pc.divide(
                pc.subtract(cast("pc.NumericOrTemporalArray", self.native), lower),
                width,
            )
            bin_indices: ArrowChunkedArray = cast(
                "ArrowChunkedArray", pc.floor(bin_proportions)
            )

            # NOTE: stubs leave unannotated
            if_else: Incomplete = pc.if_else

            # shift bins so they are right-closed
            bin_indices = if_else(
                pc.and_(
                    pc.equal(bin_indices, bin_proportions),
                    pc.greater(bin_indices, 0),
                ),
                pc.subtract(bin_indices, 1),
                bin_indices,
            )
            possible = pa.Table.from_arrays(
                [pa.Array.from_pandas(np.arange(bin_count, dtype="int64"))], ["values"]
            )
            counts = (  # count bin id occurrences
                pa.Table.from_arrays(
                    pc.value_counts(bin_indices).flatten(),
                    names=["values", "counts"],
                )
                # nan values are implicitly dropped in value_counts
                .filter(~pc.field("values").is_nan())
                .cast(pa.schema([("values", pa.int64()), ("counts", pa.int64())]))
                # align bin ids to all possible bin ids (populate in missing bins)
                .join(possible, keys="values", join_type="right outer")
                .sort_by("values")
            )
            # empty bin intervals should have a 0 count
            counts_coalesce = cast(
                "ArrowArray",
                pc.coalesce(cast("ArrowArray", counts.column("counts")), lit(0)),
            )
            counts = counts.set_column(0, "counts", counts_coalesce)

            # extract left/right side of the intervals
            bin_left = pc.add(lower, pc.multiply(counts.column("values"), width))
            bin_right = pc.add(bin_left, width)
            return counts.column("counts"), bin_right

        def _hist_from_bins(bins: Sequence[int | float]):  # type: ignore[no-untyped-def] # noqa: ANN202
            bin_indices = np.searchsorted(bins, self.native, side="left")
            obs_cats, obs_counts = np.unique(bin_indices, return_counts=True)
            obj_cats = np.arange(1, len(bins))
            counts = np.zeros_like(obj_cats)
            counts[np.isin(obj_cats, obs_cats)] = obs_counts[np.isin(obs_cats, obj_cats)]

            bin_right = bins[1:]
            return counts, bin_right

        if bins is not None:
            if len(bins) < 2:
                counts, bin_right = [], []
            else:
                counts, bin_right = _hist_from_bins(bins)

        elif bin_count is not None:
            if bin_count == 0:
                counts, bin_right = [], []
            else:
                counts, bin_right = _hist_from_bin_count(bin_count)

        else:  # pragma: no cover
            # caller guarantees that either bins or bin_count is specified
            msg = "must provide one of `bin_count` or `bins`"
            raise InvalidOperationError(msg)

        data: dict[str, Any] = {}
        if include_breakpoint:
            data["breakpoint"] = bin_right
        data["count"] = counts

        return ArrowDataFrame(
            pa.Table.from_pydict(data),
            backend_version=self._backend_version,
            version=self._version,
            validate_column_names=True,
        )

    def __iter__(self: Self) -> Iterator[Any]:
        for x in self.native:
            yield maybe_extract_py_scalar(x, return_py_scalar=True)

    def __contains__(self: Self, other: Any) -> bool:
        from pyarrow import ArrowInvalid  # ignore-banned-imports
        from pyarrow import ArrowNotImplementedError  # ignore-banned-imports
        from pyarrow import ArrowTypeError  # ignore-banned-imports

        try:
            other_ = lit(other) if other is not None else lit(None, type=self._type)
            return maybe_extract_py_scalar(
                pc.is_in(other_, self.native), return_py_scalar=True
            )
        except (ArrowInvalid, ArrowNotImplementedError, ArrowTypeError) as exc:
            from narwhals.exceptions import InvalidOperationError

            msg = f"Unable to compare other of type {type(other)} with series of type {self.dtype}."
            raise InvalidOperationError(msg) from exc

    @property
    def dt(self: Self) -> ArrowSeriesDateTimeNamespace:
        return ArrowSeriesDateTimeNamespace(self)

    @property
    def cat(self: Self) -> ArrowSeriesCatNamespace:
        return ArrowSeriesCatNamespace(self)

    @property
    def str(self: Self) -> ArrowSeriesStringNamespace:
        return ArrowSeriesStringNamespace(self)

    @property
    def list(self: Self) -> ArrowSeriesListNamespace:
        return ArrowSeriesListNamespace(self)

    @property
    def struct(self: Self) -> ArrowSeriesStructNamespace:
        return ArrowSeriesStructNamespace(self)
