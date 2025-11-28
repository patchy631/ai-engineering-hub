from __future__ import annotations

from typing import TYPE_CHECKING, Callable, overload

from altair.utils.core import sanitize_pandas_dataframe
from altair.utils.data import DataTransformerRegistry as _DataTransformerRegistry
from altair.utils.data import (
    MaxRowsError,
    check_data_type,
    limit_rows,
    sample,
    to_csv,
    to_json,
    to_values,
)

if TYPE_CHECKING:
    from altair.utils.data import DataType, ToValuesReturnType
    from altair.utils.plugin_registry import PluginEnabler


@overload
def default_data_transformer(
    data: None = ..., max_rows: int = ...
) -> Callable[[DataType], ToValuesReturnType]: ...
@overload
def default_data_transformer(
    data: DataType, max_rows: int = ...
) -> ToValuesReturnType: ...
def default_data_transformer(
    data: DataType | None = None, max_rows: int = 5000
) -> Callable[[DataType], ToValuesReturnType] | ToValuesReturnType:
    if data is None:

        def pipe(data: DataType, /) -> ToValuesReturnType:
            data = limit_rows(data, max_rows=max_rows)
            return to_values(data)

        return pipe

    else:
        return to_values(limit_rows(data, max_rows=max_rows))


class DataTransformerRegistry(_DataTransformerRegistry):
    def disable_max_rows(self) -> PluginEnabler:
        """Disable the MaxRowsError."""
        options = self.options
        if self.active in {"default", "vegafusion"}:
            options = options.copy()
            options["max_rows"] = None
        return self.enable(**options)


__all__ = (
    "DataTransformerRegistry",
    "MaxRowsError",
    "check_data_type",
    "default_data_transformer",
    "limit_rows",
    "sample",
    "sanitize_pandas_dataframe",
    "to_csv",
    "to_json",
    "to_values",
)
