from .core import (
    SHORTHAND_KEYS,
    display_traceback,
    infer_encoding_types,
    infer_vegalite_type_for_pandas,
    parse_shorthand,
    sanitize_narwhals_dataframe,
    sanitize_pandas_dataframe,
    update_nested,
    use_signature,
)
from .deprecation import AltairDeprecationWarning, deprecated, deprecated_warn
from .html import spec_to_html
from .plugin_registry import PluginRegistry
from .schemapi import Optional, SchemaBase, SchemaLike, Undefined, is_undefined

__all__ = (
    "SHORTHAND_KEYS",
    "AltairDeprecationWarning",
    "Optional",
    "PluginRegistry",
    "SchemaBase",
    "SchemaLike",
    "Undefined",
    "deprecated",
    "deprecated_warn",
    "display_traceback",
    "infer_encoding_types",
    "infer_vegalite_type_for_pandas",
    "is_undefined",
    "parse_shorthand",
    "sanitize_narwhals_dataframe",
    "sanitize_pandas_dataframe",
    "spec_to_html",
    "update_nested",
    "use_signature",
)
