from __future__ import annotations

import json
import pathlib
import warnings
from typing import IO, TYPE_CHECKING, Any, Literal

from altair.utils._vegafusion_data import using_vegafusion
from altair.utils.deprecation import deprecated_warn
from altair.vegalite.v5.data import data_transformers

from .mimebundle import spec_to_mimebundle

if TYPE_CHECKING:
    from pathlib import Path


def write_file_or_filename(
    fp: str | Path | IO,
    content: str | bytes,
    mode: str = "w",
    encoding: str | None = None,
) -> None:
    """Write content to fp, whether fp is a string, a pathlib Path or a file-like object."""
    if isinstance(fp, (str, pathlib.Path)):
        with pathlib.Path(fp).open(mode=mode, encoding=encoding) as f:
            f.write(content)
    else:
        fp.write(content)


def set_inspect_format_argument(
    format: str | None, fp: str | Path | IO, inline: bool
) -> str:
    """Inspect the format argument in the save function."""
    if format is None:
        if isinstance(fp, (str, pathlib.Path)):
            format = pathlib.Path(fp).suffix.lstrip(".")
        else:
            msg = (
                "must specify file format: "
                "['png', 'svg', 'pdf', 'html', 'json', 'vega']"
            )
            raise ValueError(msg)

    if format != "html" and inline:
        warnings.warn("inline argument ignored for non HTML formats.", stacklevel=1)

    return format


def set_inspect_mode_argument(
    mode: Literal["vega-lite"] | None,
    embed_options: dict[str, Any],
    spec: dict[str, Any],
    vegalite_version: str | None,
) -> Literal["vega-lite"]:
    """Inspect the mode argument in the save function."""
    if mode is None:
        if "mode" in embed_options:
            mode = embed_options["mode"]
        elif "$schema" in spec:
            mode = spec["$schema"].split("/")[-2]
        else:
            mode = "vega-lite"

    if mode != "vega-lite":
        msg = "mode must be 'vega-lite', " f"not '{mode}'"
        raise ValueError(msg)

    if mode == "vega-lite" and vegalite_version is None:
        msg = "must specify vega-lite version"
        raise ValueError(msg)

    return mode


def save(
    chart,
    fp: str | Path | IO,
    vega_version: str | None,
    vegaembed_version: str | None,
    format: Literal["json", "html", "png", "svg", "pdf"] | None = None,
    mode: Literal["vega-lite"] | None = None,
    vegalite_version: str | None = None,
    embed_options: dict | None = None,
    json_kwds: dict | None = None,
    scale_factor: float = 1,
    engine: Literal["vl-convert"] | None = None,
    inline: bool = False,
    **kwargs,
) -> None:
    """
    Save a chart to file in a variety of formats.

    Supported formats are [json, html, png, svg, pdf]

    Parameters
    ----------
    chart : alt.Chart
        the chart instance to save
    fp : string filename, pathlib.Path or file-like object
        file to which to write the chart.
    format : string (optional)
        the format to write: one of ['json', 'html', 'png', 'svg', 'pdf'].
        If not specified, the format will be determined from the filename.
    mode : string (optional)
        Must be 'vega-lite'. If not specified, then infer the mode from
        the '$schema' property of the spec, or the ``opt`` dictionary.
        If it's not specified in either of those places, then use 'vega-lite'.
    vega_version : string (optional)
        For html output, the version of vega.js to use
    vegalite_version : string (optional)
        For html output, the version of vegalite.js to use
    vegaembed_version : string (optional)
        For html output, the version of vegaembed.js to use
    embed_options : dict (optional)
        The vegaEmbed options dictionary. Default is {}
        (See https://github.com/vega/vega-embed for details)
    json_kwds : dict (optional)
        Additional keyword arguments are passed to the output method
        associated with the specified format.
    scale_factor : float (optional)
        scale_factor to use to change size/resolution of png or svg output
    engine: string {'vl-convert'}
        the conversion engine to use for 'png', 'svg', and 'pdf' formats
    inline: bool (optional)
        If False (default), the required JavaScript libraries are loaded
        from a CDN location in the resulting html file.
        If True, the required JavaScript libraries are inlined into the resulting
        html file so that it will work without an internet connection.
        The vl-convert-python package is required if True.
    **kwargs :
        additional kwargs passed to spec_to_mimebundle.
    """
    if _ := kwargs.pop("webdriver", None):
        deprecated_warn(
            "The webdriver argument is not relevant for the new vl-convert engine which replaced altair_saver. "
            "The argument will be removed in a future release.",
            version="5.0.0",
        )

    json_kwds = json_kwds or {}
    encoding = kwargs.get("encoding", "utf-8")
    format = set_inspect_format_argument(format, fp, inline)  # type: ignore[assignment]

    def perform_save() -> None:
        spec = chart.to_dict(context={"pre_transform": False})

        inner_mode = set_inspect_mode_argument(
            mode, embed_options or {}, spec, vegalite_version
        )

        if format == "json":
            json_spec = json.dumps(spec, **json_kwds)
            write_file_or_filename(fp, json_spec, mode="w", encoding=encoding)
        elif format == "html":
            if inline:
                kwargs["template"] = "inline"
            mb_html = spec_to_mimebundle(
                spec=spec,
                format=format,
                mode=inner_mode,
                vega_version=vega_version,
                vegalite_version=vegalite_version,
                vegaembed_version=vegaembed_version,
                embed_options=embed_options,
                json_kwds=json_kwds,
                **kwargs,
            )
            write_file_or_filename(
                fp, mb_html["text/html"], mode="w", encoding=encoding
            )
        elif format == "png":
            mb_png = spec_to_mimebundle(
                spec=spec,
                format=format,
                mode=inner_mode,
                vega_version=vega_version,
                vegalite_version=vegalite_version,
                vegaembed_version=vegaembed_version,
                embed_options=embed_options,
                scale_factor=scale_factor,
                engine=engine,
                **kwargs,
            )
            write_file_or_filename(fp, mb_png[0]["image/png"], mode="wb")
        elif format in {"svg", "pdf", "vega"}:
            mb_any = spec_to_mimebundle(
                spec=spec,
                format=format,
                mode=inner_mode,
                vega_version=vega_version,
                vegalite_version=vegalite_version,
                vegaembed_version=vegaembed_version,
                embed_options=embed_options,
                scale_factor=scale_factor,
                engine=engine,
                **kwargs,
            )
            if format == "pdf":
                write_file_or_filename(fp, mb_any["application/pdf"], mode="wb")
            else:
                write_file_or_filename(
                    fp, mb_any["image/svg+xml"], mode="w", encoding=encoding
                )
        else:
            msg = f"Unsupported format: '{format}'"
            raise ValueError(msg)

    if using_vegafusion():
        # When the vegafusion data transformer is enabled, transforms will be
        # evaluated during save and the resulting data will be included in the
        # vega specification that is saved.
        with data_transformers.disable_max_rows():
            perform_save()
    else:
        # Temporarily turn off any data transformers so that all data is inlined
        # when calling chart.to_dict. This is relevant for vl-convert which cannot access
        # local json files which could be created by a json data transformer. Furthermore,
        # we don't exit the with statement until this function completed due to the issue
        # described at https://github.com/vega/vl-convert/issues/31
        with data_transformers.enable("default"), data_transformers.disable_max_rows():
            perform_save()
