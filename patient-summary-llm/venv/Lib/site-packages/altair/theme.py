"""Customizing chart configuration defaults."""

from __future__ import annotations

from functools import wraps as _wraps
from typing import TYPE_CHECKING, Any
from typing import overload as _overload

from altair.vegalite.v5.schema._config import (
    AreaConfigKwds,
    AutoSizeParamsKwds,
    AxisConfigKwds,
    AxisResolveMapKwds,
    BarConfigKwds,
    BindCheckboxKwds,
    BindDirectKwds,
    BindInputKwds,
    BindRadioSelectKwds,
    BindRangeKwds,
    BoxPlotConfigKwds,
    BrushConfigKwds,
    CompositionConfigKwds,
    ConfigKwds,
    DateTimeKwds,
    DerivedStreamKwds,
    ErrorBandConfigKwds,
    ErrorBarConfigKwds,
    FeatureGeometryGeoJsonPropertiesKwds,
    FormatConfigKwds,
    GeoJsonFeatureCollectionKwds,
    GeoJsonFeatureKwds,
    GeometryCollectionKwds,
    GradientStopKwds,
    HeaderConfigKwds,
    IntervalSelectionConfigKwds,
    IntervalSelectionConfigWithoutTypeKwds,
    LegendConfigKwds,
    LegendResolveMapKwds,
    LegendStreamBindingKwds,
    LinearGradientKwds,
    LineConfigKwds,
    LineStringKwds,
    LocaleKwds,
    MarkConfigKwds,
    MergedStreamKwds,
    MultiLineStringKwds,
    MultiPointKwds,
    MultiPolygonKwds,
    NumberLocaleKwds,
    OverlayMarkDefKwds,
    PaddingKwds,
    PointKwds,
    PointSelectionConfigKwds,
    PointSelectionConfigWithoutTypeKwds,
    PolygonKwds,
    ProjectionConfigKwds,
    ProjectionKwds,
    RadialGradientKwds,
    RangeConfigKwds,
    RectConfigKwds,
    ResolveKwds,
    RowColKwds,
    ScaleConfigKwds,
    ScaleInvalidDataConfigKwds,
    ScaleResolveMapKwds,
    SelectionConfigKwds,
    StepKwds,
    StyleConfigIndexKwds,
    ThemeConfig,
    TickConfigKwds,
    TimeIntervalStepKwds,
    TimeLocaleKwds,
    TitleConfigKwds,
    TitleParamsKwds,
    TooltipContentKwds,
    TopLevelSelectionParameterKwds,
    VariableParameterKwds,
    ViewBackgroundKwds,
    ViewConfigKwds,
)
from altair.vegalite.v5.theme import themes as _themes

if TYPE_CHECKING:
    import sys
    from typing import Any, Callable, Literal

    if sys.version_info >= (3, 11):
        from typing import LiteralString
    else:
        from typing_extensions import LiteralString
    if sys.version_info >= (3, 10):
        from typing import ParamSpec
    else:
        from typing_extensions import ParamSpec

    from altair.utils.plugin_registry import Plugin

    P = ParamSpec("P")

__all__ = [
    "AreaConfigKwds",
    "AutoSizeParamsKwds",
    "AxisConfigKwds",
    "AxisResolveMapKwds",
    "BarConfigKwds",
    "BindCheckboxKwds",
    "BindDirectKwds",
    "BindInputKwds",
    "BindRadioSelectKwds",
    "BindRangeKwds",
    "BoxPlotConfigKwds",
    "BrushConfigKwds",
    "CompositionConfigKwds",
    "ConfigKwds",
    "DateTimeKwds",
    "DerivedStreamKwds",
    "ErrorBandConfigKwds",
    "ErrorBarConfigKwds",
    "FeatureGeometryGeoJsonPropertiesKwds",
    "FormatConfigKwds",
    "GeoJsonFeatureCollectionKwds",
    "GeoJsonFeatureKwds",
    "GeometryCollectionKwds",
    "GradientStopKwds",
    "HeaderConfigKwds",
    "IntervalSelectionConfigKwds",
    "IntervalSelectionConfigWithoutTypeKwds",
    "LegendConfigKwds",
    "LegendResolveMapKwds",
    "LegendStreamBindingKwds",
    "LineConfigKwds",
    "LineStringKwds",
    "LinearGradientKwds",
    "LocaleKwds",
    "MarkConfigKwds",
    "MergedStreamKwds",
    "MultiLineStringKwds",
    "MultiPointKwds",
    "MultiPolygonKwds",
    "NumberLocaleKwds",
    "OverlayMarkDefKwds",
    "PaddingKwds",
    "PointKwds",
    "PointSelectionConfigKwds",
    "PointSelectionConfigWithoutTypeKwds",
    "PolygonKwds",
    "ProjectionConfigKwds",
    "ProjectionKwds",
    "RadialGradientKwds",
    "RangeConfigKwds",
    "RectConfigKwds",
    "ResolveKwds",
    "RowColKwds",
    "ScaleConfigKwds",
    "ScaleInvalidDataConfigKwds",
    "ScaleResolveMapKwds",
    "SelectionConfigKwds",
    "StepKwds",
    "StyleConfigIndexKwds",
    "ThemeConfig",
    "TickConfigKwds",
    "TimeIntervalStepKwds",
    "TimeLocaleKwds",
    "TitleConfigKwds",
    "TitleParamsKwds",
    "TooltipContentKwds",
    "TopLevelSelectionParameterKwds",
    "VariableParameterKwds",
    "ViewBackgroundKwds",
    "ViewConfigKwds",
    "active",
    "enable",
    "get",
    "names",
    "options",
    "register",
    "unregister",
]


def register(
    name: LiteralString, *, enable: bool
) -> Callable[[Plugin[ThemeConfig]], Plugin[ThemeConfig]]:
    """
    Decorator for registering a theme function.

    Parameters
    ----------
    name
        Unique name assigned in registry.
    enable
        Auto-enable the wrapped theme.

    Examples
    --------
    Register and enable a theme::

        import altair as alt
        from altair import theme


        @theme.register("param_font_size", enable=True)
        def custom_theme() -> theme.ThemeConfig:
            sizes = 12, 14, 16, 18, 20
            return {
                "autosize": {"contains": "content", "resize": True},
                "background": "#F3F2F1",
                "config": {
                    "axisX": {"labelFontSize": sizes[1], "titleFontSize": sizes[1]},
                    "axisY": {"labelFontSize": sizes[1], "titleFontSize": sizes[1]},
                    "font": "'Lato', 'Segoe UI', Tahoma, Verdana, sans-serif",
                    "headerColumn": {"labelFontSize": sizes[1]},
                    "headerFacet": {"labelFontSize": sizes[1]},
                    "headerRow": {"labelFontSize": sizes[1]},
                    "legend": {"labelFontSize": sizes[0], "titleFontSize": sizes[1]},
                    "text": {"fontSize": sizes[0]},
                    "title": {"fontSize": sizes[-1]},
                },
                "height": {"step": 28},
                "width": 350,
            }

    We can then see the ``name`` parameter displayed when checking::

        theme.active
        "param_font_size"

    Until another theme has been enabled, all charts will use defaults set in ``custom_theme()``::

        from vega_datasets import data

        source = data.stocks()
        lines = (
            alt.Chart(source, title=alt.Title("Stocks"))
            .mark_line()
            .encode(x="date:T", y="price:Q", color="symbol:N")
        )
        lines.interactive(bind_y=False)

    """

    # HACK: See for `LiteralString` requirement in `name`
    # https://github.com/vega/altair/pull/3526#discussion_r1743350127
    def decorate(func: Plugin[ThemeConfig], /) -> Plugin[ThemeConfig]:
        _register(name, func)
        if enable:
            _themes.enable(name)

        @_wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ThemeConfig:
            return func(*args, **kwargs)

        return wrapper

    return decorate


def unregister(name: LiteralString) -> Plugin[ThemeConfig]:
    """
    Remove and return a previously registered theme.

    Parameters
    ----------
    name
        Unique name assigned during ``alt.theme.register``.

    Raises
    ------
    TypeError
        When ``name`` has not been registered.
    """
    plugin = _register(name, None)
    if plugin is None:
        msg = (
            f"Found no theme named {name!r} in registry.\n"
            f"Registered themes:\n"
            f"{names()!r}"
        )
        raise TypeError(msg)
    else:
        return plugin


enable = _themes.enable
get = _themes.get
names = _themes.names
active: str
"""Return the name of the currently active theme."""
options: dict[str, Any]
"""Return the current themes options dictionary."""


def __dir__() -> list[str]:
    return __all__


@_overload
def __getattr__(name: Literal["active"]) -> str: ...  # type: ignore[misc]
@_overload
def __getattr__(name: Literal["options"]) -> dict[str, Any]: ...  # type: ignore[misc]
def __getattr__(name: str) -> Any:
    if name == "active":
        return _themes.active
    elif name == "options":
        return _themes.options
    else:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)


def _register(
    name: LiteralString, fn: Plugin[ThemeConfig] | None, /
) -> Plugin[ThemeConfig] | None:
    if fn is None:
        return _themes._plugins.pop(name, None)
    elif _themes.plugin_type(fn):
        _themes._plugins[name] = fn
        return fn
    else:
        msg = f"{type(fn).__name__!r} is not a callable theme\n\n{fn!r}"
        raise TypeError(msg)
