from __future__ import annotations

import struct
from typing import TYPE_CHECKING, Any, Literal, cast, overload

from ._importers import import_vl_convert, vl_version_for_vl_convert
from .html import spec_to_html

if TYPE_CHECKING:
    import sys

    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

MimeBundleFormat: TypeAlias = Literal[
    "html", "json", "png", "svg", "pdf", "vega", "vega-lite"
]


@overload
def spec_to_mimebundle(
    spec: dict[str, Any],
    format: Literal["json", "vega-lite"],
    mode: Literal["vega-lite"] | None = ...,
    vega_version: str | None = ...,
    vegaembed_version: str | None = ...,
    vegalite_version: str | None = ...,
    embed_options: dict[str, Any] | None = ...,
    engine: Literal["vl-convert"] | None = ...,
    **kwargs,
) -> dict[str, dict[str, Any]]: ...
@overload
def spec_to_mimebundle(
    spec: dict[str, Any],
    format: Literal["html"],
    mode: Literal["vega-lite"] | None = ...,
    vega_version: str | None = ...,
    vegaembed_version: str | None = ...,
    vegalite_version: str | None = ...,
    embed_options: dict[str, Any] | None = ...,
    engine: Literal["vl-convert"] | None = ...,
    **kwargs,
) -> dict[str, str]: ...
@overload
def spec_to_mimebundle(
    spec: dict[str, Any],
    format: Literal["pdf", "svg", "vega"],
    mode: Literal["vega-lite"] | None = ...,
    vega_version: str | None = ...,
    vegaembed_version: str | None = ...,
    vegalite_version: str | None = ...,
    embed_options: dict[str, Any] | None = ...,
    engine: Literal["vl-convert"] | None = ...,
    **kwargs,
) -> dict[str, Any]: ...
@overload
def spec_to_mimebundle(
    spec: dict[str, Any],
    format: Literal["png"],
    mode: Literal["vega-lite"] | None = ...,
    vega_version: str | None = ...,
    vegaembed_version: str | None = ...,
    vegalite_version: str | None = ...,
    embed_options: dict[str, Any] | None = ...,
    engine: Literal["vl-convert"] | None = ...,
    **kwargs,
) -> tuple[dict[str, Any], dict[str, Any]]: ...
def spec_to_mimebundle(
    spec: dict[str, Any],
    format: MimeBundleFormat,
    mode: Literal["vega-lite"] | None = None,
    vega_version: str | None = None,
    vegaembed_version: str | None = None,
    vegalite_version: str | None = None,
    embed_options: dict[str, Any] | None = None,
    engine: Literal["vl-convert"] | None = None,
    **kwargs,
) -> dict[str, Any] | tuple[dict[str, Any], dict[str, Any]]:
    """
    Convert a vega-lite specification to a mimebundle.

    The mimebundle type is controlled by the ``format`` argument, which can be
    one of the following ['html', 'json', 'png', 'svg', 'pdf', 'vega', 'vega-lite']

    Parameters
    ----------
    spec : dict
        a dictionary representing a vega-lite plot spec
    format : string {'html', 'json', 'png', 'svg', 'pdf', 'vega', 'vega-lite'}
        the file format to be saved.
    mode : string {'vega-lite'}
        The rendering mode.
    vega_version : string
        The version of vega.js to use
    vegaembed_version : string
        The version of vegaembed.js to use
    vegalite_version : string
        The version of vegalite.js to use. Only required if mode=='vega-lite'
    embed_options : dict (optional)
        The vegaEmbed options dictionary. Defaults to the embed options set with
        alt.renderers.set_embed_options().
        (See https://github.com/vega/vega-embed for details)
    engine: string {'vl-convert'}
        the conversion engine to use for 'png', 'svg', 'pdf', and 'vega' formats
    **kwargs :
        Additional arguments will be passed to the generating function

    Returns
    -------
    output : dict
        a mime-bundle representing the image

    Note
    ----
    The png, svg, pdf, and vega outputs require the vl-convert package
    """
    # Local import to avoid circular ImportError
    from altair import renderers
    from altair.utils.display import compile_with_vegafusion, using_vegafusion

    if mode != "vega-lite":
        msg = "mode must be 'vega-lite'"
        raise ValueError(msg)

    internal_mode: Literal["vega-lite", "vega"] = mode
    if using_vegafusion():
        spec = compile_with_vegafusion(spec)
        internal_mode = "vega"

    # Default to the embed options set by alt.renderers.set_embed_options
    if embed_options is None:
        final_embed_options = renderers.options.get("embed_options", {})
    else:
        final_embed_options = embed_options

    embed_options = preprocess_embed_options(final_embed_options)

    if format in {"png", "svg", "pdf", "vega"}:
        return _spec_to_mimebundle_with_engine(
            spec,
            cast(Literal["png", "svg", "pdf", "vega"], format),
            internal_mode,
            engine=engine,
            format_locale=embed_options.get("formatLocale", None),
            time_format_locale=embed_options.get("timeFormatLocale", None),
            **kwargs,
        )
    elif format == "html":
        html = spec_to_html(
            spec,
            mode=internal_mode,
            vega_version=vega_version,
            vegaembed_version=vegaembed_version,
            vegalite_version=vegalite_version,
            embed_options=embed_options,
            **kwargs,
        )
        return {"text/html": html}
    elif format == "vega-lite":
        if vegalite_version is None:
            msg = "Must specify vegalite_version"
            raise ValueError(msg)
        return {f"application/vnd.vegalite.v{vegalite_version[0]}+json": spec}
    elif format == "json":
        return {"application/json": spec}
    else:
        msg = (
            "format must be one of "
            "['html', 'json', 'png', 'svg', 'pdf', 'vega', 'vega-lite']"
        )
        raise ValueError(msg)


def _spec_to_mimebundle_with_engine(
    spec: dict,
    format: Literal["png", "svg", "pdf", "vega"],
    mode: Literal["vega-lite", "vega"],
    format_locale: str | dict | None = None,
    time_format_locale: str | dict | None = None,
    **kwargs,
) -> Any:
    """
    Helper for Vega-Lite to mimebundle conversions that require an engine.

    Parameters
    ----------
    spec : dict
        a dictionary representing a vega-lite plot spec
    format : string {'png', 'svg', 'pdf', 'vega'}
        the format of the mimebundle to be returned
    mode : string {'vega-lite', 'vega'}
        The rendering mode.
    engine: string {'vl-convert'}
        the conversion engine to use
    format_locale : str or dict
        d3-format locale name or dictionary. Defaults to "en-US" for United States English.
        See https://github.com/d3/d3-format/tree/main/locale for available names and example
        definitions.
    time_format_locale : str or dict
        d3-time-format locale name or dictionary. Defaults to "en-US" for United States English.
        See https://github.com/d3/d3-time-format/tree/main/locale for available names and example
        definitions.
    **kwargs :
        Additional arguments will be passed to the conversion function
    """
    # Normalize the engine string (if any) by lower casing
    # and removing underscores and hyphens
    engine = kwargs.pop("engine", None)
    normalized_engine = _validate_normalize_engine(engine, format)

    if normalized_engine == "vlconvert":
        vlc = import_vl_convert()
        vl_version = vl_version_for_vl_convert()
        if format == "vega":
            if mode == "vega":
                vg = spec
            else:
                vg = vlc.vegalite_to_vega(spec, vl_version=vl_version)
            return {"application/vnd.vega.v5+json": vg}
        elif format == "svg":
            if mode == "vega":
                svg = vlc.vega_to_svg(
                    spec,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            else:
                svg = vlc.vegalite_to_svg(
                    spec,
                    vl_version=vl_version,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            return {"image/svg+xml": svg}
        elif format == "png":
            scale = kwargs.get("scale_factor", 1)
            # The default ppi for a PNG file is 72
            default_ppi = 72
            ppi = kwargs.get("ppi", default_ppi)
            if mode == "vega":
                png = vlc.vega_to_png(
                    spec,
                    scale=scale,
                    ppi=ppi,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            else:
                png = vlc.vegalite_to_png(
                    spec,
                    vl_version=vl_version,
                    scale=scale,
                    ppi=ppi,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            factor = ppi / default_ppi
            w, h = _pngxy(png)
            return {"image/png": png}, {
                "image/png": {"width": w / factor, "height": h / factor}
            }
        elif format == "pdf":
            scale = kwargs.get("scale_factor", 1)
            if mode == "vega":
                pdf = vlc.vega_to_pdf(
                    spec,
                    scale=scale,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            else:
                pdf = vlc.vegalite_to_pdf(
                    spec,
                    vl_version=vl_version,
                    scale=scale,
                    format_locale=format_locale,
                    time_format_locale=time_format_locale,
                )
            return {"application/pdf": pdf}
        else:
            # This should be validated above
            # but raise exception for the sake of future development
            msg = f"Unexpected format {format!r}"
            raise ValueError(msg)
    else:
        # This should be validated above
        # but raise exception for the sake of future development
        msg = f"Unexpected normalized_engine {normalized_engine!r}"
        raise ValueError(msg)


def _validate_normalize_engine(
    engine: Literal["vl-convert"] | None,
    format: Literal["png", "svg", "pdf", "vega"],
) -> str:
    """
    Helper to validate and normalize the user-provided engine.

    engine : {None, 'vl-convert'}
        the user-provided engine string
    format : string {'png', 'svg', 'pdf', 'vega'}
        the format of the mimebundle to be returned
    """
    # Try to import vl_convert
    try:
        vlc = import_vl_convert()
    except ImportError:
        vlc = None

    # Normalize engine string by lower casing and removing underscores and hyphens
    normalized_engine = (
        None if engine is None else engine.lower().replace("-", "").replace("_", "")
    )

    # Validate or infer default value of normalized_engine
    if normalized_engine == "vlconvert":
        if vlc is None:
            msg = "The 'vl-convert' conversion engine requires the vl-convert-python package"
            raise ValueError(msg)
    elif normalized_engine is None:
        if vlc is not None:
            normalized_engine = "vlconvert"
        else:
            msg = (
                f"Saving charts in {format!r} format requires the vl-convert-python package: "
                "see https://altair-viz.github.io/user_guide/saving_charts.html#png-svg-and-pdf-format"
            )
            raise ValueError(msg)
    else:
        msg = f"Invalid conversion engine {engine!r}. Expected vl-convert"
        raise ValueError(msg)
    return normalized_engine


def _pngxy(data):
    """
    read the (width, height) from a PNG header.

    Taken from IPython.display
    """
    ihdr = data.index(b"IHDR")
    # next 8 bytes are width/height
    return struct.unpack(">ii", data[ihdr + 4 : ihdr + 12])


def preprocess_embed_options(embed_options: dict) -> dict:
    """
    Preprocess embed options to a form compatible with Vega Embed.

    Parameters
    ----------
    embed_options : dict
        The embed options dictionary to preprocess.

    Returns
    -------
    embed_opts : dict
        The preprocessed embed options dictionary.
    """
    embed_options = (embed_options or {}).copy()

    # Convert locale strings to objects compatible with Vega Embed using vl-convert
    format_locale = embed_options.get("formatLocale", None)
    if isinstance(format_locale, str):
        vlc = import_vl_convert()
        embed_options["formatLocale"] = vlc.get_format_locale(format_locale)

    time_format_locale = embed_options.get("timeFormatLocale", None)
    if isinstance(time_format_locale, str):
        vlc = import_vl_convert()
        embed_options["timeFormatLocale"] = vlc.get_time_format_locale(
            time_format_locale
        )

    return embed_options
