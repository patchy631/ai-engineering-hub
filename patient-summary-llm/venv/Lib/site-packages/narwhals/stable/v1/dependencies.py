from __future__ import annotations

from narwhals.dependencies import get_cudf
from narwhals.dependencies import get_ibis
from narwhals.dependencies import get_modin
from narwhals.dependencies import get_numpy
from narwhals.dependencies import get_pandas
from narwhals.dependencies import get_polars
from narwhals.dependencies import get_pyarrow
from narwhals.dependencies import is_cudf_dataframe
from narwhals.dependencies import is_cudf_series
from narwhals.dependencies import is_dask_dataframe
from narwhals.dependencies import is_ibis_table
from narwhals.dependencies import is_into_dataframe
from narwhals.dependencies import is_into_series
from narwhals.dependencies import is_modin_dataframe
from narwhals.dependencies import is_modin_series
from narwhals.dependencies import is_narwhals_dataframe
from narwhals.dependencies import is_narwhals_lazyframe
from narwhals.dependencies import is_narwhals_series
from narwhals.dependencies import is_numpy_array
from narwhals.dependencies import is_pandas_dataframe
from narwhals.dependencies import is_pandas_index
from narwhals.dependencies import is_pandas_like_dataframe
from narwhals.dependencies import is_pandas_like_series
from narwhals.dependencies import is_pandas_series
from narwhals.dependencies import is_polars_dataframe
from narwhals.dependencies import is_polars_lazyframe
from narwhals.dependencies import is_polars_series
from narwhals.dependencies import is_pyarrow_chunked_array
from narwhals.dependencies import is_pyarrow_table

__all__ = [
    "get_cudf",
    "get_ibis",
    "get_modin",
    "get_numpy",
    "get_pandas",
    "get_polars",
    "get_pyarrow",
    "is_cudf_dataframe",
    "is_cudf_series",
    "is_dask_dataframe",
    "is_ibis_table",
    "is_into_dataframe",
    "is_into_series",
    "is_modin_dataframe",
    "is_modin_series",
    "is_narwhals_dataframe",
    "is_narwhals_lazyframe",
    "is_narwhals_series",
    "is_numpy_array",
    "is_pandas_dataframe",
    "is_pandas_index",
    "is_pandas_like_dataframe",
    "is_pandas_like_series",
    "is_pandas_series",
    "is_polars_dataframe",
    "is_polars_lazyframe",
    "is_polars_series",
    "is_pyarrow_chunked_array",
    "is_pyarrow_table",
]
