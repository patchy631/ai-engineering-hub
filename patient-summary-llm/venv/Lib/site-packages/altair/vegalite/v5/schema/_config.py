# The contents of this file are automatically written by
# tools/generate_schema_wrapper.py. Do not modify directly.

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, Literal, TypedDict

if sys.version_info >= (3, 14):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from ._typing import PaddingKwds, RowColKwds

if TYPE_CHECKING:
    # ruff: noqa: F405
    from collections.abc import Sequence

    from ._typing import *  # noqa: F403


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
]


class AreaConfigKwds(TypedDict, total=False):
    """
    :class:`altair.AreaConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    line
        A flag for overlaying line on top of area marks, or an object defining the
        properties of the overlayed lines.

        * If this value is an empty object (``{}``) or ``true``, lines with default
          properties will be used.

        * If this value is ``false``, no lines would be automatically added to area marks.

        **Default value:** ``false``.
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    point
        A flag for overlaying points on top of line or area marks, or an object defining the
        properties of the overlayed points.

        * If this property is ``"transparent"``, transparent points will be used (for
          enhancing tooltips and selections).

        * If this property is an empty object (``{}``) or ``true``, filled points with
          default properties will be used.

        * If this property is ``false``, no points would be automatically added to line or
          area marks.

        **Default value:** ``false``.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    line: bool | OverlayMarkDefKwds
    lineBreak: str
    lineHeight: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    point: bool | OverlayMarkDefKwds | Literal["transparent"]
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class AutoSizeParamsKwds(TypedDict, total=False):
    """
    :class:`altair.AutoSizeParams` ``TypedDict`` wrapper.

    Parameters
    ----------
    contains
        Determines how size calculation should be performed, one of ``"content"`` or
        ``"padding"``. The default setting (``"content"``) interprets the width and height
        settings as the data rectangle (plotting) dimensions, to which padding is then
        added. In contrast, the ``"padding"`` setting includes the padding within the view
        size calculations, such that the width and height settings indicate the **total**
        intended size of the view.

        **Default value**: ``"content"``
    resize
        A boolean flag indicating if autosize layout should be re-calculated on every view
        update.

        **Default value**: ``false``
    type
        The sizing format type. One of ``"pad"``, ``"fit"``, ``"fit-x"``, ``"fit-y"``,  or
        ``"none"``. See the `autosize type
        <https://vega.github.io/vega-lite/docs/size.html#autosize>`__ documentation for
        descriptions of each.

        **Default value**: ``"pad"``
    """

    contains: Literal["content", "padding"]
    resize: bool
    type: AutosizeType_T


class AxisConfigKwds(TypedDict, total=False):
    """
    :class:`altair.AxisConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG group, removing the axis from the ARIA accessibility tree.

        **Default value:** ``true``
    bandPosition
        An interpolation fraction indicating where, for ``band`` scales, axis ticks should
        be positioned. A value of ``0`` places ticks at the left edge of their bands. A
        value of ``0.5`` places ticks in the middle of their bands.

        **Default value:** ``0.5``
    description
        A text description of this axis for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If the ``aria`` property is true, for SVG output the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__
        will be set to this description. If the description is unspecified it will be
        automatically generated.
    disable
        Disable axis by default.
    domain
        A boolean flag indicating if the domain (the axis baseline) should be included as
        part of the axis.

        **Default value:** ``true``
    domainCap
        The stroke cap for the domain line's ending style. One of ``"butt"``, ``"round"`` or
        ``"square"``.

        **Default value:** ``"butt"``
    domainColor
        Color of axis domain line.

        **Default value:** ``"gray"``.
    domainDash
        An array of alternating [stroke, space] lengths for dashed domain lines.
    domainDashOffset
        The pixel offset at which to start drawing with the domain dash array.
    domainOpacity
        Opacity of the axis domain line.
    domainWidth
        Stroke width of axis domain line

        **Default value:** ``1``
    format
        When used with the default ``"number"`` and ``"time"`` format type, the text
        formatting pattern for labels of guides (axes, legends, headers) and text marks.

        * If the format type is ``"number"`` (e.g., for quantitative fields), this is D3's
          `number format pattern <https://github.com/d3/d3-format#locale_format>`__.
        * If the format type is ``"time"`` (e.g., for temporal fields), this is D3's `time
          format pattern <https://github.com/d3/d3-time-format#locale_format>`__.

        See the `format documentation <https://vega.github.io/vega-lite/docs/format.html>`__
        for more examples.

        When used with a `custom formatType
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__, this
        value will be passed as ``format`` alongside ``datum.value`` to the registered
        function.

        **Default value:**  Derived from `numberFormat
        <https://vega.github.io/vega-lite/docs/config.html#format>`__ config for number
        format and from `timeFormat
        <https://vega.github.io/vega-lite/docs/config.html#format>`__ config for time
        format.
    formatType
        The format type for labels. One of ``"number"``, ``"time"``, or a `registered custom
        format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__.

        **Default value:**

        * ``"time"`` for temporal fields and ordinal and nominal fields with ``timeUnit``.
        * ``"number"`` for quantitative fields as well as ordinal and nominal fields without
          ``timeUnit``.
    grid
        A boolean flag indicating if grid lines should be included as part of the axis

        **Default value:** ``true`` for `continuous scales
        <https://vega.github.io/vega-lite/docs/scale.html#continuous>`__ that are not
        binned; otherwise, ``false``.
    gridCap
        The stroke cap for grid lines' ending style. One of ``"butt"``, ``"round"`` or
        ``"square"``.

        **Default value:** ``"butt"``
    gridColor
        Color of gridlines.

        **Default value:** ``"lightGray"``.
    gridDash
        An array of alternating [stroke, space] lengths for dashed grid lines.
    gridDashOffset
        The pixel offset at which to start drawing with the grid dash array.
    gridOpacity
        The stroke opacity of grid (value between [0,1])

        **Default value:** ``1``
    gridWidth
        The grid width, in pixels.

        **Default value:** ``1``
    labelAlign
        Horizontal text alignment of axis tick labels, overriding the default setting for
        the current axis orientation.
    labelAngle
        The rotation angle of the axis labels.

        **Default value:** ``-90`` for nominal and ordinal fields; ``0`` otherwise.
    labelBaseline
        Vertical text baseline of axis tick labels, overriding the default setting for the
        current axis orientation. One of ``"alphabetic"`` (default), ``"top"``,
        ``"middle"``, ``"bottom"``, ``"line-top"``, or ``"line-bottom"``. The ``"line-top"``
        and ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but
        are calculated relative to the *lineHeight* rather than *fontSize* alone.
    labelBound
        Indicates if labels should be hidden if they exceed the axis range. If ``false``
        (the default) no bounds overlap analysis is performed. If ``true``, labels will be
        hidden if they exceed the axis range by more than 1 pixel. If this property is a
        number, it specifies the pixel tolerance: the maximum amount by which a label
        bounding box may exceed the axis range.

        **Default value:** ``false``.
    labelColor
        The color of the tick label, can be in hex color code or regular color name.
    labelExpr
        `Vega expression <https://vega.github.io/vega/docs/expressions/>`__ for customizing
        labels.

        **Note:** The label text and value can be assessed via the ``label`` and ``value``
        properties of the axis's backing ``datum`` object.
    labelFlush
        Indicates if the first and last axis labels should be aligned flush with the scale
        range. Flush alignment for a horizontal axis will left-align the first label and
        right-align the last label. For vertical axes, bottom and top text baselines are
        applied instead. If this property is a number, it also indicates the number of
        pixels by which to offset the first and last labels; for example, a value of 2 will
        flush-align the first and last labels and also push them 2 pixels outward from the
        center of the axis. The additional adjustment can sometimes help the labels better
        visually group with corresponding axis ticks.

        **Default value:** ``true`` for axis of a continuous x-scale. Otherwise, ``false``.
    labelFlushOffset
        Indicates the number of pixels by which to offset flush-adjusted labels. For
        example, a value of ``2`` will push flush-adjusted labels 2 pixels outward from the
        center of the axis. Offsets can help the labels better visually group with
        corresponding axis ticks.

        **Default value:** ``0``.
    labelFont
        The font of the tick label.
    labelFontSize
        The font size of the label, in pixels.
    labelFontStyle
        Font style of the title.
    labelFontWeight
        Font weight of axis tick labels.
    labelLimit
        Maximum allowed pixel width of axis tick labels.

        **Default value:** ``180``
    labelLineHeight
        Line height in pixels for multi-line label text or label text with ``"line-top"`` or
        ``"line-bottom"`` baseline.
    labelOffset
        Position offset in pixels to apply to labels, in addition to tickOffset.

        **Default value:** ``0``
    labelOpacity
        The opacity of the labels.
    labelOverlap
        The strategy to use for resolving overlap of axis labels. If ``false`` (the
        default), no overlap reduction is attempted. If set to ``true`` or ``"parity"``, a
        strategy of removing every other label is used (this works well for standard linear
        axes). If set to ``"greedy"``, a linear scan of the labels is performed, removing
        any labels that overlaps with the last visible label (this often works better for
        log-scaled axes).

        **Default value:** ``true`` for non-nominal fields with non-log scales; ``"greedy"``
        for log scales; otherwise ``false``.
    labelPadding
        The padding in pixels between labels and ticks.

        **Default value:** ``2``
    labelSeparation
        The minimum separation that must be between label bounding boxes for them to be
        considered non-overlapping (default ``0``). This property is ignored if
        *labelOverlap* resolution is not enabled.
    labels
        A boolean flag indicating if labels should be included as part of the axis.

        **Default value:** ``true``.
    maxExtent
        The maximum extent in pixels that axis ticks and labels should use. This determines
        a maximum offset value for axis titles.

        **Default value:** ``undefined``.
    minExtent
        The minimum extent in pixels that axis ticks and labels should use. This determines
        a minimum offset value for axis titles.

        **Default value:** ``30`` for y-axis; ``undefined`` for x-axis.
    offset
        The offset, in pixels, by which to displace the axis from the edge of the enclosing
        group or data rectangle.

        **Default value:** derived from the `axis config
        <https://vega.github.io/vega-lite/docs/config.html#facet-scale-config>`__'s
        ``offset`` (``0`` by default)
    orient
        The orientation of the axis. One of ``"top"``, ``"bottom"``, ``"left"`` or
        ``"right"``. The orientation can be used to further specialize the axis type (e.g.,
        a y-axis oriented towards the right edge of the chart).

        **Default value:** ``"bottom"`` for x-axes and ``"left"`` for y-axes.
    position
        The anchor position of the axis in pixels. For x-axes with top or bottom
        orientation, this sets the axis group x coordinate. For y-axes with left or right
        orientation, this sets the axis group y coordinate.

        **Default value**: ``0``
    style
        A string or array of strings indicating the name of custom styles to apply to the
        axis. A style is a named collection of axis property defined within the `style
        configuration <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__. If
        style is an array, later styles will override earlier styles.

        **Default value:** (none) **Note:** Any specified style will augment the default
        style. For example, an x-axis mark with ``"style": "foo"`` will use ``config.axisX``
        and ``config.style.foo`` (the specified style ``"foo"`` has higher precedence).
    tickBand
        For band scales, indicates if ticks and grid lines should be placed at the
        ``"center"`` of a band (default) or at the band ``"extent"``s to indicate intervals
    tickCap
        The stroke cap for the tick lines' ending style. One of ``"butt"``, ``"round"`` or
        ``"square"``.

        **Default value:** ``"butt"``
    tickColor
        The color of the axis's tick.

        **Default value:** ``"gray"``
    tickCount
        A desired number of ticks, for axes visualizing quantitative scales. The resulting
        number may be different so that values are "nice" (multiples of 2, 5, 10) and lie
        within the underlying scale's range.

        For scales of type ``"time"`` or ``"utc"``, the tick count can instead be a time
        interval specifier. Legal string values are ``"millisecond"``, ``"second"``,
        ``"minute"``, ``"hour"``, ``"day"``, ``"week"``, ``"month"``, and ``"year"``.
        Alternatively, an object-valued interval specifier of the form ``{"interval":
        "month", "step": 3}`` includes a desired number of interval steps. Here, ticks are
        generated for each quarter (Jan, Apr, Jul, Oct) boundary.

        **Default value**: Determine using a formula ``ceil(width/40)`` for x and
        ``ceil(height/40)`` for y.
    tickDash
        An array of alternating [stroke, space] lengths for dashed tick mark lines.
    tickDashOffset
        The pixel offset at which to start drawing with the tick mark dash array.
    tickExtra
        Boolean flag indicating if an extra axis tick should be added for the initial
        position of the axis. This flag is useful for styling axes for ``band`` scales such
        that ticks are placed on band boundaries rather in the middle of a band. Use in
        conjunction with ``"bandPosition": 1`` and an axis ``"padding"`` value of ``0``.
    tickMinStep
        The minimum desired step between axis ticks, in terms of scale domain values. For
        example, a value of ``1`` indicates that ticks should not be less than 1 unit apart.
        If ``tickMinStep`` is specified, the ``tickCount`` value will be adjusted, if
        necessary, to enforce the minimum step value.
    tickOffset
        Position offset in pixels to apply to ticks, labels, and gridlines.
    tickOpacity
        Opacity of the ticks.
    tickRound
        Boolean flag indicating if pixel position values should be rounded to the nearest
        integer.

        **Default value:** ``true``
    tickSize
        The size in pixels of axis ticks.

        **Default value:** ``5``
    tickWidth
        The width, in pixels, of ticks.

        **Default value:** ``1``
    ticks
        Boolean value that determines whether the axis should include ticks.

        **Default value:** ``true``
    title
        A title for the field. If ``null``, the title will be removed.

        **Default value:**  derived from the field's name and transformation function
        (``aggregate``, ``bin`` and ``timeUnit``). If the field has an aggregate function,
        the function is displayed as part of the title (e.g., ``"Sum of Profit"``). If the
        field is binned or has a time unit applied, the applied function is shown in
        parentheses (e.g., ``"Profit (binned)"``, ``"Transaction Date (year-month)"``).
        Otherwise, the title is simply the field name.

        **Notes**:

        1) You can customize the default field title format by providing the `fieldTitle
        <https://vega.github.io/vega-lite/docs/config.html#top-level-config>`__ property in
        the `config <https://vega.github.io/vega-lite/docs/config.html>`__ or `fieldTitle
        function via the compile function's options
        <https://vega.github.io/vega-lite/usage/compile.html#field-title>`__.

        2) If both field definition's ``title`` and axis, header, or legend ``title`` are
        defined, axis/header/legend title will be used.
    titleAlign
        Horizontal text alignment of axis titles.
    titleAnchor
        Text anchor position for placing axis titles.
    titleAngle
        Angle in degrees of axis titles.
    titleBaseline
        Vertical text baseline for axis titles. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or ``"line-bottom"``. The
        ``"line-top"`` and ``"line-bottom"`` values operate similarly to ``"top"`` and
        ``"bottom"``, but are calculated relative to the *lineHeight* rather than *fontSize*
        alone.
    titleColor
        Color of the title, can be in hex color code or regular color name.
    titleFont
        Font of the title. (e.g., ``"Helvetica Neue"``).
    titleFontSize
        Font size of the title.
    titleFontStyle
        Font style of the title.
    titleFontWeight
        Font weight of the title. This can be either a string (e.g ``"bold"``, ``"normal"``)
        or a number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400``
        and ``"bold"`` = ``700``).
    titleLimit
        Maximum allowed pixel width of axis titles.
    titleLineHeight
        Line height in pixels for multi-line title text or title text with ``"line-top"`` or
        ``"line-bottom"`` baseline.
    titleOpacity
        Opacity of the axis title.
    titlePadding
        The padding, in pixels, between title and axis.
    titleX
        X-coordinate of the axis title relative to the axis group.
    titleY
        Y-coordinate of the axis title relative to the axis group.
    translate
        Coordinate space translation offset for axis layout. By default, axes are translated
        by a 0.5 pixel offset for both the x and y coordinates in order to align stroked
        lines with the pixel grid. However, for vector graphics output these pixel-specific
        adjustments may be undesirable, in which case translate can be changed (for example,
        to zero).

        **Default value:** ``0.5``
    values
        Explicitly set the visible axis tick values.
    zindex
        A non-negative integer indicating the z-index of the axis. If zindex is 0, axes
        should be drawn behind all chart elements. To put them in front, set ``zindex`` to
        ``1`` or more.

        **Default value:** ``0`` (behind the marks).
    """

    aria: bool
    bandPosition: float
    description: str
    disable: bool
    domain: bool
    domainCap: StrokeCap_T
    domainColor: ColorHex | ColorName_T | None
    domainDash: Sequence[float]
    domainDashOffset: float
    domainOpacity: float
    domainWidth: float
    format: str
    formatType: str
    grid: bool
    gridCap: StrokeCap_T
    gridColor: ColorHex | ColorName_T | None
    gridDash: Sequence[float]
    gridDashOffset: float
    gridOpacity: float
    gridWidth: float
    labelAlign: Align_T
    labelAngle: float
    labelBaseline: TextBaseline_T
    labelBound: bool | float
    labelColor: ColorHex | ColorName_T | None
    labelExpr: str
    labelFlush: bool | float
    labelFlushOffset: float
    labelFont: str
    labelFontSize: float
    labelFontStyle: str
    labelFontWeight: FontWeight_T
    labelLimit: float
    labelLineHeight: float
    labelOffset: float
    labelOpacity: float
    labelOverlap: bool | Literal["greedy", "parity"]
    labelPadding: float
    labelSeparation: float
    labels: bool
    maxExtent: float
    minExtent: float
    offset: float
    orient: AxisOrient_T
    position: float
    style: str | Sequence[str]
    tickBand: Literal["center", "extent"]
    tickCap: StrokeCap_T
    tickColor: ColorHex | ColorName_T | None
    tickCount: float | TimeIntervalStepKwds | TimeInterval_T
    tickDash: Sequence[float]
    tickDashOffset: float
    tickExtra: bool
    tickMinStep: float
    tickOffset: float
    tickOpacity: float
    tickRound: bool
    tickSize: float
    tickWidth: float
    ticks: bool
    title: str | Sequence[str] | None
    titleAlign: Align_T
    titleAnchor: TitleAnchor_T
    titleAngle: float
    titleBaseline: TextBaseline_T
    titleColor: ColorHex | ColorName_T | None
    titleFont: str
    titleFontSize: float
    titleFontStyle: str
    titleFontWeight: FontWeight_T
    titleLimit: float
    titleLineHeight: float
    titleOpacity: float
    titlePadding: float
    titleX: float
    titleY: float
    translate: float
    values: Sequence[str] | Sequence[bool] | Sequence[float] | Sequence[DateTimeKwds]
    zindex: float


class AxisResolveMapKwds(TypedDict, total=False):
    """
    :class:`altair.AxisResolveMap` ``TypedDict`` wrapper.

    Parameters
    ----------
    x

    y

    """

    x: ResolveMode_T
    y: ResolveMode_T


class BarConfigKwds(TypedDict, total=False):
    """
    :class:`altair.BarConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    binSpacing
        Offset between bars for binned field. The ideal value for this is either 0
        (preferred by statisticians) or 1 (Vega-Lite default, D3 example style).

        **Default value:** ``1``
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    continuousBandSize
        The default size of the bars on continuous scales.

        **Default value:** ``5``
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusEnd
        * For vertical bars, top-left and top-right corner radius.

        * For horizontal bars, top-right and bottom-right corner radius.
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    discreteBandSize
        The default size of the bars with discrete dimensions. If unspecified, the default
        size is  ``step-2``, which provides 2 pixel offset between bars.
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    minBandSize
        The minimum band size for bar and rectangle marks. **Default value:** ``0.25``
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    binSpacing: float
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    continuousBandSize: float
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusEnd: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    discreteBandSize: float
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    minBandSize: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class BindCheckboxKwds(TypedDict, total=False):
    """
    :class:`altair.BindCheckbox` ``TypedDict`` wrapper.

    Parameters
    ----------
    input

    debounce
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    element
        An optional CSS selector string indicating the parent element to which the input
        element should be added. By default, all input elements are added within the parent
        container of the Vega view.
    name
        By default, the signal name is used to label input elements. This ``name`` property
        can be used instead to specify a custom label for the bound signal.
    """

    input: Literal["checkbox"]
    debounce: float
    element: str
    name: str


class BindDirectKwds(TypedDict, total=False):
    """
    :class:`altair.BindDirect` ``TypedDict`` wrapper.

    Parameters
    ----------
    element
        An input element that exposes a *value* property and supports the `EventTarget
        <https://developer.mozilla.org/en-US/docs/Web/API/EventTarget>`__ interface, or a
        CSS selector string to such an element. When the element updates and dispatches an
        event, the *value* property will be used as the new, bound signal value. When the
        signal updates independent of the element, the *value* property will be set to the
        signal value and a new event will be dispatched on the element.
    debounce
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    event
        The event (default ``"input"``) to listen for to track changes on the external
        element.
    """

    element: str
    debounce: float
    event: str


class BindInputKwds(TypedDict, total=False):
    """
    :class:`altair.BindInput` ``TypedDict`` wrapper.

    Parameters
    ----------
    autocomplete
        A hint for form autofill. See the `HTML autocomplete attribute
        <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete>`__ for
        additional information.
    debounce
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    element
        An optional CSS selector string indicating the parent element to which the input
        element should be added. By default, all input elements are added within the parent
        container of the Vega view.
    input
        The type of input element to use. The valid values are ``"checkbox"``, ``"radio"``,
        ``"range"``, ``"select"``, and any other legal `HTML form input type
        <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input>`__.
    name
        By default, the signal name is used to label input elements. This ``name`` property
        can be used instead to specify a custom label for the bound signal.
    placeholder
        Text that appears in the form control when it has no value set.
    """

    autocomplete: str
    debounce: float
    element: str
    input: str
    name: str
    placeholder: str


class BindRadioSelectKwds(TypedDict, total=False):
    """
    :class:`altair.BindRadioSelect` ``TypedDict`` wrapper.

    Parameters
    ----------
    input

    options
        An array of options to select from.
    debounce
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    element
        An optional CSS selector string indicating the parent element to which the input
        element should be added. By default, all input elements are added within the parent
        container of the Vega view.
    labels
        An array of label strings to represent the ``options`` values. If unspecified, the
        ``options`` value will be coerced to a string and used as the label.
    name
        By default, the signal name is used to label input elements. This ``name`` property
        can be used instead to specify a custom label for the bound signal.
    """

    input: Literal["radio", "select"]
    options: Sequence[Any]
    debounce: float
    element: str
    labels: Sequence[str]
    name: str


class BindRangeKwds(TypedDict, total=False):
    """
    :class:`altair.BindRange` ``TypedDict`` wrapper.

    Parameters
    ----------
    input

    debounce
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    element
        An optional CSS selector string indicating the parent element to which the input
        element should be added. By default, all input elements are added within the parent
        container of the Vega view.
    max
        Sets the maximum slider value. Defaults to the larger of the signal value and
        ``100``.
    min
        Sets the minimum slider value. Defaults to the smaller of the signal value and
        ``0``.
    name
        By default, the signal name is used to label input elements. This ``name`` property
        can be used instead to specify a custom label for the bound signal.
    step
        Sets the minimum slider increment. If undefined, the step size will be automatically
        determined based on the ``min`` and ``max`` values.
    """

    input: Literal["range"]
    debounce: float
    element: str
    max: float
    min: float
    name: str
    step: float


class BoxPlotConfigKwds(TypedDict, total=False):
    """
    :class:`altair.BoxPlotConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    box

    extent
        The extent of the whiskers. Available options include:

        * ``"min-max"``: min and max are the lower and upper whiskers respectively.
        * A number representing multiple of the interquartile range. This number will be
          multiplied by the IQR to determine whisker boundary, which spans from the smallest
          data to the largest data within the range *[Q1 - k * IQR, Q3 + k * IQR]* where
          *Q1* and *Q3* are the first and third quartiles while *IQR* is the interquartile
          range (*Q3-Q1*).

        **Default value:** ``1.5``.
    median

    outliers

    rule

    size
        Size of the box and median tick of a box plot
    ticks

    """

    box: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    extent: float | Literal["min-max"]
    median: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    outliers: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    rule: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    size: float
    ticks: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )


class BrushConfigKwds(TypedDict, total=False):
    """
    :class:`altair.BrushConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    cursor
        The mouse cursor used over the interval mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    fill
        The fill color of the interval mark.

        **Default value:** ``"#333333"``
    fillOpacity
        The fill opacity of the interval mark (a value between ``0`` and ``1``).

        **Default value:** ``0.125``
    stroke
        The stroke color of the interval mark.

        **Default value:** ``"#ffffff"``
    strokeDash
        An array of alternating stroke and space lengths, for creating dashed or dotted
        lines.
    strokeDashOffset
        The offset (in pixels) with which to begin drawing the stroke dash array.
    strokeOpacity
        The stroke opacity of the interval mark (a value between ``0`` and ``1``).
    strokeWidth
        The stroke width of the interval mark.
    """

    cursor: Cursor_T
    fill: ColorHex | ColorName_T
    fillOpacity: float
    stroke: ColorHex | ColorName_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeOpacity: float
    strokeWidth: float


class CompositionConfigKwds(TypedDict, total=False):
    """
    :class:`altair.CompositionConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    columns
        The number of columns to include in the view composition layout.

        **Default value**: ``undefined`` -- An infinite number of columns (a single row)
        will be assumed. This is equivalent to ``hconcat`` (for ``concat``) and to using the
        ``column`` channel (for ``facet`` and ``repeat``).

        **Note**:

        1) This property is only for:

        * the general (wrappable) ``concat`` operator (not ``hconcat``/``vconcat``)
        * the ``facet`` and ``repeat`` operator with one field/repetition definition
          (without row/column nesting)

        2) Setting the ``columns`` to ``1`` is equivalent to ``vconcat`` (for ``concat``)
        and to using the ``row`` channel (for ``facet`` and ``repeat``).
    spacing
        The default spacing in pixels between composed sub-views.

        **Default value**: ``20``
    """

    columns: float
    spacing: float


class ConfigKwds(TypedDict, total=False):
    """
    :class:`altair.Config` ``TypedDict`` wrapper.

    Parameters
    ----------
    arc
        Arc-specific Config
    area
        Area-Specific Config
    aria
        A boolean flag indicating if ARIA default attributes should be included for marks
        and guides (SVG output only). If false, the ``"aria-hidden"`` attribute will be set
        for all guides, removing them from the ARIA accessibility tree and Vega-Lite will
        not generate default descriptions for marks.

        **Default value:** ``true``.
    autosize
        How the visualization size should be determined. If a string, should be one of
        ``"pad"``, ``"fit"`` or ``"none"``. Object values can additionally specify
        parameters for content sizing and automatic resizing.

        **Default value**: ``pad``
    axis
        Axis configuration, which determines default properties for all ``x`` and ``y``
        `axes <https://vega.github.io/vega-lite/docs/axis.html>`__. For a full list of axis
        configuration options, please see the `corresponding section of the axis
        documentation <https://vega.github.io/vega-lite/docs/axis.html#config>`__.
    axisBand
        Config for axes with "band" scales.
    axisBottom
        Config for x-axis along the bottom edge of the chart.
    axisDiscrete
        Config for axes with "point" or "band" scales.
    axisLeft
        Config for y-axis along the left edge of the chart.
    axisPoint
        Config for axes with "point" scales.
    axisQuantitative
        Config for quantitative axes.
    axisRight
        Config for y-axis along the right edge of the chart.
    axisTemporal
        Config for temporal axes.
    axisTop
        Config for x-axis along the top edge of the chart.
    axisX
        X-axis specific config.
    axisXBand
        Config for x-axes with "band" scales.
    axisXDiscrete
        Config for x-axes with "point" or "band" scales.
    axisXPoint
        Config for x-axes with "point" scales.
    axisXQuantitative
        Config for x-quantitative axes.
    axisXTemporal
        Config for x-temporal axes.
    axisY
        Y-axis specific config.
    axisYBand
        Config for y-axes with "band" scales.
    axisYDiscrete
        Config for y-axes with "point" or "band" scales.
    axisYPoint
        Config for y-axes with "point" scales.
    axisYQuantitative
        Config for y-quantitative axes.
    axisYTemporal
        Config for y-temporal axes.
    background
        CSS color property to use as the background of the entire view.

        **Default value:** ``"white"``
    bar
        Bar-Specific Config
    boxplot
        Box Config
    circle
        Circle-Specific Config
    concat
        Default configuration for all concatenation and repeat view composition operators
        (``concat``, ``hconcat``, ``vconcat``, and ``repeat``)
    countTitle
        Default axis and legend title for count fields.

        **Default value:** ``'Count of Records``.
    customFormatTypes
        Allow the ``formatType`` property for text marks and guides to accept a custom
        formatter function `registered as a Vega expression
        <https://vega.github.io/vega-lite/usage/compile.html#format-type>`__.
    errorband
        ErrorBand Config
    errorbar
        ErrorBar Config
    facet
        Default configuration for the ``facet`` view composition operator
    fieldTitle
        Defines how Vega-Lite generates title for fields. There are three possible styles:

        * ``"verbal"`` (Default) - displays function in a verbal style (e.g., "Sum of
          field", "Year-month of date", "field (binned)").
        * ``"function"`` - displays function using parentheses and capitalized texts (e.g.,
          "SUM(field)", "YEARMONTH(date)", "BIN(field)").
        * ``"plain"`` - displays only the field name without functions (e.g., "field",
          "date", "field").
    font
        Default font for all text marks, titles, and labels.
    geoshape
        Geoshape-Specific Config
    header
        Header configuration, which determines default properties for all `headers
        <https://vega.github.io/vega-lite/docs/header.html>`__.

        For a full list of header configuration options, please see the `corresponding
        section of in the header documentation
        <https://vega.github.io/vega-lite/docs/header.html#config>`__.
    headerColumn
        Header configuration, which determines default properties for column `headers
        <https://vega.github.io/vega-lite/docs/header.html>`__.

        For a full list of header configuration options, please see the `corresponding
        section of in the header documentation
        <https://vega.github.io/vega-lite/docs/header.html#config>`__.
    headerFacet
        Header configuration, which determines default properties for non-row/column facet
        `headers <https://vega.github.io/vega-lite/docs/header.html>`__.

        For a full list of header configuration options, please see the `corresponding
        section of in the header documentation
        <https://vega.github.io/vega-lite/docs/header.html#config>`__.
    headerRow
        Header configuration, which determines default properties for row `headers
        <https://vega.github.io/vega-lite/docs/header.html>`__.

        For a full list of header configuration options, please see the `corresponding
        section of in the header documentation
        <https://vega.github.io/vega-lite/docs/header.html#config>`__.
    image
        Image-specific Config
    legend
        Legend configuration, which determines default properties for all `legends
        <https://vega.github.io/vega-lite/docs/legend.html>`__. For a full list of legend
        configuration options, please see the `corresponding section of in the legend
        documentation <https://vega.github.io/vega-lite/docs/legend.html#config>`__.
    line
        Line-Specific Config
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property provides a global default for text marks, which is
        overridden by mark or style config settings, and by the lineBreak mark encoding
        channel. If signal-valued, either string or regular expression (regexp) values are
        valid.
    locale
        Locale definitions for string parsing and formatting of number and date values. The
        locale object should contain ``number`` and/or ``time`` properties with `locale
        definitions <https://vega.github.io/vega/docs/api/locale/>`__. Locale definitions
        provided in the config block may be overridden by the View constructor locale
        option.
    mark
        Mark Config
    normalizedNumberFormat
        If normalizedNumberFormatType is not specified, D3 number format for axis labels,
        text marks, and tooltips of normalized stacked fields (fields with ``stack:
        "normalize"``). For example ``"s"`` for SI units. Use `D3's number format pattern
        <https://github.com/d3/d3-format#locale_format>`__.

        If ``config.normalizedNumberFormatType`` is specified and
        ``config.customFormatTypes`` is ``true``, this value will be passed as ``format``
        alongside ``datum.value`` to the ``config.numberFormatType`` function. **Default
        value:** ``%``
    normalizedNumberFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.normalizedNumberFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-format, which is
        exposed as `format in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#format>`__. **Note:** You must also
        set ``customFormatTypes`` to ``true`` to use this feature.
    numberFormat
        If numberFormatType is not specified, D3 number format for guide labels, text marks,
        and tooltips of non-normalized fields (fields *without* ``stack: "normalize"``). For
        example ``"s"`` for SI units. Use `D3's number format pattern
        <https://github.com/d3/d3-format#locale_format>`__.

        If ``config.numberFormatType`` is specified and ``config.customFormatTypes`` is
        ``true``, this value will be passed as ``format`` alongside ``datum.value`` to the
        ``config.numberFormatType`` function.
    numberFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.numberFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-format, which is
        exposed as `format in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#format>`__. **Note:** You must also
        set ``customFormatTypes`` to ``true`` to use this feature.
    padding
        The default visualization padding, in pixels, from the edge of the visualization
        canvas to the data rectangle. If a number, specifies padding for all sides. If an
        object, the value should have the format ``{"left": 5, "top": 5, "right": 5,
        "bottom": 5}`` to specify padding for each side of the visualization.

        **Default value**: ``5``
    params
        Dynamic variables or selections that parameterize a visualization.
    point
        Point-Specific Config
    projection
        Projection configuration, which determines default properties for all `projections
        <https://vega.github.io/vega-lite/docs/projection.html>`__. For a full list of
        projection configuration options, please see the `corresponding section of the
        projection documentation
        <https://vega.github.io/vega-lite/docs/projection.html#config>`__.
    range
        An object hash that defines default range arrays or schemes for using with scales.
        For a full list of scale range configuration options, please see the `corresponding
        section of the scale documentation
        <https://vega.github.io/vega-lite/docs/scale.html#config>`__.
    rect
        Rect-Specific Config
    rule
        Rule-Specific Config
    scale
        Scale configuration determines default properties for all `scales
        <https://vega.github.io/vega-lite/docs/scale.html>`__. For a full list of scale
        configuration options, please see the `corresponding section of the scale
        documentation <https://vega.github.io/vega-lite/docs/scale.html#config>`__.
    selection
        An object hash for defining default properties for each type of selections.
    square
        Square-Specific Config
    style
        An object hash that defines key-value mappings to determine default properties for
        marks with a given `style
        <https://vega.github.io/vega-lite/docs/mark.html#mark-def>`__. The keys represent
        styles names; the values have to be valid `mark configuration objects
        <https://vega.github.io/vega-lite/docs/mark.html#config>`__.
    text
        Text-Specific Config
    tick
        Tick-Specific Config
    timeFormat
        Default time format for raw time values (without time units) in text marks, legend
        labels and header labels.

        **Default value:** ``"%b %d, %Y"`` **Note:** Axes automatically determine the format
        for each label automatically so this config does not affect axes.
    timeFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.timeFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-time-format,
        which is exposed as `timeFormat in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#timeFormat>`__. **Note:** You must
        also set ``customFormatTypes`` to ``true`` and there must *not* be a ``timeUnit``
        defined to use this feature.
    title
        Title configuration, which determines default properties for all `titles
        <https://vega.github.io/vega-lite/docs/title.html>`__. For a full list of title
        configuration options, please see the `corresponding section of the title
        documentation <https://vega.github.io/vega-lite/docs/title.html#config>`__.
    tooltipFormat
        Define `custom format configuration
        <https://vega.github.io/vega-lite/docs/config.html#format>`__ for tooltips. If
        unspecified, default format config will be applied.
    trail
        Trail-Specific Config
    view
        Default properties for `single view plots
        <https://vega.github.io/vega-lite/docs/spec.html#single>`__.
    """

    arc: RectConfigKwds
    area: AreaConfigKwds
    aria: bool
    autosize: AutoSizeParamsKwds | AutosizeType_T
    axis: AxisConfigKwds
    axisBand: AxisConfigKwds
    axisBottom: AxisConfigKwds
    axisDiscrete: AxisConfigKwds
    axisLeft: AxisConfigKwds
    axisPoint: AxisConfigKwds
    axisQuantitative: AxisConfigKwds
    axisRight: AxisConfigKwds
    axisTemporal: AxisConfigKwds
    axisTop: AxisConfigKwds
    axisX: AxisConfigKwds
    axisXBand: AxisConfigKwds
    axisXDiscrete: AxisConfigKwds
    axisXPoint: AxisConfigKwds
    axisXQuantitative: AxisConfigKwds
    axisXTemporal: AxisConfigKwds
    axisY: AxisConfigKwds
    axisYBand: AxisConfigKwds
    axisYDiscrete: AxisConfigKwds
    axisYPoint: AxisConfigKwds
    axisYQuantitative: AxisConfigKwds
    axisYTemporal: AxisConfigKwds
    background: ColorHex | ColorName_T
    bar: BarConfigKwds
    boxplot: BoxPlotConfigKwds
    circle: MarkConfigKwds
    concat: CompositionConfigKwds
    countTitle: str
    customFormatTypes: bool
    errorband: ErrorBandConfigKwds
    errorbar: ErrorBarConfigKwds
    facet: CompositionConfigKwds
    fieldTitle: Literal["verbal", "functional", "plain"]
    font: str
    geoshape: MarkConfigKwds
    header: HeaderConfigKwds
    headerColumn: HeaderConfigKwds
    headerFacet: HeaderConfigKwds
    headerRow: HeaderConfigKwds
    image: RectConfigKwds
    legend: LegendConfigKwds
    line: LineConfigKwds
    lineBreak: str
    locale: LocaleKwds
    mark: MarkConfigKwds
    normalizedNumberFormat: str
    normalizedNumberFormatType: str
    numberFormat: str
    numberFormatType: str
    padding: float | PaddingKwds
    params: Sequence[VariableParameterKwds | TopLevelSelectionParameterKwds]
    point: MarkConfigKwds
    projection: ProjectionConfigKwds
    range: RangeConfigKwds
    rect: RectConfigKwds
    rule: MarkConfigKwds
    scale: ScaleConfigKwds
    selection: SelectionConfigKwds
    square: MarkConfigKwds
    style: StyleConfigIndexKwds
    text: MarkConfigKwds
    tick: TickConfigKwds
    timeFormat: str
    timeFormatType: str
    title: TitleConfigKwds
    tooltipFormat: FormatConfigKwds
    trail: LineConfigKwds
    view: ViewConfigKwds


class DateTimeKwds(TypedDict, total=False):
    """
    :class:`altair.DateTime` ``TypedDict`` wrapper.

    Parameters
    ----------
    date
        Integer value representing the date (day of the month) from 1-31.
    day
        Value representing the day of a week. This can be one of: (1) integer value -- ``1``
        represents Monday; (2) case-insensitive day name (e.g., ``"Monday"``); (3)
        case-insensitive, 3-character short day name (e.g., ``"Mon"``).

        **Warning:** A DateTime definition object with ``day``** should not be combined with
        ``year``, ``quarter``, ``month``, or ``date``.
    hours
        Integer value representing the hour of a day from 0-23.
    milliseconds
        Integer value representing the millisecond segment of time.
    minutes
        Integer value representing the minute segment of time from 0-59.
    month
        One of: (1) integer value representing the month from ``1``-``12``. ``1`` represents
        January; (2) case-insensitive month name (e.g., ``"January"``); (3)
        case-insensitive, 3-character short month name (e.g., ``"Jan"``).
    quarter
        Integer value representing the quarter of the year (from 1-4).
    seconds
        Integer value representing the second segment (0-59) of a time value
    utc
        A boolean flag indicating if date time is in utc time. If false, the date time is in
        local time
    year
        Integer value representing the year.
    """

    date: float
    day: str | float
    hours: float
    milliseconds: float
    minutes: float
    month: str | float
    quarter: float
    seconds: float
    utc: bool
    year: float


class DerivedStreamKwds(TypedDict, total=False):
    """
    :class:`altair.DerivedStream` ``TypedDict`` wrapper.

    Parameters
    ----------
    stream

    between

    consume

    debounce

    filter

    markname

    marktype

    throttle

    """

    stream: MergedStreamKwds | DerivedStreamKwds
    between: Sequence[MergedStreamKwds | DerivedStreamKwds]
    consume: bool
    debounce: float
    filter: str | Sequence[str]
    markname: str
    marktype: MarkType_T
    throttle: float


class ErrorBandConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ErrorBandConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    band

    borders

    extent
        The extent of the band. Available options include:

        * ``"ci"``: Extend the band to the confidence interval of the mean.
        * ``"stderr"``: The size of band are set to the value of standard error, extending
          from the mean.
        * ``"stdev"``: The size of band are set to the value of standard deviation,
          extending from the mean.
        * ``"iqr"``: Extend the band to the q1 and q3.

        **Default value:** ``"stderr"``.
    interpolate
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
    tension
        The tension parameter for the interpolation type of the error band.
    """

    band: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    borders: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    extent: ErrorBarExtent_T
    interpolate: Interpolate_T
    tension: float


class ErrorBarConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ErrorBarConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    extent
        The extent of the rule. Available options include:

        * ``"ci"``: Extend the rule to the confidence interval of the mean.
        * ``"stderr"``: The size of rule are set to the value of standard error, extending
          from the mean.
        * ``"stdev"``: The size of rule are set to the value of standard deviation,
          extending from the mean.
        * ``"iqr"``: Extend the rule to the q1 and q3.

        **Default value:** ``"stderr"``.
    rule

    size
        Size of the ticks of an error bar
    thickness
        Thickness of the ticks and the bar of an error bar
    ticks

    """

    extent: ErrorBarExtent_T
    rule: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )
    size: float
    thickness: float
    ticks: (
        bool
        | BarConfigKwds
        | AreaConfigKwds
        | LineConfigKwds
        | MarkConfigKwds
        | RectConfigKwds
        | TickConfigKwds
    )


class FeatureGeometryGeoJsonPropertiesKwds(TypedDict, total=False):
    """
    :class:`altair.FeatureGeometryGeoJsonProperties` ``TypedDict`` wrapper.

    Parameters
    ----------
    geometry
        The feature's geometry
    properties
        Properties associated with this feature.
    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    id
        A value that uniquely identifies this feature in a
        https://tools.ietf.org/html/rfc7946#section-3.2.
    """

    geometry: (
        PointKwds
        | PolygonKwds
        | LineStringKwds
        | MultiPointKwds
        | MultiPolygonKwds
        | MultiLineStringKwds
        | GeometryCollectionKwds
    )
    properties: None
    type: Literal["Feature"]
    bbox: Sequence[float]
    id: str | float


class FormatConfigKwds(TypedDict, total=False):
    """
    :class:`altair.FormatConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    normalizedNumberFormat
        If normalizedNumberFormatType is not specified, D3 number format for axis labels,
        text marks, and tooltips of normalized stacked fields (fields with ``stack:
        "normalize"``). For example ``"s"`` for SI units. Use `D3's number format pattern
        <https://github.com/d3/d3-format#locale_format>`__.

        If ``config.normalizedNumberFormatType`` is specified and
        ``config.customFormatTypes`` is ``true``, this value will be passed as ``format``
        alongside ``datum.value`` to the ``config.numberFormatType`` function. **Default
        value:** ``%``
    normalizedNumberFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.normalizedNumberFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-format, which is
        exposed as `format in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#format>`__. **Note:** You must also
        set ``customFormatTypes`` to ``true`` to use this feature.
    numberFormat
        If numberFormatType is not specified, D3 number format for guide labels, text marks,
        and tooltips of non-normalized fields (fields *without* ``stack: "normalize"``). For
        example ``"s"`` for SI units. Use `D3's number format pattern
        <https://github.com/d3/d3-format#locale_format>`__.

        If ``config.numberFormatType`` is specified and ``config.customFormatTypes`` is
        ``true``, this value will be passed as ``format`` alongside ``datum.value`` to the
        ``config.numberFormatType`` function.
    numberFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.numberFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-format, which is
        exposed as `format in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#format>`__. **Note:** You must also
        set ``customFormatTypes`` to ``true`` to use this feature.
    timeFormat
        Default time format for raw time values (without time units) in text marks, legend
        labels and header labels.

        **Default value:** ``"%b %d, %Y"`` **Note:** Axes automatically determine the format
        for each label automatically so this config does not affect axes.
    timeFormatType
        `Custom format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__ for
        ``config.timeFormat``.

        **Default value:** ``undefined`` -- This is equilvalent to call D3-time-format,
        which is exposed as `timeFormat in Vega-Expression
        <https://vega.github.io/vega/docs/expressions/#timeFormat>`__. **Note:** You must
        also set ``customFormatTypes`` to ``true`` and there must *not* be a ``timeUnit``
        defined to use this feature.
    """

    normalizedNumberFormat: str
    normalizedNumberFormatType: str
    numberFormat: str
    numberFormatType: str
    timeFormat: str
    timeFormatType: str


class GeoJsonFeatureKwds(TypedDict, total=False):
    """
    :class:`altair.GeoJsonFeature` ``TypedDict`` wrapper.

    Parameters
    ----------
    geometry
        The feature's geometry
    properties
        Properties associated with this feature.
    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    id
        A value that uniquely identifies this feature in a
        https://tools.ietf.org/html/rfc7946#section-3.2.
    """

    geometry: (
        PointKwds
        | PolygonKwds
        | LineStringKwds
        | MultiPointKwds
        | MultiPolygonKwds
        | MultiLineStringKwds
        | GeometryCollectionKwds
    )
    properties: None
    type: Literal["Feature"]
    bbox: Sequence[float]
    id: str | float


class GeoJsonFeatureCollectionKwds(TypedDict, total=False):
    """
    :class:`altair.GeoJsonFeatureCollection` ``TypedDict`` wrapper.

    Parameters
    ----------
    features

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    features: Sequence[FeatureGeometryGeoJsonPropertiesKwds]
    type: Literal["FeatureCollection"]
    bbox: Sequence[float]


class GeometryCollectionKwds(TypedDict, total=False):
    """
    :class:`altair.GeometryCollection` ``TypedDict`` wrapper.

    Parameters
    ----------
    geometries

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    geometries: Sequence[
        PointKwds
        | PolygonKwds
        | LineStringKwds
        | MultiPointKwds
        | MultiPolygonKwds
        | MultiLineStringKwds
        | GeometryCollectionKwds
    ]
    type: Literal["GeometryCollection"]
    bbox: Sequence[float]


class GradientStopKwds(TypedDict, total=False):
    """
    :class:`altair.GradientStop` ``TypedDict`` wrapper.

    Parameters
    ----------
    color
        The color value at this point in the gradient.
    offset
        The offset fraction for the color stop, indicating its position within the gradient.
    """

    color: ColorHex | ColorName_T
    offset: float


class HeaderConfigKwds(TypedDict, total=False):
    """
    :class:`altair.HeaderConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    format
        When used with the default ``"number"`` and ``"time"`` format type, the text
        formatting pattern for labels of guides (axes, legends, headers) and text marks.

        * If the format type is ``"number"`` (e.g., for quantitative fields), this is D3's
          `number format pattern <https://github.com/d3/d3-format#locale_format>`__.
        * If the format type is ``"time"`` (e.g., for temporal fields), this is D3's `time
          format pattern <https://github.com/d3/d3-time-format#locale_format>`__.

        See the `format documentation <https://vega.github.io/vega-lite/docs/format.html>`__
        for more examples.

        When used with a `custom formatType
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__, this
        value will be passed as ``format`` alongside ``datum.value`` to the registered
        function.

        **Default value:**  Derived from `numberFormat
        <https://vega.github.io/vega-lite/docs/config.html#format>`__ config for number
        format and from `timeFormat
        <https://vega.github.io/vega-lite/docs/config.html#format>`__ config for time
        format.
    formatType
        The format type for labels. One of ``"number"``, ``"time"``, or a `registered custom
        format type
        <https://vega.github.io/vega-lite/docs/config.html#custom-format-type>`__.

        **Default value:**

        * ``"time"`` for temporal fields and ordinal and nominal fields with ``timeUnit``.
        * ``"number"`` for quantitative fields as well as ordinal and nominal fields without
          ``timeUnit``.
    labelAlign
        Horizontal text alignment of header labels. One of ``"left"``, ``"center"``, or
        ``"right"``.
    labelAnchor
        The anchor position for placing the labels. One of ``"start"``, ``"middle"``, or
        ``"end"``. For example, with a label orientation of top these anchor positions map
        to a left-, center-, or right-aligned label.
    labelAngle
        The rotation angle of the header labels.

        **Default value:** ``0`` for column header, ``-90`` for row header.
    labelBaseline
        The vertical text baseline for the header labels. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or ``"line-bottom"``. The
        ``"line-top"`` and ``"line-bottom"`` values operate similarly to ``"top"`` and
        ``"bottom"``, but are calculated relative to the ``titleLineHeight`` rather than
        ``titleFontSize`` alone.
    labelColor
        The color of the header label, can be in hex color code or regular color name.
    labelExpr
        `Vega expression <https://vega.github.io/vega/docs/expressions/>`__ for customizing
        labels.

        **Note:** The label text and value can be assessed via the ``label`` and ``value``
        properties of the header's backing ``datum`` object.
    labelFont
        The font of the header label.
    labelFontSize
        The font size of the header label, in pixels.
    labelFontStyle
        The font style of the header label.
    labelFontWeight
        The font weight of the header label.
    labelLimit
        The maximum length of the header label in pixels. The text value will be
        automatically truncated if the rendered size exceeds the limit.

        **Default value:** ``0``, indicating no limit
    labelLineHeight
        Line height in pixels for multi-line header labels or title text with ``"line-top"``
        or ``"line-bottom"`` baseline.
    labelOrient
        The orientation of the header label. One of ``"top"``, ``"bottom"``, ``"left"`` or
        ``"right"``.
    labelPadding
        The padding, in pixel, between facet header's label and the plot.

        **Default value:** ``10``
    labels
        A boolean flag indicating if labels should be included as part of the header.

        **Default value:** ``true``.
    orient
        Shortcut for setting both labelOrient and titleOrient.
    title
        Set to null to disable title for the axis, legend, or header.
    titleAlign
        Horizontal text alignment (to the anchor) of header titles.
    titleAnchor
        The anchor position for placing the title. One of ``"start"``, ``"middle"``, or
        ``"end"``. For example, with an orientation of top these anchor positions map to a
        left-, center-, or right-aligned title.
    titleAngle
        The rotation angle of the header title.

        **Default value:** ``0``.
    titleBaseline
        The vertical text baseline for the header title. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or ``"line-bottom"``. The
        ``"line-top"`` and ``"line-bottom"`` values operate similarly to ``"top"`` and
        ``"bottom"``, but are calculated relative to the ``titleLineHeight`` rather than
        ``titleFontSize`` alone.

        **Default value:** ``"middle"``
    titleColor
        Color of the header title, can be in hex color code or regular color name.
    titleFont
        Font of the header title. (e.g., ``"Helvetica Neue"``).
    titleFontSize
        Font size of the header title.
    titleFontStyle
        The font style of the header title.
    titleFontWeight
        Font weight of the header title. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    titleLimit
        The maximum length of the header title in pixels. The text value will be
        automatically truncated if the rendered size exceeds the limit.

        **Default value:** ``0``, indicating no limit
    titleLineHeight
        Line height in pixels for multi-line header title text or title text with
        ``"line-top"`` or ``"line-bottom"`` baseline.
    titleOrient
        The orientation of the header title. One of ``"top"``, ``"bottom"``, ``"left"`` or
        ``"right"``.
    titlePadding
        The padding, in pixel, between facet header's title and the label.

        **Default value:** ``10``
    """

    format: str
    formatType: str
    labelAlign: Align_T
    labelAnchor: TitleAnchor_T
    labelAngle: float
    labelBaseline: TextBaseline_T
    labelColor: ColorHex | ColorName_T
    labelExpr: str
    labelFont: str
    labelFontSize: float
    labelFontStyle: str
    labelFontWeight: FontWeight_T
    labelLimit: float
    labelLineHeight: float
    labelOrient: Orient_T
    labelPadding: float
    labels: bool
    orient: Orient_T
    title: None
    titleAlign: Align_T
    titleAnchor: TitleAnchor_T
    titleAngle: float
    titleBaseline: TextBaseline_T
    titleColor: ColorHex | ColorName_T
    titleFont: str
    titleFontSize: float
    titleFontStyle: str
    titleFontWeight: FontWeight_T
    titleLimit: float
    titleLineHeight: float
    titleOrient: Orient_T
    titlePadding: float


class IntervalSelectionConfigKwds(TypedDict, total=False):
    """
    :class:`altair.IntervalSelectionConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    type
        Determines the default event processing and data query for the selection. Vega-Lite
        currently supports two selection types:

        * ``"point"`` -- to select multiple discrete data values; the first value is
          selected on ``click`` and additional values toggled on shift-click.
        * ``"interval"`` -- to select a continuous range of data values on ``drag``.
    clear
        Clears the selection, emptying it of all values. This property can be a `Event
        Stream <https://vega.github.io/vega/docs/event-streams/>`__ or ``false`` to disable
        clear.

        **Default value:** ``dblclick``.

        **See also:** `clear examples
        <https://vega.github.io/vega-lite/docs/selection.html#clear>`__ in the
        documentation.
    encodings
        An array of encoding channels. The corresponding data field values must match for a
        data tuple to fall within the selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    fields
        An array of field names whose values must match for a data tuple to fall within the
        selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    mark
        An interval selection also adds a rectangle mark to depict the extents of the
        interval. The ``mark`` property can be used to customize the appearance of the mark.

        **See also:** `mark examples
        <https://vega.github.io/vega-lite/docs/selection.html#mark>`__ in the documentation.
    on
        A `Vega event stream <https://vega.github.io/vega/docs/event-streams/>`__ (object or
        selector) that triggers the selection. For interval selections, the event stream
        must specify a `start and end
        <https://vega.github.io/vega/docs/event-streams/#between-filters>`__.

        **See also:** `on examples
        <https://vega.github.io/vega-lite/docs/selection.html#on>`__ in the documentation.
    resolve
        With layered and multi-view displays, a strategy that determines how selections'
        data queries are resolved when applied in a filter transform, conditional encoding
        rule, or scale domain.

        One of:

        * ``"global"`` -- only one brush exists for the entire SPLOM. When the user begins
          to drag, any previous brushes are cleared, and a new one is constructed.
        * ``"union"`` -- each cell contains its own brush, and points are highlighted if
          they lie within *any* of these individual brushes.
        * ``"intersect"`` -- each cell contains its own brush, and points are highlighted
          only if they fall within *all* of these individual brushes.

        **Default value:** ``global``.

        **See also:** `resolve examples
        <https://vega.github.io/vega-lite/docs/selection.html#resolve>`__ in the
        documentation.
    translate
        When truthy, allows a user to interactively move an interval selection
        back-and-forth. Can be ``true``, ``false`` (to disable panning), or a `Vega event
        stream definition <https://vega.github.io/vega/docs/event-streams/>`__ which must
        include a start and end event to trigger continuous panning. Discrete panning (e.g.,
        pressing the left/right arrow keys) will be supported in future versions.

        **Default value:** ``true``, which corresponds to ``[pointerdown, window:pointerup]
        > window:pointermove!``. This default allows users to clicks and drags within an
        interval selection to reposition it.

        **See also:** `translate examples
        <https://vega.github.io/vega-lite/docs/selection.html#translate>`__ in the
        documentation.
    zoom
        When truthy, allows a user to interactively resize an interval selection. Can be
        ``true``, ``false`` (to disable zooming), or a `Vega event stream definition
        <https://vega.github.io/vega/docs/event-streams/>`__. Currently, only ``wheel``
        events are supported, but custom event streams can still be used to specify filters,
        debouncing, and throttling. Future versions will expand the set of events that can
        trigger this transformation.

        **Default value:** ``true``, which corresponds to ``wheel!``. This default allows
        users to use the mouse wheel to resize an interval selection.

        **See also:** `zoom examples
        <https://vega.github.io/vega-lite/docs/selection.html#zoom>`__ in the documentation.
    """

    type: Literal["interval"]
    clear: str | bool | MergedStreamKwds | DerivedStreamKwds
    encodings: Sequence[SingleDefUnitChannel_T]
    fields: Sequence[str]
    mark: BrushConfigKwds
    on: str | MergedStreamKwds | DerivedStreamKwds
    resolve: SelectionResolution_T
    translate: str | bool
    zoom: str | bool


class IntervalSelectionConfigWithoutTypeKwds(TypedDict, total=False):
    """
    :class:`altair.IntervalSelectionConfigWithoutType` ``TypedDict`` wrapper.

    Parameters
    ----------
    clear
        Clears the selection, emptying it of all values. This property can be a `Event
        Stream <https://vega.github.io/vega/docs/event-streams/>`__ or ``false`` to disable
        clear.

        **Default value:** ``dblclick``.

        **See also:** `clear examples
        <https://vega.github.io/vega-lite/docs/selection.html#clear>`__ in the
        documentation.
    encodings
        An array of encoding channels. The corresponding data field values must match for a
        data tuple to fall within the selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    fields
        An array of field names whose values must match for a data tuple to fall within the
        selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    mark
        An interval selection also adds a rectangle mark to depict the extents of the
        interval. The ``mark`` property can be used to customize the appearance of the mark.

        **See also:** `mark examples
        <https://vega.github.io/vega-lite/docs/selection.html#mark>`__ in the documentation.
    on
        A `Vega event stream <https://vega.github.io/vega/docs/event-streams/>`__ (object or
        selector) that triggers the selection. For interval selections, the event stream
        must specify a `start and end
        <https://vega.github.io/vega/docs/event-streams/#between-filters>`__.

        **See also:** `on examples
        <https://vega.github.io/vega-lite/docs/selection.html#on>`__ in the documentation.
    resolve
        With layered and multi-view displays, a strategy that determines how selections'
        data queries are resolved when applied in a filter transform, conditional encoding
        rule, or scale domain.

        One of:

        * ``"global"`` -- only one brush exists for the entire SPLOM. When the user begins
          to drag, any previous brushes are cleared, and a new one is constructed.
        * ``"union"`` -- each cell contains its own brush, and points are highlighted if
          they lie within *any* of these individual brushes.
        * ``"intersect"`` -- each cell contains its own brush, and points are highlighted
          only if they fall within *all* of these individual brushes.

        **Default value:** ``global``.

        **See also:** `resolve examples
        <https://vega.github.io/vega-lite/docs/selection.html#resolve>`__ in the
        documentation.
    translate
        When truthy, allows a user to interactively move an interval selection
        back-and-forth. Can be ``true``, ``false`` (to disable panning), or a `Vega event
        stream definition <https://vega.github.io/vega/docs/event-streams/>`__ which must
        include a start and end event to trigger continuous panning. Discrete panning (e.g.,
        pressing the left/right arrow keys) will be supported in future versions.

        **Default value:** ``true``, which corresponds to ``[pointerdown, window:pointerup]
        > window:pointermove!``. This default allows users to clicks and drags within an
        interval selection to reposition it.

        **See also:** `translate examples
        <https://vega.github.io/vega-lite/docs/selection.html#translate>`__ in the
        documentation.
    zoom
        When truthy, allows a user to interactively resize an interval selection. Can be
        ``true``, ``false`` (to disable zooming), or a `Vega event stream definition
        <https://vega.github.io/vega/docs/event-streams/>`__. Currently, only ``wheel``
        events are supported, but custom event streams can still be used to specify filters,
        debouncing, and throttling. Future versions will expand the set of events that can
        trigger this transformation.

        **Default value:** ``true``, which corresponds to ``wheel!``. This default allows
        users to use the mouse wheel to resize an interval selection.

        **See also:** `zoom examples
        <https://vega.github.io/vega-lite/docs/selection.html#zoom>`__ in the documentation.
    """

    clear: str | bool | MergedStreamKwds | DerivedStreamKwds
    encodings: Sequence[SingleDefUnitChannel_T]
    fields: Sequence[str]
    mark: BrushConfigKwds
    on: str | MergedStreamKwds | DerivedStreamKwds
    resolve: SelectionResolution_T
    translate: str | bool
    zoom: str | bool


class LegendConfigKwds(TypedDict, total=False):
    """
    :class:`altair.LegendConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG group, removing the legend from the ARIA accessibility tree.

        **Default value:** ``true``
    clipHeight
        The height in pixels to clip symbol legend entries and limit their size.
    columnPadding
        The horizontal padding in pixels between symbol legend entries.

        **Default value:** ``10``.
    columns
        The number of columns in which to arrange symbol legend entries. A value of ``0`` or
        lower indicates a single row with one column per entry.
    cornerRadius
        Corner radius for the full legend.
    description
        A text description of this legend for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If the ``aria`` property is true, for SVG output the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__
        will be set to this description. If the description is unspecified it will be
        automatically generated.
    direction
        The direction of the legend, one of ``"vertical"`` or ``"horizontal"``.

        **Default value:**

        * For top-/bottom-``orient``ed legends, ``"horizontal"``
        * For left-/right-``orient``ed legends, ``"vertical"``
        * For top/bottom-left/right-``orient``ed legends, ``"horizontal"`` for gradient
          legends and ``"vertical"`` for symbol legends.
    disable
        Disable legend by default
    fillColor
        Background fill color for the full legend.
    gradientDirection
        The default direction (``"horizontal"`` or ``"vertical"``) for gradient legends.

        **Default value:** ``"vertical"``.
    gradientHorizontalMaxLength
        Max legend length for a horizontal gradient when ``config.legend.gradientLength`` is
        undefined.

        **Default value:** ``200``
    gradientHorizontalMinLength
        Min legend length for a horizontal gradient when ``config.legend.gradientLength`` is
        undefined.

        **Default value:** ``100``
    gradientLabelLimit
        The maximum allowed length in pixels of color ramp gradient labels.
    gradientLabelOffset
        Vertical offset in pixels for color ramp gradient labels.

        **Default value:** ``2``.
    gradientLength
        The length in pixels of the primary axis of a color gradient. This value corresponds
        to the height of a vertical gradient or the width of a horizontal gradient.

        **Default value:** ``200``.
    gradientOpacity
        Opacity of the color gradient.
    gradientStrokeColor
        The color of the gradient stroke, can be in hex color code or regular color name.

        **Default value:** ``"lightGray"``.
    gradientStrokeWidth
        The width of the gradient stroke, in pixels.

        **Default value:** ``0``.
    gradientThickness
        The thickness in pixels of the color gradient. This value corresponds to the width
        of a vertical gradient or the height of a horizontal gradient.

        **Default value:** ``16``.
    gradientVerticalMaxLength
        Max legend length for a vertical gradient when ``config.legend.gradientLength`` is
        undefined.

        **Default value:** ``200``
    gradientVerticalMinLength
        Min legend length for a vertical gradient when ``config.legend.gradientLength`` is
        undefined.

        **Default value:** ``100``
    gridAlign
        The alignment to apply to symbol legends rows and columns. The supported string
        values are ``"all"``, ``"each"`` (the default), and ``none``. For more information,
        see the `grid layout documentation <https://vega.github.io/vega/docs/layout>`__.

        **Default value:** ``"each"``.
    labelAlign
        The alignment of the legend label, can be left, center, or right.
    labelBaseline
        The position of the baseline of legend label, can be ``"top"``, ``"middle"``,
        ``"bottom"``, or ``"alphabetic"``.

        **Default value:** ``"middle"``.
    labelColor
        The color of the legend label, can be in hex color code or regular color name.
    labelFont
        The font of the legend label.
    labelFontSize
        The font size of legend label.

        **Default value:** ``10``.
    labelFontStyle
        The font style of legend label.
    labelFontWeight
        The font weight of legend label.
    labelLimit
        Maximum allowed pixel width of legend tick labels.

        **Default value:** ``160``.
    labelOffset
        The offset of the legend label.

        **Default value:** ``4``.
    labelOpacity
        Opacity of labels.
    labelOverlap
        The strategy to use for resolving overlap of labels in gradient legends. If
        ``false``, no overlap reduction is attempted. If set to ``true`` or ``"parity"``, a
        strategy of removing every other label is used. If set to ``"greedy"``, a linear
        scan of the labels is performed, removing any label that overlaps with the last
        visible label (this often works better for log-scaled axes).

        **Default value:** ``"greedy"`` for ``log scales otherwise ``true`.
    labelPadding
        Padding in pixels between the legend and legend labels.
    labelSeparation
        The minimum separation that must be between label bounding boxes for them to be
        considered non-overlapping (default ``0``). This property is ignored if
        *labelOverlap* resolution is not enabled.
    layout

    legendX
        Custom x-position for legend with orient "none".
    legendY
        Custom y-position for legend with orient "none".
    offset
        The offset in pixels by which to displace the legend from the data rectangle and
        axes.

        **Default value:** ``18``.
    orient
        The orientation of the legend, which determines how the legend is positioned within
        the scene. One of ``"left"``, ``"right"``, ``"top"``, ``"bottom"``, ``"top-left"``,
        ``"top-right"``, ``"bottom-left"``, ``"bottom-right"``, ``"none"``.

        **Default value:** ``"right"``
    padding
        The padding between the border and content of the legend group.

        **Default value:** ``0``.
    rowPadding
        The vertical padding in pixels between symbol legend entries.

        **Default value:** ``2``.
    strokeColor
        Border stroke color for the full legend.
    strokeDash
        Border stroke dash pattern for the full legend.
    strokeWidth
        Border stroke width for the full legend.
    symbolBaseFillColor
        Default fill color for legend symbols. Only applied if there is no ``"fill"`` scale
        color encoding for the legend.

        **Default value:** ``"transparent"``.
    symbolBaseStrokeColor
        Default stroke color for legend symbols. Only applied if there is no ``"fill"``
        scale color encoding for the legend.

        **Default value:** ``"gray"``.
    symbolDash
        An array of alternating [stroke, space] lengths for dashed symbol strokes.
    symbolDashOffset
        The pixel offset at which to start drawing with the symbol stroke dash array.
    symbolDirection
        The default direction (``"horizontal"`` or ``"vertical"``) for symbol legends.

        **Default value:** ``"vertical"``.
    symbolFillColor
        The color of the legend symbol,
    symbolLimit
        The maximum number of allowed entries for a symbol legend. Additional entries will
        be dropped.
    symbolOffset
        Horizontal pixel offset for legend symbols.

        **Default value:** ``0``.
    symbolOpacity
        Opacity of the legend symbols.
    symbolSize
        The size of the legend symbol, in pixels.

        **Default value:** ``100``.
    symbolStrokeColor
        Stroke color for legend symbols.
    symbolStrokeWidth
        The width of the symbol's stroke.

        **Default value:** ``1.5``.
    symbolType
        The symbol shape. One of the plotting shapes ``circle`` (default), ``square``,
        ``cross``, ``diamond``, ``triangle-up``, ``triangle-down``, ``triangle-right``, or
        ``triangle-left``, the line symbol ``stroke``, or one of the centered directional
        shapes ``arrow``, ``wedge``, or ``triangle``. Alternatively, a custom `SVG path
        string <https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths>`__ can be
        provided. For correct sizing, custom shape paths should be defined within a square
        bounding box with coordinates ranging from -1 to 1 along both the x and y
        dimensions.

        **Default value:** ``"circle"``.
    tickCount
        The desired number of tick values for quantitative legends.
    title
        Set to null to disable title for the axis, legend, or header.
    titleAlign
        Horizontal text alignment for legend titles.

        **Default value:** ``"left"``.
    titleAnchor
        Text anchor position for placing legend titles.
    titleBaseline
        Vertical text baseline for legend titles.  One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or ``"line-bottom"``. The
        ``"line-top"`` and ``"line-bottom"`` values operate similarly to ``"top"`` and
        ``"bottom"``, but are calculated relative to the *lineHeight* rather than *fontSize*
        alone.

        **Default value:** ``"top"``.
    titleColor
        The color of the legend title, can be in hex color code or regular color name.
    titleFont
        The font of the legend title.
    titleFontSize
        The font size of the legend title.
    titleFontStyle
        The font style of the legend title.
    titleFontWeight
        The font weight of the legend title. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    titleLimit
        Maximum allowed pixel width of legend titles.

        **Default value:** ``180``.
    titleLineHeight
        Line height in pixels for multi-line title text or title text with ``"line-top"`` or
        ``"line-bottom"`` baseline.
    titleOpacity
        Opacity of the legend title.
    titleOrient
        Orientation of the legend title.
    titlePadding
        The padding, in pixels, between title and legend.

        **Default value:** ``5``.
    unselectedOpacity
        The opacity of unselected legend entries.

        **Default value:** 0.35.
    zindex
        The integer z-index indicating the layering of the legend group relative to other
        axis, mark, and legend groups.
    """

    aria: bool
    clipHeight: float
    columnPadding: float
    columns: float
    cornerRadius: float
    description: str
    direction: Orientation_T
    disable: bool
    fillColor: ColorHex | ColorName_T | None
    gradientDirection: Orientation_T
    gradientHorizontalMaxLength: float
    gradientHorizontalMinLength: float
    gradientLabelLimit: float
    gradientLabelOffset: float
    gradientLength: float
    gradientOpacity: float
    gradientStrokeColor: ColorHex | ColorName_T | None
    gradientStrokeWidth: float
    gradientThickness: float
    gradientVerticalMaxLength: float
    gradientVerticalMinLength: float
    gridAlign: LayoutAlign_T
    labelAlign: Align_T
    labelBaseline: TextBaseline_T
    labelColor: ColorHex | ColorName_T | None
    labelFont: str
    labelFontSize: float
    labelFontStyle: str
    labelFontWeight: FontWeight_T
    labelLimit: float
    labelOffset: float
    labelOpacity: float
    labelOverlap: bool | Literal["greedy", "parity"]
    labelPadding: float
    labelSeparation: float
    layout: Map
    legendX: float
    legendY: float
    offset: float
    orient: LegendOrient_T
    padding: float
    rowPadding: float
    strokeColor: ColorHex | ColorName_T | None
    strokeDash: Sequence[float]
    strokeWidth: float
    symbolBaseFillColor: ColorHex | ColorName_T | None
    symbolBaseStrokeColor: ColorHex | ColorName_T | None
    symbolDash: Sequence[float]
    symbolDashOffset: float
    symbolDirection: Orientation_T
    symbolFillColor: ColorHex | ColorName_T | None
    symbolLimit: float
    symbolOffset: float
    symbolOpacity: float
    symbolSize: float
    symbolStrokeColor: ColorHex | ColorName_T | None
    symbolStrokeWidth: float
    symbolType: str
    tickCount: float | TimeIntervalStepKwds | TimeInterval_T
    title: None
    titleAlign: Align_T
    titleAnchor: TitleAnchor_T
    titleBaseline: TextBaseline_T
    titleColor: ColorHex | ColorName_T | None
    titleFont: str
    titleFontSize: float
    titleFontStyle: str
    titleFontWeight: FontWeight_T
    titleLimit: float
    titleLineHeight: float
    titleOpacity: float
    titleOrient: Orient_T
    titlePadding: float
    unselectedOpacity: float
    zindex: float


class LegendResolveMapKwds(TypedDict, total=False):
    """
    :class:`altair.LegendResolveMap` ``TypedDict`` wrapper.

    Parameters
    ----------
    angle

    color

    fill

    fillOpacity

    opacity

    shape

    size

    stroke

    strokeDash

    strokeOpacity

    strokeWidth

    """

    angle: ResolveMode_T
    color: ResolveMode_T
    fill: ResolveMode_T
    fillOpacity: ResolveMode_T
    opacity: ResolveMode_T
    shape: ResolveMode_T
    size: ResolveMode_T
    stroke: ResolveMode_T
    strokeDash: ResolveMode_T
    strokeOpacity: ResolveMode_T
    strokeWidth: ResolveMode_T


class LegendStreamBindingKwds(TypedDict, total=False):
    """
    :class:`altair.LegendStreamBinding` ``TypedDict`` wrapper.

    Parameters
    ----------
    legend

    """

    legend: str | MergedStreamKwds | DerivedStreamKwds


class LineConfigKwds(TypedDict, total=False):
    """
    :class:`altair.LineConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    point
        A flag for overlaying points on top of line or area marks, or an object defining the
        properties of the overlayed points.

        * If this property is ``"transparent"``, transparent points will be used (for
          enhancing tooltips and selections).

        * If this property is an empty object (``{}``) or ``true``, filled points with
          default properties will be used.

        * If this property is ``false``, no points would be automatically added to line or
          area marks.

        **Default value:** ``false``.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    point: bool | OverlayMarkDefKwds | Literal["transparent"]
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class LineStringKwds(TypedDict, total=False):
    """
    :class:`altair.LineString` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[Sequence[float]]
    type: Literal["LineString"]
    bbox: Sequence[float]


class LinearGradientKwds(TypedDict, total=False):
    """
    :class:`altair.LinearGradient` ``TypedDict`` wrapper.

    Parameters
    ----------
    gradient
        The type of gradient. Use ``"linear"`` for a linear gradient.
    stops
        An array of gradient stops defining the gradient color sequence.
    id

    x1
        The starting x-coordinate, in normalized [0, 1] coordinates, of the linear gradient.

        **Default value:** ``0``
    x2
        The ending x-coordinate, in normalized [0, 1] coordinates, of the linear gradient.

        **Default value:** ``1``
    y1
        The starting y-coordinate, in normalized [0, 1] coordinates, of the linear gradient.

        **Default value:** ``0``
    y2
        The ending y-coordinate, in normalized [0, 1] coordinates, of the linear gradient.

        **Default value:** ``0``
    """

    gradient: Literal["linear"]
    stops: Sequence[GradientStopKwds]
    id: str
    x1: float
    x2: float
    y1: float
    y2: float


class LocaleKwds(TypedDict, total=False):
    """
    :class:`altair.Locale` ``TypedDict`` wrapper.

    Parameters
    ----------
    number
        Locale definition for formatting numbers.
    time
        Locale definition for formatting dates and times.
    """

    number: NumberLocaleKwds
    time: TimeLocaleKwds


class MarkConfigKwds(TypedDict, total=False):
    """
    :class:`altair.MarkConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class MergedStreamKwds(TypedDict, total=False):
    """
    :class:`altair.MergedStream` ``TypedDict`` wrapper.

    Parameters
    ----------
    merge

    between

    consume

    debounce

    filter

    markname

    marktype

    throttle

    """

    merge: Sequence[MergedStreamKwds | DerivedStreamKwds]
    between: Sequence[MergedStreamKwds | DerivedStreamKwds]
    consume: bool
    debounce: float
    filter: str | Sequence[str]
    markname: str
    marktype: MarkType_T
    throttle: float


class MultiLineStringKwds(TypedDict, total=False):
    """
    :class:`altair.MultiLineString` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[Sequence[Sequence[float]]]
    type: Literal["MultiLineString"]
    bbox: Sequence[float]


class MultiPointKwds(TypedDict, total=False):
    """
    :class:`altair.MultiPoint` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[Sequence[float]]
    type: Literal["MultiPoint"]
    bbox: Sequence[float]


class MultiPolygonKwds(TypedDict, total=False):
    """
    :class:`altair.MultiPolygon` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[Sequence[Sequence[Sequence[float]]]]
    type: Literal["MultiPolygon"]
    bbox: Sequence[float]


class NumberLocaleKwds(TypedDict, total=False):
    """
    :class:`altair.NumberLocale` ``TypedDict`` wrapper.

    Parameters
    ----------
    currency
        The currency prefix and suffix (e.g., ["$", ""]).
    decimal
        The decimal point (e.g., ".").
    grouping
        The array of group sizes (e.g., [3]), cycled as needed.
    thousands
        The group separator (e.g., ",").
    minus
        The minus sign (defaults to hyphen-minus, "-").
    nan
        The not-a-number value (defaults to "NaN").
    numerals
        An array of ten strings to replace the numerals 0-9.
    percent
        The percent sign (defaults to "%").
    """

    currency: Sequence[str]
    decimal: str
    grouping: Sequence[float]
    thousands: str
    minus: str
    nan: str
    numerals: Sequence[str]
    percent: str


class OverlayMarkDefKwds(TypedDict, total=False):
    """
    :class:`altair.OverlayMarkDef` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    clip
        Whether a mark be clipped to the enclosing group's width and height.
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    radius2Offset
        Offset for radius2.
    radiusOffset
        Offset for radius.
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    style
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
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    theta2Offset
        Offset for theta2.
    thetaOffset
        Offset for theta.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2Offset
        Offset for x2-position.
    xOffset
        Offset for x-position.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2Offset
        Offset for y2-position.
    yOffset
        Offset for y-position.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    blend: Blend_T
    clip: bool
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    radius: float
    radius2: float
    radius2Offset: float
    radiusOffset: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    style: str | Sequence[str]
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    theta2Offset: float
    thetaOffset: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    x2Offset: float
    xOffset: float
    y: float | Literal["height"]
    y2: float | Literal["height"]
    y2Offset: float
    yOffset: float


class PointKwds(TypedDict, total=False):
    """
    :class:`altair.Point` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates
        A Position is an array of coordinates.
        https://tools.ietf.org/html/rfc7946#section-3.1.1 Array should contain between two
        and three elements. The previous GeoJSON specification allowed more elements (e.g.,
        which could be used to represent M values), but the current specification only
        allows X, Y, and (optionally) Z to be defined.
    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[float]
    type: Literal["Point"]
    bbox: Sequence[float]


class PointSelectionConfigKwds(TypedDict, total=False):
    """
    :class:`altair.PointSelectionConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    type
        Determines the default event processing and data query for the selection. Vega-Lite
        currently supports two selection types:

        * ``"point"`` -- to select multiple discrete data values; the first value is
          selected on ``click`` and additional values toggled on shift-click.
        * ``"interval"`` -- to select a continuous range of data values on ``drag``.
    clear
        Clears the selection, emptying it of all values. This property can be a `Event
        Stream <https://vega.github.io/vega/docs/event-streams/>`__ or ``false`` to disable
        clear.

        **Default value:** ``dblclick``.

        **See also:** `clear examples
        <https://vega.github.io/vega-lite/docs/selection.html#clear>`__ in the
        documentation.
    encodings
        An array of encoding channels. The corresponding data field values must match for a
        data tuple to fall within the selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    fields
        An array of field names whose values must match for a data tuple to fall within the
        selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    nearest
        When true, an invisible voronoi diagram is computed to accelerate discrete
        selection. The data value *nearest* the mouse cursor is added to the selection.

        **Default value:** ``false``, which means that data values must be interacted with
        directly (e.g., clicked on) to be added to the selection.

        **See also:** `nearest examples
        <https://vega.github.io/vega-lite/docs/selection.html#nearest>`__ documentation.
    on
        A `Vega event stream <https://vega.github.io/vega/docs/event-streams/>`__ (object or
        selector) that triggers the selection. For interval selections, the event stream
        must specify a `start and end
        <https://vega.github.io/vega/docs/event-streams/#between-filters>`__.

        **See also:** `on examples
        <https://vega.github.io/vega-lite/docs/selection.html#on>`__ in the documentation.
    resolve
        With layered and multi-view displays, a strategy that determines how selections'
        data queries are resolved when applied in a filter transform, conditional encoding
        rule, or scale domain.

        One of:

        * ``"global"`` -- only one brush exists for the entire SPLOM. When the user begins
          to drag, any previous brushes are cleared, and a new one is constructed.
        * ``"union"`` -- each cell contains its own brush, and points are highlighted if
          they lie within *any* of these individual brushes.
        * ``"intersect"`` -- each cell contains its own brush, and points are highlighted
          only if they fall within *all* of these individual brushes.

        **Default value:** ``global``.

        **See also:** `resolve examples
        <https://vega.github.io/vega-lite/docs/selection.html#resolve>`__ in the
        documentation.
    toggle
        Controls whether data values should be toggled (inserted or removed from a point
        selection) or only ever inserted into point selections.

        One of:

        * ``true`` -- the default behavior, which corresponds to ``"event.shiftKey"``.  As a
          result, data values are toggled when the user interacts with the shift-key
          pressed.
        * ``false`` -- disables toggling behaviour; the selection will only ever contain a
          single data value corresponding to the most recent interaction.
        * A `Vega expression <https://vega.github.io/vega/docs/expressions/>`__ which is
          re-evaluated as the user interacts. If the expression evaluates to ``true``, the
          data value is toggled into or out of the point selection. If the expression
          evaluates to ``false``, the point selection is first cleared, and the data value
          is then inserted. For example, setting the value to the Vega expression ``"true"``
          will toggle data values without the user pressing the shift-key.

        **Default value:** ``true``

        **See also:** `toggle examples
        <https://vega.github.io/vega-lite/docs/selection.html#toggle>`__ in the
        documentation.
    """

    type: Literal["point"]
    clear: str | bool | MergedStreamKwds | DerivedStreamKwds
    encodings: Sequence[SingleDefUnitChannel_T]
    fields: Sequence[str]
    nearest: bool
    on: str | MergedStreamKwds | DerivedStreamKwds
    resolve: SelectionResolution_T
    toggle: str | bool


class PointSelectionConfigWithoutTypeKwds(TypedDict, total=False):
    """
    :class:`altair.PointSelectionConfigWithoutType` ``TypedDict`` wrapper.

    Parameters
    ----------
    clear
        Clears the selection, emptying it of all values. This property can be a `Event
        Stream <https://vega.github.io/vega/docs/event-streams/>`__ or ``false`` to disable
        clear.

        **Default value:** ``dblclick``.

        **See also:** `clear examples
        <https://vega.github.io/vega-lite/docs/selection.html#clear>`__ in the
        documentation.
    encodings
        An array of encoding channels. The corresponding data field values must match for a
        data tuple to fall within the selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    fields
        An array of field names whose values must match for a data tuple to fall within the
        selection.

        **See also:** The `projection with encodings and fields section
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ in the
        documentation.
    nearest
        When true, an invisible voronoi diagram is computed to accelerate discrete
        selection. The data value *nearest* the mouse cursor is added to the selection.

        **Default value:** ``false``, which means that data values must be interacted with
        directly (e.g., clicked on) to be added to the selection.

        **See also:** `nearest examples
        <https://vega.github.io/vega-lite/docs/selection.html#nearest>`__ documentation.
    on
        A `Vega event stream <https://vega.github.io/vega/docs/event-streams/>`__ (object or
        selector) that triggers the selection. For interval selections, the event stream
        must specify a `start and end
        <https://vega.github.io/vega/docs/event-streams/#between-filters>`__.

        **See also:** `on examples
        <https://vega.github.io/vega-lite/docs/selection.html#on>`__ in the documentation.
    resolve
        With layered and multi-view displays, a strategy that determines how selections'
        data queries are resolved when applied in a filter transform, conditional encoding
        rule, or scale domain.

        One of:

        * ``"global"`` -- only one brush exists for the entire SPLOM. When the user begins
          to drag, any previous brushes are cleared, and a new one is constructed.
        * ``"union"`` -- each cell contains its own brush, and points are highlighted if
          they lie within *any* of these individual brushes.
        * ``"intersect"`` -- each cell contains its own brush, and points are highlighted
          only if they fall within *all* of these individual brushes.

        **Default value:** ``global``.

        **See also:** `resolve examples
        <https://vega.github.io/vega-lite/docs/selection.html#resolve>`__ in the
        documentation.
    toggle
        Controls whether data values should be toggled (inserted or removed from a point
        selection) or only ever inserted into point selections.

        One of:

        * ``true`` -- the default behavior, which corresponds to ``"event.shiftKey"``.  As a
          result, data values are toggled when the user interacts with the shift-key
          pressed.
        * ``false`` -- disables toggling behaviour; the selection will only ever contain a
          single data value corresponding to the most recent interaction.
        * A `Vega expression <https://vega.github.io/vega/docs/expressions/>`__ which is
          re-evaluated as the user interacts. If the expression evaluates to ``true``, the
          data value is toggled into or out of the point selection. If the expression
          evaluates to ``false``, the point selection is first cleared, and the data value
          is then inserted. For example, setting the value to the Vega expression ``"true"``
          will toggle data values without the user pressing the shift-key.

        **Default value:** ``true``

        **See also:** `toggle examples
        <https://vega.github.io/vega-lite/docs/selection.html#toggle>`__ in the
        documentation.
    """

    clear: str | bool | MergedStreamKwds | DerivedStreamKwds
    encodings: Sequence[SingleDefUnitChannel_T]
    fields: Sequence[str]
    nearest: bool
    on: str | MergedStreamKwds | DerivedStreamKwds
    resolve: SelectionResolution_T
    toggle: str | bool


class PolygonKwds(TypedDict, total=False):
    """
    :class:`altair.Polygon` ``TypedDict`` wrapper.

    Parameters
    ----------
    coordinates

    type
        Specifies the type of GeoJSON object.
    bbox
        Bounding box of the coordinate range of the object's Geometries, Features, or
        Feature Collections. https://tools.ietf.org/html/rfc7946#section-5
    """

    coordinates: Sequence[Sequence[Sequence[float]]]
    type: Literal["Polygon"]
    bbox: Sequence[float]


class ProjectionKwds(TypedDict, total=False):
    """
    :class:`altair.Projection` ``TypedDict`` wrapper.

    Parameters
    ----------
    center
        The projection's center, a two-element array of longitude and latitude in degrees.

        **Default value:** ``[0, 0]``
    clipAngle
        The projection's clipping circle radius to the specified angle in degrees. If
        ``null``, switches to `antimeridian <http://bl.ocks.org/mbostock/3788999>`__ cutting
        rather than small-circle clipping.
    clipExtent
        The projection's viewport clip extent to the specified bounds in pixels. The extent
        bounds are specified as an array ``[[x0, y0], [x1, y1]]``, where ``x0`` is the
        left-side of the viewport, ``y0`` is the top, ``x1`` is the right and ``y1`` is the
        bottom. If ``null``, no viewport clipping is performed.
    coefficient
        The coefficient parameter for the ``hammer`` projection.

        **Default value:** ``2``
    distance
        For the ``satellite`` projection, the distance from the center of the sphere to the
        point of view, as a proportion of the sphere's radius. The recommended maximum clip
        angle for a given ``distance`` is acos(1 / distance) converted to degrees. If tilt
        is also applied, then more conservative clipping may be necessary.

        **Default value:** ``2.0``
    extent

    fit

    fraction
        The fraction parameter for the ``bottomley`` projection.

        **Default value:** ``0.5``, corresponding to a sin(ψ) where ψ = π/6.
    lobes
        The number of lobes in projections that support multi-lobe views: ``berghaus``,
        ``gingery``, or ``healpix``. The default value varies based on the projection type.
    parallel
        The parallel parameter for projections that support it: ``armadillo``, ``bonne``,
        ``craig``, ``cylindricalEqualArea``, ``cylindricalStereographic``,
        ``hammerRetroazimuthal``, ``loximuthal``, or ``rectangularPolyconic``. The default
        value varies based on the projection type.
    parallels
        For conic projections, the `two standard parallels
        <https://en.wikipedia.org/wiki/Map_projection#Conic>`__ that define the map layout.
        The default depends on the specific conic projection used.
    pointRadius
        The default radius (in pixels) to use when drawing GeoJSON ``Point`` and
        ``MultiPoint`` geometries. This parameter sets a constant default value. To modify
        the point radius in response to data, see the corresponding parameter of the GeoPath
        and GeoShape transforms.

        **Default value:** ``4.5``
    precision
        The threshold for the projection's `adaptive resampling
        <http://bl.ocks.org/mbostock/3795544>`__ to the specified value in pixels. This
        value corresponds to the `Douglas-Peucker distance
        <http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`__.
        If precision is not specified, returns the projection's current resampling precision
        which defaults to ``√0.5 ≅ 0.70710…``.
    radius
        The radius parameter for the ``airy`` or ``gingery`` projection. The default value
        varies based on the projection type.
    ratio
        The ratio parameter for the ``hill``, ``hufnagel``, or ``wagner`` projections. The
        default value varies based on the projection type.
    reflectX
        Sets whether or not the x-dimension is reflected (negated) in the output.
    reflectY
        Sets whether or not the y-dimension is reflected (negated) in the output.
    rotate
        The projection's three-axis rotation to the specified angles, which must be a two-
        or three-element array of numbers [``lambda``, ``phi``, ``gamma``] specifying the
        rotation angles in degrees about each spherical axis. (These correspond to yaw,
        pitch and roll.)

        **Default value:** ``[0, 0, 0]``
    scale
        The projection's scale (zoom) factor, overriding automatic fitting. The default
        scale is projection-specific. The scale factor corresponds linearly to the distance
        between projected points; however, scale factor values are not equivalent across
        projections.
    size
        Used in conjunction with fit, provides the width and height in pixels of the area to
        which the projection should be automatically fit.
    spacing
        The spacing parameter for the ``lagrange`` projection.

        **Default value:** ``0.5``
    tilt
        The tilt angle (in degrees) for the ``satellite`` projection.

        **Default value:** ``0``.
    translate
        The projection's translation offset as a two-element array ``[tx, ty]``.
    type
        The cartographic projection to use. This value is case-insensitive, for example
        ``"albers"`` and ``"Albers"`` indicate the same projection type. You can find all
        valid projection types `in the documentation
        <https://vega.github.io/vega-lite/docs/projection.html#projection-types>`__.

        **Default value:** ``equalEarth``
    """

    center: Sequence[float]
    clipAngle: float
    clipExtent: Sequence[Sequence[float]]
    coefficient: float
    distance: float
    extent: Sequence[Sequence[float]]
    fit: (
        GeoJsonFeatureKwds
        | GeoJsonFeatureCollectionKwds
        | Sequence[GeoJsonFeatureKwds]
        | Sequence[
            GeoJsonFeatureKwds
            | GeoJsonFeatureCollectionKwds
            | Sequence[GeoJsonFeatureKwds]
        ]
    )
    fraction: float
    lobes: float
    parallel: float
    parallels: Sequence[float]
    pointRadius: float
    precision: float
    radius: float
    ratio: float
    reflectX: bool
    reflectY: bool
    rotate: Sequence[float]
    scale: float
    size: Sequence[float]
    spacing: float
    tilt: float
    translate: Sequence[float]
    type: ProjectionType_T


class ProjectionConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ProjectionConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    center
        The projection's center, a two-element array of longitude and latitude in degrees.

        **Default value:** ``[0, 0]``
    clipAngle
        The projection's clipping circle radius to the specified angle in degrees. If
        ``null``, switches to `antimeridian <http://bl.ocks.org/mbostock/3788999>`__ cutting
        rather than small-circle clipping.
    clipExtent
        The projection's viewport clip extent to the specified bounds in pixels. The extent
        bounds are specified as an array ``[[x0, y0], [x1, y1]]``, where ``x0`` is the
        left-side of the viewport, ``y0`` is the top, ``x1`` is the right and ``y1`` is the
        bottom. If ``null``, no viewport clipping is performed.
    coefficient
        The coefficient parameter for the ``hammer`` projection.

        **Default value:** ``2``
    distance
        For the ``satellite`` projection, the distance from the center of the sphere to the
        point of view, as a proportion of the sphere's radius. The recommended maximum clip
        angle for a given ``distance`` is acos(1 / distance) converted to degrees. If tilt
        is also applied, then more conservative clipping may be necessary.

        **Default value:** ``2.0``
    extent

    fit

    fraction
        The fraction parameter for the ``bottomley`` projection.

        **Default value:** ``0.5``, corresponding to a sin(ψ) where ψ = π/6.
    lobes
        The number of lobes in projections that support multi-lobe views: ``berghaus``,
        ``gingery``, or ``healpix``. The default value varies based on the projection type.
    parallel
        The parallel parameter for projections that support it: ``armadillo``, ``bonne``,
        ``craig``, ``cylindricalEqualArea``, ``cylindricalStereographic``,
        ``hammerRetroazimuthal``, ``loximuthal``, or ``rectangularPolyconic``. The default
        value varies based on the projection type.
    parallels
        For conic projections, the `two standard parallels
        <https://en.wikipedia.org/wiki/Map_projection#Conic>`__ that define the map layout.
        The default depends on the specific conic projection used.
    pointRadius
        The default radius (in pixels) to use when drawing GeoJSON ``Point`` and
        ``MultiPoint`` geometries. This parameter sets a constant default value. To modify
        the point radius in response to data, see the corresponding parameter of the GeoPath
        and GeoShape transforms.

        **Default value:** ``4.5``
    precision
        The threshold for the projection's `adaptive resampling
        <http://bl.ocks.org/mbostock/3795544>`__ to the specified value in pixels. This
        value corresponds to the `Douglas-Peucker distance
        <http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm>`__.
        If precision is not specified, returns the projection's current resampling precision
        which defaults to ``√0.5 ≅ 0.70710…``.
    radius
        The radius parameter for the ``airy`` or ``gingery`` projection. The default value
        varies based on the projection type.
    ratio
        The ratio parameter for the ``hill``, ``hufnagel``, or ``wagner`` projections. The
        default value varies based on the projection type.
    reflectX
        Sets whether or not the x-dimension is reflected (negated) in the output.
    reflectY
        Sets whether or not the y-dimension is reflected (negated) in the output.
    rotate
        The projection's three-axis rotation to the specified angles, which must be a two-
        or three-element array of numbers [``lambda``, ``phi``, ``gamma``] specifying the
        rotation angles in degrees about each spherical axis. (These correspond to yaw,
        pitch and roll.)

        **Default value:** ``[0, 0, 0]``
    scale
        The projection's scale (zoom) factor, overriding automatic fitting. The default
        scale is projection-specific. The scale factor corresponds linearly to the distance
        between projected points; however, scale factor values are not equivalent across
        projections.
    size
        Used in conjunction with fit, provides the width and height in pixels of the area to
        which the projection should be automatically fit.
    spacing
        The spacing parameter for the ``lagrange`` projection.

        **Default value:** ``0.5``
    tilt
        The tilt angle (in degrees) for the ``satellite`` projection.

        **Default value:** ``0``.
    translate
        The projection's translation offset as a two-element array ``[tx, ty]``.
    type
        The cartographic projection to use. This value is case-insensitive, for example
        ``"albers"`` and ``"Albers"`` indicate the same projection type. You can find all
        valid projection types `in the documentation
        <https://vega.github.io/vega-lite/docs/projection.html#projection-types>`__.

        **Default value:** ``equalEarth``
    """

    center: Sequence[float]
    clipAngle: float
    clipExtent: Sequence[Sequence[float]]
    coefficient: float
    distance: float
    extent: Sequence[Sequence[float]]
    fit: (
        GeoJsonFeatureKwds
        | GeoJsonFeatureCollectionKwds
        | Sequence[GeoJsonFeatureKwds]
        | Sequence[
            GeoJsonFeatureKwds
            | GeoJsonFeatureCollectionKwds
            | Sequence[GeoJsonFeatureKwds]
        ]
    )
    fraction: float
    lobes: float
    parallel: float
    parallels: Sequence[float]
    pointRadius: float
    precision: float
    radius: float
    ratio: float
    reflectX: bool
    reflectY: bool
    rotate: Sequence[float]
    scale: float
    size: Sequence[float]
    spacing: float
    tilt: float
    translate: Sequence[float]
    type: ProjectionType_T


class RadialGradientKwds(TypedDict, total=False):
    """
    :class:`altair.RadialGradient` ``TypedDict`` wrapper.

    Parameters
    ----------
    gradient
        The type of gradient. Use ``"radial"`` for a radial gradient.
    stops
        An array of gradient stops defining the gradient color sequence.
    id

    r1
        The radius length, in normalized [0, 1] coordinates, of the inner circle for the
        gradient.

        **Default value:** ``0``
    r2
        The radius length, in normalized [0, 1] coordinates, of the outer circle for the
        gradient.

        **Default value:** ``0.5``
    x1
        The x-coordinate, in normalized [0, 1] coordinates, for the center of the inner
        circle for the gradient.

        **Default value:** ``0.5``
    x2
        The x-coordinate, in normalized [0, 1] coordinates, for the center of the outer
        circle for the gradient.

        **Default value:** ``0.5``
    y1
        The y-coordinate, in normalized [0, 1] coordinates, for the center of the inner
        circle for the gradient.

        **Default value:** ``0.5``
    y2
        The y-coordinate, in normalized [0, 1] coordinates, for the center of the outer
        circle for the gradient.

        **Default value:** ``0.5``
    """

    gradient: Literal["radial"]
    stops: Sequence[GradientStopKwds]
    id: str
    r1: float
    r2: float
    x1: float
    x2: float
    y1: float
    y2: float


class RangeConfigKwds(TypedDict, total=False):
    """
    :class:`altair.RangeConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    category
        Default `color scheme <https://vega.github.io/vega/docs/schemes/>`__ for categorical
        data.
    diverging
        Default `color scheme <https://vega.github.io/vega/docs/schemes/>`__ for diverging
        quantitative ramps.
    heatmap
        Default `color scheme <https://vega.github.io/vega/docs/schemes/>`__ for
        quantitative heatmaps.
    ordinal
        Default `color scheme <https://vega.github.io/vega/docs/schemes/>`__ for
        rank-ordered data.
    ramp
        Default `color scheme <https://vega.github.io/vega/docs/schemes/>`__ for sequential
        quantitative ramps.
    symbol
        Array of `symbol <https://vega.github.io/vega/docs/marks/symbol/>`__ names or paths
        for the default shape palette.
    """

    category: (
        Sequence[ColorHex | ColorName_T]
        | Sequence[str | bool | float | Sequence[float] | None]
        | RangeEnum_T
    )
    diverging: (
        Sequence[ColorHex | ColorName_T]
        | Sequence[str | bool | float | Sequence[float] | None]
        | RangeEnum_T
    )
    heatmap: (
        Sequence[ColorHex | ColorName_T]
        | Sequence[str | bool | float | Sequence[float] | None]
        | RangeEnum_T
    )
    ordinal: (
        Sequence[ColorHex | ColorName_T]
        | Sequence[str | bool | float | Sequence[float] | None]
        | RangeEnum_T
    )
    ramp: (
        Sequence[ColorHex | ColorName_T]
        | Sequence[str | bool | float | Sequence[float] | None]
        | RangeEnum_T
    )
    symbol: Sequence[str]


class RectConfigKwds(TypedDict, total=False):
    """
    :class:`altair.RectConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    binSpacing
        Offset between bars for binned field. The ideal value for this is either 0
        (preferred by statisticians) or 1 (Vega-Lite default, D3 example style).

        **Default value:** ``1``
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    continuousBandSize
        The default size of the bars on continuous scales.

        **Default value:** ``5``
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    discreteBandSize
        The default size of the bars with discrete dimensions. If unspecified, the default
        size is  ``step-2``, which provides 2 pixel offset between bars.
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    minBandSize
        The minimum band size for bar and rectangle marks. **Default value:** ``0.25``
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    baseline: TextBaseline_T
    binSpacing: float
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    continuousBandSize: float
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    discreteBandSize: float
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    minBandSize: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class ResolveKwds(TypedDict, total=False):
    """
    :class:`altair.Resolve` ``TypedDict`` wrapper.

    Parameters
    ----------
    axis

    legend

    scale

    """

    axis: AxisResolveMapKwds
    legend: LegendResolveMapKwds
    scale: ScaleResolveMapKwds


class ScaleConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ScaleConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    bandPaddingInner
        Default inner padding for ``x`` and ``y`` band scales.

        **Default value:**

        * ``nestedOffsetPaddingInner`` for x/y scales with nested x/y offset scales.
        * ``barBandPaddingInner`` for bar marks (``0.1`` by default)
        * ``rectBandPaddingInner`` for rect and other marks (``0`` by default)
    bandPaddingOuter
        Default outer padding for ``x`` and ``y`` band scales.

        **Default value:** ``paddingInner/2`` (which makes *width/height = number of unique
        values * step*)
    bandWithNestedOffsetPaddingInner
        Default inner padding for ``x`` and ``y`` band scales with nested ``xOffset`` and
        ``yOffset`` encoding.

        **Default value:** ``0.2``
    bandWithNestedOffsetPaddingOuter
        Default outer padding for ``x`` and ``y`` band scales with nested ``xOffset`` and
        ``yOffset`` encoding.

        **Default value:** ``0.2``
    barBandPaddingInner
        Default inner padding for ``x`` and ``y`` band-ordinal scales of ``"bar"`` marks.

        **Default value:** ``0.1``
    clamp
        If true, values that exceed the data domain are clamped to either the minimum or
        maximum range value
    continuousPadding
        Default padding for continuous x/y scales.

        **Default:** The bar width for continuous x-scale of a vertical bar and continuous
        y-scale of a horizontal bar.; ``0`` otherwise.
    invalid
        An object that defines scale outputs per channel for invalid values (nulls and NaNs
        on a continuous scale).

        * The keys in this object are the scale channels.
        * The values is either ``"zero-or-min"`` (use zero if the scale includes zero or min
          value otherwise) or a value definition ``{value: ...}``.

        *Example:* Setting this ``config.scale.invalid`` property to ``{color: {value:
        '#aaa'}}`` will make the visualization color all invalid values with '#aaa'.

        See [https://vega.github.io/vega-lite/docs/invalid-data.html](Invalid Data Docs) for
        more details.
    maxBandSize
        The default max value for mapping quantitative fields to bar's size/bandSize.

        If undefined (default), we will use the axis's size (width or height) - 1.
    maxFontSize
        The default max value for mapping quantitative fields to text's size/fontSize scale.

        **Default value:** ``40``
    maxOpacity
        Default max opacity for mapping a field to opacity.

        **Default value:** ``0.8``
    maxSize
        Default max value for point size scale.
    maxStrokeWidth
        Default max strokeWidth for the scale of strokeWidth for rule and line marks and of
        size for trail marks.

        **Default value:** ``4``
    minBandSize
        The default min value for mapping quantitative fields to bar and tick's
        size/bandSize scale.

        **Default value:** ``2``
    minFontSize
        The default min value for mapping quantitative fields to text's size/fontSize scale.

        **Default value:** ``8``
    minOpacity
        Default minimum opacity for mapping a field to opacity.

        **Default value:** ``0.3``
    minSize
        Default minimum value for point size scale.

        **Default value:** ``9``
    minStrokeWidth
        Default minimum strokeWidth for the scale of strokeWidth for rule and line marks and
        of size for trail marks.

        **Default value:** ``1``
    offsetBandPaddingInner
        Default padding inner for xOffset/yOffset's band scales.

        **Default Value:** ``0``
    offsetBandPaddingOuter
        Default padding outer for xOffset/yOffset's band scales.

        **Default Value:** ``0``
    pointPadding
        Default outer padding for ``x`` and ``y`` point-ordinal scales.

        **Default value:** ``0.5`` (which makes *width/height = number of unique values *
        step*)
    quantileCount
        Default range cardinality for `quantile
        <https://vega.github.io/vega-lite/docs/scale.html#quantile>`__ scale.

        **Default value:** ``4``
    quantizeCount
        Default range cardinality for `quantize
        <https://vega.github.io/vega-lite/docs/scale.html#quantize>`__ scale.

        **Default value:** ``4``
    rectBandPaddingInner
        Default inner padding for ``x`` and ``y`` band-ordinal scales of ``"rect"`` marks.

        **Default value:** ``0``
    round
        If true, rounds numeric output values to integers. This can be helpful for snapping
        to the pixel grid. (Only available for ``x``, ``y``, and ``size`` scales.)
    tickBandPaddingInner
        Default inner padding for ``x`` and ``y`` band-ordinal scales of ``"tick"`` marks.

        **Default value:** ``0.25``
    useUnaggregatedDomain
        Use the source data range before aggregation as scale domain instead of aggregated
        data for aggregate axis.

        This is equivalent to setting ``domain`` to ``"unaggregate"`` for aggregated
        *quantitative* fields by default.

        This property only works with aggregate functions that produce values within the raw
        data domain (``"mean"``, ``"average"``, ``"median"``, ``"q1"``, ``"q3"``, ``"min"``,
        ``"max"``). For other aggregations that produce values outside of the raw data
        domain (e.g. ``"count"``, ``"sum"``), this property is ignored.

        **Default value:** ``false``
    xReverse
        Reverse x-scale by default (useful for right-to-left charts).
    zero
        Default ``scale.zero`` for `continuous
        <https://vega.github.io/vega-lite/docs/scale.html#continuous>`__ scales except for
        (1) x/y-scales of non-ranged bar or area charts and (2) size scales.

        **Default value:** ``true``
    """

    bandPaddingInner: float
    bandPaddingOuter: float
    bandWithNestedOffsetPaddingInner: float
    bandWithNestedOffsetPaddingOuter: float
    barBandPaddingInner: float
    clamp: bool
    continuousPadding: float
    invalid: ScaleInvalidDataConfigKwds
    maxBandSize: float
    maxFontSize: float
    maxOpacity: float
    maxSize: float
    maxStrokeWidth: float
    minBandSize: float
    minFontSize: float
    minOpacity: float
    minSize: float
    minStrokeWidth: float
    offsetBandPaddingInner: float
    offsetBandPaddingOuter: float
    pointPadding: float
    quantileCount: float
    quantizeCount: float
    rectBandPaddingInner: float
    round: bool
    tickBandPaddingInner: float
    useUnaggregatedDomain: bool
    xReverse: bool
    zero: bool


class ScaleInvalidDataConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ScaleInvalidDataConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    angle

    color

    fill

    fillOpacity

    opacity

    radius

    shape

    size

    stroke

    strokeDash

    strokeOpacity

    strokeWidth

    theta

    x

    xOffset

    y

    yOffset

    """

    angle: Value[float] | Literal["zero-or-min"]
    color: (
        Literal["zero-or-min"]
        | Value[ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T]
    )
    fill: (
        Literal["zero-or-min"]
        | Value[ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None]
    )
    fillOpacity: Value[float] | Literal["zero-or-min"]
    opacity: Value[float] | Literal["zero-or-min"]
    radius: Value[float] | Literal["zero-or-min"]
    shape: Value[str] | Literal["zero-or-min"]
    size: Value[float] | Literal["zero-or-min"]
    stroke: (
        Literal["zero-or-min"]
        | Value[ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None]
    )
    strokeDash: Literal["zero-or-min"] | Value[Sequence[float]]
    strokeOpacity: Value[float] | Literal["zero-or-min"]
    strokeWidth: Value[float] | Literal["zero-or-min"]
    theta: Value[float] | Literal["zero-or-min"]
    x: Literal["zero-or-min"] | Value[float | Literal["width"]]
    xOffset: Value[float] | Literal["zero-or-min"]
    y: Literal["zero-or-min"] | Value[float | Literal["height"]]
    yOffset: Value[float] | Literal["zero-or-min"]


class ScaleResolveMapKwds(TypedDict, total=False):
    """
    :class:`altair.ScaleResolveMap` ``TypedDict`` wrapper.

    Parameters
    ----------
    angle

    color

    fill

    fillOpacity

    opacity

    radius

    shape

    size

    stroke

    strokeDash

    strokeOpacity

    strokeWidth

    theta

    x

    xOffset

    y

    yOffset

    """

    angle: ResolveMode_T
    color: ResolveMode_T
    fill: ResolveMode_T
    fillOpacity: ResolveMode_T
    opacity: ResolveMode_T
    radius: ResolveMode_T
    shape: ResolveMode_T
    size: ResolveMode_T
    stroke: ResolveMode_T
    strokeDash: ResolveMode_T
    strokeOpacity: ResolveMode_T
    strokeWidth: ResolveMode_T
    theta: ResolveMode_T
    x: ResolveMode_T
    xOffset: ResolveMode_T
    y: ResolveMode_T
    yOffset: ResolveMode_T


class SelectionConfigKwds(TypedDict, total=False):
    """
    :class:`altair.SelectionConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    interval
        The default definition for an `interval
        <https://vega.github.io/vega-lite/docs/parameter.html#select>`__ selection. All
        properties and transformations for an interval selection definition (except
        ``type``) may be specified here.

        For instance, setting ``interval`` to ``{"translate": false}`` disables the ability
        to move interval selections by default.
    point
        The default definition for a `point
        <https://vega.github.io/vega-lite/docs/parameter.html#select>`__ selection. All
        properties and transformations  for a point selection definition (except ``type``)
        may be specified here.

        For instance, setting ``point`` to ``{"on": "dblclick"}`` populates point selections
        on double-click by default.
    """

    interval: IntervalSelectionConfigWithoutTypeKwds
    point: PointSelectionConfigWithoutTypeKwds


class StepKwds(TypedDict, closed=True, total=False):  # type: ignore[call-arg]
    """
    :class:`altair.Step` ``TypedDict`` wrapper.

    Parameters
    ----------
    step
        The size (width/height) per discrete step.

    Notes
    -----
    The following keys may be specified as string literals **only**:

        ['for']

    See `PEP728`_ for type checker compatibility.

    .. _PEP728:
        https://peps.python.org/pep-0728/#reference-implementation
    """

    step: float
    __extra_items__: StepFor_T


class StyleConfigIndexKwds(TypedDict, closed=True, total=False):  # type: ignore[call-arg]
    """
    :class:`altair.StyleConfigIndex` ``TypedDict`` wrapper.

    Parameters
    ----------
    arc
        Arc-specific Config
    area
        Area-Specific Config
    bar
        Bar-Specific Config
    circle
        Circle-Specific Config
    geoshape
        Geoshape-Specific Config
    image
        Image-specific Config
    line
        Line-Specific Config
    mark
        Mark Config
    point
        Point-Specific Config
    rect
        Rect-Specific Config
    rule
        Rule-Specific Config
    square
        Square-Specific Config
    text
        Text-Specific Config
    tick
        Tick-Specific Config
    trail
        Trail-Specific Config

    Notes
    -----
    The following keys may be specified as string literals **only**:

        ['group-subtitle', 'group-title', 'guide-label', 'guide-title']

    See `PEP728`_ for type checker compatibility.

    .. _PEP728:
        https://peps.python.org/pep-0728/#reference-implementation
    """

    arc: RectConfigKwds
    area: AreaConfigKwds
    bar: BarConfigKwds
    circle: MarkConfigKwds
    geoshape: MarkConfigKwds
    image: RectConfigKwds
    line: LineConfigKwds
    mark: MarkConfigKwds
    point: MarkConfigKwds
    rect: RectConfigKwds
    rule: MarkConfigKwds
    square: MarkConfigKwds
    text: MarkConfigKwds
    tick: TickConfigKwds
    trail: LineConfigKwds
    __extra_items__: MarkConfigKwds


class TickConfigKwds(TypedDict, total=False):
    """
    :class:`altair.TickConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        The horizontal alignment of the text or ranged marks (area, bar, image, rect, rule).
        One of ``"left"``, ``"right"``, ``"center"``.

        **Note:** Expression reference is *not* supported for range marks.
    angle
        The rotation angle of the text, in degrees.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG element, removing the mark item from the ARIA accessibility tree.
    ariaRole
        Sets the type of user interface element of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "role" attribute. Warning: this
        property is experimental and may be changed in the future.
    ariaRoleDescription
        A human-readable, author-localized description for the role of the mark item for
        `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the "aria-roledescription" attribute.
        Warning: this property is experimental and may be changed in the future.
    aspect
        Whether to keep aspect ratio of image marks.
    bandSize
        The width of the ticks.

        **Default value:**  3/4 of step (width step for horizontal ticks and height step for
        vertical ticks).
    baseline
        For text marks, the vertical text baseline. One of ``"alphabetic"`` (default),
        ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, ``"line-bottom"``, or an
        expression reference that provides one of the valid values. The ``"line-top"`` and
        ``"line-bottom"`` values operate similarly to ``"top"`` and ``"bottom"``, but are
        calculated relative to the ``lineHeight`` rather than ``fontSize`` alone.

        For range marks, the vertical alignment of the marks. One of ``"top"``,
        ``"middle"``, ``"bottom"``.

        **Note:** Expression reference is *not* supported for range marks.
    blend
        The color blend mode for drawing an item on its current background. Any valid `CSS
        mix-blend-mode <https://developer.mozilla.org/en-US/docs/Web/CSS/mix-blend-mode>`__
        value can be used.

        __Default value:__ ``"source-over"``
    color
        Default color.

        **Default value:**  :raw-html:`<span style="color: #4682b4;">` ■ :raw-html:`</span>`
        ``"#4682b4"``

        **Note:**

        * This property cannot be used in a `style config
          <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
        * The ``fill`` and ``stroke`` properties have higher precedence than ``color`` and
          will override ``color``.
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cornerRadiusBottomLeft
        The radius in pixels of rounded rectangles' bottom left corner.

        **Default value:** ``0``
    cornerRadiusBottomRight
        The radius in pixels of rounded rectangles' bottom right corner.

        **Default value:** ``0``
    cornerRadiusTopLeft
        The radius in pixels of rounded rectangles' top right corner.

        **Default value:** ``0``
    cornerRadiusTopRight
        The radius in pixels of rounded rectangles' top left corner.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the mark. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    description
        A text description of the mark item for `ARIA accessibility
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ (SVG output
        only). If specified, this property determines the `"aria-label" attribute
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/ARIA_Techniques/Using_the_aria-label_attribute>`__.
    dir
        The direction of the text. One of ``"ltr"`` (left-to-right) or ``"rtl"``
        (right-to-left). This property determines on which side is truncated in response to
        the limit parameter.

        **Default value:** ``"ltr"``
    dx
        The horizontal offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    dy
        The vertical offset, in pixels, between the text label and its anchor point. The
        offset is applied after rotation by the *angle* property.
    ellipsis
        The ellipsis string for text truncated in response to the limit parameter.

        **Default value:** ``"…"``
    endAngle
        The end angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    fill
        Default fill color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove fill.

        **Default value:** (None)
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    filled
        Whether the mark's color should be used as fill color instead of stroke color.

        **Default value:** ``false`` for all ``point``, ``line``, and ``rule`` marks as well
        as ``geoshape`` marks for `graticule
        <https://vega.github.io/vega-lite/docs/data.html#graticule>`__ data sources;
        otherwise, ``true``.

        **Note:** This property cannot be used in a `style config
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__.
    font
        The typeface to set the text in (e.g., ``"Helvetica Neue"``).
    fontSize
        The font size, in pixels.

        **Default value:** ``11``
    fontStyle
        The font style (e.g., ``"italic"``).
    fontWeight
        The font weight. This can be either a string (e.g ``"bold"``, ``"normal"``) or a
        number (``100``, ``200``, ``300``, ..., ``900`` where ``"normal"`` = ``400`` and
        ``"bold"`` = ``700``).
    height
        Height of the marks.
    href
        A URL to load upon mouse click. If defined, the mark acts as a hyperlink.
    innerRadius
        The inner radius in pixels of arc marks. ``innerRadius`` is an alias for
        ``radius2``.

        **Default value:** ``0``
    interpolate
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
    invalid
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
    limit
        The maximum length of the text mark in pixels. The text value will be automatically
        truncated if the rendered size exceeds the limit.

        **Default value:** ``0`` -- indicating no limit
    lineBreak
        A delimiter, such as a newline character, upon which to break text strings into
        multiple lines. This property is ignored if the text is array-valued.
    lineHeight
        The line height in pixels (the spacing between subsequent lines of text) for
        multi-line text marks.
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    order
        For line and trail marks, this ``order`` property can be set to ``null`` or
        ``false`` to make the lines use the original order in the data sources.
    orient
        The orientation of a non-stacked bar, tick, area, and line charts. The value is
        either horizontal (default) or vertical.

        * For bar, rule and tick, this determines whether the size of the bar and tick
          should be applied to x or y dimension.
        * For area, this property determines the orient property of the Vega output.
        * For line and trail marks, this property determines the sort order of the points in
          the line if ``config.sortLineBy`` is not specified. For stacked charts, this is
          always determined by the orientation of the stack; therefore explicitly specified
          value will be ignored.
    outerRadius
        The outer radius in pixels of arc marks. ``outerRadius`` is an alias for ``radius``.

        **Default value:** ``0``
    padAngle
        The angular padding applied to sides of the arc, in radians.
    radius
        For arc mark, the primary (outer) radius in pixels.

        For text marks, polar coordinate radial offset, in pixels, of the text from the
        origin determined by the ``x`` and ``y`` properties.

        **Default value:** ``min(plot_width, plot_height)/2``
    radius2
        The secondary (inner) radius in pixels of arc marks.

        **Default value:** ``0``
    shape
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
    size
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
    smooth
        A boolean flag (default true) indicating if the image should be smoothed when
        resized. If false, individual pixels should be scaled directly rather than
        interpolated with smoothing. For SVG rendering, this option may not work in some
        browsers due to lack of standardization.
    startAngle
        The start angle in radians for arc marks. A value of ``0`` indicates up (north),
        increasing values proceed clockwise.
    stroke
        Default stroke color. This property has higher precedence than ``config.color``. Set
        to ``null`` to remove stroke.

        **Default value:** (None)
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOffset
        The offset in pixels at which to draw the group stroke and fill. If unspecified, the
        default behavior is to dynamically offset stroked groups such that 1 pixel stroke
        widths align with the pixel grid.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    tension
        Depending on the interpolation type, sets the tension parameter (for line and area
        marks).
    text
        Placeholder text if the ``text`` channel is not specified
    theta
        * For arc marks, the arc length in radians if theta2 is not specified, otherwise the
          start arc angle. (A value of 0 indicates up or “north”, increasing values proceed
          clockwise.)

        * For text marks, polar coordinate angle in radians.
    theta2
        The end angle of arc marks in radians. A value of 0 indicates up or “north”,
        increasing values proceed clockwise.
    thickness
        Thickness of the tick mark.

        **Default value:**  ``1``
    timeUnitBandPosition
        Default relative band position for a time unit. If set to ``0``, the marks will be
        positioned at the beginning of the time unit band step. If set to ``0.5``, the marks
        will be positioned in the middle of the time unit band step.
    timeUnitBandSize
        Default relative band size for a time unit. If set to ``1``, the bandwidth of the
        marks will be equal to the time unit band step. If set to ``0.5``, bandwidth of the
        marks will be half of the time unit band step.
    tooltip
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
    url
        The URL of the image file for image marks.
    width
        Width of the marks.
    x
        X coordinates of the marks, or width of horizontal ``"bar"`` and ``"area"`` without
        specified ``x2`` or ``width``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    x2
        X2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"width"`` for the width
        of the plot.
    y
        Y coordinates of the marks, or height of vertical ``"bar"`` and ``"area"`` without
        specified ``y2`` or ``height``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    y2
        Y2 coordinates for ranged ``"area"``, ``"bar"``, ``"rect"``, and  ``"rule"``.

        The ``value`` of this channel can be a number or a string ``"height"`` for the
        height of the plot.
    """

    align: Align_T
    angle: float
    aria: bool
    ariaRole: str
    ariaRoleDescription: str
    aspect: bool
    bandSize: float
    baseline: TextBaseline_T
    blend: Blend_T
    color: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T
    cornerRadius: float
    cornerRadiusBottomLeft: float
    cornerRadiusBottomRight: float
    cornerRadiusTopLeft: float
    cornerRadiusTopRight: float
    cursor: Cursor_T
    description: str
    dir: TextDirection_T
    dx: float
    dy: float
    ellipsis: str
    endAngle: float
    fill: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    fillOpacity: float
    filled: bool
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    height: float
    href: str
    innerRadius: float
    interpolate: Interpolate_T
    invalid: MarkInvalidDataMode_T | None
    limit: float
    lineBreak: str
    lineHeight: float
    opacity: float
    order: bool | None
    orient: Orientation_T
    outerRadius: float
    padAngle: float
    radius: float
    radius2: float
    shape: str
    size: float
    smooth: bool
    startAngle: float
    stroke: ColorHex | LinearGradientKwds | RadialGradientKwds | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOffset: float
    strokeOpacity: float
    strokeWidth: float
    tension: float
    text: str | Sequence[str]
    theta: float
    theta2: float
    thickness: float
    timeUnitBandPosition: float
    timeUnitBandSize: float
    tooltip: str | bool | float | TooltipContentKwds | None
    url: str
    width: float
    x: float | Literal["width"]
    x2: float | Literal["width"]
    y: float | Literal["height"]
    y2: float | Literal["height"]


class TimeIntervalStepKwds(TypedDict, total=False):
    """
    :class:`altair.TimeIntervalStep` ``TypedDict`` wrapper.

    Parameters
    ----------
    interval

    step

    """

    interval: TimeInterval_T
    step: float


class TimeLocaleKwds(TypedDict, total=False):
    """
    :class:`altair.TimeLocale` ``TypedDict`` wrapper.

    Parameters
    ----------
    date
        The date (%x) format specifier (e.g., "%m/%d/%Y").
    dateTime
        The date and time (%c) format specifier (e.g., "%a %b %e %X %Y").
    days
        The full names of the weekdays, starting with Sunday.
    months
        The full names of the months (starting with January).
    periods
        The A.M. and P.M. equivalents (e.g., ["AM", "PM"]).
    shortDays
        The abbreviated names of the weekdays, starting with Sunday.
    shortMonths
        The abbreviated names of the months (starting with January).
    time
        The time (%X) format specifier (e.g., "%H:%M:%S").
    """

    date: str
    dateTime: str
    days: Sequence[str]
    months: Sequence[str]
    periods: Sequence[str]
    shortDays: Sequence[str]
    shortMonths: Sequence[str]
    time: str


class TitleConfigKwds(TypedDict, total=False):
    """
    :class:`altair.TitleConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    align
        Horizontal text alignment for title text. One of ``"left"``, ``"center"``, or
        ``"right"``.
    anchor
        The anchor position for placing the title and subtitle text. One of ``"start"``,
        ``"middle"``, or ``"end"``. For example, with an orientation of top these anchor
        positions map to a left-, center-, or right-aligned title.
    angle
        Angle in degrees of title and subtitle text.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG group, removing the title from the ARIA accessibility tree.

        **Default value:** ``true``
    baseline
        Vertical text baseline for title and subtitle text. One of ``"alphabetic"``
        (default), ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or
        ``"line-bottom"``. The ``"line-top"`` and ``"line-bottom"`` values operate similarly
        to ``"top"`` and ``"bottom"``, but are calculated relative to the *lineHeight*
        rather than *fontSize* alone.
    color
        Text color for title text.
    dx
        Delta offset for title and subtitle text x-coordinate.
    dy
        Delta offset for title and subtitle text y-coordinate.
    font
        Font name for title text.
    fontSize
        Font size in pixels for title text.
    fontStyle
        Font style for title text.
    fontWeight
        Font weight for title text. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    frame
        The reference frame for the anchor position, one of ``"bounds"`` (to anchor relative
        to the full bounding box) or ``"group"`` (to anchor relative to the group width or
        height).
    limit
        The maximum allowed length in pixels of title and subtitle text.
    lineHeight
        Line height in pixels for multi-line title text or title text with ``"line-top"`` or
        ``"line-bottom"`` baseline.
    offset
        The orthogonal offset in pixels by which to displace the title group from its
        position along the edge of the chart.
    orient
        Default title orientation (``"top"``, ``"bottom"``, ``"left"``, or ``"right"``)
    subtitleColor
        Text color for subtitle text.
    subtitleFont
        Font name for subtitle text.
    subtitleFontSize
        Font size in pixels for subtitle text.
    subtitleFontStyle
        Font style for subtitle text.
    subtitleFontWeight
        Font weight for subtitle text. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    subtitleLineHeight
        Line height in pixels for multi-line subtitle text.
    subtitlePadding
        The padding in pixels between title and subtitle text.
    zindex
        The integer z-index indicating the layering of the title group relative to other
        axis, mark, and legend groups.

        **Default value:** ``0``.
    """

    align: Align_T
    anchor: TitleAnchor_T
    angle: float
    aria: bool
    baseline: TextBaseline_T
    color: ColorHex | ColorName_T | None
    dx: float
    dy: float
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    frame: str | TitleFrame_T
    limit: float
    lineHeight: float
    offset: float
    orient: TitleOrient_T
    subtitleColor: ColorHex | ColorName_T | None
    subtitleFont: str
    subtitleFontSize: float
    subtitleFontStyle: str
    subtitleFontWeight: FontWeight_T
    subtitleLineHeight: float
    subtitlePadding: float
    zindex: float


class TitleParamsKwds(TypedDict, total=False):
    """
    :class:`altair.TitleParams` ``TypedDict`` wrapper.

    Parameters
    ----------
    text
        The title text.
    align
        Horizontal text alignment for title text. One of ``"left"``, ``"center"``, or
        ``"right"``.
    anchor
        The anchor position for placing the title. One of ``"start"``, ``"middle"``, or
        ``"end"``. For example, with an orientation of top these anchor positions map to a
        left-, center-, or right-aligned title.

        **Default value:** ``"middle"`` for `single
        <https://vega.github.io/vega-lite/docs/spec.html>`__ and `layered
        <https://vega.github.io/vega-lite/docs/layer.html>`__ views. ``"start"`` for other
        composite views.

        **Note:** `For now <https://github.com/vega/vega-lite/issues/2875>`__, ``anchor`` is
        only customizable only for `single
        <https://vega.github.io/vega-lite/docs/spec.html>`__ and `layered
        <https://vega.github.io/vega-lite/docs/layer.html>`__ views. For other composite
        views, ``anchor`` is always ``"start"``.
    angle
        Angle in degrees of title and subtitle text.
    aria
        A boolean flag indicating if `ARIA attributes
        <https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA>`__ should be
        included (SVG output only). If ``false``, the "aria-hidden" attribute will be set on
        the output SVG group, removing the title from the ARIA accessibility tree.

        **Default value:** ``true``
    baseline
        Vertical text baseline for title and subtitle text. One of ``"alphabetic"``
        (default), ``"top"``, ``"middle"``, ``"bottom"``, ``"line-top"``, or
        ``"line-bottom"``. The ``"line-top"`` and ``"line-bottom"`` values operate similarly
        to ``"top"`` and ``"bottom"``, but are calculated relative to the *lineHeight*
        rather than *fontSize* alone.
    color
        Text color for title text.
    dx
        Delta offset for title and subtitle text x-coordinate.
    dy
        Delta offset for title and subtitle text y-coordinate.
    font
        Font name for title text.
    fontSize
        Font size in pixels for title text.
    fontStyle
        Font style for title text.
    fontWeight
        Font weight for title text. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    frame
        The reference frame for the anchor position, one of ``"bounds"`` (to anchor relative
        to the full bounding box) or ``"group"`` (to anchor relative to the group width or
        height).
    limit
        The maximum allowed length in pixels of title and subtitle text.
    lineHeight
        Line height in pixels for multi-line title text or title text with ``"line-top"`` or
        ``"line-bottom"`` baseline.
    offset
        The orthogonal offset in pixels by which to displace the title group from its
        position along the edge of the chart.
    orient
        Default title orientation (``"top"``, ``"bottom"``, ``"left"``, or ``"right"``)
    style
        A `mark style property <https://vega.github.io/vega-lite/docs/config.html#style>`__
        to apply to the title text mark.

        **Default value:** ``"group-title"``.
    subtitle
        The subtitle Text.
    subtitleColor
        Text color for subtitle text.
    subtitleFont
        Font name for subtitle text.
    subtitleFontSize
        Font size in pixels for subtitle text.
    subtitleFontStyle
        Font style for subtitle text.
    subtitleFontWeight
        Font weight for subtitle text. This can be either a string (e.g ``"bold"``,
        ``"normal"``) or a number (``100``, ``200``, ``300``, ..., ``900`` where
        ``"normal"`` = ``400`` and ``"bold"`` = ``700``).
    subtitleLineHeight
        Line height in pixels for multi-line subtitle text.
    subtitlePadding
        The padding in pixels between title and subtitle text.
    zindex
        The integer z-index indicating the layering of the title group relative to other
        axis, mark and legend groups.

        **Default value:** ``0``.
    """

    text: str | Sequence[str]
    align: Align_T
    anchor: TitleAnchor_T
    angle: float
    aria: bool
    baseline: TextBaseline_T
    color: ColorHex | ColorName_T | None
    dx: float
    dy: float
    font: str
    fontSize: float
    fontStyle: str
    fontWeight: FontWeight_T
    frame: str | TitleFrame_T
    limit: float
    lineHeight: float
    offset: float
    orient: TitleOrient_T
    style: str | Sequence[str]
    subtitle: str | Sequence[str]
    subtitleColor: ColorHex | ColorName_T | None
    subtitleFont: str
    subtitleFontSize: float
    subtitleFontStyle: str
    subtitleFontWeight: FontWeight_T
    subtitleLineHeight: float
    subtitlePadding: float
    zindex: float


class TooltipContentKwds(TypedDict, total=False):
    """
    :class:`altair.TooltipContent` ``TypedDict`` wrapper.

    Parameters
    ----------
    content

    """

    content: Literal["encoding", "data"]


class TopLevelSelectionParameterKwds(TypedDict, total=False):
    """
    :class:`altair.TopLevelSelectionParameter` ``TypedDict`` wrapper.

    Parameters
    ----------
    name
        Required. A unique name for the selection parameter. Selection names should be valid
        JavaScript identifiers: they should contain only alphanumeric characters (or "$", or
        "_") and may not start with a digit. Reserved keywords that may not be used as
        parameter names are "datum", "event", "item", and "parent".
    select
        Determines the default event processing and data query for the selection. Vega-Lite
        currently supports two selection types:

        * ``"point"`` -- to select multiple discrete data values; the first value is
          selected on ``click`` and additional values toggled on shift-click.
        * ``"interval"`` -- to select a continuous range of data values on ``drag``.
    bind
        When set, a selection is populated by input elements (also known as dynamic query
        widgets) or by interacting with the corresponding legend. Direct manipulation
        interaction is disabled by default; to re-enable it, set the selection's `on
        <https://vega.github.io/vega-lite/docs/selection.html#common-selection-properties>`__
        property.

        Legend bindings are restricted to selections that only specify a single field or
        encoding.

        Query widget binding takes the form of Vega's `input element binding definition
        <https://vega.github.io/vega/docs/signals/#bind>`__ or can be a mapping between
        projected field/encodings and binding definitions.

        **See also:** `bind <https://vega.github.io/vega-lite/docs/bind.html>`__
        documentation.
    value
        Initialize the selection with a mapping between `projected channels or field names
        <https://vega.github.io/vega-lite/docs/selection.html#project>`__ and initial
        values.

        **See also:** `init <https://vega.github.io/vega-lite/docs/value.html>`__
        documentation.
    views
        By default, top-level selections are applied to every view in the visualization. If
        this property is specified, selections will only be applied to views with the given
        names.
    """

    name: str
    select: PointSelectionConfigKwds | IntervalSelectionConfigKwds | SelectionType_T
    bind: (
        BindInputKwds
        | BindRangeKwds
        | BindDirectKwds
        | BindCheckboxKwds
        | BindRadioSelectKwds
        | LegendStreamBindingKwds
        | Literal["legend", "scales"]
    )
    value: DateTimeKwds | Sequence[Map] | PrimitiveValue_T
    views: Sequence[str]


class VariableParameterKwds(TypedDict, total=False):
    """
    :class:`altair.VariableParameter` ``TypedDict`` wrapper.

    Parameters
    ----------
    name
        A unique name for the variable parameter. Parameter names should be valid JavaScript
        identifiers: they should contain only alphanumeric characters (or "$", or "_") and
        may not start with a digit. Reserved keywords that may not be used as parameter
        names are "datum", "event", "item", and "parent".
    bind
        Binds the parameter to an external input element such as a slider, selection list or
        radio button group.
    expr
        An expression for the value of the parameter. This expression may include other
        parameters, in which case the parameter will automatically update in response to
        upstream parameter changes.
    react
        A boolean flag (default ``true``) indicating if the update expression should be
        automatically re-evaluated when any upstream signal dependencies update. If
        ``false``, the update expression will not register any dependencies on other
        signals, even for initialization.

        **Default value:** ``true``
    value
        The `initial value <http://vega.github.io/vega-lite/docs/value.html>`__ of the
        parameter.

        **Default value:** ``undefined``
    """

    name: str
    bind: (
        BindInputKwds
        | BindRangeKwds
        | BindDirectKwds
        | BindCheckboxKwds
        | BindRadioSelectKwds
    )
    expr: str
    react: bool
    value: Any


class ViewBackgroundKwds(TypedDict, total=False):
    """
    :class:`altair.ViewBackground` ``TypedDict`` wrapper.

    Parameters
    ----------
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the view. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    fill
        The fill color.

        **Default value:** ``undefined``
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    stroke
        The stroke color.

        **Default value:** ``"#ddd"``
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    style
        A string or array of strings indicating the name of custom styles to apply to the
        view background. A style is a named collection of mark property defaults defined
        within the `style configuration
        <https://vega.github.io/vega-lite/docs/mark.html#style-config>`__. If style is an
        array, later styles will override earlier styles.

        **Default value:** ``"cell"`` **Note:** Any specified view background properties
        will augment the default style.
    """

    cornerRadius: float
    cursor: Cursor_T
    fill: ColorHex | ColorName_T | None
    fillOpacity: float
    opacity: float
    stroke: ColorHex | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOpacity: float
    strokeWidth: float
    style: str | Sequence[str]


class ViewConfigKwds(TypedDict, total=False):
    """
    :class:`altair.ViewConfig` ``TypedDict`` wrapper.

    Parameters
    ----------
    clip
        Whether the view should be clipped.
    continuousHeight
        The default height when the plot has a continuous y-field for x or latitude, or has
        arc marks.

        **Default value:** ``200``
    continuousWidth
        The default width when the plot has a continuous field for x or longitude, or has
        arc marks.

        **Default value:** ``200``
    cornerRadius
        The radius in pixels of rounded rectangles or arcs' corners.

        **Default value:** ``0``
    cursor
        The mouse cursor used over the view. Any valid `CSS cursor type
        <https://developer.mozilla.org/en-US/docs/Web/CSS/cursor#Values>`__ can be used.
    discreteHeight
        The default height when the plot has non arc marks and either a discrete y-field or
        no y-field. The height can be either a number indicating a fixed height or an object
        in the form of ``{step: number}`` defining the height per discrete step.

        **Default value:** a step size based on ``config.view.step``.
    discreteWidth
        The default width when the plot has non-arc marks and either a discrete x-field or
        no x-field. The width can be either a number indicating a fixed width or an object
        in the form of ``{step: number}`` defining the width per discrete step.

        **Default value:** a step size based on ``config.view.step``.
    fill
        The fill color.

        **Default value:** ``undefined``
    fillOpacity
        The fill opacity (value between [0,1]).

        **Default value:** ``1``
    opacity
        The overall opacity (value between [0,1]).

        **Default value:** ``0.7`` for non-aggregate plots with ``point``, ``tick``,
        ``circle``, or ``square`` marks or layered ``bar`` charts and ``1`` otherwise.
    step
        Default step size for x-/y- discrete fields.
    stroke
        The stroke color.

        **Default value:** ``"#ddd"``
    strokeCap
        The stroke cap for line ending style. One of ``"butt"``, ``"round"``, or
        ``"square"``.

        **Default value:** ``"butt"``
    strokeDash
        An array of alternating stroke, space lengths for creating dashed or dotted lines.
    strokeDashOffset
        The offset (in pixels) into which to begin drawing with the stroke dash array.
    strokeJoin
        The stroke line join method. One of ``"miter"``, ``"round"`` or ``"bevel"``.

        **Default value:** ``"miter"``
    strokeMiterLimit
        The miter limit at which to bevel a line join.
    strokeOpacity
        The stroke opacity (value between [0,1]).

        **Default value:** ``1``
    strokeWidth
        The stroke width, in pixels.
    """

    clip: bool
    continuousHeight: float
    continuousWidth: float
    cornerRadius: float
    cursor: Cursor_T
    discreteHeight: float
    discreteWidth: float
    fill: ColorHex | ColorName_T | None
    fillOpacity: float
    opacity: float
    step: float
    stroke: ColorHex | ColorName_T | None
    strokeCap: StrokeCap_T
    strokeDash: Sequence[float]
    strokeDashOffset: float
    strokeJoin: StrokeJoin_T
    strokeMiterLimit: float
    strokeOpacity: float
    strokeWidth: float


class ThemeConfig(TypedDict, total=False):
    """
    Top-Level Configuration ``TypedDict`` for creating a consistent theme.

    Parameters
    ----------
    align
        The alignment to apply to grid rows and columns. The supported string values are
        ``"all"``, ``"each"``, and ``"none"``.

        * For ``"none"``, a flow layout will be used, in which adjacent subviews are simply
          placed one after the other.
        * For ``"each"``, subviews will be aligned into a clean grid structure, but each row
          or column may be of variable size.
        * For ``"all"``, subviews will be aligned and each row or column will be sized
          identically based on the maximum observed size. String values for this property
          will be applied to both grid rows and columns.

        Alternatively, an object value of the form ``{"row": string, "column": string}`` can
        be used to supply different alignments for rows and columns.

        **Default value:** ``"all"``.
    autosize
        How the visualization size should be determined. If a string, should be one of
        ``"pad"``, ``"fit"`` or ``"none"``. Object values can additionally specify
        parameters for content sizing and automatic resizing.

        **Default value**: ``pad``
    background
        CSS color property to use as the background of the entire view.

        **Default value:** ``"white"``
    bounds
        The bounds calculation method to use for determining the extent of a sub-plot. One
        of ``full`` (the default) or ``flush``.

        * If set to ``full``, the entire calculated bounds (including axes, title, and
          legend) will be used.
        * If set to ``flush``, only the specified width and height values for the sub-view
          will be used. The ``flush`` setting can be useful when attempting to place
          sub-plots without axes or legends into a uniform grid structure.

        **Default value:** ``"full"``
    center
        Boolean flag indicating if subviews should be centered relative to their respective
        rows or columns.

        An object value of the form ``{"row": boolean, "column": boolean}`` can be used to
        supply different centering values for rows and columns.

        **Default value:** ``false``
    config
        Vega-Lite configuration object. This property can only be defined at the top-level
        of a specification.
    description
        Description of this mark for commenting purpose.
    height
        The height of a visualization.

        * For a plot with a continuous y-field, height should be a number.
        * For a plot with either a discrete y-field or no y-field, height can be either a
          number indicating a fixed height or an object in the form of ``{step: number}``
          defining the height per discrete step. (No y-field is equivalent to having one
          discrete step.)
        * To enable responsive sizing on height, it should be set to ``"container"``.

        **Default value:** Based on ``config.view.continuousHeight`` for a plot with a
        continuous y-field and ``config.view.discreteHeight`` otherwise.

        **Note:** For plots with `row and column channels
        <https://vega.github.io/vega-lite/docs/encoding.html#facet>`__, this represents the
        height of a single view and the ``"container"`` option cannot be used.

        **See also:** `height <https://vega.github.io/vega-lite/docs/size.html>`__
        documentation.
    name
        Name of the visualization for later reference.
    padding
        The default visualization padding, in pixels, from the edge of the visualization
        canvas to the data rectangle. If a number, specifies padding for all sides. If an
        object, the value should have the format ``{"left": 5, "top": 5, "right": 5,
        "bottom": 5}`` to specify padding for each side of the visualization.

        **Default value**: ``5``
    params
        An array of parameters that may either be simple variables, or more complex
        selections that map user input to data queries.
    projection
        An object defining properties of geographic projection, which will be applied to
        ``shape`` path for ``"geoshape"`` marks and to ``latitude`` and ``"longitude"``
        channels for other marks.
    resolve
        Scale, axis, and legend resolutions for view composition specifications.
    spacing
        The spacing in pixels between sub-views of the composition operator. An object of
        the form ``{"row": number, "column": number}`` can be used to set different spacing
        values for rows and columns.

        **Default value**: Depends on ``"spacing"`` property of `the view composition
        configuration <https://vega.github.io/vega-lite/docs/config.html#view-config>`__
        (``20`` by default)
    title
        Title for the plot.
    usermeta
        Optional metadata that will be passed to Vega. This object is completely ignored by
        Vega and Vega-Lite and can be used for custom metadata.
    view
        An object defining the view background's fill and stroke.

        **Default value:** none (transparent)
    width
        The width of a visualization.

        * For a plot with a continuous x-field, width should be a number.
        * For a plot with either a discrete x-field or no x-field, width can be either a
          number indicating a fixed width or an object in the form of ``{step: number}``
          defining the width per discrete step. (No x-field is equivalent to having one
          discrete step.)
        * To enable responsive sizing on width, it should be set to ``"container"``.

        **Default value:** Based on ``config.view.continuousWidth`` for a plot with a
        continuous x-field and ``config.view.discreteWidth`` otherwise.

        **Note:** For plots with `row and column channels
        <https://vega.github.io/vega-lite/docs/encoding.html#facet>`__, this represents the
        width of a single view and the ``"container"`` option cannot be used.

        **See also:** `width <https://vega.github.io/vega-lite/docs/size.html>`__
        documentation.
    """

    align: RowColKwds[LayoutAlign_T] | LayoutAlign_T
    autosize: AutoSizeParamsKwds | AutosizeType_T
    background: ColorHex | ColorName_T
    bounds: Literal["full", "flush"]
    center: bool | RowColKwds[bool]
    config: ConfigKwds
    description: str
    height: float | StepKwds | Literal["container"]
    name: str
    padding: float | PaddingKwds
    params: Sequence[VariableParameterKwds | TopLevelSelectionParameterKwds]
    projection: ProjectionKwds
    resolve: ResolveKwds
    spacing: float | RowColKwds[float]
    title: str | Sequence[str] | TitleParamsKwds
    usermeta: Map
    view: ViewBackgroundKwds
    width: float | StepKwds | Literal["container"]
