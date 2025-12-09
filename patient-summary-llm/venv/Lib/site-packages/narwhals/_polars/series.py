from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Sequence
from typing import cast
from typing import overload

import polars as pl

from narwhals._polars.utils import catch_polars_exception
from narwhals._polars.utils import extract_args_kwargs
from narwhals._polars.utils import extract_native
from narwhals._polars.utils import narwhals_to_native_dtype
from narwhals._polars.utils import native_to_narwhals_dtype
from narwhals.utils import Implementation
from narwhals.utils import validate_backend_version

if TYPE_CHECKING:
    from types import ModuleType
    from typing import TypeVar

    from typing_extensions import Self

    from narwhals._polars.dataframe import PolarsDataFrame
    from narwhals.dtypes import DType
    from narwhals.typing import _1DArray
    from narwhals.utils import Version

    T = TypeVar("T")


class PolarsSeries:
    def __init__(
        self: Self,
        series: pl.Series,
        *,
        backend_version: tuple[int, ...],
        version: Version,
    ) -> None:
        self._native_series: pl.Series = series
        self._backend_version = backend_version
        self._implementation = Implementation.POLARS
        self._version = version
        validate_backend_version(self._implementation, self._backend_version)

    def __repr__(self: Self) -> str:  # pragma: no cover
        return "PolarsSeries"

    def __narwhals_series__(self: Self) -> Self:
        return self

    def __native_namespace__(self: Self) -> ModuleType:
        if self._implementation is Implementation.POLARS:
            return self._implementation.to_native_namespace()

        msg = f"Expected polars, got: {type(self._implementation)}"  # pragma: no cover
        raise AssertionError(msg)

    def _change_version(self: Self, version: Version) -> Self:
        return self.__class__(
            self._native_series, backend_version=self._backend_version, version=version
        )

    def _from_native_series(self: Self, series: pl.Series) -> Self:
        return self.__class__(
            series, backend_version=self._backend_version, version=self._version
        )

    @overload
    def _from_native_object(self: Self, series: pl.Series) -> Self: ...

    @overload
    def _from_native_object(self: Self, series: pl.DataFrame) -> PolarsDataFrame: ...

    @overload
    def _from_native_object(self: Self, series: T) -> T: ...

    def _from_native_object(
        self: Self, series: pl.Series | pl.DataFrame | T
    ) -> Self | PolarsDataFrame | T:
        if isinstance(series, pl.Series):
            return self._from_native_series(series)
        if isinstance(series, pl.DataFrame):
            from narwhals._polars.dataframe import PolarsDataFrame

            return PolarsDataFrame(
                series, backend_version=self._backend_version, version=self._version
            )
        # scalar
        return series

    def __getattr__(self: Self, attr: str) -> Any:
        if attr == "as_py":  # pragma: no cover
            raise AttributeError

        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._from_native_object(
                getattr(self._native_series, attr)(*args, **kwargs)
            )

        return func

    def __len__(self: Self) -> int:
        return len(self._native_series)

    @property
    def name(self: Self) -> str:
        return self._native_series.name

    @property
    def dtype(self: Self) -> DType:
        return native_to_narwhals_dtype(
            self._native_series.dtype, self._version, self._backend_version
        )

    @property
    def native(self) -> pl.Series:
        return self._native_series

    def alias(self, name: str) -> Self:
        return self._from_native_object(self._native_series.alias(name))

    @overload
    def __getitem__(self: Self, item: int) -> Any: ...

    @overload
    def __getitem__(self: Self, item: slice | Sequence[int] | pl.Series) -> Self: ...

    def __getitem__(
        self: Self, item: int | slice | Sequence[int] | pl.Series
    ) -> Any | Self:
        return self._from_native_object(self._native_series.__getitem__(item))

    def cast(self: Self, dtype: DType) -> Self:
        dtype_pl = narwhals_to_native_dtype(dtype, self._version, self._backend_version)
        return self._from_native_series(self.native.cast(dtype_pl))

    def replace_strict(
        self: Self, old: Sequence[Any], new: Sequence[Any], *, return_dtype: DType | None
    ) -> Self:
        ser = self._native_series
        dtype = (
            narwhals_to_native_dtype(return_dtype, self._version, self._backend_version)
            if return_dtype
            else None
        )
        if self._backend_version < (1,):
            msg = f"`replace_strict` is only available in Polars>=1.0, found version {self._backend_version}"
            raise NotImplementedError(msg)
        return self._from_native_series(ser.replace_strict(old, new, return_dtype=dtype))

    def __array__(self: Self, dtype: Any, *, copy: bool | None) -> _1DArray:
        if self._backend_version < (0, 20, 29):
            return self._native_series.__array__(dtype=dtype)
        return self._native_series.__array__(dtype=dtype, copy=copy)

    def __eq__(self: Self, other: object) -> Self:  # type: ignore[override]
        return self._from_native_series(self._native_series.__eq__(extract_native(other)))

    def __ne__(self: Self, other: object) -> Self:  # type: ignore[override]
        return self._from_native_series(self._native_series.__ne__(extract_native(other)))

    def __ge__(self: Self, other: Any) -> Self:
        return self._from_native_series(self._native_series.__ge__(extract_native(other)))

    def __gt__(self: Self, other: Any) -> Self:
        return self._from_native_series(self._native_series.__gt__(extract_native(other)))

    def __le__(self: Self, other: Any) -> Self:
        return self._from_native_series(self._native_series.__le__(extract_native(other)))

    def __lt__(self: Self, other: Any) -> Self:
        return self._from_native_series(self._native_series.__lt__(extract_native(other)))

    def __and__(self: Self, other: PolarsSeries | bool | Any) -> Self:
        return self._from_native_series(
            self._native_series.__and__(extract_native(other))
        )

    def __or__(self: Self, other: PolarsSeries | bool | Any) -> Self:
        return self._from_native_series(self._native_series.__or__(extract_native(other)))

    def __add__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__add__(extract_native(other))
        )

    def __radd__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__radd__(extract_native(other))
        )

    def __sub__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__sub__(extract_native(other))
        )

    def __rsub__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__rsub__(extract_native(other))
        )

    def __mul__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__mul__(extract_native(other))
        )

    def __rmul__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__rmul__(extract_native(other))
        )

    def __pow__(self: Self, other: PolarsSeries | Any) -> Self:
        return self._from_native_series(
            self._native_series.__pow__(extract_native(other))
        )

    def __rpow__(self: Self, other: PolarsSeries | Any) -> Self:
        result = self._native_series.__rpow__(extract_native(other))
        if self._backend_version < (1, 16, 1):
            # Explicitly set alias to work around https://github.com/pola-rs/polars/issues/20071
            result = result.alias(self.name)
        return self._from_native_series(result)

    def __invert__(self: Self) -> Self:
        return self._from_native_series(self._native_series.__invert__())

    def is_nan(self: Self) -> Self:
        native = self._native_series
        try:
            native_is_nan = native.is_nan()
        except Exception as e:  # noqa: BLE001
            raise catch_polars_exception(e, self._backend_version) from None
        if self._backend_version < (1, 18):  # pragma: no cover
            return self._from_native_series(
                pl.select(pl.when(native.is_not_null()).then(native_is_nan))[native.name]
            )
        return self._from_native_series(native_is_nan)

    def median(self: Self) -> Any:
        from narwhals.exceptions import InvalidOperationError

        if not self.dtype.is_numeric():
            msg = "`median` operation not supported for non-numeric input type."
            raise InvalidOperationError(msg)

        return self._native_series.median()

    def to_dummies(self: Self, *, separator: str, drop_first: bool) -> PolarsDataFrame:
        from narwhals._polars.dataframe import PolarsDataFrame

        if self._backend_version < (0, 20, 15):
            has_nulls = self._native_series.is_null().any()
            result = self._native_series.to_dummies(separator=separator)
            output_columns = result.columns
            if drop_first:
                _ = output_columns.pop(int(has_nulls))

            result = result.select(output_columns)
        else:
            result = self._native_series.to_dummies(
                separator=separator, drop_first=drop_first
            )
        result = result.with_columns(pl.all().cast(pl.Int8))
        return PolarsDataFrame(
            result, backend_version=self._backend_version, version=self._version
        )

    def ewm_mean(
        self: Self,
        *,
        com: float | None,
        span: float | None,
        half_life: float | None,
        alpha: float | None,
        adjust: bool,
        min_samples: int,
        ignore_nulls: bool,
    ) -> Self:
        native_series = self._native_series

        extra_kwargs = (
            {"min_periods": min_samples}
            if self._backend_version < (1, 21, 0)
            else {"min_samples": min_samples}
        )

        native_result = native_series.ewm_mean(
            com=com,
            span=span,
            half_life=half_life,
            alpha=alpha,
            adjust=adjust,
            ignore_nulls=ignore_nulls,
            **extra_kwargs,
        )
        if self._backend_version < (1,):  # pragma: no cover
            return self._from_native_series(
                pl.select(
                    pl.when(~native_series.is_null()).then(native_result).otherwise(None)
                )[native_series.name]
            )

        return self._from_native_series(native_result)

    def rolling_var(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        if self._backend_version < (1,):  # pragma: no cover
            msg = "`rolling_var` not implemented for polars older than 1.0"
            raise NotImplementedError(msg)

        extra_kwargs = (
            {"min_periods": min_samples}
            if self._backend_version < (1, 21, 0)
            else {"min_samples": min_samples}
        )

        return self._from_native_series(
            self._native_series.rolling_var(
                window_size=window_size,
                center=center,
                ddof=ddof,
                **extra_kwargs,  # type: ignore[arg-type]
            )
        )

    def rolling_std(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
        ddof: int,
    ) -> Self:
        if self._backend_version < (1,):  # pragma: no cover
            msg = "`rolling_std` not implemented for polars older than 1.0"
            raise NotImplementedError(msg)

        extra_kwargs = (
            {"min_periods": min_samples}
            if self._backend_version < (1, 21, 0)
            else {"min_samples": min_samples}
        )

        return self._from_native_series(
            self._native_series.rolling_std(
                window_size=window_size,
                center=center,
                ddof=ddof,
                **extra_kwargs,  # type: ignore[arg-type]
            )
        )

    def rolling_sum(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self:
        extra_kwargs = (
            {"min_periods": min_samples}
            if self._backend_version < (1, 21, 0)
            else {"min_samples": min_samples}
        )

        return self._from_native_series(
            self._native_series.rolling_sum(
                window_size=window_size,
                center=center,
                **extra_kwargs,  # type: ignore[arg-type]
            )
        )

    def rolling_mean(
        self: Self,
        window_size: int,
        *,
        min_samples: int,
        center: bool,
    ) -> Self:
        extra_kwargs = (
            {"min_periods": min_samples}
            if self._backend_version < (1, 21, 0)
            else {"min_samples": min_samples}
        )

        return self._from_native_series(
            self._native_series.rolling_mean(
                window_size=window_size,
                center=center,
                **extra_kwargs,  # type: ignore[arg-type]
            )
        )

    def sort(self: Self, *, descending: bool, nulls_last: bool) -> Self:
        if self._backend_version < (0, 20, 6):
            result = self._native_series.sort(descending=descending)

            if nulls_last:
                is_null = result.is_null()
                result = pl.concat([result.filter(~is_null), result.filter(is_null)])
        else:
            result = self._native_series.sort(
                descending=descending, nulls_last=nulls_last
            )

        return self._from_native_series(result)

    def scatter(self: Self, indices: int | Sequence[int], values: Any) -> Self:
        values = extract_native(values)
        s = self._native_series.clone()
        s.scatter(indices, values)
        return self._from_native_series(s)

    def value_counts(
        self: Self,
        *,
        sort: bool,
        parallel: bool,
        name: str | None,
        normalize: bool,
    ) -> PolarsDataFrame:
        from narwhals._polars.dataframe import PolarsDataFrame

        if self._backend_version < (1, 0, 0):
            value_name_ = name or ("proportion" if normalize else "count")

            result = self._native_series.value_counts(sort=sort, parallel=parallel)
            result = result.select(
                **{
                    (self._native_series.name): pl.col(self._native_series.name),
                    value_name_: pl.col("count") / pl.sum("count")
                    if normalize
                    else pl.col("count"),
                }
            )

        else:
            result = self._native_series.value_counts(
                sort=sort, parallel=parallel, name=name, normalize=normalize
            )

        return PolarsDataFrame(
            result, backend_version=self._backend_version, version=self._version
        )

    def cum_count(self: Self, *, reverse: bool) -> Self:
        if self._backend_version < (0, 20, 4):
            not_null_series = ~self._native_series.is_null()
            result = not_null_series.cum_sum(reverse=reverse)
        else:
            result = self._native_series.cum_count(reverse=reverse)

        return self._from_native_series(result)

    def __contains__(self: Self, other: Any) -> bool:
        try:
            return self._native_series.__contains__(other)
        except Exception as e:  # noqa: BLE001
            raise catch_polars_exception(e, self._backend_version) from None

    def hist(
        self: Self,
        bins: list[float | int] | None,
        *,
        bin_count: int | None,
        include_breakpoint: bool,
    ) -> PolarsDataFrame:
        from narwhals._polars.dataframe import PolarsDataFrame

        if (bins is not None and len(bins) <= 1) or (bin_count == 0):  # pragma: no cover
            data: list[pl.Series] = []
            if include_breakpoint:
                data.append(pl.Series("breakpoint", [], dtype=pl.Float64))
            data.append(pl.Series("count", [], dtype=pl.UInt32))
            return PolarsDataFrame(
                pl.DataFrame(data),
                backend_version=self._backend_version,
                version=self._version,
            )
        elif (self._backend_version < (1, 15)) and self._native_series.count() < 1:
            data_dict: dict[str, Sequence[Any] | pl.Series]
            if bins is not None:
                data_dict = {
                    "breakpoint": bins[1:],
                    "count": pl.zeros(n=len(bins) - 1, dtype=pl.Int64, eager=True),
                }
            elif bin_count is not None:
                data_dict = {
                    "breakpoint": pl.int_range(0, bin_count, eager=True) / bin_count,
                    "count": pl.zeros(n=bin_count, dtype=pl.Int64, eager=True),
                }

            if not include_breakpoint:
                del data_dict["breakpoint"]

            return PolarsDataFrame(
                pl.DataFrame(data_dict),
                backend_version=self._backend_version,
                version=self._version,
            )

        # polars <1.15 does not adjust the bins when they have equivalent min/max
        # polars <1.5 with bin_count=...
        # returns bins that range from -inf to +inf and has bin_count + 1 bins.
        #   for compat: convert `bin_count=` call to `bins=`
        if (
            (self._backend_version < (1, 15))
            and (bin_count is not None)
            and (self._native_series.count() > 0)
        ):  # pragma: no cover
            lower = cast("float", self._native_series.min())
            upper = cast("float", self._native_series.max())
            pad_lowest_bin = False
            if lower == upper:
                width = 1 / bin_count
                lower -= 0.5
                upper += 0.5
            else:
                pad_lowest_bin = True
                width = (upper - lower) / bin_count

            bins = (pl.int_range(0, bin_count + 1, eager=True) * width + lower).to_list()
            if pad_lowest_bin:
                bins[0] -= 0.001 * abs(bins[0]) if bins[0] != 0 else 0.001
            bin_count = None

        # Polars inconsistently handles NaN values when computing histograms
        #   against predefined bins: https://github.com/pola-rs/polars/issues/21082
        series = self._native_series
        if self._backend_version < (1, 15) or bins is not None:
            series = series.set(series.is_nan(), None)

        df = series.hist(
            bins=bins,
            bin_count=bin_count,
            include_category=False,
            include_breakpoint=include_breakpoint,
        )
        if not include_breakpoint:
            df.columns = ["count"]

        #  polars<1.15 implicitly adds -inf and inf to either end of bins
        if self._backend_version < (1, 15) and bins is not None:  # pragma: no cover
            r = pl.int_range(0, len(df))
            df = df.filter((r > 0) & (r < len(df) - 1))

        if self._backend_version < (1, 0) and include_breakpoint:
            df = df.rename({"break_point": "breakpoint"})

        return PolarsDataFrame(
            df, backend_version=self._backend_version, version=self._version
        )

    def to_polars(self: Self) -> pl.Series:
        return self._native_series

    @property
    def dt(self: Self) -> PolarsSeriesDateTimeNamespace:
        return PolarsSeriesDateTimeNamespace(self)

    @property
    def str(self: Self) -> PolarsSeriesStringNamespace:
        return PolarsSeriesStringNamespace(self)

    @property
    def cat(self: Self) -> PolarsSeriesCatNamespace:
        return PolarsSeriesCatNamespace(self)

    @property
    def list(self: Self) -> PolarsSeriesListNamespace:
        return PolarsSeriesListNamespace(self)

    @property
    def struct(self: Self) -> PolarsSeriesStructNamespace:
        return PolarsSeriesStructNamespace(self)


class PolarsSeriesDateTimeNamespace:
    def __init__(self: Self, series: PolarsSeries) -> None:
        self._compliant_series = series

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._compliant_series._from_native_series(
                getattr(self._compliant_series._native_series.dt, attr)(*args, **kwargs)
            )

        return func


class PolarsSeriesStringNamespace:
    def __init__(self: Self, series: PolarsSeries) -> None:
        self._compliant_series = series

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._compliant_series._from_native_series(
                getattr(self._compliant_series._native_series.str, attr)(*args, **kwargs)
            )

        return func


class PolarsSeriesCatNamespace:
    def __init__(self: Self, series: PolarsSeries) -> None:
        self._compliant_series = series

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._compliant_series._from_native_series(
                getattr(self._compliant_series._native_series.cat, attr)(*args, **kwargs)
            )

        return func


class PolarsSeriesListNamespace:
    def __init__(self: Self, series: PolarsSeries) -> None:
        self._series = series

    def len(self: Self) -> PolarsSeries:
        native_series = self._series._native_series
        native_result = native_series.list.len()

        if self._series._backend_version < (1, 16):  # pragma: no cover
            native_result = pl.select(
                pl.when(~native_series.is_null()).then(native_result).otherwise(None)
            )[native_series.name].cast(pl.UInt32())

        elif self._series._backend_version < (1, 17):  # pragma: no cover
            native_result = native_series.cast(pl.UInt32())

        return self._series._from_native_series(native_result)

    # TODO(FBruzzesi): Remove `pragma: no cover` once other namespace methods are added
    def __getattr__(self: Self, attr: str) -> Any:  # pragma: no cover
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._series._from_native_series(
                getattr(self._series._native_series.list, attr)(*args, **kwargs)
            )

        return func


class PolarsSeriesStructNamespace:
    def __init__(self: Self, series: PolarsSeries) -> None:
        self._compliant_series = series

    def __getattr__(self: Self, attr: str) -> Any:
        def func(*args: Any, **kwargs: Any) -> Any:
            args, kwargs = extract_args_kwargs(args, kwargs)  # type: ignore[assignment]
            return self._compliant_series._from_native_series(
                getattr(self._compliant_series._native_series.struct, attr)(
                    *args, **kwargs
                )
            )

        return func
