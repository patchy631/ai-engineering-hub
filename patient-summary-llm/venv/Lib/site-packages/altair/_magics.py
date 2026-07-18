"""Magic functions for rendering vega-lite specifications."""

from __future__ import annotations

import json
import warnings
from importlib.util import find_spec
from typing import Any

from IPython.core import magic_arguments
from narwhals.stable.v1.dependencies import is_pandas_dataframe

from altair.vegalite import v5 as vegalite_v5

__all__ = ["vegalite"]

RENDERERS = {
    "vega-lite": {
        "5": vegalite_v5.VegaLite,
    },
}


TRANSFORMERS = {
    "vega-lite": {
        "5": vegalite_v5.data_transformers,
    },
}


def _prepare_data(data, data_transformers):
    """Convert input data to data for use within schema."""
    if data is None or isinstance(data, dict):
        return data
    elif is_pandas_dataframe(data):
        if func := data_transformers.get():
            data = func(data)
        return data
    elif isinstance(data, str):
        return {"url": data}
    else:
        warnings.warn(f"data of type {type(data)} not recognized", stacklevel=1)
        return data


def _get_variable(name: str) -> Any:
    """Get a variable from the notebook namespace."""
    from IPython.core.getipython import get_ipython

    if ip := get_ipython():
        if name not in ip.user_ns:
            msg = f"argument '{name}' does not match the name of any defined variable"
            raise NameError(msg)
        return ip.user_ns[name]
    else:
        msg = (
            "Magic command must be run within an IPython "
            "environment, in which get_ipython() is defined."
        )
        raise ValueError(msg)


@magic_arguments.magic_arguments()
@magic_arguments.argument(
    "data",
    nargs="?",
    help="local variablename of a pandas DataFrame to be used as the dataset",
)
@magic_arguments.argument("-v", "--version", dest="version", default="v5")
@magic_arguments.argument("-j", "--json", dest="json", action="store_true")
def vegalite(line, cell) -> vegalite_v5.VegaLite:
    """
    Cell magic for displaying vega-lite visualizations in CoLab.

    %%vegalite [dataframe] [--json] [--version='v5']

    Visualize the contents of the cell using Vega-Lite, optionally
    specifying a pandas DataFrame object to be used as the dataset.

    if --json is passed, then input is parsed as json rather than yaml.
    """
    args = magic_arguments.parse_argstring(vegalite, line)
    existing_versions = {"v5": "5"}
    version = existing_versions[args.version]
    assert version in RENDERERS["vega-lite"]
    VegaLite = RENDERERS["vega-lite"][version]
    data_transformers = TRANSFORMERS["vega-lite"][version]

    if args.json:
        spec = json.loads(cell)
    elif not find_spec("yaml"):
        try:
            spec = json.loads(cell)
        except json.JSONDecodeError as err:
            msg = (
                "%%vegalite: spec is not valid JSON. "
                "Install pyyaml to parse spec as yaml"
            )
            raise ValueError(msg) from err
    else:
        import yaml

        spec = yaml.load(cell, Loader=yaml.SafeLoader)

    if args.data is not None:
        data = _get_variable(args.data)
        spec["data"] = _prepare_data(data, data_transformers)

    return VegaLite(spec)
