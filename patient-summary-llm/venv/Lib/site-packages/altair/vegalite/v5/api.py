from __future__ import annotations

import functools
import hashlib
import io
import itertools
import json
import operator
import sys
import typing as t
import warnings
from collections.abc import Mapping, Sequence
from copy import deepcopy as _deepcopy
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, overload

import jsonschema
import narwhals.stable.v1 as nw

from altair import theme, utils
from altair.expr import core as _expr_core
from altair.utils import Optional, SchemaBase, Undefined
from altair.utils._vegafusion_data import (
    compile_with_vegafusion as _compile_with_vegafusion,
)
from altair.utils._vegafusion_data import using_vegafusion as _using_vegafusion
from altair.utils.data import DataType
from altair.utils.data import is_data_type as _is_data_type
from altair.utils.schemapi import ConditionLike, _TypeMap

from .compiler import vegalite_compilers
from .data import data_transformers
from .display import VEGA_VERSION, VEGAEMBED_VERSION, VEGALITE_VERSION, renderers
from .schema import SCHEMA_URL, channels, core, mixins
from .schema._typing import Map, PrimitiveValue_T, SingleDefUnitChannel_T, Temporal

if sys.version_info >= (3, 14):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
if sys.version_info >= (3, 12):
    from typing import Protocol, TypeAliasType, runtime_checkable
else:
    from typing_extensions import (  # noqa: F401
        Protocol,
        TypeAliasType,
        runtime_checkable,
    )
if sys.version_info >= (3, 11):
    from typing import LiteralString
else:
    from typing_extensions import LiteralString
if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    from pathlib import Path
    from typing import IO

    from altair.utils.core import DataFrameLike

    if sys.version_info >= (3, 13):
        from typing import Required, TypeIs
    else:
        from typing_extensions import Required, TypeIs
    if sys.version_info >= (3, 11):
        from typing import Never, Self
    else:
        from typing_extensions import Never, Self

    from altair.expr.core import (
        BinaryExpression,
        Expression,
        GetAttrExpression,
        GetItemExpression,
        IntoExpression,
    )
    from altair.utils.display import MimeBundleType

    from .schema._config import BrushConfigKwds, DerivedStreamKwds, MergedStreamKwds
    from .schema._typing import (
        AggregateOp_T,
        AutosizeType_T,
        ColorName_T,
        CompositeMark_T,
        ImputeMethod_T,
        LayoutAlign_T,
        Mark_T,
        MultiTimeUnit_T,
        OneOrSeq,
        ProjectionType_T,
        ResolveMode_T,
        SelectionResolution_T,
        SelectionType_T,
        SingleTimeUnit_T,
        StackOffset_T,
    )
    from .schema.channels import Column, Facet, Row
    from .schema.core import (
        AggregatedFieldDef,
        AggregateOp,
        AnyMark,
        BindCheckbox,
        Binding,
        BindInput,
        BindRadioSelect,
        BindRange,
        BinParams,
        BrushConfig,
        DateTime,
        Expr,
        ExprRef,
        FacetedEncoding,
        FacetFieldDef,
        FieldName,
        GraticuleGenerator,
        ImputeMethod,
        ImputeSequence,
        InlineData,
        InlineDataset,
        IntervalSelectionConfig,
        JoinAggregateFieldDef,
        LayerRepeatMapping,
        LookupSelection,
        NamedData,
        ParameterName,
        PointSelectionConfig,
        PredicateComposition,
        ProjectionType,
        RepeatMapping,
        RepeatRef,
        SelectionParameter,
        SequenceGenerator,
        SortField,
        SphereGenerator,
        Step,
        TimeUnit,
        TopLevelSelectionParameter,
        Transform,
        UrlData,
        VariableParameter,
        Vector2number,
        Vector2Vector2number,
        Vector3number,
        WindowFieldDef,
    )

__all__ = [
    "TOPLEVEL_ONLY_KEYS",
    "Bin",
    "ChainedWhen",
    "Chart",
    "ChartDataType",
    "ConcatChart",
    "DataType",
    "FacetChart",
    "FacetMapping",
    "HConcatChart",
    "Impute",
    "LayerChart",
    "LookupData",
    "Parameter",
    "ParameterExpression",
    "RepeatChart",
    "SelectionExpression",
    "SelectionPredicateComposition",
    "Then",
    "Title",
    "TopLevelMixin",
    "VConcatChart",
    "When",
    "binding",
    "binding_checkbox",
    "binding_radio",
    "binding_range",
    "binding_select",
    "check_fields_and_encodings",
    "concat",
    "condition",
    "graticule",
    "hconcat",
    "layer",
    "mixins",
    "param",
    "repeat",
    "selection",
    "selection_interval",
    "selection_multi",
    "selection_point",
    "selection_single",
    "sequence",
    "sphere",
    "topo_feature",
    "value",
    "vconcat",
    "when",
]

ChartDataType: TypeAlias = Optional[Union[DataType, core.Data, str, core.Generator]]
_TSchemaBase = TypeVar("_TSchemaBase", bound=SchemaBase)


# ------------------------------------------------------------------------
# Data Utilities
def _dataset_name(values: dict[str, Any] | list | InlineDataset) -> str:
    """
    Generate a unique hash of the data.

    Parameters
    ----------
    values : list, dict, core.InlineDataset
        A representation of data values.

    Returns
    -------
    name : string
        A unique name generated from the hash of the values.
    """
    if isinstance(values, core.InlineDataset):
        values = values.to_dict()
    if values == [{}]:
        return "empty"
    values_json = json.dumps(values, sort_keys=True, default=str)
    hsh = hashlib.sha256(values_json.encode()).hexdigest()[:32]
    return "data-" + hsh


def _consolidate_data(
    data: ChartDataType | UrlData, context: dict[str, Any]
) -> ChartDataType | NamedData | InlineData | UrlData:
    """
    If data is specified inline, then move it to context['datasets'].

    This function will modify context in-place, and return a new version of data
    """
    values: Any = Undefined
    kwds = {}

    if isinstance(data, core.InlineData):
        if utils.is_undefined(data.name) and not utils.is_undefined(data.values):
            if isinstance(data.values, core.InlineDataset):
                values = data.to_dict()["values"]
            else:
                values = data.values
            kwds = {"format": data.format}

    elif isinstance(data, dict) and "name" not in data and "values" in data:
        values = data["values"]
        kwds = {k: v for k, v in data.items() if k != "values"}

    if not utils.is_undefined(values):
        name = _dataset_name(values)
        data = core.NamedData(name=name, **kwds)
        context.setdefault("datasets", {})[name] = values

    return data


def _prepare_data(
    data: ChartDataType, context: dict[str, Any] | None = None
) -> ChartDataType | NamedData | InlineData | UrlData | Any:
    """
    Convert input data to data for use within schema.

    Parameters
    ----------
    data :
        The input dataset in the form of a DataFrame, dictionary, altair data
        object, or other type that is recognized by the data transformers.
    context : dict (optional)
        The to_dict context in which the data is being prepared. This is used
        to keep track of information that needs to be passed up and down the
        recursive serialization routine, such as global named datasets.
    """
    if data is Undefined:
        return data

    # convert dataframes  or objects with __geo_interface__ to dict
    elif not isinstance(data, dict) and _is_data_type(data):
        if func := data_transformers.get():
            data = func(nw.to_native(data, pass_through=True))

    # convert string input to a URLData
    elif isinstance(data, str):
        data = core.UrlData(data)

    # consolidate inline data to top-level datasets
    if context is not None and data_transformers.consolidate_datasets:
        data = _consolidate_data(data, context)

    # if data is still not a recognized type, then return
    if not isinstance(data, (dict, core.Data)):
        warnings.warn(f"data of type {type(data)} not recognized", stacklevel=1)

    return data


# ------------------------------------------------------------------------
# Aliases & specializations
Bin = core.BinParams
Impute = core.ImputeParams
Title = core.TitleParams


class LookupData(core.LookupData):
    @utils.use_signature(core.LookupData)
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def to_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """Convert the chart to a dictionary suitable for JSON export."""
        copy = self.copy(deep=False)
        copy.data = _prepare_data(copy.data, kwargs.get("context"))
        return super(LookupData, copy).to_dict(*args, **kwargs)


class FacetMapping(core.FacetMapping):
    """
    FacetMapping schema wrapper.

    Parameters
    ----------
    column : str, :class:`FacetFieldDef`, :class:`Column`
        A field definition for the horizontal facet of trellis plots.
    row : str, :class:`FacetFieldDef`, :class:`Row`
        A field definition for the vertical facet of trellis plots.
    """

    _class_is_valid_at_instantiation = False

    def __init__(
        self,
        column: Optional[str | FacetFieldDef | Column] = Undefined,
        row: Optional[str | FacetFieldDef | Row] = Undefined,
        **kwargs: Any,
    ) -> None:
        super().__init__(column=column, row=row, **kwargs)  # type: ignore[arg-type]

    def to_dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        copy = self.copy(deep=False)
        context = kwargs.get("context", {})
        data = context.get("data", None)
        if isinstance(self.row, str):
            copy.row = core.FacetFieldDef(**utils.parse_shorthand(self.row, data))
        if isinstance(self.column, str):
            copy.column = core.FacetFieldDef(**utils.parse_shorthand(self.column, data))
        return super(FacetMapping, copy).to_dict(*args, **kwargs)


# ------------------------------------------------------------------------
# Encoding will contain channel objects that aren't valid at instantiation
core.FacetedEncoding._class_is_valid_at_instantiation = False

# ------------------------------------------------------------------------
# These are parameters that are valid at the top level, but are not valid
# for specs that are within a composite chart
# (layer, hconcat, vconcat, facet, repeat)
TOPLEVEL_ONLY_KEYS = {"background", "config", "autosize", "padding", "$schema"}


# -------------------------------------------------------------------------
# Tools for working with parameters
class Parameter(_expr_core.OperatorMixin):
    """A Parameter object."""

    _schema: t.ClassVar[_TypeMap[Literal["object"]]] = {"type": "object"}
    _counter: int = 0

    @classmethod
    def _get_name(cls) -> str:
        cls._counter += 1
        return f"param_{cls._counter}"

    def __init__(
        self,
        name: str | None = None,
        empty: Optional[bool] = Undefined,
        param: Optional[
            VariableParameter | TopLevelSelectionParameter | SelectionParameter
        ] = Undefined,
        param_type: Optional[Literal["variable", "selection"]] = Undefined,
    ) -> None:
        if name is None:
            name = self._get_name()
        self.name = name
        self.empty = empty
        self.param = param
        self.param_type = param_type

    @utils.deprecated(
        version="5.0.0",
        alternative="to_dict",
        message="No need to call '.ref()' anymore.",
    )
    def ref(self) -> dict[str, Any]:
        """'ref' is deprecated. No need to call '.ref()' anymore."""
        return self.to_dict()

    def to_dict(self) -> dict[str, str | dict[str, Any]]:
        if self.param_type == "variable":
            return {"expr": self.name}
        elif self.param_type == "selection":
            nm: Any = self.name
            return {"param": nm.to_dict() if hasattr(nm, "to_dict") else nm}
        else:
            msg = f"Unrecognized parameter type: {self.param_type}"
            raise ValueError(msg)

    def __invert__(self) -> PredicateComposition | Any:
        if self.param_type == "selection":
            return core.PredicateComposition({"not": {"param": self.name}})
        else:
            return _expr_core.OperatorMixin.__invert__(self)

    def __and__(self, other: Any) -> PredicateComposition | Any:
        if self.param_type == "selection":
            if isinstance(other, Parameter):
                other = {"param": other.name}
            return core.PredicateComposition({"and": [{"param": self.name}, other]})
        else:
            return _expr_core.OperatorMixin.__and__(self, other)

    def __or__(self, other: Any) -> PredicateComposition | Any:
        if self.param_type == "selection":
            if isinstance(other, Parameter):
                other = {"param": other.name}
            return core.PredicateComposition({"or": [{"param": self.name}, other]})
        else:
            return _expr_core.OperatorMixin.__or__(self, other)

    def __repr__(self) -> str:
        return f"Parameter({self.name!r}, {self.param})"

    def _to_expr(self) -> str:
        return self.name

    def _from_expr(self, expr: IntoExpression) -> ParameterExpression:
        return ParameterExpression(expr=expr)

    def __getattr__(self, field_name: str) -> GetAttrExpression | SelectionExpression:
        if field_name.startswith("__") and field_name.endswith("__"):
            raise AttributeError(field_name)
        _attrexpr = _expr_core.GetAttrExpression(self.name, field_name)
        # If self is a SelectionParameter and field_name is in its
        # fields or encodings list, then we want to return an expression.
        if check_fields_and_encodings(self, field_name):
            return SelectionExpression(_attrexpr)
        return _expr_core.GetAttrExpression(self.name, field_name)

    # TODO: Are there any special cases to consider for __getitem__?
    # This was copied from v4.
    def __getitem__(self, field_name: str) -> GetItemExpression:
        return _expr_core.GetItemExpression(self.name, field_name)


# Enables use of ~, &, | with compositions of selection objects.
SelectionPredicateComposition = core.PredicateComposition


class ParameterExpression(_expr_core.OperatorMixin):
    _schema: t.ClassVar[_TypeMap[Literal["object"]]] = {"type": "object"}

    def __init__(self, expr: IntoExpression) -> None:
        self.expr = expr

    def to_dict(self) -> dict[str, str]:
        return {"expr": repr(self.expr)}

    def _to_expr(self) -> str:
        return repr(self.expr)

    def _from_expr(self, expr: IntoExpression) -> ParameterExpression:
        return ParameterExpression(expr=expr)


class SelectionExpression(_expr_core.OperatorMixin):
    _schema: t.ClassVar[_TypeMap[Literal["object"]]] = {"type": "object"}

    def __init__(self, expr: IntoExpression) -> None:
        self.expr = expr

    def to_dict(self) -> dict[str, str]:
        return {"expr": repr(self.expr)}

    def _to_expr(self) -> str:
        return repr(self.expr)

    def _from_expr(self, expr: IntoExpression) -> SelectionExpression:
        return SelectionExpression(expr=expr)


def check_fields_and_encodings(parameter: Parameter, field_name: str) -> bool:
    param = parameter.param
    if utils.is_undefined(param) or isinstance(param, core.VariableParameter):
        return False
    for prop in ["fields", "encodings"]:
        try:
            if field_name in getattr(param.select, prop):
                return True
        except (AttributeError, TypeError):
            pass

    return False


# -------------------------------------------------------------------------
# Tools for working with conditions
_TestPredicateType: TypeAlias = Union[
    str, _expr_core.Expression, core.PredicateComposition
]
"""https://vega.github.io/vega-lite/docs/predicate.html"""

_PredicateType: TypeAlias = Union[
    Parameter,
    core.Expr,
    "_ConditionExtra",
    _TestPredicateType,
    _expr_core.OperatorMixin,
]
"""Permitted types for `predicate`."""

_ComposablePredicateType: TypeAlias = Union[
    _expr_core.OperatorMixin, core.PredicateComposition
]
"""Permitted types for `&` reduced predicates."""

_StatementType: TypeAlias = Union[SchemaBase, Map, str]
"""Permitted types for `if_true`/`if_false`.

In python terms:
```py
if _PredicateType:
    return _StatementType
elif _PredicateType:
    return _StatementType
else:
    return _StatementType
```
"""


_FieldEqualType: TypeAlias = Union["IntoExpression", Parameter, SchemaBase]
"""
Permitted types for equality checks on field values.

Applies to the following context(s):

    import altair as alt

    alt.datum.field == ...
    alt.FieldEqualPredicate(field="field", equal=...)
    alt.when(field=...)
    alt.when().then().when(field=...)
    alt.Chart.transform_filter(field=...)
"""


def _is_test_predicate(obj: Any) -> TypeIs[_TestPredicateType]:
    return isinstance(obj, (str, _expr_core.Expression, core.PredicateComposition))


def _get_predicate_expr(p: Parameter) -> Optional[_TestPredicateType]:
    # https://vega.github.io/vega-lite/docs/predicate.html
    return getattr(p.param, "expr", Undefined)


def _predicate_to_condition(
    predicate: _PredicateType, *, empty: Optional[bool] = Undefined
) -> _Condition:
    condition: _Condition
    if isinstance(predicate, Parameter):
        predicate_expr = _get_predicate_expr(predicate)
        if predicate.param_type == "selection" or utils.is_undefined(predicate_expr):
            condition = {"param": predicate.name}
            if isinstance(empty, bool):
                condition["empty"] = empty
            elif isinstance(predicate.empty, bool):
                condition["empty"] = predicate.empty
        else:
            condition = {"test": predicate_expr}
    elif _is_test_predicate(predicate):
        condition = {"test": predicate}
    elif isinstance(predicate, dict):
        condition = predicate
    elif isinstance(predicate, _expr_core.OperatorMixin):
        condition = {"test": predicate._to_expr()}
    else:
        msg = (
            f"Expected a predicate, but got: {type(predicate).__name__!r}\n\n"
            f"From `predicate={predicate!r}`."
        )
        raise TypeError(msg)
    return condition


def _condition_to_selection(
    condition: _Condition,
    if_true: _StatementType,
    if_false: _StatementType,
    **kwargs: Any,
) -> SchemaBase | _Conditional[_Condition]:
    selection: SchemaBase | _Conditional[_Condition]
    if isinstance(if_true, SchemaBase):
        if_true = if_true.to_dict()
    elif isinstance(if_true, str):
        if isinstance(if_false, str):
            msg = (
                "A field cannot be used for both the `if_true` and `if_false` "
                "values of a condition. "
                "One of them has to specify a `value` or `datum` definition."
            )
            raise ValueError(msg)
        else:
            if_true = utils.parse_shorthand(if_true)
            if_true.update(kwargs)
    cond_mutable: Any = dict(condition)
    cond_mutable.update(if_true)
    if isinstance(if_false, SchemaBase):
        # For the selection, the channel definitions all allow selections
        # already. So use this SchemaBase wrapper if possible.
        selection = if_false.copy()
        selection.condition = cond_mutable
    elif isinstance(if_false, (str, dict)):
        if isinstance(if_false, str):
            if_false = utils.parse_shorthand(if_false)
            if_false.update(kwargs)
        selection = _Conditional(condition=cond_mutable, **if_false)  # type: ignore[typeddict-item]
    else:
        raise TypeError(if_false)
    return selection


class _ConditionExtra(TypedDict, closed=True, total=False):  # type: ignore[call-arg]
    # https://peps.python.org/pep-0728/
    # Likely a Field predicate
    empty: Optional[bool]
    param: Parameter | str
    test: _TestPredicateType
    value: Any
    __extra_items__: _StatementType | OneOrSeq[PrimitiveValue_T]


_Condition: TypeAlias = _ConditionExtra
"""
A singular, *possibly* non-chainable condition produced by ``.when()``.

The default **permissive** representation.

Allows arbitrary additional keys that *may* be present in a `Conditional Field`_
but not a `Conditional Value`_.

.. _Conditional Field:
    https://vega.github.io/vega-lite/docs/condition.html#field
.. _Conditional Value:
    https://vega.github.io/vega-lite/docs/condition.html#value
"""


class _ConditionClosed(TypedDict, closed=True, total=False):  # type: ignore[call-arg]
    # https://peps.python.org/pep-0728/
    # Parameter {"param", "value", "empty"}
    # Predicate {"test", "value"}
    empty: Optional[bool]
    param: Parameter | str
    test: _TestPredicateType
    value: Any


_Conditions: TypeAlias = list[_ConditionClosed]
"""
Chainable conditions produced by ``.when()`` and ``Then.when()``.

All must be a `Conditional Value`_.

.. _Conditional Value:
    https://vega.github.io/vega-lite/docs/condition.html#value
"""

_C = TypeVar("_C", _Conditions, _Condition)


class _Conditional(TypedDict, t.Generic[_C], total=False):
    """
    A dictionary representation of a conditional encoding or property.

    Parameters
    ----------
    condition
        One or more (predicate, statement) pairs which each form a condition.
    value
        An optional default value, used when no predicates were met.
    """

    condition: Required[_C]
    value: Any


IntoCondition: TypeAlias = Union[ConditionLike, _Conditional[Any]]
"""
Anything that can be converted into a conditional encoding or property.

Notes
-----
Represents all outputs from `when-then-otherwise` conditions, which are not ``SchemaBase`` types.
"""


class _Value(TypedDict, closed=True, total=False):  # type: ignore[call-arg]
    # https://peps.python.org/pep-0728/
    value: Required[Any]
    __extra_items__: Any


def _reveal_parsed_shorthand(obj: Map, /) -> dict[str, Any]:
    # Helper for producing error message on multiple field collision.
    return {k: v for k, v in obj.items() if k in utils.SHORTHAND_KEYS}


def _is_extra(*objs: Any, kwds: Map) -> Iterator[bool]:
    for el in objs:
        if isinstance(el, (SchemaBase, t.Mapping)):
            item = el.to_dict(validate=False) if isinstance(el, SchemaBase) else el
            yield not (item.keys() - kwds.keys()).isdisjoint(utils.SHORTHAND_KEYS)
        else:
            continue


def _is_condition_extra(obj: Any, *objs: Any, kwds: Map) -> TypeIs[_Condition]:
    # NOTE: Short circuits on the first conflict.
    # 1 - Originated from parse_shorthand
    # 2 - Used a wrapper or `dict` directly, including `extra_keys`
    return isinstance(obj, str) or any(_is_extra(obj, *objs, kwds=kwds))


def _is_condition_closed(obj: Map) -> TypeIs[_ConditionClosed]:
    """Return `True` if ``obj`` can be used in a chained condition."""
    return {"empty", "param", "test", "value"} >= obj.keys()


def _parse_when_constraints(
    constraints: dict[str, _FieldEqualType], /
) -> Iterator[BinaryExpression]:
    """
    Wrap kwargs with `alt.datum`.

    ```py
    # before
    alt.when(alt.datum.Origin == "Europe")

    # after
    alt.when(Origin="Europe")
    ```
    """
    for name, value in constraints.items():
        yield _expr_core.GetAttrExpression("datum", name) == value


def _validate_composables(
    predicates: Iterable[Any], /
) -> Iterator[_ComposablePredicateType]:
    for p in predicates:
        if isinstance(p, (_expr_core.OperatorMixin, core.PredicateComposition)):
            yield p
        else:
            msg = (
                f"Predicate composition is not permitted for "
                f"{type(p).__name__!r}.\n"
                f"Try wrapping {p!r} in a `Parameter` first."
            )
            raise TypeError(msg)


def _parse_when_compose(
    predicates: tuple[Any, ...],
    constraints: dict[str, _FieldEqualType],
    /,
) -> BinaryExpression:
    """
    Compose an `&` reduction predicate.

    Parameters
    ----------
    predicates
        Collected positional arguments.
    constraints
        Collected keyword arguments.

    Raises
    ------
    TypeError
        On the first non ``_ComposablePredicateType`` of `predicates`
    """
    iters = []
    if predicates:
        iters.append(_validate_composables(predicates))
    if constraints:
        iters.append(_parse_when_constraints(constraints))
    r = functools.reduce(operator.and_, itertools.chain.from_iterable(iters))
    return t.cast(_expr_core.BinaryExpression, r)


def _parse_when(
    predicate: Optional[_PredicateType],
    *more_predicates: _ComposablePredicateType,
    empty: Optional[bool],
    **constraints: _FieldEqualType,
) -> _Condition:
    composed: _PredicateType
    if utils.is_undefined(predicate):
        if more_predicates or constraints:
            composed = _parse_when_compose(more_predicates, constraints)
        else:
            msg = (
                f"At least one predicate or constraint must be provided, "
                f"but got: {predicate=}"
            )
            raise TypeError(msg)
    elif more_predicates or constraints:
        predicates = predicate, *more_predicates
        composed = _parse_when_compose(predicates, constraints)
    else:
        composed = predicate
    return _predicate_to_condition(composed, empty=empty)


def _parse_literal(val: Any, /) -> dict[str, Any]:
    if isinstance(val, str):
        return utils.parse_shorthand(val)
    else:
        msg = (
            f"Expected a shorthand `str`, but got: {type(val).__name__!r}\n\n"
            f"From `statement={val!r}`."
        )
        raise TypeError(msg)


def _parse_then(statement: _StatementType, kwds: dict[str, Any], /) -> dict[str, Any]:
    if isinstance(statement, SchemaBase):
        statement = statement.to_dict()
    elif not isinstance(statement, dict):
        statement = _parse_literal(statement)
    statement.update(kwds)
    return statement


def _parse_otherwise(
    statement: _StatementType, conditions: _Conditional[Any], kwds: dict[str, Any], /
) -> SchemaBase | _Conditional[Any]:
    selection: SchemaBase | _Conditional[Any]
    if isinstance(statement, SchemaBase):
        selection = statement.copy()
        conditions.update(**kwds)  # type: ignore[call-arg]
        selection.condition = conditions["condition"]
    else:
        if not isinstance(statement, t.Mapping):
            statement = _parse_literal(statement)
        selection = conditions
        selection.update(**statement, **kwds)  # type: ignore[call-arg]
    return selection


class _BaseWhen(Protocol):
    # NOTE: Temporary solution to non-SchemaBase copy
    _condition: _Condition

    def _when_then(
        self, statement: _StatementType, kwds: dict[str, Any], /
    ) -> _ConditionClosed | _Condition:
        condition: Any = _deepcopy(self._condition)
        then = _parse_then(statement, kwds)
        condition.update(then)
        return condition


class When(_BaseWhen):
    """
    Utility class for ``when-then-otherwise`` conditions.

    Represents the state after calling :func:`.when()`.

    This partial state requires calling :meth:`When.then()` to finish the condition.

    References
    ----------
    `polars.when <https://docs.pola.rs/py-polars/html/reference/expressions/api/polars.when.html>`__
    """

    def __init__(self, condition: _Condition, /) -> None:
        self._condition = condition

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._condition!r})"

    @overload
    def then(self, statement: str, /, **kwds: Any) -> Then[_Condition]: ...
    @overload
    def then(self, statement: _Value, /, **kwds: Any) -> Then[_Conditions]: ...
    @overload
    def then(
        self, statement: dict[str, Any] | SchemaBase, /, **kwds: Any
    ) -> Then[Any]: ...
    def then(self, statement: _StatementType, /, **kwds: Any) -> Then[Any]:
        """
        Attach a statement to this predicate.

        Parameters
        ----------
        statement
            A spec or value to use when the preceding :func:`.when()` clause is true.

            .. note::
                ``str`` will be encoded as `shorthand`_.
        **kwds
            Additional keyword args are added to the resulting ``dict``.

        Returns
        -------
        :class:`Then`

        .. _shorthand:
            https://altair-viz.github.io/user_guide/encodings/index.html#encoding-shorthands

        Examples
        --------
        Simple conditions may be expressed without defining a default::

            import altair as alt
            from vega_datasets import data

            source = data.movies()
            predicate = (alt.datum.IMDB_Rating == None) | (alt.datum.Rotten_Tomatoes_Rating == None)

            alt.Chart(source).mark_point(invalid=None).encode(
                x="IMDB_Rating:Q",
                y="Rotten_Tomatoes_Rating:Q",
                color=alt.when(predicate).then(alt.value("grey")),
            )
        """
        condition = self._when_then(statement, kwds)
        if _is_condition_extra(condition, statement, kwds=kwds):
            return Then(_Conditional(condition=condition))
        else:
            return Then(_Conditional(condition=[condition]))


class Then(ConditionLike, t.Generic[_C]):
    """
    Utility class for ``when-then-otherwise`` conditions.

    Represents the state after calling :func:`.when().then()`.

    This state is a valid condition on its own.

    It can be further specified, via multiple chained `when-then` calls,
    or finalized with :meth:`Then.otherwise()`.

    References
    ----------
    `polars.when <https://docs.pola.rs/py-polars/html/reference/expressions/api/polars.when.html>`__
    """

    def __init__(self, conditions: _Conditional[_C], /) -> None:
        self.condition: _C = conditions["condition"]

    @overload
    def otherwise(self, statement: _TSchemaBase, /, **kwds: Any) -> _TSchemaBase: ...
    @overload
    def otherwise(self, statement: str, /, **kwds: Any) -> _Conditional[_Condition]: ...
    @overload
    def otherwise(
        self, statement: _Value, /, **kwds: Any
    ) -> _Conditional[_Conditions]: ...
    @overload
    def otherwise(
        self, statement: dict[str, Any], /, **kwds: Any
    ) -> _Conditional[Any]: ...
    def otherwise(
        self, statement: _StatementType, /, **kwds: Any
    ) -> SchemaBase | _Conditional[Any]:
        """
        Finalize the condition with a default value.

        Parameters
        ----------
        statement
            A spec or value to use when no predicates were met.

            .. note::
                Roughly equivalent to an ``else`` clause.

            .. note::
                ``str`` will be encoded as `shorthand`_.
        **kwds
            Additional keyword args are added to the resulting ``dict``.

        .. _shorthand:
            https://altair-viz.github.io/user_guide/encodings/index.html#encoding-shorthands

        Examples
        --------
        Points outside of ``brush`` will not appear highlighted::

            import altair as alt
            from vega_datasets import data

            source = data.cars()
            brush = alt.selection_interval()
            color = alt.when(brush).then("Origin:N").otherwise(alt.value("grey"))

            alt.Chart(source).mark_point().encode(
                x="Horsepower:Q",
                y="Miles_per_Gallon:Q",
                color=color,
            ).add_params(brush)
        """
        conditions: _Conditional[Any]
        is_extra = functools.partial(_is_condition_extra, kwds=kwds)
        if is_extra(self.condition, statement):
            current = self.condition
            if isinstance(current, list) and len(current) == 1:
                # This case is guaranteed to have come from `When` and not `ChainedWhen`
                # The `list` isn't needed if we complete the condition here
                conditions = _Conditional(condition=current[0])  # pyright: ignore[reportArgumentType]
            elif isinstance(current, dict):
                if not is_extra(statement):
                    conditions = self.to_dict()
                else:
                    cond = _reveal_parsed_shorthand(current)
                    msg = (
                        f"Only one field may be used within a condition.\n"
                        f"Shorthand {statement!r} would conflict with {cond!r}\n\n"
                        f"Use `alt.value({statement!r})` if this is not a shorthand string."
                    )
                    raise TypeError(msg)
            else:
                # Generic message to cover less trivial cases
                msg = (
                    f"Chained conditions cannot be mixed with field conditions.\n"
                    f"{self!r}\n\n{statement!r}"
                )
                raise TypeError(msg)
        else:
            conditions = self.to_dict()
        return _parse_otherwise(statement, conditions, kwds)

    def when(
        self,
        predicate: Optional[_PredicateType] = Undefined,
        *more_predicates: _ComposablePredicateType,
        empty: Optional[bool] = Undefined,
        **constraints: _FieldEqualType,
    ) -> ChainedWhen:
        """
        Attach another predicate to the condition.

        The resulting predicate is an ``&`` reduction over ``predicate`` and optional ``*``, ``**``, arguments.

        Parameters
        ----------
        predicate
            A selection or test predicate. ``str`` input will be treated as a test operand.

            .. note::
                Accepts the same range of inputs as in :func:`.condition()`.
        *more_predicates
            Additional predicates, restricted to types supporting ``&``.
        empty
            For selection parameters, the predicate of empty selections returns ``True`` by default.
            Override this behavior, with ``empty=False``.

            .. note::
                When ``predicate`` is a ``Parameter`` that is used more than once,
                ``alt.when().then().when(..., empty=...)`` provides granular control for each occurrence.
        **constraints
            Specify `Field Equal Predicate`_'s.
            Shortcut for ``alt.datum.field_name == value``, see examples for usage.

        Returns
        -------
        :class:`ChainedWhen`
            A partial state which requires calling :meth:`ChainedWhen.then()` to finish the condition.

        .. _Field Equal Predicate:
            https://vega.github.io/vega-lite/docs/predicate.html#equal-predicate

        Examples
        --------
        Chain calls to express precise queries::

            import altair as alt
            from vega_datasets import data

            source = data.cars()
            color = (
                alt.when(alt.datum.Miles_per_Gallon >= 30, Origin="Europe")
                .then(alt.value("crimson"))
                .when(alt.datum.Horsepower > 150)
                .then(alt.value("goldenrod"))
                .otherwise(alt.value("grey"))
            )

            alt.Chart(source).mark_point().encode(x="Horsepower", y="Miles_per_Gallon", color=color)
        """
        condition = _parse_when(predicate, *more_predicates, empty=empty, **constraints)
        conditions = self.to_dict()
        current = conditions["condition"]
        if isinstance(current, list):
            conditions = t.cast(_Conditional[_Conditions], conditions)
            return ChainedWhen(condition, conditions)
        elif isinstance(current, dict):
            cond = _reveal_parsed_shorthand(current)
            msg = (
                f"Chained conditions cannot be mixed with field conditions.\n"
                f"Additional conditions would conflict with {cond!r}\n\n"
                f"Must finalize by calling `.otherwise()`."
            )
            raise TypeError(msg)
        else:
            msg = (
                f"The internal structure has been modified.\n"
                f"{type(current).__name__!r} found, but only `dict | list` are valid."
            )
            raise NotImplementedError(msg)

    def to_dict(self, *args: Any, **kwds: Any) -> _Conditional[_C]:
        return _Conditional(condition=self.condition.copy())

    def __deepcopy__(self, memo: Any) -> Self:
        return type(self)(_Conditional(condition=_deepcopy(self.condition, memo)))

    def __repr__(self) -> str:
        name = type(self).__name__
        COND = "condition: "
        LB, RB = "{", "}"
        if len(self.condition) == 1:
            args = f"{COND}{self.condition!r}".replace("\n", "\n  ")
        else:
            conds = "\n    ".join(f"{c!r}" for c in self.condition)
            args = f"{COND}[\n    " f"{conds}\n  ]"
        return f"{name}({LB}\n  {args}\n{RB})"


class ChainedWhen(_BaseWhen):
    """
    Utility class for ``when-then-otherwise`` conditions.

    Represents the state after calling :func:`.when().then().when()`.

    This partial state requires calling :meth:`ChainedWhen.then()` to finish the condition.

    References
    ----------
    `polars.when <https://docs.pola.rs/py-polars/html/reference/expressions/api/polars.when.html>`__
    """

    def __init__(
        self,
        condition: _Condition,
        conditions: _Conditional[_Conditions],
        /,
    ) -> None:
        self._condition = condition
        self._conditions = conditions

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(\n"
            f"  {self._conditions!r},\n  {self._condition!r}\n"
            ")"
        )

    def then(self, statement: _StatementType, /, **kwds: Any) -> Then[_Conditions]:
        """
        Attach a statement to this predicate.

        Parameters
        ----------
        statement
            A spec or value to use when the preceding :meth:`Then.when()` clause is true.

            .. note::
                ``str`` will be encoded as `shorthand`_.
        **kwds
            Additional keyword args are added to the resulting ``dict``.

        Returns
        -------
        :class:`Then`

        .. _shorthand:
            https://altair-viz.github.io/user_guide/encodings/index.html#encoding-shorthands

        Examples
        --------
        Multiple conditions with an implicit default::

            import altair as alt
            from vega_datasets import data

            source = data.movies()
            predicate = (alt.datum.IMDB_Rating == None) | (alt.datum.Rotten_Tomatoes_Rating == None)
            color = (
                alt.when(predicate)
                .then(alt.value("grey"))
                .when(alt.datum.IMDB_Votes < 5000)
                .then(alt.value("lightblue"))
            )

            alt.Chart(source).mark_point(invalid=None).encode(
                x="IMDB_Rating:Q", y="Rotten_Tomatoes_Rating:Q", color=color
            )
        """
        condition = self._when_then(statement, kwds)
        if _is_condition_closed(condition):
            conditions = self._conditions.copy()
            conditions["condition"].append(condition)
            return Then(conditions)
        else:
            cond = _reveal_parsed_shorthand(condition)
            msg = (
                f"Chained conditions cannot be mixed with field conditions.\n"
                f"Shorthand {statement!r} expanded to {cond!r}\n\n"
                f"Use `alt.value({statement!r})` if this is not a shorthand string."
            )
            raise TypeError(msg)


def when(
    predicate: Optional[_PredicateType] = Undefined,
    *more_predicates: _ComposablePredicateType,
    empty: Optional[bool] = Undefined,
    **constraints: _FieldEqualType,
) -> When:
    """
    Start a ``when-then-otherwise`` condition.

    The resulting predicate is an ``&`` reduction over ``predicate`` and optional ``*``, ``**``, arguments.

    Parameters
    ----------
    predicate
        A selection or test predicate. ``str`` input will be treated as a test operand.

        .. note::
            Accepts the same range of inputs as in :func:`.condition()`.
    *more_predicates
        Additional predicates, restricted to types supporting ``&``.
    empty
        For selection parameters, the predicate of empty selections returns ``True`` by default.
        Override this behavior, with ``empty=False``.

        .. note::
            When ``predicate`` is a ``Parameter`` that is used more than once,
            ``alt.when(..., empty=...)`` provides granular control for each occurrence.
    **constraints
        Specify `Field Equal Predicate`_'s.
        Shortcut for ``alt.datum.field_name == value``, see examples for usage.

    Returns
    -------
    :class:`When`
        A partial state which requires calling :meth:`When.then()` to finish the condition.

    Notes
    -----
    - Directly inspired by the ``when-then-otherwise`` syntax used in `polars.when`_.

    .. _Field Equal Predicate:
        https://vega.github.io/vega-lite/docs/predicate.html#equal-predicate
    .. _polars.when:
        https://docs.pola.rs/py-polars/html/reference/expressions/api/polars.when.html

    Examples
    --------
    Setting up a common chart::

        import altair as alt
        from vega_datasets import data

        source = data.cars()
        brush = alt.selection_interval()
        points = (
            alt.Chart(source)
            .mark_point()
            .encode(x="Horsepower", y="Miles_per_Gallon")
            .add_params(brush)
        )
        points

    Basic ``if-then-else`` conditions translate directly to ``when-then-otherwise``::

        points.encode(color=alt.when(brush).then("Origin").otherwise(alt.value("lightgray")))

    Omitting the ``.otherwise()`` clause will use the channel default instead::

        points.encode(color=alt.when(brush).then("Origin"))

    Predicates passed as positional arguments will be reduced with ``&``::

        points.encode(
            color=alt.when(
                brush, (alt.datum.Miles_per_Gallon >= 30) | (alt.datum.Horsepower >= 130)
            )
            .then("Origin")
            .otherwise(alt.value("lightgray"))
        )

    Using keyword-argument ``constraints`` can simplify compositions like::

        verbose_composition = (
            (alt.datum.Name == "Name_1")
            & (alt.datum.Color == "Green")
            & (alt.datum.Age == 25)
            & (alt.datum.StartDate == "2000-10-01")
        )
        when_verbose = alt.when(verbose_composition)
        when_concise = alt.when(Name="Name_1", Color="Green", Age=25, StartDate="2000-10-01")
    """
    condition = _parse_when(predicate, *more_predicates, empty=empty, **constraints)
    return When(condition)


# ------------------------------------------------------------------------
# Top-Level Functions


def value(value: Any, **kwargs: Any) -> _Value:
    """Specify a value for use in an encoding."""
    return _Value(value=value, **kwargs)  # type: ignore[typeddict-item]


def param(
    name: str | None = None,
    value: Optional[Any] = Undefined,
    bind: Optional[Binding] = Undefined,
    empty: Optional[bool] = Undefined,
    expr: Optional[str | Expr | Expression] = Undefined,
    **kwds: Any,
) -> Parameter:
    """
    Create a named parameter, see https://altair-viz.github.io/user_guide/interactions.html for examples.

    Although both variable parameters and selection parameters can be created using
    this 'param' function, to create a selection parameter, it is recommended to use
    either 'selection_point' or 'selection_interval' instead.

    Parameters
    ----------
    name : string (optional)
        The name of the parameter. If not specified, a unique name will be
        created.
    value : any (optional)
        The default value of the parameter. If not specified, the parameter
        will be created without a default value.
    bind : :class:`Binding` (optional)
        Binds the parameter to an external input element such as a slider,
        selection list or radio button group.
    empty : boolean (optional)
        For selection parameters, the predicate of empty selections returns
        True by default. Override this behavior, by setting this property
        'empty=False'.
    expr : str, Expression (optional)
        An expression for the value of the parameter. This expression may
        include other parameters, in which case the parameter will
        automatically update in response to upstream parameter changes.
    **kwds :
        additional keywords will be used to construct a parameter.  If 'select'
        is among the keywords, then a selection parameter will be created.
        Otherwise, a variable parameter will be created.

    Returns
    -------
    parameter: Parameter
        The parameter object that can be used in chart creation.
    """
    warn_msg = "The value of `empty` should be True or False."
    empty_remap = {"none": False, "all": True}
    parameter = Parameter(name)

    if not utils.is_undefined(empty):
        if isinstance(empty, bool) and not isinstance(empty, str):
            parameter.empty = empty
        elif empty in empty_remap:
            utils.deprecated_warn(warn_msg, version="5.0.0")
            parameter.empty = empty_remap[t.cast(str, empty)]
        else:
            raise ValueError(warn_msg)

    if _init := kwds.pop("init", None):
        utils.deprecated_warn("Use `value` instead of `init`.", version="5.0.0")
        # If both 'value' and 'init' are set, we ignore 'init'.
        if value is Undefined:
            kwds["value"] = _init

    # ignore[arg-type] comment is needed because we can also pass _expr_core.Expression
    if "select" not in kwds:
        parameter.param = core.VariableParameter(
            name=parameter.name,
            bind=bind,
            value=value,
            expr=expr,
            **kwds,
        )
        parameter.param_type = "variable"
    elif "views" in kwds:
        parameter.param = core.TopLevelSelectionParameter(
            name=parameter.name, bind=bind, value=value, expr=expr, **kwds
        )
        parameter.param_type = "selection"
    else:
        parameter.param = core.SelectionParameter(
            name=parameter.name, bind=bind, value=value, expr=expr, **kwds
        )
        parameter.param_type = "selection"

    return parameter


def _selection(type: Optional[SelectionType_T] = Undefined, **kwds: Any) -> Parameter:
    # We separate out the parameter keywords from the selection keywords

    select_kwds = {"name", "bind", "value", "empty", "init", "views"}
    param_kwds = {key: kwds.pop(key) for key in select_kwds & kwds.keys()}

    select: IntervalSelectionConfig | PointSelectionConfig
    if type == "interval":
        select = core.IntervalSelectionConfig(type=type, **kwds)
    elif type == "point":
        select = core.PointSelectionConfig(type=type, **kwds)
    elif type in {"single", "multi"}:
        select = core.PointSelectionConfig(type="point", **kwds)
        utils.deprecated_warn(
            "The types `single` and `multi` are now combined.",
            version="5.0.0",
            alternative="selection_point()",
        )
    else:
        msg = """'type' must be 'point' or 'interval'"""
        raise ValueError(msg)

    return param(select=select, **param_kwds)


@utils.deprecated(
    version="5.0.0",
    alternative="'selection_point()' or 'selection_interval()'",
    message="These functions also include more helpful docstrings.",
)
def selection(type: Optional[SelectionType_T] = Undefined, **kwds: Any) -> Parameter:
    """'selection' is deprecated use 'selection_point' or 'selection_interval' instead, depending on the type of parameter you want to create."""
    return _selection(type=type, **kwds)


_SelectionPointValue: TypeAlias = "PrimitiveValue_T | Temporal | DateTime | Sequence[Mapping[SingleDefUnitChannel_T | LiteralString, PrimitiveValue_T | Temporal | DateTime]]"
"""
Point selections can be initialized with a single primitive value:

    import altair as alt

    alt.selection_point(fields=["year"], value=1980)


You can also provide a sequence of mappings between ``encodings`` or ``fields`` to **values**:

    alt.selection_point(
        fields=["cylinders", "year"],
        value=[{"cylinders": 4, "year": 1981}, {"cylinders": 8, "year": 1972}],
    )
"""

_SelectionIntervalValueMap: TypeAlias = Mapping[
    SingleDefUnitChannel_T,
    Union[
        tuple[bool, bool],
        tuple[float, float],
        tuple[str, str],
        tuple["Temporal | DateTime", "Temporal | DateTime"],
        Sequence[bool],
        Sequence[float],
        Sequence[str],
        Sequence["Temporal | DateTime"],
    ],
]
"""
Interval selections are initialized with a mapping between ``encodings`` to **values**:

    import altair as alt

    alt.selection_interval(
        encodings=["longitude"],
        empty=False,
        value={"longitude": [-50, -110]},
    )

The values specify the **start** and **end** of the interval selection.

You can use a ``tuple`` for type-checking each sequence has **two** elements:

    alt.selection_interval(value={"x": (55, 160), "y": (13, 37)})


.. note::

    Unlike :func:`.selection_point()`, the use of ``None`` is not permitted.
"""


def selection_interval(
    name: str | None = None,
    value: Optional[_SelectionIntervalValueMap] = Undefined,
    bind: Optional[Binding | str] = Undefined,
    empty: Optional[bool] = Undefined,
    expr: Optional[str | Expr | Expression] = Undefined,
    encodings: Optional[Sequence[SingleDefUnitChannel_T]] = Undefined,
    on: Optional[str | MergedStreamKwds | DerivedStreamKwds] = Undefined,
    clear: Optional[str | bool | MergedStreamKwds | DerivedStreamKwds] = Undefined,
    resolve: Optional[SelectionResolution_T] = Undefined,
    mark: Optional[BrushConfig | BrushConfigKwds] = Undefined,
    translate: Optional[str | bool] = Undefined,
    zoom: Optional[str | bool] = Undefined,
    **kwds: Any,
) -> Parameter:
    """
    Create an interval selection parameter. Selection parameters define data queries that are driven by direct manipulation from user input (e.g., mouse clicks or drags). Interval selection parameters are used to select a continuous range of data values on drag, whereas point selection parameters (`selection_point`) are used to select multiple discrete data values.).

    Parameters
    ----------
    name : str (optional)
        The name of the parameter. If not specified, a unique name will be
        created.
    value : Any (optional)
        The default value of the parameter. If not specified, the parameter
        will be created without a default value.
    bind : :class:`Binding`, str (optional)
        Binds the parameter to an external input element such as a slider,
        selection list or radio button group.
    empty : bool (optional)
        For selection parameters, the predicate of empty selections returns
        True by default. Override this behavior, by setting this property
        'empty=False'.
    expr : :class:`Expr` (optional)
        An expression for the value of the parameter. This expression may
        include other parameters, in which case the parameter will
        automatically update in response to upstream parameter changes.
    encodings : Sequence[str] (optional)
        A list of encoding channels. The corresponding data field values
        must match for a data tuple to fall within the selection.
    on : str (optional)
        A Vega event stream (object or selector) that triggers the selection.
        For interval selections, the event stream must specify a start and end.
    clear : str, bool (optional)
        Clears the selection, emptying it of all values. This property can
        be an Event Stream or False to disable clear.  Default is 'dblclick'.
    resolve : Literal['global', 'union', 'intersect'] (optional)
        With layered and multi-view displays, a strategy that determines
        how selections' data queries are resolved when applied in a filter
        transform, conditional encoding rule, or scale domain.
        One of:

        * 'global': only one brush exists for the entire SPLOM. When the
          user begins to drag, any previous brushes are cleared, and a
          new one is constructed.
        * 'union': each cell contains its own brush, and points are
          highlighted if they lie within any of these individual brushes.
        * 'intersect': each cell contains its own brush, and points are
          highlighted only if they fall within all of these individual
          brushes.

        The default is 'global'.
    mark : :class:`BrushConfig` (optional)
        An interval selection also adds a rectangle mark to depict the
        extents of the interval. The ``mark`` property can be used to
        customize the appearance of the mark.
    translate : str, bool (optional)
        When truthy, allows a user to interactively move an interval
        selection back-and-forth. Can be True, False (to disable panning),
        or a Vega event stream definition which must include a start and
        end event to trigger continuous panning. Discrete panning (e.g.,
        pressing the left/right arrow keys) will be supported in future
        versions.
        The default value is True, which corresponds to
        [pointerdown, window:pointerup] > window:pointermove!
        This default allows users to click and drag within an interval
        selection to reposition it.
    zoom : str, bool (optional)
        When truthy, allows a user to interactively resize an interval
        selection. Can be True, False (to disable zooming), or a Vega
        event stream definition. Currently, only wheel events are supported,
        but custom event streams can still be used to specify filters,
        debouncing, and throttling. Future versions will expand the set of
        events that can trigger this transformation.
        The default value is True, which corresponds to wheel!. This
        default allows users to use the mouse wheel to resize an interval
        selection.
    **kwds : Any
        Additional keywords to control the selection.

    Returns
    -------
    parameter: Parameter
        The parameter object that can be used in chart creation.
    """
    return _selection(
        type="interval",
        name=name,
        value=value,
        bind=bind,
        empty=empty,
        expr=expr,
        encodings=encodings,
        on=on,
        clear=clear,
        resolve=resolve,
        mark=mark,
        translate=translate,
        zoom=zoom,
        **kwds,
    )


def selection_point(
    name: str | None = None,
    value: Optional[_SelectionPointValue] = Undefined,
    bind: Optional[Binding | str] = Undefined,
    empty: Optional[bool] = Undefined,
    expr: Optional[str | Expr | Expression] = Undefined,
    encodings: Optional[Sequence[SingleDefUnitChannel_T]] = Undefined,
    fields: Optional[Sequence[str]] = Undefined,
    on: Optional[str | MergedStreamKwds | DerivedStreamKwds] = Undefined,
    clear: Optional[str | bool | MergedStreamKwds | DerivedStreamKwds] = Undefined,
    resolve: Optional[SelectionResolution_T] = Undefined,
    toggle: Optional[str | bool] = Undefined,
    nearest: Optional[bool] = Undefined,
    **kwds: Any,
) -> Parameter:
    """
    Create a point selection parameter. Selection parameters define data queries that are driven by direct manipulation from user input (e.g., mouse clicks or drags). Point selection parameters are used to select multiple discrete data values; the first value is selected on click and additional values toggled on shift-click. To select a continuous range of data values on drag interval selection parameters (`selection_interval`) can be used instead.

    Parameters
    ----------
    name : str (optional)
        The name of the parameter. If not specified, a unique name will be
        created.
    value : Any (optional)
        The default value of the parameter. If not specified, the parameter
        will be created without a default value.
    bind : :class:`Binding`, str (optional)
        Binds the parameter to an external input element such as a slider,
        selection list or radio button group.
    empty : bool (optional)
        For selection parameters, the predicate of empty selections returns
        True by default. Override this behavior, by setting this property
        'empty=False'.
    expr : :class:`Expr` (optional)
        An expression for the value of the parameter. This expression may
        include other parameters, in which case the parameter will
        automatically update in response to upstream parameter changes.
    encodings : Sequence[str] (optional)
        A list of encoding channels. The corresponding data field values
        must match for a data tuple to fall within the selection.
    fields : Sequence[str] (optional)
        A list of field names whose values must match for a data tuple to
        fall within the selection.
    on : str (optional)
        A Vega event stream (object or selector) that triggers the selection.
        For interval selections, the event stream must specify a start and end.
    clear : str, bool (optional)
        Clears the selection, emptying it of all values. This property can
        be an Event Stream or False to disable clear.  Default is 'dblclick'.
    resolve : Literal['global', 'union', 'intersect'] (optional)
        With layered and multi-view displays, a strategy that determines
        how selections' data queries are resolved when applied in a filter
        transform, conditional encoding rule, or scale domain.
        One of:

        * 'global': only one brush exists for the entire SPLOM. When the
          user begins to drag, any previous brushes are cleared, and a
          new one is constructed.
        * 'union': each cell contains its own brush, and points are
          highlighted if they lie within any of these individual brushes.
        * 'intersect': each cell contains its own brush, and points are
          highlighted only if they fall within all of these individual
          brushes.

        The default is 'global'.
    toggle : str, bool (optional)
        Controls whether data values should be toggled (inserted or
        removed from a point selection) or only ever inserted into
        point selections.
        One of:

        * True (default): the toggle behavior, which corresponds to
          "event.shiftKey". As a result, data values are toggled
          when the user interacts with the shift-key pressed.
        * False: disables toggling behaviour; the selection will
          only ever contain a single data value corresponding
          to the most recent interaction.
        * A Vega expression which is re-evaluated as the user interacts.
          If the expression evaluates to True, the data value is
          toggled into or out of the point selection. If the expression
          evaluates to False, the point selection is first cleared, and
          the data value is then inserted. For example, setting the
          value to the Vega expression True will toggle data values
          without the user pressing the shift-key.

    nearest : bool (optional)
        When true, an invisible voronoi diagram is computed to accelerate
        discrete selection. The data value nearest the mouse cursor is
        added to the selection.  The default is False, which means that
        data values must be interacted with directly (e.g., clicked on)
        to be added to the selection.
    **kwds : Any
        Additional keywords to control the selection.

    Returns
    -------
    parameter: Parameter
        The parameter object that can be used in chart creation.
    """
    return _selection(
        type="point",
        name=name,
        value=value,
        bind=bind,
        empty=empty,
        expr=expr,
        encodings=encodings,
        fields=fields,
        on=on,
        clear=clear,
        resolve=resolve,
        toggle=toggle,
        nearest=nearest,
        **kwds,
    )


@utils.deprecated(version="5.0.0", alternative="selection_point")
def selection_multi(**kwargs: Any) -> Parameter:
    """'selection_multi' is deprecated.  Use 'selection_point'."""
    return _selection(type="point", **kwargs)


@utils.deprecated(version="5.0.0", alternative="selection_point")
def selection_single(**kwargs: Any) -> Parameter:
    """'selection_single' is deprecated.  Use 'selection_point'."""
    return _selection(type="point", **kwargs)


def binding(
    input: str,
    *,
    autocomplete: Optional[str] = Undefined,
    debounce: Optional[float] = Undefined,
    element: Optional[str] = Undefined,
    name: Optional[str] = Undefined,
    placeholder: Optional[str] = Undefined,
) -> BindInput:
    """
    A generic binding.

    Parameters
    ----------
    input : str
        The type of input element to use. The valid values are ``"checkbox"``, ``"radio"``,
        ``"range"``, ``"select"``, and any other legal `HTML form input type
        <https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input>`__.
    autocomplete : str
        A hint for form autofill. See the `HTML autocomplete attribute
        <https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/autocomplete>`__ for
        additional information.
    debounce : float
        If defined, delays event handling until the specified milliseconds have elapsed
        since the last event was fired.
    element : str
        An optional CSS selector string indicating the parent element to which the input
        element should be added. By default, all input elements are added within the parent
        container of the Vega view.
    name : str
        By default, the signal name is used to label input elements. This ``name`` property
        can be used instead to specify a custom label for the bound signal.
    placeholder : str
        Text that appears in the form control when it has no value set.
    """
    return core.BindInput(
        autocomplete=autocomplete,
        debounce=debounce,
        element=element,
        input=input,
        name=name,
        placeholder=placeholder,
    )


@utils.use_signature(core.BindCheckbox)
def binding_checkbox(**kwargs: Any) -> BindCheckbox:
    """A checkbox binding."""
    return core.BindCheckbox(input="checkbox", **kwargs)


@utils.use_signature(core.BindRadioSelect)
def binding_radio(**kwargs: Any) -> BindRadioSelect:
    """A radio button binding."""
    return core.BindRadioSelect(input="radio", **kwargs)


@utils.use_signature(core.BindRadioSelect)
def binding_select(**kwargs: Any) -> BindRadioSelect:
    """A select binding."""
    return core.BindRadioSelect(input="select", **kwargs)


@utils.use_signature(core.BindRange)
def binding_range(**kwargs: Any) -> BindRange:
    """A range binding."""
    return core.BindRange(input="range", **kwargs)


@overload
def condition(
    predicate: _PredicateType,
    if_true: _StatementType,
    if_false: _TSchemaBase,
    *,
    empty: Optional[bool] = ...,
    **kwargs: Any,
) -> _TSchemaBase: ...
@overload
def condition(
    predicate: _PredicateType,
    if_true: Map | SchemaBase,
    if_false: Map | str,
    *,
    empty: Optional[bool] = ...,
    **kwargs: Any,
) -> _Conditional[_Condition]: ...
@overload
def condition(
    predicate: _PredicateType,
    if_true: Map | str,
    if_false: Map,
    *,
    empty: Optional[bool] = ...,
    **kwargs: Any,
) -> _Conditional[_Condition]: ...
@overload
def condition(
    predicate: _PredicateType, if_true: str, if_false: str, **kwargs: Any
) -> Never: ...
# TODO: update the docstring
def condition(
    predicate: _PredicateType,
    if_true: _StatementType,
    if_false: _StatementType,
    *,
    empty: Optional[bool] = Undefined,
    **kwargs: Any,
) -> SchemaBase | _Conditional[_Condition]:
    """
    A conditional attribute or encoding.

    Parameters
    ----------
    predicate: Parameter, PredicateComposition, expr.Expression, dict, or string
        the selection predicate or test predicate for the condition.
        if a string is passed, it will be treated as a test operand.
    if_true:
        the spec or object to use if the selection predicate is true
    if_false:
        the spec or object to use if the selection predicate is false
    empty
        For selection parameters, the predicate of empty selections returns ``True`` by default.
        Override this behavior, with ``empty=False``.

        .. note::
            When ``predicate`` is a ``Parameter`` that is used more than once,
            ``alt.condition(..., empty=...)`` provides granular control for each :func:`.condition()`.
    **kwargs:
        additional keyword args are added to the resulting dict

    Returns
    -------
    spec: dict or VegaLiteSchema
        the spec that describes the condition
    """
    condition = _predicate_to_condition(predicate, empty=empty)
    return _condition_to_selection(condition, if_true, if_false, **kwargs)


# --------------------------------------------------------------------
# Top-level objects


def _top_schema_base(  # noqa: ANN202
    obj: Any, /
):  # -> <subclass of SchemaBase and TopLevelMixin>
    """
    Enforces an intersection type w/ `SchemaBase` & `TopLevelMixin` objects.

    Use for methods, called from `TopLevelMixin` that are defined in `SchemaBase`.

    Notes
    -----
    - The `super` sub-branch is not statically checked *here*.
        - It would widen the inferred intersection to:
            - `(<subclass of SchemaBase and TopLevelMixin> | super)`
        - Both dunder attributes are not in the `super` type stubs
            - Requiring 2x *# type: ignore[attr-defined]*
    - However it is required at runtime for any cases that use `super(..., copy)`.
    - The inferred type **is** used statically **outside** of this function.
    """
    if (isinstance(obj, SchemaBase) and isinstance(obj, TopLevelMixin)) or (
        not TYPE_CHECKING
        and (
            isinstance(obj, super)
            and issubclass(obj.__self_class__, SchemaBase)
            and obj.__thisclass__ is TopLevelMixin
        )
    ):
        return obj
    else:
        msg = f"{type(obj).__name__!r} does not derive from {SchemaBase.__name__!r}"
        raise TypeError(msg)


class TopLevelMixin(mixins.ConfigMethodMixin):
    """Mixin for top-level chart objects such as Chart, LayeredChart, etc."""

    _class_is_valid_at_instantiation: bool = False
    data: Any

    def to_dict(  # noqa: C901
        self,
        validate: bool = True,
        *,
        format: Literal["vega-lite", "vega"] = "vega-lite",
        ignore: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Convert the chart to a dictionary suitable for JSON export.

        Parameters
        ----------
        validate : bool, optional
            If True (default), then validate the result against the schema.
        format : {"vega-lite", "vega"}, optional
            The chart specification format.
            The `"vega"` format relies on the active Vega-Lite compiler plugin, which
            by default requires the vl-convert-python package.
        ignore : list[str], optional
            A list of keys to ignore.
        context : dict[str, Any], optional
            A context dictionary.

        Raises
        ------
        SchemaValidationError :
            If ``validate`` and the result does not conform to the schema.

        Notes
        -----
        - ``ignore``, ``context`` are usually not needed to be specified as a user.
        - *Technical*: ``ignore`` will **not** be passed to child :meth:`.to_dict()`.
        """
        # Validate format
        if format not in {"vega-lite", "vega"}:
            msg = f'The format argument must be either "vega-lite" or "vega". Received {format!r}'
            raise ValueError(msg)

        # We make use of three context markers:
        # - 'data' points to the data that should be referenced for column type
        #   inference.
        # - 'top_level' is a boolean flag that is assumed to be true; if it's
        #   true then a "$schema" arg is added to the dict.
        # - 'datasets' is a dict of named datasets that should be inserted
        #   in the top-level object
        # - 'pre_transform' whether data transformations should be pre-evaluated
        #   if the current data transformer supports it (currently only used when
        #   the "vegafusion" transformer is enabled)

        # note: not a deep copy because we want datasets and data arguments to
        # be passed by reference
        context = context.copy() if context else {}
        context.setdefault("datasets", {})
        is_top_level = context.get("top_level", True)

        copy = _top_schema_base(self).copy(deep=False)
        original_data = getattr(copy, "data", Undefined)
        if not utils.is_undefined(original_data):
            try:
                data = nw.from_native(original_data, eager_or_interchange_only=True)
            except TypeError:
                # Non-narwhalifiable type supported by Altair, such as dict
                data = original_data
            copy.data = _prepare_data(data, context)
            context["data"] = data

        # remaining to_dict calls are not at top level
        context["top_level"] = False

        vegalite_spec: Any = _top_schema_base(super(TopLevelMixin, copy)).to_dict(
            validate=validate, ignore=ignore, context=dict(context, pre_transform=False)
        )

        # TODO: following entries are added after validation. Should they be validated?
        if is_top_level:
            # since this is top-level we add $schema if it's missing
            if "$schema" not in vegalite_spec:
                vegalite_spec["$schema"] = SCHEMA_URL

            if func := theme.get():
                vegalite_spec = utils.update_nested(func(), vegalite_spec, copy=True)
            else:
                msg = (
                    f"Expected a theme to be set but got {None!r}.\n"
                    f"Call `themes.enable('default')` to reset the `ThemeRegistry`."
                )
                raise TypeError(msg)

            # update datasets
            if context["datasets"]:
                vegalite_spec.setdefault("datasets", {}).update(context["datasets"])

        if context.get("pre_transform", True) and _using_vegafusion():
            if format == "vega-lite":
                msg = (
                    'When the "vegafusion" data transformer is enabled, the \n'
                    "to_dict() and to_json() chart methods must be called with "
                    'format="vega". \n'
                    "For example: \n"
                    '    >>> chart.to_dict(format="vega")\n'
                    '    >>> chart.to_json(format="vega")'
                )
                raise ValueError(msg)
            else:
                return _compile_with_vegafusion(vegalite_spec)
        elif format == "vega":
            plugin = vegalite_compilers.get()
            if plugin is None:
                msg = "No active vega-lite compiler plugin found"
                raise ValueError(msg)
            return plugin(vegalite_spec)
        else:
            return vegalite_spec

    def to_json(
        self,
        validate: bool = True,
        indent: int | str | None = 2,
        sort_keys: bool = True,
        *,
        format: Literal["vega-lite", "vega"] = "vega-lite",
        ignore: list[str] | None = None,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Convert a chart to a JSON string.

        Parameters
        ----------
        validate : bool, optional
            If True (default), then validate the result against the schema.
        indent : int, optional
            The number of spaces of indentation to use. The default is 2.
        sort_keys : bool, optional
            If True (default), sort keys in the output.
        format : {"vega-lite", "vega"}, optional
            The chart specification format.
            The `"vega"` format relies on the active Vega-Lite compiler plugin, which
            by default requires the vl-convert-python package.
        ignore : list[str], optional
            A list of keys to ignore.
        context : dict[str, Any], optional
            A context dictionary.
        **kwargs
            Additional keyword arguments are passed to ``json.dumps()``

        Raises
        ------
        SchemaValidationError :
            If ``validate`` and the result does not conform to the schema.

        Notes
        -----
        - ``ignore``, ``context`` are usually not needed to be specified as a user.
        - *Technical*: ``ignore`` will **not** be passed to child :meth:`.to_dict()`.
        """
        if ignore is None:
            ignore = []
        if context is None:
            context = {}
        spec = self.to_dict(
            validate=validate, format=format, ignore=ignore, context=context
        )
        return json.dumps(spec, indent=indent, sort_keys=sort_keys, **kwargs)

    def to_html(
        self,
        base_url: str = "https://cdn.jsdelivr.net/npm",
        output_div: str = "vis",
        embed_options: dict | None = None,
        json_kwds: dict | None = None,
        fullhtml: bool = True,
        requirejs: bool = False,
        inline: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Embed a Vega/Vega-Lite spec into an HTML page.

        Parameters
        ----------
        base_url : string (optional)
            The base url from which to load the javascript libraries.
        output_div : string (optional)
            The id of the div element where the plot will be shown.
        embed_options : dict (optional)
            Dictionary of options to pass to the vega-embed script. Default
            entry is {'mode': mode}.
        json_kwds : dict (optional)
            Dictionary of keywords to pass to json.dumps().
        fullhtml : boolean (optional)
            If True (default) then return a full html page. If False, then return
            an HTML snippet that can be embedded into an HTML page.
        requirejs : boolean (optional)
            If False (default) then load libraries from base_url using <script>
            tags. If True, then load libraries using requirejs
        inline: bool (optional)
            If False (default), the required JavaScript libraries are loaded
            from a CDN location in the resulting html file.
            If True, the required JavaScript libraries are inlined into the resulting
            html file so that it will work without an internet connection.
            The vl-convert-python package is required if True.
        **kwargs :
            additional kwargs passed to spec_to_html.

        Returns
        -------
        output : string
            an HTML string for rendering the chart.
        """
        if inline:
            kwargs["template"] = "inline"
        return utils.spec_to_html(
            self.to_dict(),
            mode="vega-lite",
            vegalite_version=VEGALITE_VERSION,
            vegaembed_version=VEGAEMBED_VERSION,
            vega_version=VEGA_VERSION,
            base_url=base_url,
            output_div=output_div,
            embed_options=embed_options,
            json_kwds=json_kwds,
            fullhtml=fullhtml,
            requirejs=requirejs,
            **kwargs,
        )

    def to_url(self, *, fullscreen: bool = False) -> str:
        """
        Convert a chart to a URL that opens the chart specification in the Vega chart editor.

        The chart specification (including any inline data) is encoded in the URL.

        This method requires that the vl-convert-python package is installed.

        Parameters
        ----------
        fullscreen : bool
            If True, editor will open chart in fullscreen mode. Default False
        """
        from altair.utils._importers import import_vl_convert

        vlc = import_vl_convert()
        if _using_vegafusion():
            return vlc.vega_to_url(self.to_dict(format="vega"), fullscreen=fullscreen)
        else:
            return vlc.vegalite_to_url(self.to_dict(), fullscreen=fullscreen)

    def open_editor(self, *, fullscreen: bool = False) -> None:
        """
        Opens the chart specification in the Vega chart editor using the default browser.

        Parameters
        ----------
        fullscreen : bool
            If True, editor will open chart in fullscreen mode. Default False
        """
        import webbrowser

        webbrowser.open(self.to_url(fullscreen=fullscreen))

    def save(
        self,
        fp: str | Path | IO,
        format: Literal["json", "html", "png", "svg", "pdf"] | None = None,
        override_data_transformer: bool = True,
        scale_factor: float = 1.0,
        mode: str | None = None,
        vegalite_version: str = VEGALITE_VERSION,
        vega_version: str = VEGA_VERSION,
        vegaembed_version: str = VEGAEMBED_VERSION,
        embed_options: dict | None = None,
        json_kwds: dict | None = None,
        engine: str | None = None,
        inline: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Save a chart to file in a variety of formats.

        Supported formats are json, html, png, svg, pdf; the last three require
        the vl-convert-python package to be installed.

        Parameters
        ----------
        fp : string filename or file-like object
            file in which to write the chart.
        format : string (optional)
            the format to write: one of ['json', 'html', 'png', 'svg', 'pdf'].
            If not specified, the format will be determined from the filename.
        override_data_transformer : `boolean` (optional)
            If True (default), then the save action will be done with
            the MaxRowsError disabled. If False, then do not change the data
            transformer.
        scale_factor : float (optional)
            scale_factor to use to change size/resolution of png or svg output
        mode : string (optional)
            Must be 'vega-lite'. If not specified, then infer the mode from
            the '$schema' property of the spec, or the ``opt`` dictionary.
            If it's not specified in either of those places, then use 'vega-lite'.
        vegalite_version : string (optional)
            For html output, the version of vegalite.js to use
        vega_version : string (optional)
            For html output, the version of vega.js to use
        vegaembed_version : string (optional)
            For html output, the version of vegaembed.js to use
        embed_options : dict (optional)
            The vegaEmbed options dictionary. Default is {}
            (See https://github.com/vega/vega-embed for details)
        json_kwds : dict (optional)
            Additional keyword arguments are passed to the output method
            associated with the specified format.
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
            utils.deprecated_warn(
                "The webdriver argument is not relevant for the new vl-convert engine which replaced altair_saver. "
                "The argument will be removed in a future release.",
                version="5.0.0",
            )

        from altair.utils.save import save

        kwds: dict[str, Any] = dict(
            chart=self,
            fp=fp,
            format=format,
            scale_factor=scale_factor,
            mode=mode,
            vegalite_version=vegalite_version,
            vega_version=vega_version,
            vegaembed_version=vegaembed_version,
            embed_options=embed_options,
            json_kwds=json_kwds,
            engine=engine,
            inline=inline,
            **kwargs,
        )

        # By default we override the data transformer. This makes it so
        # that save() will succeed even for large datasets that would
        # normally trigger a MaxRowsError
        if override_data_transformer:
            with data_transformers.disable_max_rows():
                save(**kwds)
        else:
            save(**kwds)

    # Fallback for when rendering fails; the full repr is too long to be
    # useful in nearly all cases.
    def __repr__(self) -> str:
        return f"alt.{self.__class__.__name__}(...)"

    # Layering and stacking
    def __add__(self, other: ChartType) -> LayerChart:
        if not is_chart_type(other):
            msg = "Only Chart objects can be layered."
            raise ValueError(msg)
        return layer(t.cast("ChartType", self), other)

    def __and__(self, other: ChartType) -> VConcatChart:
        if not is_chart_type(other):
            msg = "Only Chart objects can be concatenated."
            raise ValueError(msg)
        # Too difficult to type check this
        return vconcat(t.cast("ChartType", self), other)

    def __or__(self, other: ChartType) -> HConcatChart | ConcatChart:
        if not is_chart_type(other):
            msg = "Only Chart objects can be concatenated."
            raise ValueError(msg)
        elif isinstance(self, ConcatChart):
            return concat(self, other)
        else:
            return hconcat(t.cast("ChartType", self), other)

    def repeat(
        self,
        repeat: Optional[list[str]] = Undefined,
        row: Optional[list[str]] = Undefined,
        column: Optional[list[str]] = Undefined,
        layer: Optional[list[str]] = Undefined,
        columns: Optional[int] = Undefined,
        **kwargs: Any,
    ) -> RepeatChart:
        """
        Return a RepeatChart built from the chart.

        Fields within the chart can be set to correspond to the row or
        column using `alt.repeat('row')` and `alt.repeat('column')`.

        Parameters
        ----------
        repeat : list
            a list of data column names to be repeated. This cannot be
            used along with the ``row``, ``column`` or ``layer`` argument.
        row : list
            a list of data column names to be mapped to the row facet
        column : list
            a list of data column names to be mapped to the column facet
        layer : list
            a list of data column names to be layered. This cannot be
            used along with the ``row``, ``column`` or ``repeat`` argument.
        columns : int
            the maximum number of columns before wrapping. Only referenced
            if ``repeat`` is specified.
        **kwargs :
            additional keywords passed to RepeatChart.

        Returns
        -------
        chart : RepeatChart
            a repeated chart.
        """
        repeat_specified = repeat is not Undefined
        rowcol_specified = row is not Undefined or column is not Undefined
        layer_specified = layer is not Undefined

        if repeat_specified and rowcol_specified:
            msg = "repeat argument cannot be combined with row/column argument."
            raise ValueError(msg)
        elif repeat_specified and layer_specified:
            msg = "repeat argument cannot be combined with layer argument."
            raise ValueError(msg)

        repeat_arg: list[str] | LayerRepeatMapping | RepeatMapping
        if repeat_specified:
            assert isinstance(repeat, list)
            repeat_arg = repeat
        elif layer_specified:
            repeat_arg = core.LayerRepeatMapping(layer=layer, row=row, column=column)
        else:
            repeat_arg = core.RepeatMapping(row=row, column=column)

        return RepeatChart(
            spec=t.cast("ChartType", self), repeat=repeat_arg, columns=columns, **kwargs
        )

    def properties(self, **kwargs: Any) -> Self:
        """
        Set top-level properties of the Chart.

        Argument names and types are the same as class initialization.
        """
        copy = _top_schema_base(self).copy(deep=False)
        for key, val in kwargs.items():
            if key == "selection" and isinstance(val, Parameter):
                # TODO: Can this be removed
                # For backward compatibility with old selection interface.
                setattr(copy, key, {val.name: val.selection})
            else:
                # Don't validate data, because it hasn't been processed.
                if key != "data":
                    _top_schema_base(self).validate_property(key, val)
                setattr(copy, key, val)
        return t.cast("Self", copy)

    def project(
        self,
        type: Optional[
            ProjectionType_T | ProjectionType | ExprRef | Parameter
        ] = Undefined,
        center: Optional[list[float] | Vector2number | ExprRef | Parameter] = Undefined,
        clipAngle: Optional[float | ExprRef | Parameter] = Undefined,
        clipExtent: Optional[
            list[list[float]] | Vector2Vector2number | ExprRef | Parameter
        ] = Undefined,
        coefficient: Optional[float | ExprRef | Parameter] = Undefined,
        distance: Optional[float | ExprRef | Parameter] = Undefined,
        fraction: Optional[float | ExprRef | Parameter] = Undefined,
        lobes: Optional[float | ExprRef | Parameter] = Undefined,
        parallel: Optional[float | ExprRef | Parameter] = Undefined,
        precision: Optional[float | ExprRef | Parameter] = Undefined,
        radius: Optional[float | ExprRef | Parameter] = Undefined,
        ratio: Optional[float | ExprRef | Parameter] = Undefined,
        reflectX: Optional[bool | ExprRef | Parameter] = Undefined,
        reflectY: Optional[bool | ExprRef | Parameter] = Undefined,
        rotate: Optional[
            list[float] | Vector2number | Vector3number | ExprRef | Parameter
        ] = Undefined,
        scale: Optional[float | ExprRef | Parameter] = Undefined,
        spacing: Optional[float | Vector2number | ExprRef | Parameter] = Undefined,
        tilt: Optional[float | ExprRef | Parameter] = Undefined,
        translate: Optional[
            list[float] | Vector2number | ExprRef | Parameter
        ] = Undefined,
        **kwds: Any,
    ) -> Self:
        """
        Add a geographic projection to the chart.

        This is generally used either with ``mark_geoshape`` or with the
        ``latitude``/``longitude`` encodings.

        Available projection types are
        ['albers', 'albersUsa', 'azimuthalEqualArea', 'azimuthalEquidistant',
        'conicConformal', 'conicEqualArea', 'conicEquidistant', 'equalEarth', 'equirectangular',
        'gnomonic', 'identity', 'mercator', 'orthographic', 'stereographic', 'transverseMercator']

        Parameters
        ----------
        type : str
            The cartographic projection to use. This value is case-insensitive, for example
            `"albers"` and `"Albers"` indicate the same projection type. You can find all valid
            projection types [in the
            documentation](https://vega.github.io/vega-lite/docs/projection.html#projection-types).

            **Default value:** `equalEarth`
        center : List(float)
            Sets the projection's center to the specified center, a two-element array of
            longitude and latitude in degrees.

            **Default value:** `[0, 0]`
        clipAngle : float
            Sets the projection's clipping circle radius to the specified angle in degrees. If
            `null`, switches to [antimeridian](http://bl.ocks.org/mbostock/3788999) cutting
            rather than small-circle clipping.
        clipExtent : List(List(float))
            Sets the projection's viewport clip extent to the specified bounds in pixels. The
            extent bounds are specified as an array `[[x0, y0], [x1, y1]]`, where `x0` is the
            left-side of the viewport, `y0` is the top, `x1` is the right and `y1` is the
            bottom. If `null`, no viewport clipping is performed.
        coefficient : float
            The coefficient parameter for the ``hammer`` projection.

            **Default value:** ``2``
        distance : float
            For the ``satellite`` projection, the distance from the center of the sphere to the
            point of view, as a proportion of the sphere's radius. The recommended maximum clip
            angle for a given ``distance`` is acos(1 / distance) converted to degrees. If tilt
            is also applied, then more conservative clipping may be necessary.

            **Default value:** ``2.0``
        fraction : float
            The fraction parameter for the ``bottomley`` projection.

            **Default value:** ``0.5``, corresponding to a sin(ψ) where ψ = π/6.
        lobes : float
            The number of lobes in projections that support multi-lobe views: ``berghaus``,
            ``gingery``, or ``healpix``. The default value varies based on the projection type.
        parallel : float
            For conic projections, the `two standard parallels
            <https://en.wikipedia.org/wiki/Map_projection#Conic>`__ that define the map layout.
            The default depends on the specific conic projection used.
        precision : float
            Sets the threshold for the projection's [adaptive
            resampling](http://bl.ocks.org/mbostock/3795544) to the specified value in pixels.
            This value corresponds to the [Douglas-Peucker
            distance](http://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm).
             If precision is not specified, returns the projection's current resampling
            precision which defaults to `√0.5 ≅ 0.70710…`.
        radius : float
            The radius parameter for the ``airy`` or ``gingery`` projection. The default value
            varies based on the projection type.
        ratio : float
            The ratio parameter for the ``hill``, ``hufnagel``, or ``wagner`` projections. The
            default value varies based on the projection type.
        reflectX : boolean
            Sets whether or not the x-dimension is reflected (negated) in the output.
        reflectY : boolean
            Sets whether or not the y-dimension is reflected (negated) in the output.
        rotate : List(float)
            Sets the projection's three-axis rotation to the specified angles, which must be a
            two- or three-element array of numbers [`lambda`, `phi`, `gamma`] specifying the
            rotation angles in degrees about each spherical axis. (These correspond to yaw,
            pitch and roll.)

            **Default value:** `[0, 0, 0]`
        scale : float
            The projection's scale (zoom) factor, overriding automatic fitting. The default
            scale is projection-specific. The scale factor corresponds linearly to the distance
            between projected points; however, scale factor values are not equivalent across
            projections.
        spacing : float
            The spacing parameter for the ``lagrange`` projection.

            **Default value:** ``0.5``
        tilt : float
            The tilt angle (in degrees) for the ``satellite`` projection.

            **Default value:** ``0``.
        translate : List(float)
            The projection's translation offset as a two-element array ``[tx, ty]``,
            overriding automatic fitting.

        """
        projection = core.Projection(
            center=center,
            clipAngle=clipAngle,
            clipExtent=clipExtent,
            coefficient=coefficient,
            distance=distance,
            fraction=fraction,
            lobes=lobes,
            parallel=parallel,
            precision=precision,
            radius=radius,
            ratio=ratio,
            reflectX=reflectX,
            reflectY=reflectY,
            rotate=rotate,
            scale=scale,
            spacing=spacing,
            tilt=tilt,
            translate=translate,
            type=type,
            **kwds,
        )
        return self.properties(projection=projection)

    def _add_transform(self, *transforms: Transform) -> Self:
        """Copy the chart and add specified transforms to chart.transform."""
        copy = _top_schema_base(self).copy(deep=["transform"])
        if copy.transform is Undefined:
            copy.transform = []
        copy.transform.extend(transforms)
        return t.cast("Self", copy)

    def transform_aggregate(
        self,
        aggregate: Optional[list[AggregatedFieldDef]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        **kwds: dict[str, Any] | str,
    ) -> Self:
        """
        Add an :class:`AggregateTransform` to the schema.

        Parameters
        ----------
        aggregate : List(:class:`AggregatedFieldDef`)
            Array of objects that define fields to aggregate.
        groupby : List(string)
            The data fields to group by. If not specified, a single group containing all data
            objects will be used.
        **kwds : Union[TypingDict[str, Any], str]
            additional keywords are converted to aggregates using standard
            shorthand parsing.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        The aggregate transform allows you to specify transforms directly using
        the same shorthand syntax as used in encodings:

        >>> import altair as alt
        >>> chart1 = alt.Chart().transform_aggregate(
        ...     mean_acc="mean(Acceleration)", groupby=["Origin"]
        ... )
        >>> print(chart1.transform[0].to_json())  # doctest: +NORMALIZE_WHITESPACE
        {
          "aggregate": [
            {
              "as": "mean_acc",
              "field": "Acceleration",
              "op": "mean"
            }
          ],
          "groupby": [
            "Origin"
          ]
        }

        It also supports including AggregatedFieldDef instances or dicts directly,
        so you can create the above transform like this:

        >>> chart2 = alt.Chart().transform_aggregate(
        ...     [alt.AggregatedFieldDef(field="Acceleration", op="mean", **{"as": "mean_acc"})],
        ...     groupby=["Origin"],
        ... )
        >>> chart2.transform == chart1.transform
        True

        See Also
        --------
        alt.AggregateTransform : underlying transform object

        """
        if aggregate is Undefined:
            aggregate = []
        for key, val in kwds.items():
            parsed = utils.parse_shorthand(val)
            dct = {
                "as": key,
                "field": parsed.get("field", Undefined),
                "op": parsed.get("aggregate", Undefined),
            }
            assert isinstance(aggregate, list)
            aggregate.append(core.AggregatedFieldDef(**dct))
        return self._add_transform(
            core.AggregateTransform(aggregate=aggregate, groupby=groupby)
        )

    def transform_bin(
        self,
        as_: Optional[str | FieldName | list[str | FieldName]] = Undefined,
        field: Optional[str | FieldName] = Undefined,
        bin: Literal[True] | BinParams = True,
        **kwargs: Any,
    ) -> Self:
        """
        Add a :class:`BinTransform` to the schema.

        Parameters
        ----------
        as_ : anyOf(string, List(string))
            The output fields at which to write the start and end bin values.
        bin : anyOf(boolean, :class:`BinParams`)
            An object indicating bin properties, or simply ``true`` for using default bin
            parameters.
        field : string
            The data field to bin.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        >>> import altair as alt
        >>> chart = alt.Chart().transform_bin("x_binned", "x")
        >>> chart.transform[0]
        BinTransform({
          as: 'x_binned',
          bin: True,
          field: 'x'
        })

        >>> chart = alt.Chart().transform_bin("x_binned", "x", bin=alt.Bin(maxbins=10))
        >>> chart.transform[0]
        BinTransform({
          as: 'x_binned',
          bin: BinParams({
            maxbins: 10
          }),
          field: 'x'
        })

        See Also
        --------
        alt.BinTransform : underlying transform object

        """
        if as_ is not Undefined:
            if "as" in kwargs:
                msg = "transform_bin: both 'as_' and 'as' passed as arguments."
                raise ValueError(msg)
            kwargs["as"] = as_
        kwargs["bin"] = bin
        kwargs["field"] = field
        return self._add_transform(core.BinTransform(**kwargs))

    def transform_calculate(
        self,
        as_: Optional[str | FieldName] = Undefined,
        calculate: Optional[str | Expr | Expression] = Undefined,
        **kwargs: str | Expr | Expression,
    ) -> Self:
        """
        Add a :class:`CalculateTransform` to the schema.

        Parameters
        ----------
        as_ : string
            The field for storing the computed formula value.
        calculate : string or alt.expr.Expression
            An `expression <https://vega.github.io/vega-lite/docs/types.html#expression>`__
            string. Use the variable ``datum`` to refer to the current data object.
        **kwargs
            transforms can also be passed by keyword argument; see Examples

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        >>> import altair as alt
        >>> from altair import datum, expr

        >>> chart = alt.Chart().transform_calculate(y=2 * expr.sin(datum.x))
        >>> chart.transform[0]
        CalculateTransform({
          as: 'y',
          calculate: (2 * sin(datum.x))
        })

        It's also possible to pass the ``CalculateTransform`` arguments directly:

        >>> kwds = {"as_": "y", "calculate": "2 * sin(datum.x)"}
        >>> chart = alt.Chart().transform_calculate(**kwds)
        >>> chart.transform[0]
        CalculateTransform({
          as: 'y',
          calculate: '2 * sin(datum.x)'
        })

        As the first form is easier to write and understand, that is the
        recommended method.

        See Also
        --------
        alt.CalculateTransform : underlying transform object
        """
        calc_as: Optional[str | FieldName | Expr | Expression]
        if as_ is Undefined:
            calc_as = kwargs.pop("as", Undefined)
        elif "as" in kwargs:
            msg = "transform_calculate: both 'as_' and 'as' passed as arguments."
            raise ValueError(msg)
        else:
            calc_as = as_
        if calc_as is not Undefined or calculate is not Undefined:
            dct: dict[str, Any] = {"as": calc_as, "calculate": calculate}
            self = self._add_transform(core.CalculateTransform(**dct))
        for a, calculate in kwargs.items():
            dct = {"as": a, "calculate": calculate}
            self = self._add_transform(core.CalculateTransform(**dct))
        return self

    def transform_density(
        self,
        density: str | FieldName,
        as_: Optional[list[str | FieldName]] = Undefined,
        bandwidth: Optional[float] = Undefined,
        counts: Optional[bool] = Undefined,
        cumulative: Optional[bool] = Undefined,
        extent: Optional[list[float]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        maxsteps: Optional[int] = Undefined,
        minsteps: Optional[int] = Undefined,
        steps: Optional[int] = Undefined,
        resolve: Optional[ResolveMode_T] = Undefined,
    ) -> Self:
        """
        Add a :class:`DensityTransform` to the spec.

        Parameters
        ----------
        density : str
            The data field for which to perform density estimation.
        as_ : [str, str]
            The output fields for the sample value and corresponding density estimate.
            **Default value:** ``["value", "density"]``
        bandwidth : float
            The bandwidth (standard deviation) of the Gaussian kernel. If unspecified or set to
            zero, the bandwidth value is automatically estimated from the input data using
            Scott's rule.
        counts : boolean
            A boolean flag indicating if the output values should be probability estimates
            (false) or smoothed counts (true).
            **Default value:** ``false``
        cumulative : boolean
            A boolean flag indicating whether to produce density estimates (false) or cumulative
            density estimates (true).
            **Default value:** ``false``
        extent : List([float, float])
            A [min, max] domain from which to sample the distribution. If unspecified, the
            extent will be determined by the observed minimum and maximum values of the density
            value field.
        groupby : List(str)
            The data fields to group by. If not specified, a single group containing all data
            objects will be used.
        maxsteps : int
            The maximum number of samples to take along the extent domain for plotting the
            density. **Default value:** ``200``
        minsteps : int
            The minimum number of samples to take along the extent domain for plotting the
            density. **Default value:** ``25``
        steps : int
            The exact number of samples to take along the extent domain for plotting the
            density. If specified, overrides both minsteps and maxsteps to set an exact number
            of uniform samples. Potentially useful in conjunction with a fixed extent to ensure
            consistent sample points for stacked densities.
        resolve : Literal['independent', 'shared']
            Indicates how parameters for multiple densities should be resolved. If
            ``"independent"``, each density may have its own domain extent and dynamic number of
            curve sample steps. If ``"shared"``, the KDE transform will ensure that all
            densities are defined over a shared domain and curve steps, enabling stacking.

            **Default value:** ``"shared"``
        """
        return self._add_transform(
            core.DensityTransform(
                density=density,
                bandwidth=bandwidth,
                counts=counts,
                cumulative=cumulative,
                extent=extent,
                groupby=groupby,
                maxsteps=maxsteps,
                minsteps=minsteps,
                steps=steps,
                resolve=resolve,
                **{"as": as_},
            )
        )

    def transform_impute(
        self,
        impute: str | FieldName,
        key: str | FieldName,
        frame: Optional[list[int | None]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        keyvals: Optional[list[Any] | ImputeSequence] = Undefined,
        method: Optional[ImputeMethod_T | ImputeMethod] = Undefined,
        value: Optional[Any] = Undefined,
    ) -> Self:
        """
        Add an :class:`ImputeTransform` to the schema.

        Parameters
        ----------
        impute : string
            The data field for which the missing values should be imputed.
        key : string
            A key field that uniquely identifies data objects within a group.
            Missing key values (those occurring in the data but not in the current group) will
            be imputed.
        frame : List(anyOf(None, int))
            A frame specification as a two-element array used to control the window over which
            the specified method is applied. The array entries should either be a number
            indicating the offset from the current data object, or null to indicate unbounded
            rows preceding or following the current data object.  For example, the value ``[-5,
            5]`` indicates that the window should include five objects preceding and five
            objects following the current object.
            **Default value:** :  ``[null, null]`` indicating that the window includes all
            objects.
        groupby : List(string)
            An optional array of fields by which to group the values.
            Imputation will then be performed on a per-group basis.
        keyvals : anyOf(List(Mapping(required=[])), :class:`ImputeSequence`)
            Defines the key values that should be considered for imputation.
            An array of key values or an object defining a `number sequence
            <https://vega.github.io/vega-lite/docs/impute.html#sequence-def>`__.
            If provided, this will be used in addition to the key values observed within the
            input data.  If not provided, the values will be derived from all unique values of
            the ``key`` field. For ``impute`` in ``encoding``, the key field is the x-field if
            the y-field is imputed, or vice versa.
            If there is no impute grouping, this property *must* be specified.
        method : :class:`ImputeMethod`
            The imputation method to use for the field value of imputed data objects.
            One of ``value``, ``mean``, ``median``, ``max`` or ``min``.
            **Default value:**  ``"value"``
        value : Mapping(required=[])
            The field value to use when the imputation ``method`` is ``"value"``.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.ImputeTransform : underlying transform object
        """
        return self._add_transform(
            core.ImputeTransform(
                impute=impute,
                key=key,
                frame=frame,
                groupby=groupby,
                keyvals=keyvals,
                method=method,
                value=value,
            )
        )

    def transform_joinaggregate(
        self,
        joinaggregate: Optional[list[JoinAggregateFieldDef]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        **kwargs: str,
    ) -> Self:
        """
        Add a :class:`JoinAggregateTransform` to the schema.

        Parameters
        ----------
        joinaggregate : List(:class:`JoinAggregateFieldDef`)
            The definition of the fields in the join aggregate, and what calculations to use.
        groupby : List(string)
            The data fields for partitioning the data objects into separate groups. If
            unspecified, all data points will be in a single group.
        **kwargs
            joinaggregates can also be passed by keyword argument; see Examples.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        >>> import altair as alt
        >>> chart = alt.Chart().transform_joinaggregate(x="sum(y)")
        >>> chart.transform[0]
        JoinAggregateTransform({
          joinaggregate: [JoinAggregateFieldDef({
            as: 'x',
            field: 'y',
            op: 'sum'
          })]
        })

        See Also
        --------
        alt.JoinAggregateTransform : underlying transform object
        """
        if joinaggregate is Undefined:
            joinaggregate = []
        for key, val in kwargs.items():
            parsed = utils.parse_shorthand(val)
            dct = {
                "as": key,
                "field": parsed.get("field", Undefined),
                "op": parsed.get("aggregate", Undefined),
            }
            assert isinstance(joinaggregate, list)
            joinaggregate.append(core.JoinAggregateFieldDef(**dct))
        return self._add_transform(
            core.JoinAggregateTransform(joinaggregate=joinaggregate, groupby=groupby)
        )

    def transform_extent(
        self, extent: str | FieldName, param: str | ParameterName
    ) -> Self:
        """
        Add a :class:`ExtentTransform` to the spec.

        Parameters
        ----------
        extent : str
            The field of which to get the extent.
        param : str
            The name of the output parameter which will be created by
            the extent transform.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining
        """
        return self._add_transform(core.ExtentTransform(extent=extent, param=param))

    def transform_filter(
        self,
        predicate: Optional[_PredicateType] = Undefined,
        *more_predicates: _ComposablePredicateType,
        empty: Optional[bool] = Undefined,
        **constraints: _FieldEqualType,
    ) -> Self:
        """
        Add a :class:`FilterTransform` to the spec.

        The resulting predicate is an ``&`` reduction over ``predicate`` and optional ``*``, ``**``, arguments.

        Parameters
        ----------
        predicate
            A selection or test predicate. ``str`` input will be treated as a test operand.
        *more_predicates
            Additional predicates, restricted to types supporting ``&``.
        empty
            For selection parameters, the predicate of empty selections returns ``True`` by default.
            Override this behavior, with ``empty=False``.

            .. note::
                When ``predicate`` is a ``Parameter`` that is used more than once,
                ``self.transform_filter(..., empty=...)`` provides granular control for each occurrence.
        **constraints
            Specify `Field Equal Predicate`_'s.
            Shortcut for ``alt.datum.field_name == value``, see examples for usage.

        Warns
        -----
        AltairDeprecationWarning
            If called using ``filter`` as a keyword argument.

        See Also
        --------
        alt.when : Uses a similar syntax for defining conditional values.

        Notes
        -----
        - Directly inspired by the syntax used in `polars.DataFrame.filter`_.

        .. _Field Equal Predicate:
            https://vega.github.io/vega-lite/docs/predicate.html#equal-predicate
        .. _polars.DataFrame.filter:
            https://docs.pola.rs/api/python/stable/reference/dataframe/api/polars.DataFrame.filter.html

        Examples
        --------
        Setting up a common chart::

            import altair as alt
            from altair import datum
            from vega_datasets import data

            source = data.population.url
            chart = (
                alt.Chart(source)
                .mark_line()
                .encode(
                    x="age:O",
                    y="sum(people):Q",
                    color=alt.Color("year:O").legend(symbolType="square"),
                )
            )
            chart

        Singular predicates can be expressed via ``datum``::

            chart.transform_filter(datum.year <= 1980)

        We can also use selection parameters directly::

            selection = alt.selection_point(encodings=["color"], bind="legend")
            chart.transform_filter(selection).add_params(selection)

        Or a field predicate::

            between_1950_60 = alt.FieldRangePredicate(field="year", range=[1950, 1960])
            chart.transform_filter(between_1950_60) | chart.transform_filter(~between_1950_60)

        Predicates can be composed together using logical operands::

            chart.transform_filter(between_1950_60 | (datum.year == 1850))

        Predicates passed as positional arguments will be reduced with ``&``::

            chart.transform_filter(datum.year > 1980, datum.age != 90)

        Using keyword-argument ``constraints`` can simplify compositions like::

            verbose_composition = chart.transform_filter((datum.year == 2000) & (datum.sex == 1))
            chart.transform_filter(year=2000, sex=1)
        """
        if depr_filter := t.cast(Any, constraints.pop("filter", None)):
            utils.deprecated_warn(
                "Passing `filter` as a keyword is ambiguous.\n\n"
                "Use a positional argument for `<5.5.0` behavior.\n"
                "Or, `alt.datum['filter'] == ...` if referring to a column named 'filter'.",
                version="5.5.0",
            )
            if utils.is_undefined(predicate):
                predicate = depr_filter
            else:
                more_predicates = *more_predicates, depr_filter
        cond = _parse_when(predicate, *more_predicates, empty=empty, **constraints)
        return self._add_transform(core.FilterTransform(filter=cond.get("test", cond)))

    def transform_flatten(
        self,
        flatten: list[str | FieldName],
        as_: Optional[list[str | FieldName]] = Undefined,
    ) -> Self:
        """
        Add a :class:`FlattenTransform` to the schema.

        Parameters
        ----------
        flatten : List(string)
            An array of one or more data fields containing arrays to flatten.
            If multiple fields are specified, their array values should have a parallel
            structure, ideally with the same length.
            If the lengths of parallel arrays do not match,
            the longest array will be used with ``null`` values added for missing entries.
        as : List(string)
            The output field names for extracted array values.
            **Default value:** The field name of the corresponding array field

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.FlattenTransform : underlying transform object
        """
        return self._add_transform(
            core.FlattenTransform(flatten=flatten, **{"as": as_})
        )

    def transform_fold(
        self,
        fold: list[str | FieldName],
        as_: Optional[list[str | FieldName]] = Undefined,
    ) -> Self:
        """
        Add a :class:`FoldTransform` to the spec.

        Parameters
        ----------
        fold : List(string)
            An array of data fields indicating the properties to fold.
        as : [string, string]
            The output field names for the key and value properties produced by the fold
            transform. Default: ``["key", "value"]``

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        Chart.transform_pivot : pivot transform - opposite of fold.
        alt.FoldTransform : underlying transform object
        """
        return self._add_transform(core.FoldTransform(fold=fold, **{"as": as_}))

    def transform_loess(
        self,
        on: str | FieldName,
        loess: str | FieldName,
        as_: Optional[list[str | FieldName]] = Undefined,
        bandwidth: Optional[float] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
    ) -> Self:
        """
        Add a :class:`LoessTransform` to the spec.

        Parameters
        ----------
        on : str
            The data field of the independent variable to use a predictor.
        loess : str
            The data field of the dependent variable to smooth.
        as_ : [str, str]
            The output field names for the smoothed points generated by the loess transform.
            **Default value:** The field names of the input x and y values.
        bandwidth : float
            A bandwidth parameter in the range ``[0, 1]`` that determines the amount of
            smoothing. **Default value:** ``0.3``
        groupby : List(str)
            The data fields to group by. If not specified, a single group containing all data
            objects will be used.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        Chart.transform_regression: regression transform
        alt.LoessTransform : underlying transform object
        """
        return self._add_transform(
            core.LoessTransform(
                loess=loess, on=on, bandwidth=bandwidth, groupby=groupby, **{"as": as_}
            )
        )

    def transform_lookup(
        self,
        lookup: Optional[str] = Undefined,
        from_: Optional[LookupData | LookupSelection] = Undefined,
        as_: Optional[str | FieldName | list[str | FieldName]] = Undefined,
        default: Optional[str] = Undefined,
        **kwargs: Any,
    ) -> Self:
        """
        Add a :class:`DataLookupTransform` or :class:`SelectionLookupTransform` to the chart.

        Parameters
        ----------
        lookup : string
            Key in primary data source.
        from_ : anyOf(:class:`LookupData`, :class:`LookupSelection`)
            Secondary data reference.
        as_ : anyOf(string, List(string))
            The output fields on which to store the looked up data values.

            For data lookups, this property may be left blank if ``from_.fields``
            has been specified (those field names will be used); if ``from_.fields``
            has not been specified, ``as_`` must be a string.

            For selection lookups, this property is optional: if unspecified,
            looked up values will be stored under a property named for the selection;
            and if specified, it must correspond to ``from_.fields``.
        default : string
            The default value to use if lookup fails. **Default value:** ``null``

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.DataLookupTransform : underlying transform object
        alt.SelectionLookupTransform : underlying transform object
        """
        if as_ is not Undefined:
            if "as" in kwargs:
                msg = "transform_lookup: both 'as_' and 'as' passed as arguments."
                raise ValueError(msg)
            kwargs["as"] = as_
        if from_ is not Undefined:
            if "from" in kwargs:
                msg = "transform_lookup: both 'from_' and 'from' passed as arguments."
                raise ValueError(msg)
            kwargs["from"] = from_
        kwargs["lookup"] = lookup
        kwargs["default"] = default
        return self._add_transform(core.LookupTransform(**kwargs))

    def transform_pivot(
        self,
        pivot: str | FieldName,
        value: str | FieldName,
        groupby: Optional[list[str | FieldName]] = Undefined,
        limit: Optional[int] = Undefined,
        op: Optional[AggregateOp_T | AggregateOp] = Undefined,
    ) -> Self:
        """
        Add a :class:`PivotTransform` to the chart.

        Parameters
        ----------
        pivot : str
            The data field to pivot on. The unique values of this field become new field names
            in the output stream.
        value : str
            The data field to populate pivoted fields. The aggregate values of this field become
            the values of the new pivoted fields.
        groupby : List(str)
            The optional data fields to group by. If not specified, a single group containing
            all data objects will be used.
        limit : int
            An optional parameter indicating the maximum number of pivoted fields to generate.
            The default ( ``0`` ) applies no limit. The pivoted ``pivot`` names are sorted in
            ascending order prior to enforcing the limit.
            **Default value:** ``0``
        op : Literal['argmax', 'argmin', 'average', 'count', 'distinct', 'max', 'mean', 'median', 'min', 'missing', 'product', 'q1', 'q3', 'ci0', 'ci1', 'stderr', 'stdev', 'stdevp', 'sum', 'valid', 'values', 'variance', 'variancep', 'exponential', 'exponentialb']
            The aggregation operation to apply to grouped ``value`` field values.
            **Default value:** ``sum``

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        Chart.transform_fold : fold transform - opposite of pivot.
        alt.PivotTransform : underlying transform object
        """
        return self._add_transform(
            core.PivotTransform(
                pivot=pivot, value=value, groupby=groupby, limit=limit, op=op
            )
        )

    def transform_quantile(
        self,
        quantile: str | FieldName,
        as_: Optional[list[str | FieldName]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        probs: Optional[list[float]] = Undefined,
        step: Optional[float] = Undefined,
    ) -> Self:
        """
        Add a :class:`QuantileTransform` to the chart.

        Parameters
        ----------
        quantile : str
            The data field for which to perform quantile estimation.
        as : [str, str]
            The output field names for the probability and quantile values.
        groupby : List(str)
            The data fields to group by. If not specified, a single group containing all data
            objects will be used.
        probs : List(float)
            An array of probabilities in the range (0, 1) for which to compute quantile values.
            If not specified, the *step* parameter will be used.
        step : float
            A probability step size (default 0.01) for sampling quantile values. All values from
            one-half the step size up to 1 (exclusive) will be sampled. This parameter is only
            used if the *probs* parameter is not provided. **Default value:** ``["prob", "value"]``

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.QuantileTransform : underlying transform object
        """
        return self._add_transform(
            core.QuantileTransform(
                quantile=quantile,
                groupby=groupby,
                probs=probs,
                step=step,
                **{"as": as_},
            )
        )

    def transform_regression(
        self,
        on: str | FieldName,
        regression: str | FieldName,
        as_: Optional[list[str | FieldName]] = Undefined,
        extent: Optional[list[float]] = Undefined,
        groupby: Optional[list[str | FieldName]] = Undefined,
        method: Optional[
            Literal["linear", "log", "exp", "pow", "quad", "poly"]
        ] = Undefined,
        order: Optional[int] = Undefined,
        params: Optional[bool] = Undefined,
    ) -> Self:
        """
        Add a :class:`RegressionTransform` to the chart.

        Parameters
        ----------
        on : str
            The data field of the independent variable to use a predictor.
        regression : str
            The data field of the dependent variable to predict.
        as_ : [str, str]
            The output field names for the smoothed points generated by the regression
            transform. **Default value:** The field names of the input x and y values.
        extent : [float, float]
            A [min, max] domain over the independent (x) field for the starting and ending
            points of the generated trend line.
        groupby : List(str)
            The data fields to group by. If not specified, a single group containing all data
            objects will be used.
        method : enum('linear', 'log', 'exp', 'pow', 'quad', 'poly')
            The functional form of the regression model. One of ``"linear"``, ``"log"``,
            ``"exp"``, ``"pow"``, ``"quad"``, or ``"poly"``.  **Default value:** ``"linear"``
        order : int
            The polynomial order (number of coefficients) for the 'poly' method.
            **Default value:** ``3``
        params : boolean
            A boolean flag indicating if the transform should return the regression model
            parameters (one object per group), rather than trend line points.
            The resulting objects include a ``coef`` array of fitted coefficient values
            (starting with the intercept term and then including terms of increasing order)
            and an ``rSquared`` value (indicating the total variance explained by the model).
            **Default value:** ``false``

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        Chart.transform_loess : LOESS transform
        alt.RegressionTransform : underlying transform object
        """
        return self._add_transform(
            core.RegressionTransform(
                regression=regression,
                on=on,
                extent=extent,
                groupby=groupby,
                method=method,
                order=order,
                params=params,
                **{"as": as_},
            )
        )

    def transform_sample(self, sample: int = 1000) -> Self:
        """
        Add a :class:`SampleTransform` to the schema.

        Parameters
        ----------
        sample : int
            The maximum number of data objects to include in the sample. Default: 1000.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.SampleTransform : underlying transform object
        """
        return self._add_transform(core.SampleTransform(sample))

    def transform_stack(
        self,
        as_: str | FieldName | list[str],
        stack: str | FieldName,
        groupby: list[str | FieldName],
        offset: Optional[StackOffset_T] = Undefined,
        sort: Optional[list[SortField]] = Undefined,
    ) -> Self:
        """
        Add a :class:`StackTransform` to the schema.

        Parameters
        ----------
        as_ : anyOf(string, List(string))
            Output field names. This can be either a string or an array of strings with
            two elements denoting the name for the fields for stack start and stack end
            respectively.
            If a single string(eg."val") is provided, the end field will be "val_end".
        stack : string
            The field which is stacked.
        groupby : List(string)
            The data fields to group by.
        offset : enum('zero', 'center', 'normalize')
            Mode for stacking marks. Default: 'zero'.
        sort : List(:class:`SortField`)
            Field that determines the order of leaves in the stacked charts.

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        See Also
        --------
        alt.StackTransform : underlying transform object
        """
        return self._add_transform(
            core.StackTransform(
                stack=stack, groupby=groupby, offset=offset, sort=sort, **{"as": as_}
            )
        )

    def transform_timeunit(
        self,
        as_: Optional[str | FieldName] = Undefined,
        field: Optional[str | FieldName] = Undefined,
        timeUnit: Optional[MultiTimeUnit_T | SingleTimeUnit_T | TimeUnit] = Undefined,
        **kwargs: str,
    ) -> Self:
        """
        Add a :class:`TimeUnitTransform` to the schema.

        Parameters
        ----------
        as_ : string
            The output field to write the timeUnit value.
        field : string
            The data field to apply time unit.
        timeUnit : str or :class:`TimeUnit`
            The timeUnit.
        **kwargs
            transforms can also be passed by keyword argument; see Examples

        Returns
        -------
        self : Chart object
            returns chart to allow for chaining

        Examples
        --------
        >>> import altair as alt
        >>> from altair import datum, expr

        >>> chart = alt.Chart().transform_timeunit(month="month(date)")
        >>> chart.transform[0]
        TimeUnitTransform({
          as: 'month',
          field: 'date',
          timeUnit: 'month'
        })

        It's also possible to pass the ``TimeUnitTransform`` arguments directly;
        this is most useful in cases where the desired field name is not a
        valid python identifier:

        >>> kwds = {"as": "month", "timeUnit": "month", "field": "The Month"}
        >>> chart = alt.Chart().transform_timeunit(**kwds)
        >>> chart.transform[0]
        TimeUnitTransform({
          as: 'month',
          field: 'The Month',
          timeUnit: 'month'
        })

        As the first form is easier to write and understand, that is the
        recommended method.

        See Also
        --------
        alt.TimeUnitTransform : underlying transform object

        """
        if as_ is Undefined:
            as_ = kwargs.pop("as", Undefined)
        elif "as" in kwargs:
            msg = "transform_timeunit: both 'as_' and 'as' passed as arguments."
            raise ValueError(msg)
        if as_ is not Undefined:
            dct: dict[str, Any] = {"as": as_, "timeUnit": timeUnit, "field": field}
            self = self._add_transform(core.TimeUnitTransform(**dct))
        for as_, shorthand in kwargs.items():
            dct = utils.parse_shorthand(
                shorthand,
                parse_timeunits=True,
                parse_aggregates=False,
                parse_types=False,
            )
            dct.pop("type", None)
            dct["as"] = as_
            if "timeUnit" not in dct:
                msg = f"'{shorthand}' must include a valid timeUnit"
                raise ValueError(msg)
            self = self._add_transform(core.TimeUnitTransform(**dct))
        return self

    def transform_window(
        self,
        window: Optional[list[WindowFieldDef]] = Undefined,
        frame: Optional[list[int | None]] = Undefined,
        groupby: Optional[list[str]] = Undefined,
        ignorePeers: Optional[bool] = Undefined,
        sort: Optional[list[SortField | dict[str, str]]] = Undefined,
        **kwargs: str,
    ) -> Self:
        """
        Add a :class:`WindowTransform` to the schema.

        Parameters
        ----------
        window : List(:class:`WindowFieldDef`)
            The definition of the fields in the window, and what calculations to use.
        frame : List(anyOf(None, int))
            A frame specification as a two-element array indicating how the sliding window
            should proceed. The array entries should either be a number indicating the offset
            from the current data object, or null to indicate unbounded rows preceding or
            following the current data object. The default value is ``[null, 0]``, indicating
            that the sliding window includes the current object and all preceding objects. The
            value ``[-5, 5]`` indicates that the window should include five objects preceding
            and five objects following the current object. Finally, ``[null, null]`` indicates
            that the window frame should always include all data objects. The only operators
            affected are the aggregation operations and the ``first_value``, ``last_value``, and
            ``nth_value`` window operations. The other window operations are not affected by
            this.

            **Default value:** :  ``[null, 0]`` (includes the current object and all preceding
            objects)
        groupby : List(string)
            The data fields for partitioning the data objects into separate windows. If
            unspecified, all data points will be in a single group.
        ignorePeers : boolean
            Indicates if the sliding window frame should ignore peer values. (Peer values are
            those considered identical by the sort criteria). The default is false, causing the
            window frame to expand to include all peer values. If set to true, the window frame
            will be defined by offset values only. This setting only affects those operations
            that depend on the window frame, namely aggregation operations and the first_value,
            last_value, and nth_value window operations.

            **Default value:** ``false``
        sort : List(:class:`SortField`)
            A sort field definition for sorting data objects within a window. If two data
            objects are considered equal by the comparator, they are considered “peer” values of
            equal rank. If sort is not specified, the order is undefined: data objects are
            processed in the order they are observed and none are considered peers (the
            ignorePeers parameter is ignored and treated as if set to ``true`` ).
        **kwargs
            transforms can also be passed by keyword argument; see Examples

        Examples
        --------
        A cumulative line chart

        >>> import altair as alt
        >>> import numpy as np
        >>> import pandas as pd
        >>> data = pd.DataFrame({"x": np.arange(100), "y": np.random.randn(100)})
        >>> chart = (
        ...     alt.Chart(data)
        ...     .mark_line()
        ...     .encode(x="x:Q", y="ycuml:Q")
        ...     .transform_window(ycuml="sum(y)")
        ... )
        >>> chart.transform[0]
        WindowTransform({
          window: [WindowFieldDef({
            as: 'ycuml',
            field: 'y',
            op: 'sum'
          })]
        })

        """
        w = window if isinstance(window, list) else []
        if kwargs:
            for as_, shorthand in kwargs.items():
                kwds: dict[str, Any] = {"as": as_}
                kwds.update(
                    utils.parse_shorthand(
                        shorthand,
                        parse_aggregates=False,
                        parse_window_ops=True,
                        parse_timeunits=False,
                        parse_types=False,
                    )
                )
                w.append(core.WindowFieldDef(**kwds))

        return self._add_transform(
            core.WindowTransform(
                window=w or Undefined,
                frame=frame,
                groupby=groupby,
                ignorePeers=ignorePeers,
                sort=sort,
            )
        )

    # Display-related methods

    def _repr_mimebundle_(self, *args, **kwds) -> MimeBundleType | None:  # type:ignore[return]  # noqa: ANN002, ANN003
        """Return a MIME bundle for display in Jupyter frontends."""
        # Catch errors explicitly to get around issues in Jupyter frontend
        # see https://github.com/ipython/ipython/issues/11038
        try:
            dct = self.to_dict(context={"pre_transform": False})
        except Exception:
            utils.display_traceback(in_ipython=True)
            return {}
        else:
            if renderer := renderers.get():
                return renderer(dct)

    def display(
        self,
        renderer: Optional[Literal["canvas", "svg"]] = Undefined,
        theme: Optional[str] = Undefined,
        actions: Optional[bool | dict] = Undefined,
        **kwargs: Any,
    ) -> None:
        """
        Display chart in Jupyter notebook or JupyterLab.

        Parameters are passed as options to vega-embed within supported frontends.
        See https://github.com/vega/vega-embed#options for details.

        Parameters
        ----------
        renderer : string ('canvas' or 'svg')
            The renderer to use
        theme : string
            The Vega theme name to use; see https://github.com/vega/vega-themes
        actions : bool or dict
            Specify whether action links ("Open In Vega Editor", etc.) are
            included in the view.
        **kwargs :
            Additional parameters are also passed to vega-embed as options.

        """
        from IPython.display import display

        if renderer is not Undefined:
            kwargs["renderer"] = renderer
        if theme is not Undefined:
            kwargs["theme"] = theme
        if actions is not Undefined:
            kwargs["actions"] = actions

        if kwargs:
            options = renderers.options.copy()
            options["embed_options"] = options.get("embed_options", {}).copy()
            options["embed_options"].update(kwargs)
            with renderers.enable(**options):
                display(self)
        else:
            display(self)

    @utils.deprecated(version="4.1.0", alternative="show")
    def serve(
        self,
        ip="127.0.0.1",  # noqa: ANN001
        port=8888,  # noqa: ANN001
        n_retries=50,  # noqa: ANN001
        files=None,  # noqa: ANN001
        jupyter_warning=True,  # noqa: ANN001
        open_browser=True,  # noqa: ANN001
        http_server=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ) -> None:
        """'serve' is deprecated. Use 'show' instead."""
        from altair.utils.server import serve

        html = io.StringIO()
        self.save(html, format="html", **kwargs)
        html.seek(0)

        serve(
            html.read(),
            ip=ip,
            port=port,
            n_retries=n_retries,
            files=files,
            jupyter_warning=jupyter_warning,
            open_browser=open_browser,
            http_server=http_server,
        )

    def show(self) -> None:
        """Display the chart using the active renderer."""
        if renderers.active == "browser":
            # Opens browser window as side-effect.
            # We use a special case here so that IPython is not required
            self._repr_mimebundle_()
        else:
            # Mime-bundle based renderer, requires running in an IPython session
            from IPython.display import display

            display(self)

    @utils.use_signature(core.Resolve)
    def _set_resolve(self, **kwargs: Any):  # noqa: ANN202
        """Copy the chart and update the resolve property with kwargs."""
        if not hasattr(self, "resolve"):
            msg = f"{self.__class__} object has no attribute " "'resolve'"
            raise ValueError(msg)
        copy = _top_schema_base(self).copy(deep=["resolve"])
        if copy.resolve is Undefined:
            copy.resolve = core.Resolve()
        for key, val in kwargs.items():
            copy.resolve[key] = val
        return copy

    @utils.use_signature(core.AxisResolveMap)
    def resolve_axis(self, *args: Any, **kwargs: Any) -> Self:
        check = _top_schema_base(self)
        r = check._set_resolve(axis=core.AxisResolveMap(*args, **kwargs))
        return t.cast("Self", r)

    @utils.use_signature(core.LegendResolveMap)
    def resolve_legend(self, *args: Any, **kwargs: Any) -> Self:
        check = _top_schema_base(self)
        r = check._set_resolve(legend=core.LegendResolveMap(*args, **kwargs))
        return t.cast("Self", r)

    @utils.use_signature(core.ScaleResolveMap)
    def resolve_scale(self, *args: Any, **kwargs: Any) -> Self:
        check = _top_schema_base(self)
        r = check._set_resolve(scale=core.ScaleResolveMap(*args, **kwargs))
        return t.cast("Self", r)


class _EncodingMixin(channels._EncodingMixin):
    data: Any

    def facet(
        self,
        facet: Optional[str | Facet] = Undefined,
        row: Optional[str | FacetFieldDef | Row] = Undefined,
        column: Optional[str | FacetFieldDef | Column] = Undefined,
        data: Optional[ChartDataType] = Undefined,
        columns: Optional[int] = Undefined,
        **kwargs: Any,
    ) -> FacetChart:
        """
        Create a facet chart from the current chart.

        Faceted charts require data to be specified at the top level; if data
        is not specified, the data from the current chart will be used at the
        top level.

        Parameters
        ----------
        facet : string, Facet (optional)
            The data column to use as an encoding for a wrapped facet.
            If specified, then neither row nor column may be specified.
        column : string, Column, FacetFieldDef (optional)
            The data column to use as an encoding for a column facet.
            May be combined with row argument, but not with facet argument.
        row : string or Row, FacetFieldDef (optional)
            The data column to use as an encoding for a row facet.
            May be combined with column argument, but not with facet argument.
        data : string or dataframe (optional)
            The dataset to use for faceting. If not supplied, then data must
            be specified in the top-level chart that calls this method.
        columns : integer
            the maximum number of columns for a wrapped facet.

        Returns
        -------
        self :
            for chaining
        """
        facet_specified = facet is not Undefined
        rowcol_specified = row is not Undefined or column is not Undefined

        if facet_specified and rowcol_specified:
            msg = "facet argument cannot be combined with row/column argument."
            raise ValueError(msg)
        self = _top_schema_base(self)

        if data is Undefined:
            if self.data is Undefined:
                msg = (
                    "Facet charts require data to be specified at the top level. "
                    "If you are trying to facet layered or concatenated charts, "
                    "ensure that the same data variable is passed to each chart "
                    "or specify the data inside the facet method instead."
                )
                raise ValueError(msg)
            self = _top_schema_base(self).copy(deep=False)
            data, self.data = self.data, Undefined

        f: Facet | FacetMapping
        if not utils.is_undefined(facet):
            f = channels.Facet(facet) if isinstance(facet, str) else facet
        else:
            r: Any = row
            f = FacetMapping(row=r, column=column)

        return FacetChart(spec=self, facet=f, data=data, columns=columns, **kwargs)  # pyright: ignore[reportArgumentType]


class Chart(
    TopLevelMixin, _EncodingMixin, mixins.MarkMethodMixin, core.TopLevelUnitSpec
):
    """
    Create a basic Altair/Vega-Lite chart.

    Although it is possible to set all Chart properties as constructor attributes,
    it is more idiomatic to use methods such as ``mark_point()``, ``encode()``,
    ``transform_filter()``, ``properties()``, etc. See Altair's documentation
    for details and examples: http://altair-viz.github.io/.

    Parameters
    ----------
    data : Data
        An object describing the data source
    mark : AnyMark
        A `MarkDef` or `CompositeMarkDef` object, or a string describing the mark type
        (one of `"arc"`, `"area"`, `"bar"`, `"circle"`, `"geoshape"`, `"image"`,
        `"line"`, `"point"`, `"rule"`, `"rect"`, `"square"`, `"text"`, `"tick"`,
        `"trail"`, `"boxplot"`, `"errorband"`, and `"errorbar"`).
    encoding : FacetedEncoding
        A key-value mapping between encoding channels and definition of fields.
    autosize : anyOf(AutosizeType, AutoSizeParams)
        Sets how the visualization size should be determined. If a string, should be one of
        `"pad"`, `"fit"` or `"none"`. Object values can additionally specify parameters for
        content sizing and automatic resizing. `"fit"` is only supported for single and
        layered views that don't use `rangeStep`.  Default value: `pad`
    background : string
        CSS color property to use as the background of visualization.

        **Default value:** none (transparent)
    config : Config
        Vega-Lite configuration object.  This property can only be defined at the top-level
        of a specification.
    description : string
        Description of this mark for commenting purpose.
    height : float
        The height of a visualization.
    name : string
        Name of the visualization for later reference.
    padding : Padding
        The default visualization padding, in pixels, from the edge of the visualization
        canvas to the data rectangle.  If a number, specifies padding for all sides. If an
        object, the value should have the format `{"left": 5, "top": 5, "right": 5,
        "bottom": 5}` to specify padding for each side of the visualization.  Default
        value: `5`
    projection : Projection
        An object defining properties of geographic projection.  Works with `"geoshape"`
        marks and `"point"` or `"line"` marks that have a channel (one or more of `"X"`,
        `"X2"`, `"Y"`, `"Y2"`) with type `"latitude"`, or `"longitude"`.
    selection : Mapping(required=[])
        A key-value mapping between selection names and definitions.
    title : anyOf(string, TitleParams)
        Title for the plot.
    transform : List(Transform)
        An array of data transformations such as filter and new field calculation.
    width : float
        The width of a visualization.
    """

    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        encoding: Optional[FacetedEncoding] = Undefined,
        mark: Optional[AnyMark | Mark_T | CompositeMark_T] = Undefined,
        width: Optional[int | dict | Step | Literal["container"]] = Undefined,
        height: Optional[int | dict | Step | Literal["container"]] = Undefined,
        **kwargs: Any,
    ) -> None:
        # Data type hints won't match with what TopLevelUnitSpec expects
        # as there is some data processing happening when converting to
        # a VL spec
        super().__init__(
            data=data,  # type: ignore[arg-type]
            encoding=encoding,
            mark=mark,
            width=width,
            height=height,
            **kwargs,
        )

    _counter: int = 0

    @classmethod
    def _get_name(cls) -> str:
        cls._counter += 1
        return f"view_{cls._counter}"

    @classmethod
    def from_dict(
        cls: type[_TSchemaBase], dct: dict[str, Any], validate: bool = True
    ) -> _TSchemaBase:
        """
        Construct a ``Chart`` from a dictionary representation.

        Parameters
        ----------
        dct : dictionary
            The dict from which to construct the ``Chart``.
        validate : boolean
            If True (default), then validate the input against the schema.

        Raises
        ------
        jsonschema.ValidationError :
            If ``validate`` and ``dct`` does not conform to the schema
        """
        _tp: Any
        for tp in TopLevelMixin.__subclasses__():
            _tp = super() if tp is Chart else tp
            try:
                return _tp.from_dict(dct, validate=validate)
            except jsonschema.ValidationError:
                pass

        # As a last resort, try using the Root vegalite object
        return t.cast(_TSchemaBase, core.Root.from_dict(dct, validate))

    def to_dict(
        self,
        validate: bool = True,
        *,
        format: Literal["vega-lite", "vega"] = "vega-lite",
        ignore: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Convert the ``Chart`` to a dictionary suitable for JSON export.

        Parameters
        ----------
        validate : bool, optional
            If True (default), then validate the result against the schema.
        format : {"vega-lite", "vega"}, optional
            The chart specification format.
            The `"vega"` format relies on the active Vega-Lite compiler plugin, which
            by default requires the vl-convert-python package.
        ignore : list[str], optional
            A list of keys to ignore.
        context : dict[str, Any], optional
            A context dictionary.

        Raises
        ------
        SchemaValidationError :
            If ``validate`` and the result does not conform to the schema.

        Notes
        -----
        - ``ignore``, ``context`` are usually not needed to be specified as a user.
        - *Technical*: ``ignore`` will **not** be passed to child :meth:`.to_dict()`.
        """
        context = context or {}
        kwds: Map = {"validate": validate, "format": format, "ignore": ignore, "context": context}  # fmt: skip
        if self.data is Undefined and "data" not in context:
            # No data specified here or in parent: inject empty data
            # for easier specification of datum encodings.
            copy = self.copy(deep=False)
            copy.data = core.InlineData(values=[{}])
            return super(Chart, copy).to_dict(**kwds)
        return super().to_dict(**kwds)

    def transformed_data(
        self, row_limit: int | None = None, exclude: Iterable[str] | None = None
    ) -> DataFrameLike | None:
        """
        Evaluate a Chart's transforms.

        Evaluate the data transforms associated with a Chart and return the
        transformed data a DataFrame

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        DataFrame
            Transformed data as a DataFrame
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params:
            return self
        copy = self.copy(deep=["params"])
        if copy.params is Undefined:
            copy.params = []

        for s in params:
            copy.params.append(s.param)
        return copy

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *params) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*params)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        encodings: list[SingleDefUnitChannel_T] = []
        if bind_x:
            encodings.append("x")
        if bind_y:
            encodings.append("y")
        return self.add_params(selection_interval(bind="scales", encodings=encodings))


def _check_if_valid_subspec(
    spec: ConcatType | LayerType,
    classname: Literal[
        "ConcatChart",
        "FacetChart",
        "HConcatChart",
        "LayerChart",
        "RepeatChart",
        "VConcatChart",
    ],
) -> None:
    """Raise a `TypeError` if `spec` is not a valid sub-spec."""
    if not isinstance(spec, SchemaBase):
        msg = f"Only chart objects can be used in {classname}."
        raise TypeError(msg)
    for attr in TOPLEVEL_ONLY_KEYS:
        if spec._get(attr) is not Undefined:
            msg = (
                f"Objects with {attr!r} attribute cannot be used within {classname}. "
                f"Consider defining the {attr} attribute in the {classname} object instead."
            )
            raise TypeError(msg)


def _check_if_can_be_layered(spec: LayerType) -> None:
    """Raise a `TypeError` if `spec` cannot be layered."""

    def _get_any(spec: LayerType, *attrs: str) -> bool:
        return any(spec._get(attr) is not Undefined for attr in attrs)

    base_msg = "charts cannot be layered. Instead, layer the charts before"

    encoding: Any = spec._get("encoding")
    if not utils.is_undefined(encoding):
        for channel in ["row", "column", "facet"]:
            if encoding._get(channel) is not Undefined:
                msg = f"Faceted {base_msg} faceting."
                raise TypeError(msg)
    if isinstance(spec, (Chart, LayerChart)):
        return
    elif is_chart_type(spec) or _get_any(
        spec, "facet", "repeat", "concat", "hconcat", "vconcat"
    ):
        if isinstance(spec, FacetChart) or spec._get("facet") is not Undefined:
            msg = f"Faceted {base_msg} faceting."
        elif isinstance(spec, RepeatChart) or spec._get("repeat") is not Undefined:
            msg = f"Repeat {base_msg} repeating."
        elif isinstance(spec, (ConcatChart, HConcatChart, VConcatChart)) or _get_any(
            spec, "concat", "hconcat", "vconcat"
        ):
            msg = f"Concatenated {base_msg} concatenating."
        else:
            msg = "Should be unreachable"
            raise NotImplementedError(msg)
        raise TypeError(msg)


class RepeatChart(TopLevelMixin, core.TopLevelRepeatSpec):
    """A chart repeated across rows and columns with small changes."""

    def __init__(
        self,
        repeat: Optional[list[str] | LayerRepeatMapping | RepeatMapping] = Undefined,
        spec: Optional[ChartType] = Undefined,
        align: Optional[dict | SchemaBase | LayoutAlign_T] = Undefined,
        autosize: Optional[dict | SchemaBase | AutosizeType_T] = Undefined,
        background: Optional[
            str | dict | Parameter | SchemaBase | ColorName_T
        ] = Undefined,
        bounds: Optional[Literal["full", "flush"]] = Undefined,
        center: Optional[bool | dict | SchemaBase] = Undefined,
        columns: Optional[int] = Undefined,
        config: Optional[dict | SchemaBase] = Undefined,
        data: Optional[ChartDataType] = Undefined,
        datasets: Optional[dict | SchemaBase] = Undefined,
        description: Optional[str] = Undefined,
        name: Optional[str] = Undefined,
        padding: Optional[dict | float | Parameter | SchemaBase] = Undefined,
        params: Optional[Sequence[_Parameter]] = Undefined,
        resolve: Optional[dict | SchemaBase] = Undefined,
        spacing: Optional[dict | float | SchemaBase] = Undefined,
        title: Optional[str | dict | SchemaBase | Sequence[str]] = Undefined,
        transform: Optional[Sequence[dict | SchemaBase]] = Undefined,
        usermeta: Optional[dict | SchemaBase] = Undefined,
        **kwds: Any,
    ) -> None:
        tp_name = type(self).__name__
        if utils.is_undefined(spec):
            msg = f"{tp_name!r} requires a `spec`, but got: {spec!r}"
            raise TypeError(msg)
        _check_if_valid_subspec(spec, "RepeatChart")
        _spec_as_list = [spec]
        params, _spec_as_list = _combine_subchart_params(params, _spec_as_list)
        spec = _spec_as_list[0]
        if isinstance(spec, (Chart, LayerChart)):
            if utils.is_undefined(repeat):
                msg = f"{tp_name!r} requires a `repeat`, but got: {repeat!r}"
                raise TypeError(msg)
            params = _repeat_names(params, repeat, spec)
        super().__init__(
            repeat=repeat,
            spec=spec,
            align=align,
            autosize=autosize,
            background=background,
            bounds=bounds,
            center=center,
            columns=columns,
            config=config,
            data=data,
            datasets=datasets,
            description=description,
            name=name,
            padding=padding,
            params=params,
            resolve=resolve,
            spacing=spacing,
            title=title,
            transform=transform,
            usermeta=usermeta,
            **kwds,
        )

    def transformed_data(
        self, row_limit: int | None = None, exclude: Iterable[str] | None = None
    ) -> DataFrameLike | None:
        """
        Evaluate a RepeatChart's transforms.

        Evaluate the data transforms associated with a RepeatChart and return the
        transformed data a DataFrame

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Raises
        ------
        NotImplementedError
            RepeatChart does not yet support transformed_data
        """
        msg = "transformed_data is not yet implemented for RepeatChart"
        raise NotImplementedError(msg)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        copy = self.copy(deep=False)
        copy.spec = copy.spec.interactive(name=name, bind_x=bind_x, bind_y=bind_y)
        return copy

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or self.spec is Undefined:
            return self
        copy = self.copy()
        copy.spec = copy.spec.add_params(*params)
        return copy.copy()

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def repeat(
    repeater: Literal["row", "column", "repeat", "layer"] = "repeat",
) -> RepeatRef:
    """
    Tie a channel to the row or column within a repeated chart.

    The output of this should be passed to the ``field`` attribute of
    a channel.

    Parameters
    ----------
    repeater : {'row'|'column'|'repeat'|'layer'}
        The repeater to tie the field to. Default is 'repeat'.

    Returns
    -------
    repeat : RepeatRef object
    """
    if repeater not in {"row", "column", "repeat", "layer"}:
        msg = "repeater must be one of ['row', 'column', 'repeat', 'layer']"
        raise ValueError(msg)
    return core.RepeatRef(repeat=repeater)


class ConcatChart(TopLevelMixin, core.TopLevelConcatSpec):
    """A chart with horizontally-concatenated facets."""

    @utils.use_signature(core.TopLevelConcatSpec)
    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        concat: Sequence[ConcatType] = (),
        columns: Optional[float] = Undefined,
        **kwargs: Any,
    ) -> None:
        for spec in concat:
            _check_if_valid_subspec(spec, "ConcatChart")
        super().__init__(data=data, concat=list(concat), columns=columns, **kwargs)  # type: ignore[arg-type]
        self.concat: list[ChartType]
        self.params: Optional[Sequence[_Parameter]]
        self.data: Optional[ChartDataType]
        self.data, self.concat = _combine_subchart_data(self.data, self.concat)
        self.params, self.concat = _combine_subchart_params(self.params, self.concat)

    def __ior__(self, other: ChartType) -> Self:
        _check_if_valid_subspec(other, "ConcatChart")
        self.concat.append(other)
        self.data, self.concat = _combine_subchart_data(self.data, self.concat)
        self.params, self.concat = _combine_subchart_params(self.params, self.concat)
        return self

    def __or__(self, other: ChartType) -> Self:
        copy = self.copy(deep=["concat"])
        copy |= other
        return copy

    def transformed_data(
        self, row_limit: int | None = None, exclude: Iterable[str] | None = None
    ) -> list[DataFrameLike]:
        """
        Evaluate a ConcatChart's transforms.

        Evaluate the data transforms associated with a ConcatChart and return the
        transformed data for each subplot as a list of DataFrames

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        list of DataFrame
            Transformed data for each subplot as a list of DataFrames
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        encodings: list[SingleDefUnitChannel_T] = []
        if bind_x:
            encodings.append("x")
        if bind_y:
            encodings.append("y")
        return self.add_params(selection_interval(bind="scales", encodings=encodings))

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or not self.concat:
            return self
        copy = self.copy()
        copy.concat = [chart.add_params(*params) for chart in copy.concat]
        return copy

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def concat(*charts: ConcatType, **kwargs: Any) -> ConcatChart:
    """Concatenate charts horizontally."""
    return ConcatChart(concat=charts, **kwargs)


class HConcatChart(TopLevelMixin, core.TopLevelHConcatSpec):
    """A chart with horizontally-concatenated facets."""

    @utils.use_signature(core.TopLevelHConcatSpec)
    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        hconcat: Sequence[ConcatType] = (),
        **kwargs: Any,
    ) -> None:
        for spec in hconcat:
            _check_if_valid_subspec(spec, "HConcatChart")
        super().__init__(data=data, hconcat=list(hconcat), **kwargs)  # type: ignore[arg-type]
        self.hconcat: list[ChartType]
        self.params: Optional[Sequence[_Parameter]]
        self.data: Optional[ChartDataType]
        self.data, self.hconcat = _combine_subchart_data(self.data, self.hconcat)
        self.params, self.hconcat = _combine_subchart_params(self.params, self.hconcat)

    def __ior__(self, other: ChartType) -> Self:
        _check_if_valid_subspec(other, "HConcatChart")
        self.hconcat.append(other)
        self.data, self.hconcat = _combine_subchart_data(self.data, self.hconcat)
        self.params, self.hconcat = _combine_subchart_params(self.params, self.hconcat)
        return self

    def __or__(self, other: ChartType) -> Self:
        copy = self.copy(deep=["hconcat"])
        copy |= other
        return copy

    def transformed_data(
        self, row_limit: int | None = None, exclude: Iterable[str] | None = None
    ) -> list[DataFrameLike]:
        """
        Evaluate a HConcatChart's transforms.

        Evaluate the data transforms associated with a HConcatChart and return the
        transformed data for each subplot as a list of DataFrames

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        list of DataFrame
            Transformed data for each subplot as a list of DataFrames
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        encodings: list[SingleDefUnitChannel_T] = []
        if bind_x:
            encodings.append("x")
        if bind_y:
            encodings.append("y")
        return self.add_params(selection_interval(bind="scales", encodings=encodings))

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or not self.hconcat:
            return self
        copy = self.copy()
        copy.hconcat = [chart.add_params(*params) for chart in copy.hconcat]
        return copy

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def hconcat(*charts: ConcatType, **kwargs: Any) -> HConcatChart:
    """Concatenate charts horizontally."""
    return HConcatChart(hconcat=charts, **kwargs)


class VConcatChart(TopLevelMixin, core.TopLevelVConcatSpec):
    """A chart with vertically-concatenated facets."""

    @utils.use_signature(core.TopLevelVConcatSpec)
    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        vconcat: Sequence[ConcatType] = (),
        **kwargs: Any,
    ) -> None:
        for spec in vconcat:
            _check_if_valid_subspec(spec, "VConcatChart")
        super().__init__(data=data, vconcat=list(vconcat), **kwargs)  # type: ignore[arg-type]
        self.vconcat: list[ChartType]
        self.params: Optional[Sequence[_Parameter]]
        self.data: Optional[ChartDataType]
        self.data, self.vconcat = _combine_subchart_data(self.data, self.vconcat)
        self.params, self.vconcat = _combine_subchart_params(self.params, self.vconcat)

    def __iand__(self, other: ChartType) -> Self:
        _check_if_valid_subspec(other, "VConcatChart")
        self.vconcat.append(other)
        self.data, self.vconcat = _combine_subchart_data(self.data, self.vconcat)
        self.params, self.vconcat = _combine_subchart_params(self.params, self.vconcat)
        return self

    def __and__(self, other: ChartType) -> Self:
        copy = self.copy(deep=["vconcat"])
        copy &= other
        return copy

    def transformed_data(
        self,
        row_limit: int | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[DataFrameLike]:
        """
        Evaluate a VConcatChart's transforms.

        Evaluate the data transforms associated with a VConcatChart and return the
        transformed data for each subplot as a list of DataFrames

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        list of DataFrame
            Transformed data for each subplot as a list of DataFrames
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        encodings: list[SingleDefUnitChannel_T] = []
        if bind_x:
            encodings.append("x")
        if bind_y:
            encodings.append("y")
        return self.add_params(selection_interval(bind="scales", encodings=encodings))

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or not self.vconcat:
            return self
        copy = self.copy()
        copy.vconcat = [chart.add_params(*params) for chart in copy.vconcat]
        return copy

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def vconcat(*charts: ConcatType, **kwargs: Any) -> VConcatChart:
    """Concatenate charts vertically."""
    return VConcatChart(vconcat=charts, **kwargs)


class LayerChart(TopLevelMixin, _EncodingMixin, core.TopLevelLayerSpec):
    """A Chart with layers within a single panel."""

    @utils.use_signature(core.TopLevelLayerSpec)
    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        layer: Sequence[LayerType] = (),
        **kwargs: Any,
    ) -> None:
        # TODO: check for conflicting interaction
        for spec in layer:
            _check_if_valid_subspec(spec, "LayerChart")
            _check_if_can_be_layered(spec)
        super().__init__(data=data, layer=list(layer), **kwargs)  # type: ignore[arg-type]
        self.layer: list[ChartType]
        self.params: Optional[Sequence[_Parameter]]
        self.data: Optional[ChartDataType]
        self.data, self.layer = _combine_subchart_data(self.data, self.layer)
        # Currently (Vega-Lite 5.5) the same param can't occur on two layers
        self.layer = _remove_duplicate_params(self.layer)
        self.params, self.layer = _combine_subchart_params(self.params, self.layer)

        # Some properties are not allowed within layer; we'll move to parent.
        layer_props = ("height", "width", "view")
        combined_dict, self.layer = _remove_layer_props(self, self.layer, layer_props)

        for prop in combined_dict:
            self[prop] = combined_dict[prop]

    def transformed_data(
        self,
        row_limit: int | None = None,
        exclude: Iterable[str] | None = None,
    ) -> list[DataFrameLike]:
        """
        Evaluate a LayerChart's transforms.

        Evaluate the data transforms associated with a LayerChart and return the
        transformed data for each layer as a list of DataFrames

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        list of DataFrame
            Transformed data for each layer as a list of DataFrames
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def __iadd__(self, other: ChartType) -> Self:
        _check_if_valid_subspec(other, "LayerChart")
        _check_if_can_be_layered(other)
        self.layer.append(other)
        self.data, self.layer = _combine_subchart_data(self.data, self.layer)
        self.params, self.layer = _combine_subchart_params(self.params, self.layer)
        return self

    def __add__(self, other: ChartType) -> Self:
        copy = self.copy(deep=["layer"])
        copy += other
        return copy

    def add_layers(self, *layers: LayerChart | Chart) -> Self:
        copy = self.copy(deep=["layer"])
        for layer in layers:
            copy += layer
        return copy

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        if not self.layer:
            msg = "LayerChart: cannot call interactive() until a " "layer is defined"
            raise ValueError(msg)
        copy = self.copy(deep=["layer"])
        copy.layer[0] = copy.layer[0].interactive(
            name=name, bind_x=bind_x, bind_y=bind_y
        )
        return copy

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or not self.layer:
            return self
        copy = self.copy()
        copy.layer[0] = copy.layer[0].add_params(*params)
        return copy.copy()

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def layer(*charts: LayerType, **kwargs: Any) -> LayerChart:
    """Layer multiple charts."""
    return LayerChart(layer=charts, **kwargs)


class FacetChart(TopLevelMixin, core.TopLevelFacetSpec):
    """A Chart with layers within a single panel."""

    @utils.use_signature(core.TopLevelFacetSpec)
    def __init__(
        self,
        data: Optional[ChartDataType] = Undefined,
        spec: Optional[ChartType] = Undefined,
        facet: Optional[dict | SchemaBase] = Undefined,
        params: Optional[Sequence[_Parameter]] = Undefined,
        **kwargs: Any,
    ) -> None:
        if utils.is_undefined(spec):
            msg = f"{type(self).__name__!r} requires a `spec`, but got: {spec!r}"
            raise TypeError(msg)
        _check_if_valid_subspec(spec, "FacetChart")
        _spec_as_list = [spec]
        params, _spec_as_list = _combine_subchart_params(params, _spec_as_list)
        spec = _spec_as_list[0]
        super().__init__(data=data, spec=spec, facet=facet, params=params, **kwargs)  # type: ignore[arg-type]
        self.data: Optional[ChartDataType]
        self.spec: ChartType
        self.params: Optional[Sequence[_Parameter]]

    def transformed_data(
        self, row_limit: int | None = None, exclude: Iterable[str] | None = None
    ) -> DataFrameLike | None:
        """
        Evaluate a FacetChart's transforms.

        Evaluate the data transforms associated with a FacetChart and return the
        transformed data a DataFrame

        Parameters
        ----------
        row_limit : int (optional)
            Maximum number of rows to return for each DataFrame. None (default) for unlimited
        exclude : iterable of str
            Set of the names of charts to exclude

        Returns
        -------
        DataFrame
            Transformed data as a DataFrame
        """
        from altair.utils._transformed_data import transformed_data

        return transformed_data(self, row_limit=row_limit, exclude=exclude)

    def interactive(
        self, name: str | None = None, bind_x: bool = True, bind_y: bool = True
    ) -> Self:
        """
        Make chart axes scales interactive.

        Parameters
        ----------
        name : string
            The parameter name to use for the axes scales. This name should be
            unique among all parameters within the chart.
        bind_x : boolean, default True
            If true, then bind the interactive scales to the x-axis
        bind_y : boolean, default True
            If true, then bind the interactive scales to the y-axis

        Returns
        -------
        chart :
            copy of self, with interactive axes added

        """
        copy = self.copy(deep=False)
        copy.spec = copy.spec.interactive(name=name, bind_x=bind_x, bind_y=bind_y)
        return copy

    def add_params(self, *params: Parameter) -> Self:
        """Add one or more parameters to the chart."""
        if not params or self.spec is Undefined:
            return self
        copy = self.copy()
        copy.spec = copy.spec.add_params(*params)
        return copy.copy()

    @utils.deprecated(version="5.0.0", alternative="add_params")
    def add_selection(self, *selections) -> Self:  # noqa: ANN002
        """'add_selection' is deprecated. Use 'add_params' instead."""
        return self.add_params(*selections)


def topo_feature(url: str, feature: str, **kwargs: Any) -> UrlData:
    """
    A convenience function for extracting features from a topojson url.

    Parameters
    ----------
    url : string
        An URL from which to load the data set.

    feature : string
        The name of the TopoJSON object set to convert to a GeoJSON feature collection. For
        example, in a map of the world, there may be an object set named `"countries"`.
        Using the feature property, we can extract this set and generate a GeoJSON feature
        object for each country.

    **kwargs :
        additional keywords passed to TopoDataFormat
    """
    return core.UrlData(
        url=url, format=core.TopoDataFormat(type="topojson", feature=feature, **kwargs)
    )


def _combine_subchart_data(
    data: Optional[ChartDataType], subcharts: list[ChartType]
) -> tuple[Optional[ChartDataType], list[ChartType]]:
    def remove_data(subchart: _TSchemaBase) -> _TSchemaBase:
        if subchart.data is not Undefined:
            subchart = subchart.copy()
            subchart.data = Undefined
        return subchart

    if not subcharts:
        # No subcharts = nothing to do.
        pass
    elif data is Undefined:
        # Top level has no data; all subchart data must
        # be identical to proceed.
        subdata = subcharts[0].data
        if subdata is not Undefined and all(c.data is subdata for c in subcharts):
            data = subdata
            subcharts = [remove_data(c) for c in subcharts]
    elif all(c.data is Undefined or c.data is data for c in subcharts):
        # Top level has data; subchart data must be either
        # undefined or identical to proceed.
        subcharts = [remove_data(c) for c in subcharts]

    return data, subcharts


_Parameter: TypeAlias = Union[
    core.VariableParameter, core.TopLevelSelectionParameter, core.SelectionParameter
]


def _viewless_dict(param: _Parameter) -> dict[str, Any]:
    d = param.to_dict()
    d.pop("views", None)
    return d


def _needs_name(subchart: ChartType) -> bool:
    # Only `Chart` objects need a name
    if (subchart.name is not Undefined) or (not isinstance(subchart, Chart)):
        return False

    # Variable parameters won't receive a views property.
    return not all(isinstance(p, core.VariableParameter) for p in subchart.params)


# Convert SelectionParameters to TopLevelSelectionParameters with a views property.
def _prepare_to_lift(param: _Parameter) -> _Parameter:
    param = param.copy()

    if isinstance(param, core.VariableParameter):
        return param

    if isinstance(param, core.SelectionParameter):
        return core.TopLevelSelectionParameter(**param.to_dict(), views=[])

    if param.views is Undefined:
        param.views = []

    return param


def _remove_duplicate_params(layer: list[ChartType]) -> list[ChartType]:
    subcharts = [subchart.copy() for subchart in layer]
    found_params = []

    for subchart in subcharts:
        if (not hasattr(subchart, "params")) or (utils.is_undefined(subchart.params)):
            continue

        params: list[_Parameter] = []

        # Ensure the same selection parameter doesn't appear twice
        for param in subchart.params:
            if isinstance(param, core.VariableParameter):
                params.append(param)
                continue

            p = param.copy()
            pd = _viewless_dict(p)

            if pd not in found_params:
                params.append(p)
                found_params.append(pd)

        if len(params) == 0:
            subchart.params = Undefined
        else:
            subchart.params = params

    return subcharts


def _combine_subchart_params(  # noqa: C901
    params: Optional[Sequence[_Parameter]], subcharts: list[ChartType]
) -> tuple[Optional[Sequence[_Parameter]], list[ChartType]]:
    if utils.is_undefined(params):
        params = []

    # List of triples related to params, (param, dictionary minus views, views)
    param_info: list[tuple[_Parameter, dict[str, Any], list[str]]] = []

    # Put parameters already found into `param_info` list.
    for param in params:
        p = _prepare_to_lift(param)
        param_info.append(
            (
                p,
                _viewless_dict(p),
                [] if isinstance(p, core.VariableParameter) else p.views,
            )
        )

    subcharts = [subchart.copy() for subchart in subcharts]

    for subchart in subcharts:
        if (not hasattr(subchart, "params")) or (utils.is_undefined(subchart.params)):
            continue

        if _needs_name(subchart):
            subchart.name = subchart._get_name()

        for param in subchart.params:
            p = _prepare_to_lift(param)
            pd = _viewless_dict(p)

            dlist = [d for _, d, _ in param_info]
            found = pd in dlist

            if isinstance(p, core.VariableParameter) and found:
                continue

            if isinstance(p, core.VariableParameter) and not found:
                param_info.append((p, pd, []))
                continue

            # At this stage in the loop, p must be a TopLevelSelectionParameter.

            if isinstance(subchart, Chart) and (subchart.name not in p.views):
                p.views.append(subchart.name)

            if found:
                i = dlist.index(pd)
                _, _, old_views = param_info[i]
                new_views = [v for v in p.views if v not in old_views]
                old_views += new_views
            else:
                param_info.append((p, pd, p.views))

        subchart.params = Undefined

    for p, _, v in param_info:
        if len(v) > 0:
            p.views = v

    subparams: Any = [p for p, _, _ in param_info]

    if len(subparams) == 0:
        subparams = Undefined

    return subparams, subcharts


def _get_repeat_strings(
    repeat: list[str] | LayerRepeatMapping | RepeatMapping,
) -> list[str]:
    if isinstance(repeat, list):
        return repeat
    elif isinstance(repeat, core.LayerRepeatMapping):
        klist = ["row", "column", "layer"]
    elif isinstance(repeat, core.RepeatMapping):
        klist = ["row", "column"]
    rclist = [k for k in klist if repeat[k] is not Undefined]
    rcstrings = [[f"{k}_{v}" for v in repeat[k]] for k in rclist]
    return ["".join(s) for s in itertools.product(*rcstrings)]


def _extend_view_name(v: str, r: str, spec: Chart | LayerChart) -> str:
    # prevent the same extension from happening more than once
    if isinstance(spec, Chart):
        if v.endswith("child__" + r):
            return v
        else:
            return f"{v}_child__{r}"
    elif isinstance(spec, LayerChart):
        if v.startswith("child__" + r):
            return v
        else:
            return f"child__{r}_{v}"
    else:
        msg = f"Expected 'Chart | LayerChart', but got: {type(spec).__name__!r}"
        raise TypeError(msg)


def _repeat_names(
    params: Optional[Sequence[_Parameter]],
    repeat: list[str] | LayerRepeatMapping | RepeatMapping,
    spec: Chart | LayerChart,
) -> Optional[Sequence[_Parameter]]:
    if utils.is_undefined(params):
        return params

    repeat = _get_repeat_strings(repeat)
    params_named: list[_Parameter] = []

    for param in params:
        if not isinstance(param, core.TopLevelSelectionParameter):
            params_named.append(param)
            continue
        p = param.copy()
        views = []
        repeat_strings = _get_repeat_strings(repeat)
        for v in param.views:
            if isinstance(spec, Chart):
                if any(v.endswith(f"child__{r}") for r in repeat_strings):
                    views.append(v)
                else:
                    views += [_extend_view_name(v, r, spec) for r in repeat_strings]
            elif isinstance(spec, LayerChart):
                if any(v.startswith(f"child__{r}") for r in repeat_strings):
                    views.append(v)
                else:
                    views += [_extend_view_name(v, r, spec) for r in repeat_strings]

        p.views = views
        params_named.append(p)

    return params_named


def _remove_layer_props(  # noqa: C901
    chart: LayerChart, subcharts: list[ChartType], layer_props: Iterable[str]
) -> tuple[dict[str, Any], list[ChartType]]:
    def remove_prop(subchart: ChartType, prop: str) -> ChartType:
        # If subchart is a UnitSpec, then subchart["height"] raises a KeyError
        try:
            if subchart[prop] is not Undefined:
                subchart = subchart.copy()
                subchart[prop] = Undefined
        except KeyError:
            pass
        return subchart

    output_dict: dict[str, Any] = {}

    if not subcharts:
        # No subcharts = nothing to do.
        return output_dict, subcharts

    for prop in layer_props:
        if chart[prop] is Undefined:
            # Top level does not have this prop.
            # Check for consistent props within the subcharts.
            values = []
            for c in subcharts:
                # If c is a UnitSpec, then c["height"] raises a KeyError.
                try:
                    val = c[prop]
                    if val is not Undefined:
                        values.append(val)
                except KeyError:
                    pass
            if len(values) == 0:
                pass
            elif all(v == values[0] for v in values[1:]):
                output_dict[prop] = values[0]
            else:
                msg = f"There are inconsistent values {values} for {prop}"
                raise ValueError(msg)
        elif all(
            getattr(c, prop, Undefined) is Undefined or c[prop] == chart[prop]
            for c in subcharts
        ):
            # Top level has this prop; subchart must either not have the prop
            # or it must be Undefined or identical to proceed.
            output_dict[prop] = chart[prop]
        else:
            msg = f"There are inconsistent values {values} for {prop}"  # pyright: ignore[reportPossiblyUnboundVariable]
            raise ValueError(msg)
        subcharts = [remove_prop(c, prop) for c in subcharts]

    return output_dict, subcharts


@utils.use_signature(core.SequenceParams)
def sequence(
    start: Optional[float],
    stop: Optional[float | None] = None,
    step: Optional[float] = Undefined,
    as_: Optional[str] = Undefined,
    **kwds: Any,
) -> SequenceGenerator:
    """Sequence generator."""
    if stop is None:
        start, stop = 0, start
    params = core.SequenceParams(start=start, stop=stop, step=step, **{"as": as_})
    return core.SequenceGenerator(sequence=params, **kwds)


@utils.use_signature(core.GraticuleParams)
def graticule(**kwds: Any) -> GraticuleGenerator:
    """Graticule generator."""
    # graticule: True indicates default parameters
    graticule: Any = core.GraticuleParams(**kwds) if kwds else True
    return core.GraticuleGenerator(graticule=graticule)


def sphere() -> SphereGenerator:
    """Sphere generator."""
    return core.SphereGenerator(sphere=True)


ChartType: TypeAlias = Union[
    Chart, RepeatChart, ConcatChart, HConcatChart, VConcatChart, FacetChart, LayerChart
]
ConcatType: TypeAlias = Union[
    ChartType,
    core.FacetSpec,
    core.LayerSpec,
    core.RepeatSpec,
    core.FacetedUnitSpec,
    core.LayerRepeatSpec,
    core.NonNormalizedSpec,
    core.NonLayerRepeatSpec,
    core.ConcatSpecGenericSpec,
    core.ConcatSpecGenericSpec,
    core.HConcatSpecGenericSpec,
    core.VConcatSpecGenericSpec,
]
LayerType: TypeAlias = Union[ChartType, core.UnitSpec, core.LayerSpec]


def is_chart_type(obj: Any) -> TypeIs[ChartType]:
    """
    Return `True` if the object is an Altair chart.

    This can be a basic chart but also a repeat, concat, or facet chart.
    """
    return isinstance(
        obj,
        (Chart, RepeatChart, ConcatChart, HConcatChart, VConcatChart, FacetChart, LayerChart)
    )  # fmt: skip
