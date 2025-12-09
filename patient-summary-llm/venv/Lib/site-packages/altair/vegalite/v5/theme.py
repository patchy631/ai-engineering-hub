"""Tools for enabling and registering chart themes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Literal, get_args

from altair.utils.deprecation import deprecated_static_only
from altair.utils.plugin_registry import Plugin, PluginRegistry
from altair.vegalite.v5.schema._config import ThemeConfig
from altair.vegalite.v5.schema._typing import VegaThemes

if TYPE_CHECKING:
    import sys
    from functools import partial

    if sys.version_info >= (3, 11):
        from typing import LiteralString
    else:
        from typing_extensions import LiteralString
    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias

    from altair.utils.plugin_registry import PluginEnabler


AltairThemes: TypeAlias = Literal["default", "opaque"]
VEGA_THEMES: list[LiteralString] = list(get_args(VegaThemes))


# HACK: See for `LiteralString` requirement in `name`
# https://github.com/vega/altair/pull/3526#discussion_r1743350127
class ThemeRegistry(PluginRegistry[Plugin[ThemeConfig], ThemeConfig]):
    def enable(
        self,
        name: LiteralString | AltairThemes | VegaThemes | None = None,
        **options: Any,
    ) -> PluginEnabler[Plugin[ThemeConfig], ThemeConfig]:
        """
        Enable a theme by name.

        This can be either called directly, or used as a context manager.

        Parameters
        ----------
        name : string (optional)
            The name of the theme to enable. If not specified, then use the
            current active name.
        **options :
            Any additional parameters will be passed to the theme as keyword
            arguments

        Returns
        -------
        PluginEnabler:
            An object that allows enable() to be used as a context manager

        Notes
        -----
        Default `vega` themes can be previewed at https://vega.github.io/vega-themes/
        """
        return super().enable(name, **options)

    def get(self) -> partial[ThemeConfig] | Plugin[ThemeConfig] | None:
        """Return the currently active theme."""
        return super().get()

    def names(self) -> list[str]:
        """Return the names of the registered and entry points themes."""
        return super().names()

    @deprecated_static_only(
        "Deprecated since `altair=5.5.0`. Use @altair.theme.register instead.",
        category=None,
    )
    def register(
        self, name: str, value: Plugin[ThemeConfig] | None
    ) -> Plugin[ThemeConfig] | None:
        return super().register(name, value)


class VegaTheme:
    """Implementation of a builtin vega theme."""

    def __init__(self, theme: str) -> None:
        self.theme = theme

    def __call__(self) -> ThemeConfig:
        return {
            "usermeta": {"embedOptions": {"theme": self.theme}},
            "config": {"view": {"continuousWidth": 300, "continuousHeight": 300}},
        }

    def __repr__(self) -> str:
        return f"VegaTheme({self.theme!r})"


# The entry point group that can be used by other packages to declare other
# themes that will be auto-detected. Explicit registration is also
# allowed by the PluginRegistry API.
ENTRY_POINT_GROUP: Final = "altair.vegalite.v5.theme"

# NOTE: `themes` def has an entry point group
themes = ThemeRegistry(entry_point_group=ENTRY_POINT_GROUP)

themes.register(
    "default",
    lambda: {"config": {"view": {"continuousWidth": 300, "continuousHeight": 300}}},
)
themes.register(
    "opaque",
    lambda: {
        "config": {
            "background": "white",
            "view": {"continuousWidth": 300, "continuousHeight": 300},
        }
    },
)
themes.register("none", ThemeConfig)

for theme in VEGA_THEMES:
    themes.register(theme, VegaTheme(theme))

themes.enable("default")
