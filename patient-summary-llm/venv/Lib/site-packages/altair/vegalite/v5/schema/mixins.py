# The contents of this file are automatically written by
# tools/generate_schema_wrapper.py. Do not modify directly.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from altair.utils import SchemaBase, Undefined, use_signature

from . import core

if TYPE_CHECKING:
    from collections.abc import Sequence

if TYPE_CHECKING:
    # ruff: noqa: F405
    import sys

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self
    from altair import Parameter
    from altair.typing import Optional

    from ._typing import *  # noqa: F403


class _MarkDef(SchemaBase):
    """
    MarkDef schema wrapper.

    Parameters
    ----------
    align : dict, :class:`Align`, :class:`ExprRef`, Literal['left', 'center', 'right']
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle : dict, float, :class:`ExprRef`
        The rotation angle of the text, in degrees.
    aria : bool, dict, :class:`ExprRef`
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole : str, dict, :class:`ExprRef`
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription : str, dict, :class:`ExprRef`
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect : bool, dict, :class:`ExprRef`
        Whether to keep aspect ratio of image marks.
    bandSize : float
        The width of the ticks.

        **Default value:**  3/4 of step (width step for horizontal ticks and height step for
        vertical ticks).
    baseline : dict, :class:`ExprRef`, :class:`Baseline`, :class:`TextBaseline`, Literal['alphabetic', 'line-bottom', 'line-top', 'top', 'middle', 'bottom']
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    binSpacing : float
        Offset between bars for binned field. The ideal value for this is either 0
        (preferred by statisticians) or 1 (Vega-Lite default, D3 example style).

        **Default value:** ``1``
    blend : dict, :class:`Blend`, :class:`ExprRef`, Literal[None, 'multiply', 'screen', 'overlay', 'darken', 'lighten', 'color-dodge', 'color-burn', 'hard-light', 'soft-light', 'difference', 'exclusion', 'hue', 'saturation', 'color', 'luminosity']
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    clip : bool, dict, :class:`ExprRef`
        Whether a mark be clipped to the enclosing group's width and height.
    color : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    continuousBandSize : float
        The default size of the bars on continuous scales.

        **Default value:** ``5``
    cornerRadius : dict, float, :class:`ExprRef`
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft : dict, float, :class:`ExprRef`
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight : dict, float, :class:`ExprRef`
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusEnd : dict, float, :class:`ExprRef`
        * For vertical bars, top-left and top-right corner radius.

        * For horizontal bars, top-right and bottom-right corner radius.
    cornerRadiusTopLeft : dict, float, :class:`ExprRef`
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight : dict, float, :class:`ExprRef`
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor : dict, :class:`Cursor`, :class:`ExprRef`, Literal['auto', 'default', 'none', 'context-menu', 'help', 'pointer', 'progress', 'wait', 'cell', 'crosshair', 'text', 'vertical-text', 'alias', 'copy', 'move', 'no-drop', 'not-allowed', 'e-resize', 'n-resize', 'ne-resize', 'nw-resize', 's-resize', 'se-resize', 'sw-resize', 'w-resize', 'ew-resize', 'ns-resize', 'nesw-resize', 'nwse-resize', 'col-resize', 'row-resize', 'all-scroll', 'zoom-in', 'zoom-out', 'grab', 'grabbing']
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description : str, dict, :class:`ExprRef`
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir : dict, :class:`ExprRef`, :class:`TextDirection`, Literal['ltr', 'rtl']
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    discreteBandSize : dict, float, :class:`RelativeBandSize`
        The default size of the bars with discrete dimensions. If unspecified, the default
        size is  ``step-2``, which provides 2 pixel offset between bars.
    dx : dict, float, :class:`ExprRef`
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy : dict, float, :class:`ExprRef`
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis : str, dict, :class:`ExprRef`
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    fill : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple'], None
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity : dict, float, :class:`ExprRef`
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled : bool
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font : str, dict, :class:`ExprRef`
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize : dict, float, :class:`ExprRef`
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle : str, dict, :class:`ExprRef`, :class:`FontStyle`
        The font style (e.g., ``"italic"``).
    fontWeight : dict, :class:`ExprRef`, :class:`FontWeight`, Literal['normal', 'bold', 'lighter', 'bolder', 100, 200, 300, 400, 500, 600, 700, 800, 900]
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height : dict, float, :class:`ExprRef`, :class:`RelativeBandSize`
        Height of the marks.  One of:

        * A number representing a fixed pixel height.

        * A relative band size definition.  For example, ``{band: 0.5}`` represents half of
          the band
    href : str, dict, :class:`URI`, :class:`ExprRef`
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius : dict, float, :class:`ExprRef`
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate : dict, :class:`ExprRef`, :class:`Interpolate`, Literal['basis', 'basis-open', 'basis-closed', 'bundle', 'cardinal', 'cardinal-open', 'cardinal-closed', 'catmull-rom', 'linear', 'linear-closed', 'monotone', 'natural', 'step', 'step-before', 'step-after']
        The line interpolation method to use for line and area marks. One of the following:

        * ``"linear"``: piecewise linear segments, as in a polyline.
        * ``"linear-closed"``: close the linear segments to form a polygon.
        * ``"step"``: alternate between horizontal and vertical segments, as in a step
          function.
        * ``"step-before"``: alternate between vertical and horizontal segments, as in a
          step function.
        * ``"step-after"``: alternate between horizontal and vertical segments, as in a step
          function.
        * ``"basis"``: a B-spline, with control point duplication on the ends.
        * ``"basis-open"``: an open B-spline; may not intersect the start or end.
        * ``"basis-closed"``: a closed B-spline, as in a loop.
        * ``"cardinal"``: a Cardinal spline, with control point duplication on the ends.
        * ``"cardinal-open"``: an open Cardinal spline; may not intersect the start or end,
          but will intersect other control points.
        * ``"cardinal-closed"``: a closed Cardinal spline, as in a loop.
        * ``"bundle"``: equivalent to basis, except the tension parameter is used to
          straighten the spline.
        * ``"monotone"``: cubic interpolation that preserves monotonicity in y.
    invalid : :class:`MarkInvalidDataMode`, Literal['filter', 'break-paths-filter-domains', 'break-paths-show-domains', 'break-paths-show-path-domains', 'show'], None
        Invalid data mode, which defines how the marks and corresponding scales should
        represent invalid values (``null`` and ``NaN`` in continuous scales *without*
        defined output for invalid values).

        * ``"filter"`` — *Exclude* all invalid values from the visualization's *marks* and
          *scales*. For path marks (for line, area, trail), this option will create paths
          that connect valid points, as if the data rows with invalid values do not exist.

        * ``"break-paths-filter-domains"`` — Break path marks (for line, area, trail) at
          invalid values.  For non-path marks, this is equivalent to ``"filter"``. All
          *scale* domains will *exclude* these filtered data points.

        * ``"break-paths-show-domains"`` — Break paths (for line, area, trail) at invalid
          values.  Hide invalid values for non-path marks. All *scale* domains will
          *include* these filtered data points (for both path and non-path marks).

        * ``"show"`` or ``null`` — Show all data points in the marks and scale domains. Each
          scale will use the output for invalid values defined in ``config.scale.invalid``
          or, if unspecified, by default invalid values will produce the same visual values
          as zero (if the scale includes zero) or the minimum value (if the scale does not
          include zero).

        * ``"break-paths-show-path-domains"`` (default) — This is equivalent to
          ``"break-paths-show-domains"`` for path-based marks (line/area/trail) and
          ``"filter"`` for non-path marks.

        **Note**: If any channel's scale has an output for invalid values defined in
        ``config.scale.invalid``, all values for the scales will be considered "valid" since
        they can produce a reasonable output for the scales. Thus, fields for such channels
        will not be filtered and will not cause path breaks.
    limit : dict, float, :class:`ExprRef`
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    line : bool, dict, :class:`OverlayMarkDef`
        A flag for overlaying line on top of area marks, or an object defining the
        properties of the overlayed lines.

        * If this value is an empty object (``{}``) or ``true``, lines with default
          properties will be used.

        * If this value is ``false``, no lines would be automatically added to area marks.

        **Default value:** ``false``.
    lineBreak : str, dict, :class:`ExprRef`
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight : dict, float, :class:`ExprRef`
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    minBandSize : dict, float, :class:`ExprRef`
        The minimum band size for bar and rectangle marks. **Default value:** ``0.25``
    opacity : dict, float, :class:`ExprRef`
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order : bool, None
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient : :class:`Orientation`, Literal['horizontal', 'vertical']
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius : dict, float, :class:`ExprRef`
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle : dict, float, :class:`ExprRef`
        The angular padding applied to sides of the arc, in radians.
    point : bool, dict, Literal['transparent'], :class:`OverlayMarkDef`
        A flag for overlaying points on top of line or area marks, or an object defining the
        properties of the overlayed points.

        * If this property is ``"transparent"``, transparent points will be used (for
          enhancing tooltips and selections).

        * If this property is an empty object (``{}``) or ``true``, filled points with
          default properties will be used.

        * If this property is ``false``, no points would be automatically added to line or
          area marks.

        **Default value:** ``false``.
    radius : dict, float, :class:`ExprRef`
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2 : dict, float, :class:`ExprRef`
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    radius2Offset : dict, float, :class:`ExprRef`
        Offset for radius2.
    radiusOffset : dict, float, :class:`ExprRef`
        Offset for radius.
    shape : str, dict, :class:`ExprRef`, :class:`SymbolShape`
        Shape of the point marks. Supported values include:

        * plotting shapes: ``"circle"``, ``"square"``, ``"cross"``, ``"diamond"``,
          ``"triangle-up"``, ``"triangle-down"``, ``"triangle-right"``, or
          ``"triangle-left"``.
        * the line symbol ``"stroke"``
        * centered directional shapes ``"arrow"``, ``"wedge"``, or ``"triangle"``
        * a custom `SVG path string
          <https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths>`__ (For correct
          sizing, custom shape paths should be defined within a square bounding box with
          coordinates ranging from -1 to 1 along both the x and y dimensions.)

        **Default value:** ``"circle"``
    size : dict, float, :class:`ExprRef`
        Default size for marks.

        * For ``point``/``circle``/``square``, this represents the pixel area of the marks.
          Note that this value sets the area of the symbol; the side lengths will increase
          with the square root of this value.
        * For ``bar``, this represents the band size of the bar, in pixels.
        * For ``text``, this represents the font size, in pixels.

        **Default value:**

        * ``30`` for point, circle, square marks; width/height's ``step``
        * ``2`` for bar marks with discrete dimensions;
        * ``5`` for bar marks with continuous dimensions;
        * ``11`` for text marks.
    smooth : bool, dict, :class:`ExprRef`
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    stroke : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple'], None
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap : dict, :class:`ExprRef`, :class:`StrokeCap`, Literal['butt', 'round', 'square']
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash : dict, Sequence[float], :class:`ExprRef`
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset : dict, float, :class:`ExprRef`
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin : dict, :class:`ExprRef`, :class:`StrokeJoin`, Literal['miter', 'round', 'bevel']
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit : dict, float, :class:`ExprRef`
        The miter limit at which to bevel a line join.
    strokeOffset : dict, float, :class:`ExprRef`
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity : dict, float, :class:`ExprRef`
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth : dict, float, :class:`ExprRef`
        The stroke width, in pixels.
    style : str, Sequence[str]
        A string or array of strings indicating the name of custom styles to apply to the
        mark. A style is a named collection of mark property defaults defined within the
        `style configuration
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__. If style is an
        array, later styles will override earlier styles. Any `mark properties
        <https://vega.github.io/vega-lite/docs/encoding.html#mark-prop>`__ explicitly
        defined within the ``encoding`` will override a style default.

        **Default value:** The mark's name. For example, a bar mark will have style
        ``"bar"`` by default. **Note:** Any specified style will augment the default style.
        For example, a bar mark with ``"style": "foo"`` will receive from
        ``config.style.bar`` and ``config.style.foo`` (the specified style ``"foo"`` has
        higher precedence).
    tension : dict, float, :class:`ExprRef`
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text : str, dict, :class:`Text`, Sequence[str], :class:`ExprRef`
        Placeholder text if the ``text`` channel is not specified
    theta : dict, float, :class:`ExprRef`
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2 : dict, float, :class:`ExprRef`
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    theta2Offset : dict, float, :class:`ExprRef`
        Offset for theta2.
    thetaOffset : dict, float, :class:`ExprRef`
        Offset for theta.
    thickness : float
        Thickness of the tick mark.

        **Default value:**  ``1``
    timeUnitBandPosition : float
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize : float
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip : str, bool, dict, float, :class:`ExprRef`, :class:`TooltipContent`, None
        The tooltip text string to show upon mouse hover or an object defining which fields
        should the tooltip be derived from.

        * If ``tooltip`` is ``true`` or ``{"content": "encoding"}``, then all fields from
          ``encoding`` will be used.
        * If ``tooltip`` is ``{"content": "data"}``, then all fields that appear in the
          highlighted data point will be used.
        * If set to ``null`` or ``false``, then no tooltip will be used.

        See the `tooltip <https://vega.github.io/vega-lite/docs/tooltip.html>`__
        documentation for a detailed discussion about tooltip  in Vega-Lite.

        **Default value:** ``null``
    url : str, dict, :class:`URI`, :class:`ExprRef`
        The URL of the image file for image marks.
    width : dict, float, :class:`ExprRef`, :class:`RelativeBandSize`
        Width of the marks.  One of:

        * A number representing a fixed pixel width.

        * A relative band size definition.  For example, ``{band: 0.5}`` represents half of
          the band.
    x : dict, float, :class:`ExprRef`, Literal['width']
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2 : dict, float, :class:`ExprRef`, Literal['width']
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2Offset : dict, float, :class:`ExprRef`
        Offset for x2-position.
    xOffset : dict, float, :class:`ExprRef`
        Offset for x-position.
    y : dict, float, :class:`ExprRef`, Literal['height']
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2 : dict, float, :class:`ExprRef`, Literal['height']
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2Offset : dict, float, :class:`ExprRef`
        Offset for y2-position.
    yOffset : dict, float, :class:`ExprRef`
        Offset for y-position.
    """

    _schema = {"$ref": "#/definitions/MarkDef"}

    def __init__(
        self,
        align: Optional[Parameter | SchemaBase | Map | Align_T] = Undefined,
        angle: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        aria: Optional[bool | Parameter | SchemaBase | Map] = Undefined,
        ariaRole: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        ariaRoleDescription: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        aspect: Optional[bool | Parameter | SchemaBase | Map] = Undefined,
        bandSize: Optional[float] = Undefined,
        baseline: Optional[Parameter | SchemaBase | Map | TextBaseline_T] = Undefined,
        binSpacing: Optional[float] = Undefined,
        blend: Optional[Parameter | SchemaBase | Map | Blend_T] = Undefined,
        clip: Optional[bool | Parameter | SchemaBase | Map] = Undefined,
        color: Optional[str | Parameter | SchemaBase | Map | ColorName_T] = Undefined,
        continuousBandSize: Optional[float] = Undefined,
        cornerRadius: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        cornerRadiusBottomLeft: Optional[
            float | Parameter | SchemaBase | Map
        ] = Undefined,
        cornerRadiusBottomRight: Optional[
            float | Parameter | SchemaBase | Map
        ] = Undefined,
        cornerRadiusEnd: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        cornerRadiusTopLeft: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        cornerRadiusTopRight: Optional[
            float | Parameter | SchemaBase | Map
        ] = Undefined,
        cursor: Optional[Parameter | SchemaBase | Map | Cursor_T] = Undefined,
        description: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        dir: Optional[Parameter | SchemaBase | Map | TextDirection_T] = Undefined,
        discreteBandSize: Optional[float | SchemaBase | Map] = Undefined,
        dx: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        dy: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        ellipsis: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        fill: Optional[
            str | Parameter | SchemaBase | Map | ColorName_T | None
        ] = Undefined,
        fillOpacity: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        filled: Optional[bool] = Undefined,
        font: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        fontSize: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        fontStyle: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        fontWeight: Optional[Parameter | SchemaBase | Map | FontWeight_T] = Undefined,
        height: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        href: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        innerRadius: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        interpolate: Optional[Parameter | SchemaBase | Map | Interpolate_T] = Undefined,
        invalid: Optional[SchemaBase | MarkInvalidDataMode_T | None] = Undefined,
        limit: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        line: Optional[bool | SchemaBase | Map] = Undefined,
        lineBreak: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        lineHeight: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        minBandSize: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        opacity: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        order: Optional[bool | None] = Undefined,
        orient: Optional[SchemaBase | Orientation_T] = Undefined,
        outerRadius: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        padAngle: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        point: Optional[bool | SchemaBase | Literal["transparent"] | Map] = Undefined,
        radius: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        radius2: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        radius2Offset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        radiusOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        shape: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        size: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        smooth: Optional[bool | Parameter | SchemaBase | Map] = Undefined,
        stroke: Optional[
            str | Parameter | SchemaBase | Map | ColorName_T | None
        ] = Undefined,
        strokeCap: Optional[Parameter | SchemaBase | Map | StrokeCap_T] = Undefined,
        strokeDash: Optional[
            Parameter | SchemaBase | Sequence[float] | Map
        ] = Undefined,
        strokeDashOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        strokeJoin: Optional[Parameter | SchemaBase | Map | StrokeJoin_T] = Undefined,
        strokeMiterLimit: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        strokeOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        strokeOpacity: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        strokeWidth: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        style: Optional[str | Sequence[str]] = Undefined,
        tension: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        text: Optional[str | Parameter | SchemaBase | Sequence[str] | Map] = Undefined,
        theta: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        theta2: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        theta2Offset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        thetaOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        thickness: Optional[float] = Undefined,
        timeUnitBandPosition: Optional[float] = Undefined,
        timeUnitBandSize: Optional[float] = Undefined,
        tooltip: Optional[
            str | bool | float | Parameter | SchemaBase | Map | None
        ] = Undefined,
        url: Optional[str | Parameter | SchemaBase | Map] = Undefined,
        width: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        x: Optional[
            float | Parameter | SchemaBase | Literal["width"] | Map
        ] = Undefined,
        x2: Optional[
            float | Parameter | SchemaBase | Literal["width"] | Map
        ] = Undefined,
        x2Offset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        xOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        y: Optional[
            float | Parameter | SchemaBase | Literal["height"] | Map
        ] = Undefined,
        y2: Optional[
            float | Parameter | SchemaBase | Literal["height"] | Map
        ] = Undefined,
        y2Offset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        yOffset: Optional[float | Parameter | SchemaBase | Map] = Undefined,
        **kwds,
    ):
        super().__init__(
            align=align,
            angle=angle,
            aria=aria,
            ariaRole=ariaRole,
            ariaRoleDescription=ariaRoleDescription,
            aspect=aspect,
            bandSize=bandSize,
            baseline=baseline,
            binSpacing=binSpacing,
            blend=blend,
            clip=clip,
            color=color,
            continuousBandSize=continuousBandSize,
            cornerRadius=cornerRadius,
            cornerRadiusBottomLeft=cornerRadiusBottomLeft,
            cornerRadiusBottomRight=cornerRadiusBottomRight,
            cornerRadiusEnd=cornerRadiusEnd,
            cornerRadiusTopLeft=cornerRadiusTopLeft,
            cornerRadiusTopRight=cornerRadiusTopRight,
            cursor=cursor,
            description=description,
            dir=dir,
            discreteBandSize=discreteBandSize,
            dx=dx,
            dy=dy,
            ellipsis=ellipsis,
            fill=fill,
            fillOpacity=fillOpacity,
            filled=filled,
            font=font,
            fontSize=fontSize,
            fontStyle=fontStyle,
            fontWeight=fontWeight,
            height=height,
            href=href,
            innerRadius=innerRadius,
            interpolate=interpolate,
            invalid=invalid,
            limit=limit,
            line=line,
            lineBreak=lineBreak,
            lineHeight=lineHeight,
            minBandSize=minBandSize,
            opacity=opacity,
            order=order,
            orient=orient,
            outerRadius=outerRadius,
            padAngle=padAngle,
            point=point,
            radius=radius,
            radius2=radius2,
            radius2Offset=radius2Offset,
            radiusOffset=radiusOffset,
            shape=shape,
            size=size,
            smooth=smooth,
            stroke=stroke,
            strokeCap=strokeCap,
            strokeDash=strokeDash,
            strokeDashOffset=strokeDashOffset,
            strokeJoin=strokeJoin,
            strokeMiterLimit=strokeMiterLimit,
            strokeOffset=strokeOffset,
            strokeOpacity=strokeOpacity,
            strokeWidth=strokeWidth,
            style=style,
            tension=tension,
            text=text,
            theta=theta,
            theta2=theta2,
            theta2Offset=theta2Offset,
            thetaOffset=thetaOffset,
            thickness=thickness,
            timeUnitBandPosition=timeUnitBandPosition,
            timeUnitBandSize=timeUnitBandSize,
            tooltip=tooltip,
            url=url,
            width=width,
            x=x,
            x2=x2,
            x2Offset=x2Offset,
            xOffset=xOffset,
            y=y,
            y2=y2,
            y2Offset=y2Offset,
            yOffset=yOffset,
            **kwds,
        )


class _BoxPlotDef(SchemaBase):
    """
    BoxPlotDef schema wrapper.

    Parameters
    ----------
    box : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    clip : bool
        Whether a composite mark be clipped to the enclosing group's width and height.
    color : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    extent : float, Literal['min-max']
        The extent of the whiskers. Available options include:

        * ``"min-max"``: min and max are the lower and upper whiskers respectively.
        * A number representing multiple of the interquartile range. This number will be
          multiplied by the IQR to determine whisker boundary, which spans from the smallest
          data to the largest data within the range *[Q1 - k * IQR, Q3 + k * IQR]* where
          *Q1* and *Q3* are the first and third quartiles while *IQR* is the interquartile
          range (*Q3-Q1*).

        **Default value:** ``1.5``.
    invalid : :class:`MarkInvalidDataMode`, Literal['filter', 'break-paths-filter-domains', 'break-paths-show-domains', 'break-paths-show-path-domains', 'show'], None
        Invalid data mode, which defines how the marks and corresponding scales should
        represent invalid values (``null`` and ``NaN`` in continuous scales *without*
        defined output for invalid values).

        * ``"filter"`` — *Exclude* all invalid values from the visualization's *marks* and
          *scales*. For path marks (for line, area, trail), this option will create paths
          that connect valid points, as if the data rows with invalid values do not exist.

        * ``"break-paths-filter-domains"`` — Break path marks (for line, area, trail) at
          invalid values.  For non-path marks, this is equivalent to ``"filter"``. All
          *scale* domains will *exclude* these filtered data points.

        * ``"break-paths-show-domains"`` — Break paths (for line, area, trail) at invalid
          values.  Hide invalid values for non-path marks. All *scale* domains will
          *include* these filtered data points (for both path and non-path marks).

        * ``"show"`` or ``null`` — Show all data points in the marks and scale domains. Each
          scale will use the output for invalid values defined in ``config.scale.invalid``
          or, if unspecified, by default invalid values will produce the same visual values
          as zero (if the scale includes zero) or the minimum value (if the scale does not
          include zero).

        * ``"break-paths-show-path-domains"`` (default) — This is equivalent to
          ``"break-paths-show-domains"`` for path-based marks (line/area/trail) and
          ``"filter"`` for non-path marks.

        **Note**: If any channel's scale has an output for invalid values defined in
        ``config.scale.invalid``, all values for the scales will be considered "valid" since
        they can produce a reasonable output for the scales. Thus, fields for such channels
        will not be filtered and will not cause path breaks.
    median : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    opacity : float
        The opacity (value between [0,1]) of the mark.
    orient : :class:`Orientation`, Literal['horizontal', 'vertical']
        Orientation of the box plot. This is normally automatically determined based on
        types of fields on x and y channels. However, an explicit ``orient`` be specified
        when the orientation is ambiguous.

        **Default value:** ``"vertical"``.
    outliers : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    rule : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    size : float
        Size of the box and median tick of a box plot
    ticks : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    """

    _schema = {"$ref": "#/definitions/BoxPlotDef"}

    def __init__(
        self,
        box: Optional[bool | SchemaBase | Map] = Undefined,
        clip: Optional[bool] = Undefined,
        color: Optional[str | Parameter | SchemaBase | Map | ColorName_T] = Undefined,
        extent: Optional[float | Literal["min-max"]] = Undefined,
        invalid: Optional[SchemaBase | MarkInvalidDataMode_T | None] = Undefined,
        median: Optional[bool | SchemaBase | Map] = Undefined,
        opacity: Optional[float] = Undefined,
        orient: Optional[SchemaBase | Orientation_T] = Undefined,
        outliers: Optional[bool | SchemaBase | Map] = Undefined,
        rule: Optional[bool | SchemaBase | Map] = Undefined,
        size: Optional[float] = Undefined,
        ticks: Optional[bool | SchemaBase | Map] = Undefined,
        **kwds,
    ):
        super().__init__(
            box=box,
            clip=clip,
            color=color,
            extent=extent,
            invalid=invalid,
            median=median,
            opacity=opacity,
            orient=orient,
            outliers=outliers,
            rule=rule,
            size=size,
            ticks=ticks,
            **kwds,
        )


class _ErrorBarDef(SchemaBase):
    """
    ErrorBarDef schema wrapper.

    Parameters
    ----------
    clip : bool
        Whether a composite mark be clipped to the enclosing group's width and height.
    color : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    extent : :class:`ErrorBarExtent`, Literal['ci', 'iqr', 'stderr', 'stdev']
        The extent of the rule. Available options include:

        * ``"ci"``: Extend the rule to the confidence interval of the mean.
        * ``"stderr"``: The size of rule are set to the value of standard error, extending
          from the mean.
        * ``"stdev"``: The size of rule are set to the value of standard deviation,
          extending from the mean.
        * ``"iqr"``: Extend the rule to the q1 and q3.

        **Default value:** ``"stderr"``.
    opacity : float
        The opacity (value between [0,1]) of the mark.
    orient : :class:`Orientation`, Literal['horizontal', 'vertical']
        Orientation of the error bar. This is normally automatically determined, but can be
        specified when the orientation is ambiguous and cannot be automatically determined.
    rule : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    size : float
        Size of the ticks of an error bar
    thickness : float
        Thickness of the ticks and the bar of an error bar
    ticks : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    """

    _schema = {"$ref": "#/definitions/ErrorBarDef"}

    def __init__(
        self,
        clip: Optional[bool] = Undefined,
        color: Optional[str | Parameter | SchemaBase | Map | ColorName_T] = Undefined,
        extent: Optional[SchemaBase | ErrorBarExtent_T] = Undefined,
        opacity: Optional[float] = Undefined,
        orient: Optional[SchemaBase | Orientation_T] = Undefined,
        rule: Optional[bool | SchemaBase | Map] = Undefined,
        size: Optional[float] = Undefined,
        thickness: Optional[float] = Undefined,
        ticks: Optional[bool | SchemaBase | Map] = Undefined,
        **kwds,
    ):
        super().__init__(
            clip=clip,
            color=color,
            extent=extent,
            opacity=opacity,
            orient=orient,
            rule=rule,
            size=size,
            thickness=thickness,
            ticks=ticks,
            **kwds,
        )


class _ErrorBandDef(SchemaBase):
    """
    ErrorBandDef schema wrapper.

    Parameters
    ----------
    band : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    borders : bool, dict, :class:`BarConfig`, :class:`AreaConfig`, :class:`LineConfig`, :class:`MarkConfig`, :class:`RectConfig`, :class:`TickConfig`, :class:`AnyMarkConfig`

    clip : bool
        Whether a composite mark be clipped to the enclosing group's width and height.
    color : str, dict, :class:`Color`, :class:`ExprRef`, :class:`Gradient`, :class:`HexColor`, :class:`ColorName`, :class:`LinearGradient`, :class:`RadialGradient`, Literal['black', 'silver', 'gray', 'white', 'maroon', 'red', 'purple', 'fuchsia', 'green', 'lime', 'olive', 'yellow', 'navy', 'blue', 'teal', 'aqua', 'orange', 'aliceblue', 'antiquewhite', 'aquamarine', 'azure', 'beige', 'bisque', 'blanchedalmond', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'firebrick', 'floralwhite', 'forestgreen', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgray', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'limegreen', 'linen', 'magenta', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'oldlace', 'olivedrab', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'thistle', 'tomato', 'turquoise', 'violet', 'wheat', 'whitesmoke', 'yellowgreen', 'rebeccapurple']
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    extent : :class:`ErrorBarExtent`, Literal['ci', 'iqr', 'stderr', 'stdev']
        The extent of the band. Available options include:

        * ``"ci"``: Extend the band to the confidence interval of the mean.
        * ``"stderr"``: The size of band are set to the value of standard error, extending
          from the mean.
        * ``"stdev"``: The size of band are set to the value of standard deviation,
          extending from the mean.
        * ``"iqr"``: Extend the band to the q1 and q3.

        **Default value:** ``"stderr"``.
    interpolate : :class:`Interpolate`, Literal['basis', 'basis-open', 'basis-closed', 'bundle', 'cardinal', 'cardinal-open', 'cardinal-closed', 'catmull-rom', 'linear', 'linear-closed', 'monotone', 'natural', 'step', 'step-before', 'step-after']
        The line interpolation method for the error band. One of the following:

        * ``"linear"``: piecewise linear segments, as in a polyline.
        * ``"linear-closed"``: close the linear segments to form a polygon.
        * ``"step"``: a piecewise constant function (a step function) consisting of
          alternating horizontal and vertical lines. The y-value changes at the midpoint of
          each pair of adjacent x-values.
        * ``"step-before"``: a piecewise constant function (a step function) consisting of
          alternating horizontal and vertical lines. The y-value changes before the x-value.
        * ``"step-after"``: a piecewise constant function (a step function) consisting of
          alternating horizontal and vertical lines. The y-value changes after the x-value.
        * ``"basis"``: a B-spline, with control point duplication on the ends.
        * ``"basis-open"``: an open B-spline; may not intersect the start or end.
        * ``"basis-closed"``: a closed B-spline, as in a loop.
        * ``"cardinal"``: a Cardinal spline, with control point duplication on the ends.
        * ``"cardinal-open"``: an open Cardinal spline; may not intersect the start or end,
          but will intersect other control points.
        * ``"cardinal-closed"``: a closed Cardinal spline, as in a loop.
        * ``"bundle"``: equivalent to basis, except the tension parameter is used to
          straighten the spline.
        * ``"monotone"``: cubic interpolation that preserves monotonicity in y.
    opacity : float
        The opacity (value between [0,1]) of the mark.
    orient : :class:`Orientation`, Literal['horizontal', 'vertical']
        Orientation of the error band. This is normally automatically determined, but can be
        specified when the orientation is ambiguous and cannot be automatically determined.
    tension : float
        The tension parameter for the interpolation type of the error band.
    """

    _schema = {"$ref": "#/definitions/ErrorBandDef"}

    def __init__(
        self,
        band: Optional[bool | SchemaBase | Map] = Undefined,
        borders: Optional[bool | SchemaBase | Map] = Undefined,
        clip: Optional[bool] = Undefined,
        color: Optional[str | Parameter | SchemaBase | Map | ColorName_T] = Undefined,
        extent: Optional[SchemaBase | ErrorBarExtent_T] = Undefined,
        interpolate: Optional[SchemaBase | Interpolate_T] = Undefined,
        opacity: Optional[float] = Undefined,
        orient: Optional[SchemaBase | Orientation_T] = Undefined,
        tension: Optional[float] = Undefined,
        **kwds,
    ):
        super().__init__(
            band=band,
            borders=borders,
            clip=clip,
            color=color,
            extent=extent,
            interpolate=interpolate,
            opacity=opacity,
            orient=orient,
            tension=tension,
            **kwds,
        )


class MarkMethodMixin:
    """A mixin class that defines mark methods."""

    @use_signature(_MarkDef)
    def mark_arc(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'arc' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="arc", **kwds)
        else:
            copy.mark = "arc"
        return copy

    @use_signature(_MarkDef)
    def mark_area(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'area' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="area", **kwds)
        else:
            copy.mark = "area"
        return copy

    @use_signature(_MarkDef)
    def mark_bar(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'bar' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="bar", **kwds)
        else:
            copy.mark = "bar"
        return copy

    @use_signature(_MarkDef)
    def mark_image(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'image' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="image", **kwds)
        else:
            copy.mark = "image"
        return copy

    @use_signature(_MarkDef)
    def mark_line(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'line' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="line", **kwds)
        else:
            copy.mark = "line"
        return copy

    @use_signature(_MarkDef)
    def mark_point(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'point' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="point", **kwds)
        else:
            copy.mark = "point"
        return copy

    @use_signature(_MarkDef)
    def mark_rect(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'rect' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="rect", **kwds)
        else:
            copy.mark = "rect"
        return copy

    @use_signature(_MarkDef)
    def mark_rule(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'rule' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="rule", **kwds)
        else:
            copy.mark = "rule"
        return copy

    @use_signature(_MarkDef)
    def mark_text(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'text' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="text", **kwds)
        else:
            copy.mark = "text"
        return copy

    @use_signature(_MarkDef)
    def mark_tick(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'tick' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="tick", **kwds)
        else:
            copy.mark = "tick"
        return copy

    @use_signature(_MarkDef)
    def mark_trail(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'trail' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="trail", **kwds)
        else:
            copy.mark = "trail"
        return copy

    @use_signature(_MarkDef)
    def mark_circle(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'circle' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="circle", **kwds)
        else:
            copy.mark = "circle"
        return copy

    @use_signature(_MarkDef)
    def mark_square(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'square' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="square", **kwds)
        else:
            copy.mark = "square"
        return copy

    @use_signature(_MarkDef)
    def mark_geoshape(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'geoshape' (see :class:`MarkDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.MarkDef(type="geoshape", **kwds)
        else:
            copy.mark = "geoshape"
        return copy

    @use_signature(_BoxPlotDef)
    def mark_boxplot(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'boxplot' (see :class:`BoxPlotDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.BoxPlotDef(type="boxplot", **kwds)
        else:
            copy.mark = "boxplot"
        return copy

    @use_signature(_ErrorBarDef)
    def mark_errorbar(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'errorbar' (see :class:`ErrorBarDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.ErrorBarDef(type="errorbar", **kwds)
        else:
            copy.mark = "errorbar"
        return copy

    @use_signature(_ErrorBandDef)
    def mark_errorband(self, **kwds: Any) -> Self:
        """Set the chart's mark to 'errorband' (see :class:`ErrorBandDef`)."""
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        if any(val is not Undefined for val in kwds.values()):
            copy.mark = core.ErrorBandDef(type="errorband", **kwds)
        else:
            copy.mark = "errorband"
        return copy


class ConfigMethodMixin:
    """A mixin class that defines config methods."""

    @use_signature(core.Config)
    def configure(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=False)  # type: ignore[attr-defined]
        copy.config = core.Config(*args, **kwargs)
        return copy

    @use_signature(core.RectConfig)
    def configure_arc(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["arc"] = core.RectConfig(*args, **kwargs)
        return copy

    @use_signature(core.AreaConfig)
    def configure_area(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["area"] = core.AreaConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axis(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axis"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisBand(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisBand"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisBottom(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisBottom"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisDiscrete(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisDiscrete"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisLeft(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisLeft"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisPoint(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisPoint"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisQuantitative(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisQuantitative"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisRight(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisRight"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisTemporal(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisTemporal"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisTop(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisTop"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisX(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisX"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisXBand(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisXBand"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisXDiscrete(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisXDiscrete"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisXPoint(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisXPoint"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisXQuantitative(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisXQuantitative"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisXTemporal(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisXTemporal"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisY(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisY"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisYBand(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisYBand"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisYDiscrete(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisYDiscrete"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisYPoint(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisYPoint"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisYQuantitative(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisYQuantitative"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.AxisConfig)
    def configure_axisYTemporal(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["axisYTemporal"] = core.AxisConfig(*args, **kwargs)
        return copy

    @use_signature(core.BarConfig)
    def configure_bar(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["bar"] = core.BarConfig(*args, **kwargs)
        return copy

    @use_signature(core.BoxPlotConfig)
    def configure_boxplot(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["boxplot"] = core.BoxPlotConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_circle(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["circle"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.CompositionConfig)
    def configure_concat(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["concat"] = core.CompositionConfig(*args, **kwargs)
        return copy

    @use_signature(core.ErrorBandConfig)
    def configure_errorband(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["errorband"] = core.ErrorBandConfig(*args, **kwargs)
        return copy

    @use_signature(core.ErrorBarConfig)
    def configure_errorbar(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["errorbar"] = core.ErrorBarConfig(*args, **kwargs)
        return copy

    @use_signature(core.CompositionConfig)
    def configure_facet(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["facet"] = core.CompositionConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_geoshape(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["geoshape"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.HeaderConfig)
    def configure_header(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["header"] = core.HeaderConfig(*args, **kwargs)
        return copy

    @use_signature(core.HeaderConfig)
    def configure_headerColumn(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["headerColumn"] = core.HeaderConfig(*args, **kwargs)
        return copy

    @use_signature(core.HeaderConfig)
    def configure_headerFacet(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["headerFacet"] = core.HeaderConfig(*args, **kwargs)
        return copy

    @use_signature(core.HeaderConfig)
    def configure_headerRow(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["headerRow"] = core.HeaderConfig(*args, **kwargs)
        return copy

    @use_signature(core.RectConfig)
    def configure_image(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["image"] = core.RectConfig(*args, **kwargs)
        return copy

    @use_signature(core.LegendConfig)
    def configure_legend(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["legend"] = core.LegendConfig(*args, **kwargs)
        return copy

    @use_signature(core.LineConfig)
    def configure_line(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["line"] = core.LineConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_mark(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["mark"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_point(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["point"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.ProjectionConfig)
    def configure_projection(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["projection"] = core.ProjectionConfig(*args, **kwargs)
        return copy

    @use_signature(core.RangeConfig)
    def configure_range(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["range"] = core.RangeConfig(*args, **kwargs)
        return copy

    @use_signature(core.RectConfig)
    def configure_rect(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["rect"] = core.RectConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_rule(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["rule"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.ScaleConfig)
    def configure_scale(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["scale"] = core.ScaleConfig(*args, **kwargs)
        return copy

    @use_signature(core.SelectionConfig)
    def configure_selection(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["selection"] = core.SelectionConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_square(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["square"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.MarkConfig)
    def configure_text(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["text"] = core.MarkConfig(*args, **kwargs)
        return copy

    @use_signature(core.TickConfig)
    def configure_tick(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["tick"] = core.TickConfig(*args, **kwargs)
        return copy

    @use_signature(core.TitleConfig)
    def configure_title(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["title"] = core.TitleConfig(*args, **kwargs)
        return copy

    @use_signature(core.FormatConfig)
    def configure_tooltipFormat(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["tooltipFormat"] = core.FormatConfig(*args, **kwargs)
        return copy

    @use_signature(core.LineConfig)
    def configure_trail(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["trail"] = core.LineConfig(*args, **kwargs)
        return copy

    @use_signature(core.ViewConfig)
    def configure_view(self, *args, **kwargs) -> Self:
        copy = self.copy(deep=["config"])  # type: ignore[attr-defined]
        if copy.config is Undefined:
            copy.config = core.Config()
        copy.config["view"] = core.ViewConfig(*args, **kwargs)
        return copy
