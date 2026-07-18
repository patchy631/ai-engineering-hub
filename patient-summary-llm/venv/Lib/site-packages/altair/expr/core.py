from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Any, Literal, Union

from altair.utils import SchemaBase

if TYPE_CHECKING:
    import sys

    from altair.vegalite.v5.schema._typing import Map, PrimitiveValue_T

    if sys.version_info >= (3, 10):
        from typing import TypeAlias
    else:
        from typing_extensions import TypeAlias


class DatumType:
    """An object to assist in building Vega-Lite Expressions."""

    def __repr__(self) -> str:
        return "datum"

    def __getattr__(self, attr) -> GetAttrExpression:
        if attr.startswith("__") and attr.endswith("__"):
            raise AttributeError(attr)
        return GetAttrExpression("datum", attr)

    def __getitem__(self, attr) -> GetItemExpression:
        return GetItemExpression("datum", attr)

    def __call__(self, datum, **kwargs) -> dict[str, Any]:
        """Specify a datum for use in an encoding."""
        return dict(datum=datum, **kwargs)


datum = DatumType()


def _js_repr(val) -> str:
    """Return a javascript-safe string representation of val."""
    if val is True:
        return "true"
    elif val is False:
        return "false"
    elif val is None:
        return "null"
    elif isinstance(val, OperatorMixin):
        return val._to_expr()
    elif isinstance(val, dt.date):
        return _from_date_datetime(val)
    else:
        return repr(val)


def _from_date_datetime(obj: dt.date | dt.datetime, /) -> str:
    """
    Parse native `datetime.(date|datetime)` into a `datetime expression`_ string.

    **Month is 0-based**

    .. _datetime expression:
        https://vega.github.io/vega/docs/expressions/#datetime
    """
    fn_name: Literal["datetime", "utc"] = "datetime"
    args: tuple[int, ...] = obj.year, obj.month - 1, obj.day
    if isinstance(obj, dt.datetime):
        if tzinfo := obj.tzinfo:
            if tzinfo is dt.timezone.utc:
                fn_name = "utc"
            else:
                msg = (
                    f"Unsupported timezone {tzinfo!r}.\n"
                    "Only `'UTC'` or naive (local) datetimes are permitted.\n"
                    "See https://altair-viz.github.io/user_guide/generated/core/altair.DateTime.html"
                )
                raise TypeError(msg)
        us = obj.microsecond
        ms = us if us == 0 else us // 1_000
        args = *args, obj.hour, obj.minute, obj.second, ms
    return FunctionExpression(fn_name, args)._to_expr()


# Designed to work with Expression and VariableParameter
class OperatorMixin:
    def _to_expr(self) -> str:
        return repr(self)

    def _from_expr(self, expr) -> Any:
        return expr

    def __add__(self, other):
        comp_value = BinaryExpression("+", self, other)
        return self._from_expr(comp_value)

    def __radd__(self, other):
        comp_value = BinaryExpression("+", other, self)
        return self._from_expr(comp_value)

    def __sub__(self, other):
        comp_value = BinaryExpression("-", self, other)
        return self._from_expr(comp_value)

    def __rsub__(self, other):
        comp_value = BinaryExpression("-", other, self)
        return self._from_expr(comp_value)

    def __mul__(self, other):
        comp_value = BinaryExpression("*", self, other)
        return self._from_expr(comp_value)

    def __rmul__(self, other):
        comp_value = BinaryExpression("*", other, self)
        return self._from_expr(comp_value)

    def __truediv__(self, other):
        comp_value = BinaryExpression("/", self, other)
        return self._from_expr(comp_value)

    def __rtruediv__(self, other):
        comp_value = BinaryExpression("/", other, self)
        return self._from_expr(comp_value)

    __div__ = __truediv__

    __rdiv__ = __rtruediv__

    def __mod__(self, other):
        comp_value = BinaryExpression("%", self, other)
        return self._from_expr(comp_value)

    def __rmod__(self, other):
        comp_value = BinaryExpression("%", other, self)
        return self._from_expr(comp_value)

    def __pow__(self, other):
        # "**" Javascript operator is not supported in all browsers
        comp_value = FunctionExpression("pow", (self, other))
        return self._from_expr(comp_value)

    def __rpow__(self, other):
        # "**" Javascript operator is not supported in all browsers
        comp_value = FunctionExpression("pow", (other, self))
        return self._from_expr(comp_value)

    def __neg__(self):
        comp_value = UnaryExpression("-", self)
        return self._from_expr(comp_value)

    def __pos__(self):
        comp_value = UnaryExpression("+", self)
        return self._from_expr(comp_value)

    # comparison operators

    def __eq__(self, other):
        comp_value = BinaryExpression("===", self, other)
        return self._from_expr(comp_value)

    def __ne__(self, other):
        comp_value = BinaryExpression("!==", self, other)
        return self._from_expr(comp_value)

    def __gt__(self, other):
        comp_value = BinaryExpression(">", self, other)
        return self._from_expr(comp_value)

    def __lt__(self, other):
        comp_value = BinaryExpression("<", self, other)
        return self._from_expr(comp_value)

    def __ge__(self, other):
        comp_value = BinaryExpression(">=", self, other)
        return self._from_expr(comp_value)

    def __le__(self, other):
        comp_value = BinaryExpression("<=", self, other)
        return self._from_expr(comp_value)

    def __abs__(self):
        comp_value = FunctionExpression("abs", (self,))
        return self._from_expr(comp_value)

    # logical operators

    def __and__(self, other):
        comp_value = BinaryExpression("&&", self, other)
        return self._from_expr(comp_value)

    def __rand__(self, other):
        comp_value = BinaryExpression("&&", other, self)
        return self._from_expr(comp_value)

    def __or__(self, other):
        comp_value = BinaryExpression("||", self, other)
        return self._from_expr(comp_value)

    def __ror__(self, other):
        comp_value = BinaryExpression("||", other, self)
        return self._from_expr(comp_value)

    def __invert__(self):
        comp_value = UnaryExpression("!", self)
        return self._from_expr(comp_value)


class Expression(OperatorMixin, SchemaBase):
    """
    Expression.

    Base object for enabling build-up of Javascript expressions using
    a Python syntax. Calling ``repr(obj)`` will return a Javascript
    representation of the object and the operations it encodes.
    """

    _schema = {"type": "string"}

    def to_dict(self, *args, **kwargs):
        return repr(self)

    def __setattr__(self, attr, val) -> None:
        # We don't need the setattr magic defined in SchemaBase
        return object.__setattr__(self, attr, val)

    # item access
    def __getitem__(self, val):
        return GetItemExpression(self, val)


class UnaryExpression(Expression):
    def __init__(self, op, val) -> None:
        super().__init__(op=op, val=val)

    def __repr__(self):
        return f"({self.op}{_js_repr(self.val)})"


class BinaryExpression(Expression):
    def __init__(self, op, lhs, rhs) -> None:
        super().__init__(op=op, lhs=lhs, rhs=rhs)

    def __repr__(self):
        return f"({_js_repr(self.lhs)} {self.op} {_js_repr(self.rhs)})"


class FunctionExpression(Expression):
    def __init__(self, name, args) -> None:
        super().__init__(name=name, args=args)

    def __repr__(self):
        args = ",".join(_js_repr(arg) for arg in self.args)
        return f"{self.name}({args})"


class ConstExpression(Expression):
    def __init__(self, name) -> None:
        super().__init__(name=name)

    def __repr__(self) -> str:
        return str(self.name)


class GetAttrExpression(Expression):
    def __init__(self, group, name) -> None:
        super().__init__(group=group, name=name)

    def __repr__(self):
        return f"{self.group}.{self.name}"


class GetItemExpression(Expression):
    def __init__(self, group, name) -> None:
        super().__init__(group=group, name=name)

    def __repr__(self) -> str:
        return f"{self.group}[{self.name!r}]"


IntoExpression: TypeAlias = Union[
    "PrimitiveValue_T", dt.date, dt.datetime, OperatorMixin, "Map"
]
