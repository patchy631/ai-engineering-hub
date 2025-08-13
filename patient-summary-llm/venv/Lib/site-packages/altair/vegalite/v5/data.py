from typing import Final

from altair.utils._vegafusion_data import vegafusion_data_transformer
from altair.vegalite.data import (
    DataTransformerRegistry,
    MaxRowsError,
    default_data_transformer,
    limit_rows,
    sample,
    to_csv,
    to_json,
    to_values,
)

# ==============================================================================
# VegaLite 5 data transformers
# ==============================================================================


ENTRY_POINT_GROUP: Final = "altair.vegalite.v5.data_transformer"


data_transformers = DataTransformerRegistry(entry_point_group=ENTRY_POINT_GROUP)
data_transformers.register("default", default_data_transformer)
data_transformers.register("json", to_json)
# FIXME: `to_csv` cannot accept all `DataType` https://github.com/vega/altair/issues/3441
data_transformers.register("csv", to_csv)  # type: ignore[arg-type]
data_transformers.register("vegafusion", vegafusion_data_transformer)
data_transformers.enable("default")


__all__ = (
    "MaxRowsError",
    "default_data_transformer",
    "limit_rows",
    "sample",
    "to_csv",
    "to_json",
    "to_values",
    "vegafusion_data_transformer",
)
