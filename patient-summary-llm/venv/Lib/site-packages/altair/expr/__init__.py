# The contents of this file are automatically written by
# tools/generate_schema_wrapper.py. Do not modify directly.

"""Tools for creating transform & filter expressions with a python syntax."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any

from altair.expr.core import ConstExpression, FunctionExpression
from altair.vegalite.v5.schema.core import ExprRef as _ExprRef

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from altair.expr.core import Expression, IntoExpression


class _ExprMeta(type):
    """
    Metaclass for :class:`expr`.

    Currently providing read-only class properties, representing JavaScript constants.
    """

    @property
    def NaN(cls) -> Expression:
        """Not a number (same as JavaScript literal NaN)."""
        return ConstExpression("NaN")

    @property
    def LN10(cls) -> Expression:
        """The natural log of 10 (alias to Math.LN10)."""
        return ConstExpression("LN10")

    @property
    def E(cls) -> Expression:
        """The transcendental number e (alias to Math.E)."""
        return ConstExpression("E")

    @property
    def LOG10E(cls) -> Expression:
        """The base 10 logarithm e (alias to Math.LOG10E)."""
        return ConstExpression("LOG10E")

    @property
    def LOG2E(cls) -> Expression:
        """The base 2 logarithm of e (alias to Math.LOG2E)."""
        return ConstExpression("LOG2E")

    @property
    def SQRT1_2(cls) -> Expression:
        """The square root of 0.5 (alias to Math.SQRT1_2)."""
        return ConstExpression("SQRT1_2")

    @property
    def LN2(cls) -> Expression:
        """The natural log of 2 (alias to Math.LN2)."""
        return ConstExpression("LN2")

    @property
    def SQRT2(cls) -> Expression:
        """The square root of 2 (alias to Math.SQRT1_2)."""
        return ConstExpression("SQRT2")

    @property
    def PI(cls) -> Expression:
        """The transcendental number pi (alias to Math.PI)."""
        return ConstExpression("PI")


class expr(_ExprRef, metaclass=_ExprMeta):
    """
    Utility providing *constants* and *classmethods* to construct expressions.

    `Expressions`_ can be used to write basic formulas that enable custom interactions.

    Alternatively, an `inline expression`_ may be defined via :class:`expr()`.

    Parameters
    ----------
    expr: str
        A `vega expression`_ string.

    Returns
    -------
    ``ExprRef``

    .. _Expressions:
        https://altair-viz.github.io/user_guide/interactions.html#expressions
    .. _inline expression:
       https://altair-viz.github.io/user_guide/interactions.html#inline-expressions
    .. _vega expression:
       https://vega.github.io/vega/docs/expressions/

    Examples
    --------
    >>> import altair as alt

    >>> bind_range = alt.binding_range(min=100, max=300, name="Slider value:  ")
    >>> param_width = alt.param(bind=bind_range, name="param_width")
    >>> param_color = alt.param(
    ...     expr=alt.expr.if_(param_width < 200, "red", "black"),
    ...     name="param_color",
    ... )
    >>> y = alt.Y("yval").axis(titleColor=param_color)

    >>> y
    Y({
      axis: {'titleColor': Parameter('param_color', VariableParameter({
        expr: if((param_width < 200),'red','black'),
        name: 'param_color'
      }))},
      shorthand: 'yval'
    })

    .. _Number.isNaN:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isNan
    .. _Number.isFinite:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isFinite
    .. _Math.abs:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/abs
    .. _Math.acos:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/acos
    .. _Math.asin:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/asin
    .. _Math.atan:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/atan
    .. _Math.atan2:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/atan2
    .. _Math.ceil:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/ceil
    .. _Math.cos:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/cos
    .. _Math.exp:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/exp
    .. _Math.floor:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/floor
    .. _Math.hypot:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/hypot
    .. _Math.log:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log
    .. _Math.max:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/max
    .. _Math.min:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/min
    .. _Math.pow:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/pow
    .. _Math.random:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
    .. _Math.round:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/round
    .. _Math.sin:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sin
    .. _Math.sqrt:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sqrt
    .. _Math.tan:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/tan
    .. _normal (Gaussian) probability distribution:
       https://en.wikipedia.org/wiki/Normal_distribution
    .. _cumulative distribution function:
       https://en.wikipedia.org/wiki/Cumulative_distribution_function
    .. _probability density function:
       https://en.wikipedia.org/wiki/Probability_density_function
    .. _log-normal probability distribution:
       https://en.wikipedia.org/wiki/Log-normal_distribution
    .. _continuous uniform probability distribution:
       https://en.wikipedia.org/wiki/Continuous_uniform_distribution
    .. _*unit*:
       https://vega.github.io/vega/docs/api/time/#time-units
    .. _JavaScript's String.replace:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/replace
    .. _d3-format specifier:
       https://github.com/d3/d3-format/
    .. _*units*:
       https://vega.github.io/vega/docs/api/time/#time-units
    .. _timeUnitSpecifier API documentation:
       https://vega.github.io/vega/docs/api/time/#timeUnitSpecifier
    .. _timeFormat:
       https://vega.github.io/vega/docs/expressions/#timeFormat
    .. _utcFormat:
       https://vega.github.io/vega/docs/expressions/#utcFormat
    .. _d3-time-format specifier:
       https://github.com/d3/d3-time-format/
    .. _TimeMultiFormat object:
       https://vega.github.io/vega/docs/types/#TimeMultiFormat
    .. _UTC:
       https://en.wikipedia.org/wiki/Coordinated_Universal_Time
    .. _JavaScript's RegExp:
       https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp
    .. _RGB:
       https://en.wikipedia.org/wiki/RGB_color_model
    .. _d3-color's rgb function:
       https://github.com/d3/d3-color#rgb
    .. _HSL:
       https://en.wikipedia.org/wiki/HSL_and_HSV
    .. _d3-color's hsl function:
       https://github.com/d3/d3-color#hsl
    .. _CIE LAB:
       https://en.wikipedia.org/wiki/Lab_color_space#CIELAB
    .. _d3-color's lab function:
       https://github.com/d3/d3-color#lab
    .. _HCL:
       https://en.wikipedia.org/wiki/Lab_color_space#CIELAB
    .. _d3-color's hcl function:
       https://github.com/d3/d3-color#hcl
    .. _W3C Web Content Accessibility Guidelines:
       https://www.w3.org/TR/2008/REC-WCAG20-20081211/#contrast-ratiodef
    .. _continuous color scheme:
       https://vega.github.io/vega/docs/schemes
    .. _geoArea:
       https://github.com/d3/d3-geo#geoArea
    .. _path.area:
       https://github.com/d3/d3-geo#path_area
    .. _geoBounds:
       https://github.com/d3/d3-geo#geoBounds
    .. _path.bounds:
       https://github.com/d3/d3-geo#path_bounds
    .. _geoCentroid:
       https://github.com/d3/d3-geo#geoCentroid
    .. _path.centroid:
       https://github.com/d3/d3-geo#path_centroid
    .. _window.screen:
       https://developer.mozilla.org/en-US/docs/Web/API/Window/screen
    """

    @override
    def __new__(cls: type[_ExprRef], expr: str) -> _ExprRef:  # type: ignore[misc]
        return _ExprRef(expr=expr)

    @classmethod
    def isArray(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is an array, false otherwise."""
        return FunctionExpression("isArray", (value,))

    @classmethod
    def isBoolean(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is a boolean (``true`` or ``false``), false otherwise."""
        return FunctionExpression("isBoolean", (value,))

    @classmethod
    def isDate(cls, value: IntoExpression, /) -> Expression:
        """
        Returns true if ``value`` is a Date object, false otherwise.

        This method will return false for timestamp numbers or date-formatted strings; it recognizes
        Date objects only.
        """
        return FunctionExpression("isDate", (value,))

    @classmethod
    def isDefined(cls, value: IntoExpression, /) -> Expression:
        """
        Returns true if ``value`` is a defined value, false if ``value`` equals ``undefined``.

        This method will return true for ``null`` and ``NaN`` values.
        """
        return FunctionExpression("isDefined", (value,))

    @classmethod
    def isNumber(cls, value: IntoExpression, /) -> Expression:
        """
        Returns true if ``value`` is a number, false otherwise.

        ``NaN`` and ``Infinity`` are considered numbers.
        """
        return FunctionExpression("isNumber", (value,))

    @classmethod
    def isObject(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is an object (including arrays and Dates), false otherwise."""
        return FunctionExpression("isObject", (value,))

    @classmethod
    def isRegExp(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is a RegExp (regular expression) object, false otherwise."""
        return FunctionExpression("isRegExp", (value,))

    @classmethod
    def isString(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is a string, false otherwise."""
        return FunctionExpression("isString", (value,))

    @classmethod
    def isValid(cls, value: IntoExpression, /) -> Expression:
        """Returns true if ``value`` is not ``null``, ``undefined``, or ``NaN``, false otherwise."""
        return FunctionExpression("isValid", (value,))

    @classmethod
    def toBoolean(cls, value: IntoExpression, /) -> Expression:
        """
        Coerces the input ``value`` to a string.

        Null values and empty strings are mapped to ``null``.
        """
        return FunctionExpression("toBoolean", (value,))

    @classmethod
    def toDate(cls, value: IntoExpression, /) -> Expression:
        """
        Coerces the input ``value`` to a Date instance.

        Null values and empty strings are mapped to ``null``. If an optional *parser* function is
        provided, it is used to perform date parsing, otherwise ``Date.parse`` is used. Be aware
        that ``Date.parse`` has different implementations across browsers!
        """
        return FunctionExpression("toDate", (value,))

    @classmethod
    def toNumber(cls, value: IntoExpression, /) -> Expression:
        """
        Coerces the input ``value`` to a number.

        Null values and empty strings are mapped to ``null``.
        """
        return FunctionExpression("toNumber", (value,))

    @classmethod
    def toString(cls, value: IntoExpression, /) -> Expression:
        """
        Coerces the input ``value`` to a string.

        Null values and empty strings are mapped to ``null``.
        """
        return FunctionExpression("toString", (value,))

    @classmethod
    def if_(
        cls,
        test: IntoExpression,
        thenValue: IntoExpression,
        elseValue: IntoExpression,
        /,
    ) -> Expression:
        """
        If ``test`` is truthy, returns ``thenValue``.

        Otherwise, returns ``elseValue``. The *if* function is equivalent to the ternary operator
        ``a ? b : c``.
        """
        return FunctionExpression("if", (test, thenValue, elseValue))

    @classmethod
    def isNaN(cls, value: IntoExpression, /) -> Expression:
        """
        Returns true if ``value`` is not a number.

        Same as JavaScript's `Number.isNaN`_.

        .. _Number.isNaN:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isNan
        """
        return FunctionExpression("isNaN", (value,))

    @classmethod
    def isFinite(cls, value: IntoExpression, /) -> Expression:
        """
        Returns true if ``value`` is a finite number.

        Same as JavaScript's `Number.isFinite`_.

        .. _Number.isFinite:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isFinite
        """
        return FunctionExpression("isFinite", (value,))

    @classmethod
    def abs(cls, value: IntoExpression, /) -> Expression:
        """
        Returns the absolute value of ``value``.

        Same as JavaScript's `Math.abs`_.

        .. _Math.abs:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/abs
        """
        return FunctionExpression("abs", (value,))

    @classmethod
    def acos(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric arccosine.

        Same as JavaScript's `Math.acos`_.

        .. _Math.acos:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/acos
        """
        return FunctionExpression("acos", (value,))

    @classmethod
    def asin(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric arcsine.

        Same as JavaScript's `Math.asin`_.

        .. _Math.asin:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/asin
        """
        return FunctionExpression("asin", (value,))

    @classmethod
    def atan(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric arctangent.

        Same as JavaScript's `Math.atan`_.

        .. _Math.atan:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/atan
        """
        return FunctionExpression("atan", (value,))

    @classmethod
    def atan2(cls, dy: IntoExpression, dx: IntoExpression, /) -> Expression:
        """
        Returns the arctangent of *dy / dx*.

        Same as JavaScript's `Math.atan2`_.

        .. _Math.atan2:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/atan2
        """
        return FunctionExpression("atan2", (dy, dx))

    @classmethod
    def ceil(cls, value: IntoExpression, /) -> Expression:
        """
        Rounds ``value`` to the nearest integer of equal or greater value.

        Same as JavaScript's `Math.ceil`_.

        .. _Math.ceil:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/ceil
        """
        return FunctionExpression("ceil", (value,))

    @classmethod
    def clamp(
        cls, value: IntoExpression, min: IntoExpression, max: IntoExpression, /
    ) -> Expression:
        """Restricts ``value`` to be between the specified ``min`` and ``max``."""
        return FunctionExpression("clamp", (value, min, max))

    @classmethod
    def cos(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric cosine.

        Same as JavaScript's `Math.cos`_.

        .. _Math.cos:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/cos
        """
        return FunctionExpression("cos", (value,))

    @classmethod
    def exp(cls, exponent: IntoExpression, /) -> Expression:
        """
        Returns the value of *e* raised to the provided ``exponent``.

        Same as JavaScript's `Math.exp`_.

        .. _Math.exp:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/exp
        """
        return FunctionExpression("exp", (exponent,))

    @classmethod
    def floor(cls, value: IntoExpression, /) -> Expression:
        """
        Rounds ``value`` to the nearest integer of equal or lower value.

        Same as JavaScript's `Math.floor`_.

        .. _Math.floor:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/floor
        """
        return FunctionExpression("floor", (value,))

    @classmethod
    def hypot(cls, value: IntoExpression, /) -> Expression:
        """
        Returns the square root of the sum of squares of its arguments.

        Same as JavaScript's `Math.hypot`_.

        .. _Math.hypot:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/hypot
        """
        return FunctionExpression("hypot", (value,))

    @classmethod
    def log(cls, value: IntoExpression, /) -> Expression:
        """
        Returns the natural logarithm of ``value``.

        Same as JavaScript's `Math.log`_.

        .. _Math.log:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/log
        """
        return FunctionExpression("log", (value,))

    @classmethod
    def max(
        cls, value1: IntoExpression, value2: IntoExpression, *args: Any
    ) -> Expression:
        """
        Returns the maximum argument value.

        Same as JavaScript's `Math.max`_.

        .. _Math.max:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/max
        """
        return FunctionExpression("max", (value1, value2, *args))

    @classmethod
    def min(
        cls, value1: IntoExpression, value2: IntoExpression, *args: Any
    ) -> Expression:
        """
        Returns the minimum argument value.

        Same as JavaScript's `Math.min`_.

        .. _Math.min:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/min
        """
        return FunctionExpression("min", (value1, value2, *args))

    @classmethod
    def pow(cls, value: IntoExpression, exponent: IntoExpression, /) -> Expression:
        """
        Returns ``value`` raised to the given ``exponent``.

        Same as JavaScript's `Math.pow`_.

        .. _Math.pow:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/pow
        """
        return FunctionExpression("pow", (value, exponent))

    @classmethod
    def random(cls) -> Expression:
        """
        Returns a pseudo-random number in the range [0,1).

        Same as JavaScript's `Math.random`_.

        .. _Math.random:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/random
        """
        return FunctionExpression("random", ())

    @classmethod
    def round(cls, value: IntoExpression, /) -> Expression:
        """
        Rounds ``value`` to the nearest integer.

        Same as JavaScript's `Math.round`_.

        .. _Math.round:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/round
        """
        return FunctionExpression("round", (value,))

    @classmethod
    def sin(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric sine.

        Same as JavaScript's `Math.sin`_.

        .. _Math.sin:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sin
        """
        return FunctionExpression("sin", (value,))

    @classmethod
    def sqrt(cls, value: IntoExpression, /) -> Expression:
        """
        Square root function.

        Same as JavaScript's `Math.sqrt`_.

        .. _Math.sqrt:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sqrt
        """
        return FunctionExpression("sqrt", (value,))

    @classmethod
    def tan(cls, value: IntoExpression, /) -> Expression:
        """
        Trigonometric tangent.

        Same as JavaScript's `Math.tan`_.

        .. _Math.tan:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/tan
        """
        return FunctionExpression("tan", (value,))

    @classmethod
    def sampleNormal(
        cls, mean: IntoExpression = None, stdev: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a sample from a univariate `normal (Gaussian) probability distribution`_ with specified ``mean`` and standard deviation ``stdev``.

        If unspecified, the mean defaults to ``0`` and the standard deviation defaults to ``1``.

        .. _normal (Gaussian) probability distribution:
            https://en.wikipedia.org/wiki/Normal_distribution
        """
        return FunctionExpression("sampleNormal", (mean, stdev))

    @classmethod
    def cumulativeNormal(
        cls,
        value: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `cumulative distribution function`_ at the given input domain ``value`` for a normal distribution with specified ``mean`` and standard deviation ``stdev``.

        If unspecified, the mean defaults to ``0`` and the standard deviation defaults to ``1``.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("cumulativeNormal", (value, mean, stdev))

    @classmethod
    def densityNormal(
        cls,
        value: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `probability density function`_ at the given input domain ``value``, for a normal distribution with specified ``mean`` and standard deviation ``stdev``.

        If unspecified, the mean defaults to ``0`` and the standard deviation defaults to ``1``.

        .. _probability density function:
            https://en.wikipedia.org/wiki/Probability_density_function
        """
        return FunctionExpression("densityNormal", (value, mean, stdev))

    @classmethod
    def quantileNormal(
        cls,
        probability: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the quantile value (the inverse of the `cumulative distribution function`_) for the given input ``probability``, for a normal distribution with specified ``mean`` and standard deviation ``stdev``.

        If unspecified, the mean defaults to ``0`` and the standard deviation defaults to ``1``.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("quantileNormal", (probability, mean, stdev))

    @classmethod
    def sampleLogNormal(
        cls, mean: IntoExpression = None, stdev: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a sample from a univariate `log-normal probability distribution`_ with specified log ``mean`` and log standard deviation ``stdev``.

        If unspecified, the log mean defaults to ``0`` and the log standard deviation defaults to
        ``1``.

        .. _log-normal probability distribution:
            https://en.wikipedia.org/wiki/Log-normal_distribution
        """
        return FunctionExpression("sampleLogNormal", (mean, stdev))

    @classmethod
    def cumulativeLogNormal(
        cls,
        value: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `cumulative distribution function`_ at the given input domain ``value`` for a log-normal distribution with specified log ``mean`` and log standard deviation ``stdev``.

        If unspecified, the log mean defaults to ``0`` and the log standard deviation defaults to
        ``1``.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("cumulativeLogNormal", (value, mean, stdev))

    @classmethod
    def densityLogNormal(
        cls,
        value: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `probability density function`_ at the given input domain ``value``, for a log-normal distribution with specified log ``mean`` and log standard deviation ``stdev``.

        If unspecified, the log mean defaults to ``0`` and the log standard deviation defaults to
        ``1``.

        .. _probability density function:
            https://en.wikipedia.org/wiki/Probability_density_function
        """
        return FunctionExpression("densityLogNormal", (value, mean, stdev))

    @classmethod
    def quantileLogNormal(
        cls,
        probability: IntoExpression,
        mean: IntoExpression = None,
        stdev: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the quantile value (the inverse of the `cumulative distribution function`_) for the given input ``probability``, for a log-normal distribution with specified log ``mean`` and log standard deviation ``stdev``.

        If unspecified, the log mean defaults to ``0`` and the log standard deviation defaults to
        ``1``.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("quantileLogNormal", (probability, mean, stdev))

    @classmethod
    def sampleUniform(
        cls, min: IntoExpression = None, max: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a sample from a univariate `continuous uniform probability distribution`_ over the interval [``min``, ``max``).

        If unspecified, ``min`` defaults to ``0`` and ``max`` defaults to ``1``. If only one
        argument is provided, it is interpreted as the ``max`` value.

        .. _continuous uniform probability distribution:
            https://en.wikipedia.org/wiki/Continuous_uniform_distribution
        """
        return FunctionExpression("sampleUniform", (min, max))

    @classmethod
    def cumulativeUniform(
        cls,
        value: IntoExpression,
        min: IntoExpression = None,
        max: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `cumulative distribution function`_ at the given input domain ``value`` for a uniform distribution over the interval [``min``, ``max``).

        If unspecified, ``min`` defaults to ``0`` and ``max`` defaults to ``1``. If only one
        argument is provided, it is interpreted as the ``max`` value.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("cumulativeUniform", (value, min, max))

    @classmethod
    def densityUniform(
        cls,
        value: IntoExpression,
        min: IntoExpression = None,
        max: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the value of the `probability density function`_ at the given input domain ``value``,  for a uniform distribution over the interval [``min``, ``max``).

        If unspecified, ``min`` defaults to ``0`` and ``max`` defaults to ``1``. If only one
        argument is provided, it is interpreted as the ``max`` value.

        .. _probability density function:
            https://en.wikipedia.org/wiki/Probability_density_function
        """
        return FunctionExpression("densityUniform", (value, min, max))

    @classmethod
    def quantileUniform(
        cls,
        probability: IntoExpression,
        min: IntoExpression = None,
        max: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the quantile value (the inverse of the `cumulative distribution function`_) for the given input ``probability``,  for a uniform distribution over the interval [``min``, ``max``).

        If unspecified, ``min`` defaults to ``0`` and ``max`` defaults to ``1``. If only one
        argument is provided, it is interpreted as the ``max`` value.

        .. _cumulative distribution function:
            https://en.wikipedia.org/wiki/Cumulative_distribution_function
        """
        return FunctionExpression("quantileUniform", (probability, min, max))

    @classmethod
    def now(cls) -> Expression:
        """Returns the timestamp for the current time."""
        return FunctionExpression("now", ())

    @classmethod
    def datetime(
        cls,
        year: IntoExpression,
        month: IntoExpression,
        day: IntoExpression = None,
        hour: IntoExpression = None,
        min: IntoExpression = None,
        sec: IntoExpression = None,
        millisec: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns a new ``Date`` instance.

        The ``month`` is 0-based, such that ``1`` represents February.
        """
        return FunctionExpression(
            "datetime", (year, month, day, hour, min, sec, millisec)
        )

    @classmethod
    def date(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the day of the month for the given ``datetime`` value, in local time."""
        return FunctionExpression("date", (datetime,))

    @classmethod
    def day(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the day of the week for the given ``datetime`` value, in local time."""
        return FunctionExpression("day", (datetime,))

    @classmethod
    def dayofyear(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the one-based day of the year for the given ``datetime`` value, in local time."""
        return FunctionExpression("dayofyear", (datetime,))

    @classmethod
    def year(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the year for the given ``datetime`` value, in local time."""
        return FunctionExpression("year", (datetime,))

    @classmethod
    def quarter(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the quarter of the year (0-3) for the given ``datetime`` value, in local time."""
        return FunctionExpression("quarter", (datetime,))

    @classmethod
    def month(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the (zero-based) month for the given ``datetime`` value, in local time."""
        return FunctionExpression("month", (datetime,))

    @classmethod
    def week(cls, date: IntoExpression, /) -> Expression:
        """
        Returns the week number of the year for the given *datetime*, in local time.

        This function assumes Sunday-based weeks. Days before the first Sunday of the year are
        considered to be in week 0, the first Sunday of the year is the start of week 1, the second
        Sunday week 2, *etc.*.
        """
        return FunctionExpression("week", (date,))

    @classmethod
    def hours(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the hours component for the given ``datetime`` value, in local time."""
        return FunctionExpression("hours", (datetime,))

    @classmethod
    def minutes(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the minutes component for the given ``datetime`` value, in local time."""
        return FunctionExpression("minutes", (datetime,))

    @classmethod
    def seconds(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the seconds component for the given ``datetime`` value, in local time."""
        return FunctionExpression("seconds", (datetime,))

    @classmethod
    def milliseconds(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the milliseconds component for the given ``datetime`` value, in local time."""
        return FunctionExpression("milliseconds", (datetime,))

    @classmethod
    def time(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the epoch-based timestamp for the given ``datetime`` value."""
        return FunctionExpression("time", (datetime,))

    @classmethod
    def timezoneoffset(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the timezone offset from the local timezone to UTC for the given ``datetime`` value."""
        return FunctionExpression("timezoneoffset", (datetime,))

    @classmethod
    def timeOffset(
        cls, unit: IntoExpression, date: IntoExpression, step: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a new ``Date`` instance that offsets the given ``date`` by the specified time `*unit*`_ in the local timezone.

        The optional ``step`` argument indicates the number of time unit steps to offset by (default
        1).

        .. _*unit*:
            https://vega.github.io/vega/docs/api/time/#time-units
        """
        return FunctionExpression("timeOffset", (unit, date, step))

    @classmethod
    def timeSequence(
        cls,
        unit: IntoExpression,
        start: IntoExpression,
        stop: IntoExpression,
        step: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns an array of ``Date`` instances from ``start`` (inclusive) to ``stop`` (exclusive), with each entry separated by the given time `*unit*`_ in the local timezone.

        The optional ``step`` argument indicates the number of time unit steps to take between each
        sequence entry (default 1).

        .. _*unit*:
            https://vega.github.io/vega/docs/api/time/#time-units
        """
        return FunctionExpression("timeSequence", (unit, start, stop, step))

    @classmethod
    def utc(
        cls,
        year: IntoExpression,
        month: IntoExpression,
        day: IntoExpression = None,
        hour: IntoExpression = None,
        min: IntoExpression = None,
        sec: IntoExpression = None,
        millisec: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns a timestamp for the given UTC date.

        The ``month`` is 0-based, such that ``1`` represents February.
        """
        return FunctionExpression("utc", (year, month, day, hour, min, sec, millisec))

    @classmethod
    def utcdate(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the day of the month for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcdate", (datetime,))

    @classmethod
    def utcday(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the day of the week for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcday", (datetime,))

    @classmethod
    def utcdayofyear(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the one-based day of the year for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcdayofyear", (datetime,))

    @classmethod
    def utcyear(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the year for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcyear", (datetime,))

    @classmethod
    def utcquarter(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the quarter of the year (0-3) for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcquarter", (datetime,))

    @classmethod
    def utcmonth(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the (zero-based) month for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcmonth", (datetime,))

    @classmethod
    def utcweek(cls, date: IntoExpression, /) -> Expression:
        """
        Returns the week number of the year for the given *datetime*, in UTC time.

        This function assumes Sunday-based weeks. Days before the first Sunday of the year are
        considered to be in week 0, the first Sunday of the year is the start of week 1, the second
        Sunday week 2, *etc.*.
        """
        return FunctionExpression("utcweek", (date,))

    @classmethod
    def utchours(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the hours component for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utchours", (datetime,))

    @classmethod
    def utcminutes(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the minutes component for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcminutes", (datetime,))

    @classmethod
    def utcseconds(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the seconds component for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcseconds", (datetime,))

    @classmethod
    def utcmilliseconds(cls, datetime: IntoExpression, /) -> Expression:
        """Returns the milliseconds component for the given ``datetime`` value, in UTC time."""
        return FunctionExpression("utcmilliseconds", (datetime,))

    @classmethod
    def utcOffset(
        cls, unit: IntoExpression, date: IntoExpression, step: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a new ``Date`` instance that offsets the given ``date`` by the specified time `*unit*`_ in UTC time.

        The optional ``step`` argument indicates the number of time unit steps to offset by (default
        1).

        .. _*unit*:
            https://vega.github.io/vega/docs/api/time/#time-units
        """
        return FunctionExpression("utcOffset", (unit, date, step))

    @classmethod
    def utcSequence(
        cls,
        unit: IntoExpression,
        start: IntoExpression,
        stop: IntoExpression,
        step: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns an array of ``Date`` instances from ``start`` (inclusive) to ``stop`` (exclusive), with each entry separated by the given time `*unit*`_ in UTC time.

        The optional ``step`` argument indicates the number of time unit steps to take between each
        sequence entry (default 1).

        .. _*unit*:
            https://vega.github.io/vega/docs/api/time/#time-units
        """
        return FunctionExpression("utcSequence", (unit, start, stop, step))

    @classmethod
    def extent(cls, array: IntoExpression, /) -> Expression:
        """Returns a new *[min, max]* array with the minimum and maximum values of the input array, ignoring ``null``, ``undefined``, and ``NaN`` values."""
        return FunctionExpression("extent", (array,))

    @classmethod
    def clampRange(
        cls, range: IntoExpression, min: IntoExpression, max: IntoExpression, /
    ) -> Expression:
        """
        Clamps a two-element ``range`` array in a span-preserving manner.

        If the span of the input ``range`` is less than *(max - min)* and an endpoint exceeds either
        the ``min`` or ``max`` value, the range is translated such that the span is preserved and
        one endpoint touches the boundary of the *[min, max]* range. If the span exceeds *(max -
        min)*, the range *[min, max]* is returned.
        """
        return FunctionExpression("clampRange", (range, min, max))

    @classmethod
    def indexof(cls, array: IntoExpression, value: IntoExpression, /) -> Expression:
        """Returns the first index of ``value`` in the input ``array``."""
        return FunctionExpression("indexof", (array, value))

    @classmethod
    def inrange(cls, value: IntoExpression, range: IntoExpression, /) -> Expression:
        """Tests whether ``value`` lies within (or is equal to either) the first and last values of the ``range`` array."""
        return FunctionExpression("inrange", (value, range))

    @classmethod
    def join(
        cls, array: IntoExpression, separator: IntoExpression = None, /
    ) -> Expression:
        """Returns a new string by concatenating all of the elements of the input ``array``, separated by commas or a specified ``separator`` string."""
        return FunctionExpression("join", (array, separator))

    @classmethod
    def lastindexof(cls, array: IntoExpression, value: IntoExpression, /) -> Expression:
        """Returns the last index of ``value`` in the input ``array``."""
        return FunctionExpression("lastindexof", (array, value))

    @classmethod
    def length(cls, array: IntoExpression, /) -> Expression:
        """Returns the length of the input ``array``."""
        return FunctionExpression("length", (array,))

    @classmethod
    def lerp(cls, array: IntoExpression, fraction: IntoExpression, /) -> Expression:
        """
        Returns the linearly interpolated value between the first and last entries in the ``array`` for the provided interpolation ``fraction`` (typically between 0 and 1).

        For example, ``alt.expr.lerp([0, 50], 0.5)`` returns 25.
        """
        return FunctionExpression("lerp", (array, fraction))

    @classmethod
    def peek(cls, array: IntoExpression, /) -> Expression:
        """
        Returns the last element in the input ``array``.

        Similar to the built-in ``Array.pop`` method, except that it does not remove the last
        element. This method is a convenient shorthand for ``array[array.length - 1]``.
        """
        return FunctionExpression("peek", (array,))

    @classmethod
    def pluck(cls, array: IntoExpression, field: IntoExpression, /) -> Expression:
        """
        Retrieves the value for the specified ``field`` from a given ``array`` of objects.

        The input ``field`` string may include nested properties (e.g., ``foo.bar.bz``).
        """
        return FunctionExpression("pluck", (array, field))

    @classmethod
    def reverse(cls, array: IntoExpression, /) -> Expression:
        """
        Returns a new array with elements in a reverse order of the input ``array``.

        The first array element becomes the last, and the last array element becomes the first.
        """
        return FunctionExpression("reverse", (array,))

    @classmethod
    def sequence(cls, *args: Any) -> Expression:
        """
        Returns an array containing an arithmetic sequence of numbers.

        If ``step`` is omitted, it defaults to 1. If ``start`` is omitted, it defaults to 0. The
        ``stop`` value is exclusive; it is not included in the result. If ``step`` is positive, the
        last element is the largest *start + i * step* less than ``stop``; if ``step`` is negative,
        the last element is the smallest *start + i * step* greater than ``stop``. If the returned
        array would contain an infinite number of values, an empty range is returned. The arguments
        are not required to be integers.
        """
        return FunctionExpression("sequence", args)

    @classmethod
    def slice(
        cls, array: IntoExpression, start: IntoExpression, end: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a section of ``array`` between the ``start`` and ``end`` indices.

        If the ``end`` argument is negative, it is treated as an offset from the end of the array
        (*alt.expr.length(array) + end*).
        """
        return FunctionExpression("slice", (array, start, end))

    @classmethod
    def span(cls, array: IntoExpression, /) -> Expression:
        """Returns the span of ``array``: the difference between the last and first elements, or *array[array.length-1] - array[0]*."""
        return FunctionExpression("span", (array,))

    @classmethod
    def lower(cls, string: IntoExpression, /) -> Expression:
        """Transforms ``string`` to lower-case letters."""
        return FunctionExpression("lower", (string,))

    @classmethod
    def pad(
        cls,
        string: IntoExpression,
        length: IntoExpression,
        character: IntoExpression = None,
        align: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Pads a ``string`` value with repeated instances of a ``character`` up to a specified ``length``.

        If ``character`` is not specified, a space (' ') is used. By default, padding is added to
        the end of a string. An optional ``align`` parameter specifies if padding should be added to
        the ``'left'`` (beginning), ``'center'``, or ``'right'`` (end) of the input string.
        """
        return FunctionExpression("pad", (string, length, character, align))

    @classmethod
    def parseFloat(cls, string: IntoExpression, /) -> Expression:
        """
        Parses the input ``string`` to a floating-point value.

        Same as JavaScript's ``parseFloat``.
        """
        return FunctionExpression("parseFloat", (string,))

    @classmethod
    def parseInt(cls, string: IntoExpression, /) -> Expression:
        """
        Parses the input ``string`` to an integer value.

        Same as JavaScript's ``parseInt``.
        """
        return FunctionExpression("parseInt", (string,))

    @classmethod
    def replace(
        cls,
        string: IntoExpression,
        pattern: IntoExpression,
        replacement: IntoExpression,
        /,
    ) -> Expression:
        """
        Returns a new string with some or all matches of ``pattern`` replaced by a ``replacement`` string.

        The ``pattern`` can be a string or a regular expression. If ``pattern`` is a string, only
        the first instance will be replaced. Same as `JavaScript's String.replace`_.

        .. _JavaScript's String.replace:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/replace
        """
        return FunctionExpression("replace", (string, pattern, replacement))

    @classmethod
    def substring(
        cls,
        string: IntoExpression,
        start: IntoExpression,
        end: IntoExpression = None,
        /,
    ) -> Expression:
        """Returns a section of ``string`` between the ``start`` and ``end`` indices."""
        return FunctionExpression("substring", (string, start, end))

    @classmethod
    def trim(cls, string: IntoExpression, /) -> Expression:
        """Returns a trimmed string with preceding and trailing whitespace removed."""
        return FunctionExpression("trim", (string,))

    @classmethod
    def truncate(
        cls,
        string: IntoExpression,
        length: IntoExpression,
        align: IntoExpression = None,
        ellipsis: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Truncates an input ``string`` to a target ``length``.

        The optional ``align`` argument indicates what part of the string should be truncated:
        ``'left'`` (the beginning), ``'center'``, or ``'right'`` (the end). By default, the
        ``'right'`` end of the string is truncated. The optional ``ellipsis`` argument indicates the
        string to use to indicate truncated content; by default the ellipsis character ``…``
        (``\u2026``) is used.
        """
        return FunctionExpression("truncate", (string, length, align, ellipsis))

    @classmethod
    def upper(cls, string: IntoExpression, /) -> Expression:
        """Transforms ``string`` to upper-case letters."""
        return FunctionExpression("upper", (string,))

    @classmethod
    def merge(
        cls, object1: IntoExpression, object2: IntoExpression = None, *args: Any
    ) -> Expression:
        """
        Merges the input objects ``object1``, ``object2``, etc into a new output object.

        Inputs are visited in sequential order, such that key values from later arguments can
        overwrite those from earlier arguments. Example: ``alt.expr.merge({a:1, b:2}, {a:3}) ->
        {a:3, b:2}``.
        """
        return FunctionExpression("merge", (object1, object2, *args))

    @classmethod
    def dayFormat(cls, day: IntoExpression, /) -> Expression:
        """
        Formats a (0-6) *weekday* number as a full week day name, according to the current locale.

        For example: ``alt.expr.dayFormat(0) -> "Sunday"``.
        """
        return FunctionExpression("dayFormat", (day,))

    @classmethod
    def dayAbbrevFormat(cls, day: IntoExpression, /) -> Expression:
        """
        Formats a (0-6) *weekday* number as an abbreviated week day name, according to the current locale.

        For example: ``alt.expr.dayAbbrevFormat(0) -> "Sun"``.
        """
        return FunctionExpression("dayAbbrevFormat", (day,))

    @classmethod
    def format(cls, value: IntoExpression, specifier: IntoExpression, /) -> Expression:
        """
        Formats a numeric ``value`` as a string.

        The ``specifier`` must be a valid `d3-format specifier`_ (e.g., ``alt.expr.format(value,
        ',.2f')``. Null values are formatted as ``"null"``.

        .. _d3-format specifier:
            https://github.com/d3/d3-format/
        """
        return FunctionExpression("format", (value, specifier))

    @classmethod
    def monthFormat(cls, month: IntoExpression, /) -> Expression:
        """
        Formats a (zero-based) ``month`` number as a full month name, according to the current locale.

        For example: ``alt.expr.monthFormat(0) -> "January"``.
        """
        return FunctionExpression("monthFormat", (month,))

    @classmethod
    def monthAbbrevFormat(cls, month: IntoExpression, /) -> Expression:
        """
        Formats a (zero-based) ``month`` number as an abbreviated month name, according to the current locale.

        For example: ``alt.expr.monthAbbrevFormat(0) -> "Jan"``.
        """
        return FunctionExpression("monthAbbrevFormat", (month,))

    @classmethod
    def timeUnitSpecifier(
        cls, units: IntoExpression, specifiers: IntoExpression = None, /
    ) -> Expression:
        """
        Returns a time format specifier string for the given time `*units*`_.

        The optional ``specifiers`` object provides a set of specifier sub-strings for customizing
        the format; for more, see the `timeUnitSpecifier API documentation`_. The resulting
        specifier string can then be used as input to the `timeFormat`_ or `utcFormat`_ functions,
        or as the *format* parameter of an axis or legend. For example: ``alt.expr.timeFormat(date,
        alt.expr.timeUnitSpecifier('year'))`` or ``alt.expr.timeFormat(date,
        alt.expr.timeUnitSpecifier(['hours', 'minutes']))``.

        .. _*units*:
            https://vega.github.io/vega/docs/api/time/#time-units
        .. _timeUnitSpecifier API documentation:
            https://vega.github.io/vega/docs/api/time/#timeUnitSpecifier
        .. _timeFormat:
            https://vega.github.io/vega/docs/expressions/#timeFormat
        .. _utcFormat:
            https://vega.github.io/vega/docs/expressions/#utcFormat
        """
        return FunctionExpression("timeUnitSpecifier", (units, specifiers))

    @classmethod
    def timeFormat(
        cls, value: IntoExpression, specifier: IntoExpression, /
    ) -> Expression:
        """
        Formats a datetime ``value`` (either a ``Date`` object or timestamp) as a string, according to the local time.

        The ``specifier`` must be a valid `d3-time-format specifier`_ or `TimeMultiFormat object`_.
        For example: ``alt.expr.timeFormat(timestamp, '%A')``. Null values are formatted as
        ``"null"``.

        .. _d3-time-format specifier:
            https://github.com/d3/d3-time-format/
        .. _TimeMultiFormat object:
            https://vega.github.io/vega/docs/types/#TimeMultiFormat
        """
        return FunctionExpression("timeFormat", (value, specifier))

    @classmethod
    def timeParse(
        cls, string: IntoExpression, specifier: IntoExpression, /
    ) -> Expression:
        """
        Parses a ``string`` value to a Date object, according to the local time.

        The ``specifier`` must be a valid `d3-time-format specifier`_. For example:
        ``alt.expr.timeParse('June 30, 2015', '%B %d, %Y')``.

        .. _d3-time-format specifier:
            https://github.com/d3/d3-time-format/
        """
        return FunctionExpression("timeParse", (string, specifier))

    @classmethod
    def utcFormat(
        cls, value: IntoExpression, specifier: IntoExpression, /
    ) -> Expression:
        """
        Formats a datetime ``value`` (either a ``Date`` object or timestamp) as a string, according to `UTC`_ time.

        The ``specifier`` must be a valid `d3-time-format specifier`_ or `TimeMultiFormat object`_.
        For example: ``alt.expr.utcFormat(timestamp, '%A')``. Null values are formatted as
        ``"null"``.

        .. _UTC:
            https://en.wikipedia.org/wiki/Coordinated_Universal_Time
        .. _d3-time-format specifier:
            https://github.com/d3/d3-time-format/
        .. _TimeMultiFormat object:
            https://vega.github.io/vega/docs/types/#TimeMultiFormat
        """
        return FunctionExpression("utcFormat", (value, specifier))

    @classmethod
    def utcParse(
        cls, value: IntoExpression, specifier: IntoExpression, /
    ) -> Expression:
        """
        Parses a *string* value to a Date object, according to `UTC`_ time.

        The ``specifier`` must be a valid `d3-time-format specifier`_. For example:
        ``alt.expr.utcParse('June 30, 2015', '%B %d, %Y')``.

        .. _UTC:
            https://en.wikipedia.org/wiki/Coordinated_Universal_Time
        .. _d3-time-format specifier:
            https://github.com/d3/d3-time-format/
        """
        return FunctionExpression("utcParse", (value, specifier))

    @classmethod
    def regexp(
        cls, pattern: IntoExpression, flags: IntoExpression = None, /
    ) -> Expression:
        """
        Creates a regular expression instance from an input ``pattern`` string and optional ``flags``.

        Same as `JavaScript's RegExp`_.

        .. _JavaScript's RegExp:
            https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp
        """
        return FunctionExpression("regexp", (pattern, flags))

    @classmethod
    def test(
        cls, regexp: IntoExpression, string: IntoExpression = None, /
    ) -> Expression:
        r"""
        Evaluates a regular expression ``regexp`` against the input ``string``, returning ``true`` if the string matches the pattern, ``false`` otherwise.

        For example: ``alt.expr.test(/\\d{3}/, "32-21-9483") -> true``.
        """
        return FunctionExpression("test", (regexp, string))

    @classmethod
    def rgb(cls, *args: Any) -> Expression:
        """
        Constructs a new `RGB`_ color.

        If ``r``, ``g`` and ``b`` are specified, these represent the channel values of the returned
        color; an ``opacity`` may also be specified. If a CSS Color Module Level 3 *specifier*
        string is specified, it is parsed and then converted to the RGB color space. Uses
        `d3-color's rgb function`_.

        .. _RGB:
            https://en.wikipedia.org/wiki/RGB_color_model
        .. _d3-color's rgb function:
            https://github.com/d3/d3-color#rgb
        """
        return FunctionExpression("rgb", args)

    @classmethod
    def hsl(cls, *args: Any) -> Expression:
        """
        Constructs a new `HSL`_ color.

        If ``h``, ``s`` and ``l`` are specified, these represent the channel values of the returned
        color; an ``opacity`` may also be specified. If a CSS Color Module Level 3 *specifier*
        string is specified, it is parsed and then converted to the HSL color space. Uses
        `d3-color's hsl function`_.

        .. _HSL:
            https://en.wikipedia.org/wiki/HSL_and_HSV
        .. _d3-color's hsl function:
            https://github.com/d3/d3-color#hsl
        """
        return FunctionExpression("hsl", args)

    @classmethod
    def lab(cls, *args: Any) -> Expression:
        """
        Constructs a new `CIE LAB`_ color.

        If ``l``, ``a`` and ``b`` are specified, these represent the channel values of the returned
        color; an ``opacity`` may also be specified. If a CSS Color Module Level 3 *specifier*
        string is specified, it is parsed and then converted to the LAB color space. Uses
        `d3-color's lab function`_.

        .. _CIE LAB:
            https://en.wikipedia.org/wiki/Lab_color_space#CIELAB
        .. _d3-color's lab function:
            https://github.com/d3/d3-color#lab
        """
        return FunctionExpression("lab", args)

    @classmethod
    def hcl(cls, *args: Any) -> Expression:
        """
        Constructs a new `HCL`_ (hue, chroma, luminance) color.

        If ``h``, ``c`` and ``l`` are specified, these represent the channel values of the returned
        color; an ``opacity`` may also be specified. If a CSS Color Module Level 3 *specifier*
        string is specified, it is parsed and then converted to the HCL color space. Uses
        `d3-color's hcl function`_.

        .. _HCL:
            https://en.wikipedia.org/wiki/Lab_color_space#CIELAB
        .. _d3-color's hcl function:
            https://github.com/d3/d3-color#hcl
        """
        return FunctionExpression("hcl", args)

    @classmethod
    def luminance(cls, specifier: IntoExpression, /) -> Expression:
        """
        Returns the luminance for the given color ``specifier`` (compatible with `d3-color's rgb function`_).

        The luminance is calculated according to the `W3C Web Content Accessibility Guidelines`_.

        .. _d3-color's rgb function:
            https://github.com/d3/d3-color#rgb
        .. _W3C Web Content Accessibility Guidelines:
            https://www.w3.org/TR/2008/REC-WCAG20-20081211/#relativeluminancedef
        """
        return FunctionExpression("luminance", (specifier,))

    @classmethod
    def contrast(
        cls, specifier1: IntoExpression, specifier2: IntoExpression, /
    ) -> Expression:
        """
        Returns the contrast ratio between the input color specifiers as a float between 1 and 21.

        The contrast is calculated according to the `W3C Web Content Accessibility Guidelines`_.

        .. _W3C Web Content Accessibility Guidelines:
            https://www.w3.org/TR/2008/REC-WCAG20-20081211/#contrast-ratiodef
        """
        return FunctionExpression("contrast", (specifier1, specifier2))

    @classmethod
    def item(cls) -> Expression:
        """Returns the current scenegraph item that is the target of the event."""
        return FunctionExpression("item", ())

    @classmethod
    def group(cls, name: IntoExpression = None, /) -> Expression:
        """
        Returns the scenegraph group mark item in which the current event has occurred.

        If no arguments are provided, the immediate parent group is returned. If a group name is
        provided, the matching ancestor group item is returned.
        """
        return FunctionExpression("group", (name,))

    @classmethod
    def xy(cls, item: IntoExpression = None, /) -> Expression:
        """
        Returns the x- and y-coordinates for the current event as a two-element array.

        If no arguments are provided, the top-level coordinate space of the view is used. If a
        scenegraph ``item`` (or string group name) is provided, the coordinate space of the group
        item is used.
        """
        return FunctionExpression("xy", (item,))

    @classmethod
    def x(cls, item: IntoExpression = None, /) -> Expression:
        """
        Returns the x coordinate for the current event.

        If no arguments are provided, the top-level coordinate space of the view is used. If a
        scenegraph ``item`` (or string group name) is provided, the coordinate space of the group
        item is used.
        """
        return FunctionExpression("x", (item,))

    @classmethod
    def y(cls, item: IntoExpression = None, /) -> Expression:
        """
        Returns the y coordinate for the current event.

        If no arguments are provided, the top-level coordinate space of the view is used. If a
        scenegraph ``item`` (or string group name) is provided, the coordinate space of the group
        item is used.
        """
        return FunctionExpression("y", (item,))

    @classmethod
    def pinchDistance(cls, event: IntoExpression, /) -> Expression:
        """Returns the pixel distance between the first two touch points of a multi-touch event."""
        return FunctionExpression("pinchDistance", (event,))

    @classmethod
    def pinchAngle(cls, event: IntoExpression, /) -> Expression:
        """Returns the angle of the line connecting the first two touch points of a multi-touch event."""
        return FunctionExpression("pinchAngle", (event,))

    @classmethod
    def inScope(cls, item: IntoExpression, /) -> Expression:
        """Returns true if the given scenegraph ``item`` is a descendant of the group mark in which the event handler was defined, false otherwise."""
        return FunctionExpression("inScope", (item,))

    @classmethod
    def data(cls, name: IntoExpression, /) -> Expression:
        """
        Returns the array of data objects for the Vega data set with the given ``name``.

        If the data set is not found, returns an empty array.
        """
        return FunctionExpression("data", (name,))

    @classmethod
    def indata(
        cls, name: IntoExpression, field: IntoExpression, value: IntoExpression, /
    ) -> Expression:
        """
        Tests if the data set with a given ``name`` contains a datum with a ``field`` value that matches the input ``value``.

        For example: ``alt.expr.indata('table', 'category', value)``.
        """
        return FunctionExpression("indata", (name, field, value))

    @classmethod
    def scale(
        cls,
        name: IntoExpression,
        value: IntoExpression,
        group: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Applies the named scale transform (or projection) to the specified ``value``.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale or projection.
        """
        return FunctionExpression("scale", (name, value, group))

    @classmethod
    def invert(
        cls,
        name: IntoExpression,
        value: IntoExpression,
        group: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Inverts the named scale transform (or projection) for the specified ``value``.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale or projection.
        """
        return FunctionExpression("invert", (name, value, group))

    @classmethod
    def copy(cls, name: IntoExpression, group: IntoExpression = None, /) -> Expression:  # type: ignore[override]
        """
        Returns a copy (a new cloned instance) of the named scale transform of projection, or ``undefined`` if no scale or projection is found.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale or projection.
        """
        return FunctionExpression("copy", (name, group))

    @classmethod
    def domain(
        cls, name: IntoExpression, group: IntoExpression = None, /
    ) -> Expression:
        """
        Returns the scale domain array for the named scale transform, or an empty array if the scale is not found.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale.
        """
        return FunctionExpression("domain", (name, group))

    @classmethod
    def range(cls, name: IntoExpression, group: IntoExpression = None, /) -> Expression:
        """
        Returns the scale range array for the named scale transform, or an empty array if the scale is not found.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale.
        """
        return FunctionExpression("range", (name, group))

    @classmethod
    def bandwidth(
        cls, name: IntoExpression, group: IntoExpression = None, /
    ) -> Expression:
        """
        Returns the current band width for the named band scale transform, or zero if the scale is not found or is not a band scale.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the scale.
        """
        return FunctionExpression("bandwidth", (name, group))

    @classmethod
    def bandspace(
        cls,
        count: IntoExpression,
        paddingInner: IntoExpression = None,
        paddingOuter: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the number of steps needed within a band scale, based on the ``count`` of domain elements and the inner and outer padding values.

        While normally calculated within the scale itself, this function can be helpful for
        determining the size of a chart's layout.
        """
        return FunctionExpression("bandspace", (count, paddingInner, paddingOuter))

    @classmethod
    def gradient(
        cls,
        scale: IntoExpression,
        p0: IntoExpression,
        p1: IntoExpression,
        count: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns a linear color gradient for the ``scale`` (whose range must be a `continuous color scheme`_) and starting and ending points ``p0`` and ``p1``, each an *[x, y]* array.

        The points ``p0`` and ``p1`` should be expressed in normalized coordinates in the domain [0,
        1], relative to the bounds of the item being colored. If unspecified, ``p0`` defaults to
        ``[0, 0]`` and ``p1`` defaults to ``[1, 0]``, for a horizontal gradient that spans the full
        bounds of an item. The optional ``count`` argument indicates a desired target number of
        sample points to take from the color scale.

        .. _continuous color scheme:
            https://vega.github.io/vega/docs/schemes
        """
        return FunctionExpression("gradient", (scale, p0, p1, count))

    @classmethod
    def panLinear(cls, domain: IntoExpression, delta: IntoExpression, /) -> Expression:
        """
        Given a linear scale ``domain`` array with numeric or datetime values, returns a new two-element domain array that is the result of panning the domain by a fractional ``delta``.

        The ``delta`` value represents fractional units of the scale range; for example, ``0.5``
        indicates panning the scale domain to the right by half the scale range.
        """
        return FunctionExpression("panLinear", (domain, delta))

    @classmethod
    def panLog(cls, domain: IntoExpression, delta: IntoExpression, /) -> Expression:
        """
        Given a log scale ``domain`` array with numeric or datetime values, returns a new two-element domain array that is the result of panning the domain by a fractional ``delta``.

        The ``delta`` value represents fractional units of the scale range; for example, ``0.5``
        indicates panning the scale domain to the right by half the scale range.
        """
        return FunctionExpression("panLog", (domain, delta))

    @classmethod
    def panPow(
        cls, domain: IntoExpression, delta: IntoExpression, exponent: IntoExpression, /
    ) -> Expression:
        """
        Given a power scale ``domain`` array with numeric or datetime values and the given ``exponent``, returns a new two-element domain array that is the result of panning the domain by a fractional ``delta``.

        The ``delta`` value represents fractional units of the scale range; for example, ``0.5``
        indicates panning the scale domain to the right by half the scale range.
        """
        return FunctionExpression("panPow", (domain, delta, exponent))

    @classmethod
    def panSymlog(
        cls, domain: IntoExpression, delta: IntoExpression, constant: IntoExpression, /
    ) -> Expression:
        """
        Given a symmetric log scale ``domain`` array with numeric or datetime values parameterized by the given ``constant``, returns a new two-element domain array that is the result of panning the domain by a fractional ``delta``.

        The ``delta`` value represents fractional units of the scale range; for example, ``0.5``
        indicates panning the scale domain to the right by half the scale range.
        """
        return FunctionExpression("panSymlog", (domain, delta, constant))

    @classmethod
    def zoomLinear(
        cls,
        domain: IntoExpression,
        anchor: IntoExpression,
        scaleFactor: IntoExpression,
        /,
    ) -> Expression:
        """
        Given a linear scale ``domain`` array with numeric or datetime values, returns a new two-element domain array that is the result of zooming the domain by a ``scaleFactor``, centered at the provided fractional ``anchor``.

        The ``anchor`` value represents the zoom position in terms of fractional units of the scale
        range; for example, ``0.5`` indicates a zoom centered on the mid-point of the scale range.
        """
        return FunctionExpression("zoomLinear", (domain, anchor, scaleFactor))

    @classmethod
    def zoomLog(
        cls,
        domain: IntoExpression,
        anchor: IntoExpression,
        scaleFactor: IntoExpression,
        /,
    ) -> Expression:
        """
        Given a log scale ``domain`` array with numeric or datetime values, returns a new two-element domain array that is the result of zooming the domain by a ``scaleFactor``, centered at the provided fractional ``anchor``.

        The ``anchor`` value represents the zoom position in terms of fractional units of the scale
        range; for example, ``0.5`` indicates a zoom centered on the mid-point of the scale range.
        """
        return FunctionExpression("zoomLog", (domain, anchor, scaleFactor))

    @classmethod
    def zoomPow(
        cls,
        domain: IntoExpression,
        anchor: IntoExpression,
        scaleFactor: IntoExpression,
        exponent: IntoExpression,
        /,
    ) -> Expression:
        """
        Given a power scale ``domain`` array with numeric or datetime values and the given ``exponent``, returns a new two-element domain array that is the result of zooming the domain by a ``scaleFactor``, centered at the provided fractional ``anchor``.

        The ``anchor`` value represents the zoom position in terms of fractional units of the scale
        range; for example, ``0.5`` indicates a zoom centered on the mid-point of the scale range.
        """
        return FunctionExpression("zoomPow", (domain, anchor, scaleFactor, exponent))

    @classmethod
    def zoomSymlog(
        cls,
        domain: IntoExpression,
        anchor: IntoExpression,
        scaleFactor: IntoExpression,
        constant: IntoExpression,
        /,
    ) -> Expression:
        """
        Given a symmetric log scale ``domain`` array with numeric or datetime values parameterized by the given ``constant``, returns a new two-element domain array that is the result of zooming the domain by a ``scaleFactor``, centered at the provided fractional ``anchor``.

        The ``anchor`` value represents the zoom position in terms of fractional units of the scale
        range; for example, ``0.5`` indicates a zoom centered on the mid-point of the scale range.
        """
        return FunctionExpression("zoomSymlog", (domain, anchor, scaleFactor, constant))

    @classmethod
    def geoArea(
        cls,
        projection: IntoExpression,
        feature: IntoExpression,
        group: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the projected planar area (typically in square pixels) of a GeoJSON ``feature`` according to the named ``projection``.

        If the ``projection`` argument is ``null``, computes the spherical area in steradians using
        unprojected longitude, latitude coordinates. The optional ``group`` argument takes a
        scenegraph group mark item to indicate the specific scope in which to look up the
        projection. Uses d3-geo's `geoArea`_ and `path.area`_ methods.

        .. _geoArea:
            https://github.com/d3/d3-geo#geoArea
        .. _path.area:
            https://github.com/d3/d3-geo#path_area
        """
        return FunctionExpression("geoArea", (projection, feature, group))

    @classmethod
    def geoBounds(
        cls,
        projection: IntoExpression,
        feature: IntoExpression,
        group: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the projected planar bounding box (typically in pixels) for the specified GeoJSON ``feature``, according to the named ``projection``.

        The bounding box is represented by a two-dimensional array: [[*x₀*, *y₀*], [*x₁*, *y₁*]],
        where *x₀* is the minimum x-coordinate, *y₀* is the minimum y-coordinate, *x₁* is the
        maximum x-coordinate, and *y₁* is the maximum y-coordinate. If the ``projection`` argument
        is ``null``, computes the spherical bounding box using unprojected longitude, latitude
        coordinates. The optional ``group`` argument takes a scenegraph group mark item to indicate
        the specific scope in which to look up the projection. Uses d3-geo's `geoBounds`_ and
        `path.bounds`_ methods.

        .. _geoBounds:
            https://github.com/d3/d3-geo#geoBounds
        .. _path.bounds:
            https://github.com/d3/d3-geo#path_bounds
        """
        return FunctionExpression("geoBounds", (projection, feature, group))

    @classmethod
    def geoCentroid(
        cls,
        projection: IntoExpression,
        feature: IntoExpression,
        group: IntoExpression = None,
        /,
    ) -> Expression:
        """
        Returns the projected planar centroid (typically in pixels) for the specified GeoJSON ``feature``, according to the named ``projection``.

        If the ``projection`` argument is ``null``, computes the spherical centroid using
        unprojected longitude, latitude coordinates. The optional ``group`` argument takes a
        scenegraph group mark item to indicate the specific scope in which to look up the
        projection. Uses d3-geo's `geoCentroid`_ and `path.centroid`_ methods.

        .. _geoCentroid:
            https://github.com/d3/d3-geo#geoCentroid
        .. _path.centroid:
            https://github.com/d3/d3-geo#path_centroid
        """
        return FunctionExpression("geoCentroid", (projection, feature, group))

    @classmethod
    def geoScale(
        cls, projection: IntoExpression, group: IntoExpression = None, /
    ) -> Expression:
        """
        Returns the scale value for the named ``projection``.

        The optional ``group`` argument takes a scenegraph group mark item to indicate the specific
        scope in which to look up the projection.
        """
        return FunctionExpression("geoScale", (projection, group))

    @classmethod
    def treePath(
        cls, name: IntoExpression, source: IntoExpression, target: IntoExpression, /
    ) -> Expression:
        """
        For the hierarchy data set with the given ``name``, returns the shortest path through from the ``source`` node id to the ``target`` node id.

        The path starts at the ``source`` node, ascends to the least common ancestor of the
        ``source`` node and the ``target`` node, and then descends to the ``target`` node.
        """
        return FunctionExpression("treePath", (name, source, target))

    @classmethod
    def treeAncestors(cls, name: IntoExpression, node: IntoExpression, /) -> Expression:
        """For the hierarchy data set with the given ``name``, returns the array of ancestors nodes, starting with the input ``node``, then followed by each parent up to the root."""
        return FunctionExpression("treeAncestors", (name, node))

    @classmethod
    def containerSize(cls) -> Expression:
        """
        Returns the current CSS box size (``[el.clientWidth, el.clientHeight]``) of the parent DOM element that contains the Vega view.

        If there is no container element, returns ``[undefined, undefined]``.
        """
        return FunctionExpression("containerSize", ())

    @classmethod
    def screen(cls) -> Expression:
        """
        Returns the `window.screen`_ object, or ``{}`` if Vega is not running in a browser environment.

        .. _window.screen:
            https://developer.mozilla.org/en-US/docs/Web/API/Window/screen
        """
        return FunctionExpression("screen", ())

    @classmethod
    def windowSize(cls) -> Expression:
        """Returns the current window size (``[window.innerWidth, window.innerHeight]``) or ``[undefined, undefined]`` if Vega is not running in a browser environment."""
        return FunctionExpression("windowSize", ())

    @classmethod
    def warn(
        cls, value1: IntoExpression, value2: IntoExpression = None, *args: Any
    ) -> Expression:
        """
        Logs a warning message and returns the last argument.

        For the message to appear in the console, the visualization view must have the appropriate
        logging level set.
        """
        return FunctionExpression("warn", (value1, value2, *args))

    @classmethod
    def info(
        cls, value1: IntoExpression, value2: IntoExpression = None, *args: Any
    ) -> Expression:
        """
        Logs an informative message and returns the last argument.

        For the message to appear in the console, the visualization view must have the appropriate
        logging level set.
        """
        return FunctionExpression("info", (value1, value2, *args))

    @classmethod
    def debug(
        cls, value1: IntoExpression, value2: IntoExpression = None, *args: Any
    ) -> Expression:
        """
        Logs a debugging message and returns the last argument.

        For the message to appear in the console, the visualization view must have the appropriate
        logging level set.
        """
        return FunctionExpression("debug", (value1, value2, *args))


_ExprType = expr
# NOTE: Compatibility alias for previous type of `alt.expr`.
# `_ExprType` was not referenced in any internal imports/tests.
