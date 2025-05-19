# The contents of this file are automatically written by
# tools/generate_schema_wrapper.py. Do not modify directly.
from __future__ import annotations

import contextlib
import copy
import datetime as dt
import inspect
import json
import sys
import textwrap
from collections import defaultdict
from collections.abc import Iterable, Iterator, Mapping, Sequence
from functools import partial
from importlib.metadata import version as importlib_version
from itertools import chain, zip_longest
from math import ceil
from typing import (
    TYPE_CHECKING,
    Any,
    Final,
    Generic,
    Literal,
    TypeVar,
    Union,
    cast,
    overload,
)
from typing_extensions import TypeAlias

import jsonschema
import jsonschema.exceptions
import jsonschema.validators
import narwhals.stable.v1 as nw
from packaging.version import Version

# This leads to circular imports with the vegalite module. Currently, this works
# but be aware that when you access it in this script, the vegalite module might
# not yet be fully instantiated in case your code is being executed during import time
from altair import vegalite

if sys.version_info >= (3, 12):
    from typing import Protocol, TypeAliasType, runtime_checkable
else:
    from typing_extensions import Protocol, TypeAliasType, runtime_checkable

if TYPE_CHECKING:
    from types import ModuleType
    from typing import ClassVar

    from referencing import Registry

    from altair.typing import ChartType

    if sys.version_info >= (3, 13):
        from typing import TypeIs
    else:
        from typing_extensions import TypeIs

    if sys.version_info >= (3, 11):
        from typing import Never, Self
    else:
        from typing_extensions import Never, Self
    _OptionalModule: TypeAlias = "ModuleType | None"

ValidationErrorList: TypeAlias = list[jsonschema.exceptions.ValidationError]
GroupedValidationErrors: TypeAlias = dict[str, ValidationErrorList]

# This URI is arbitrary and could be anything else. It just cannot be an empty
# string as we need to reference the schema registered in
# the referencing.Registry.
_VEGA_LITE_ROOT_URI: Final = "urn:vega-lite-schema"

# Ideally, jsonschema specification would be parsed from the current Vega-Lite
# schema instead of being hardcoded here as a default value.
# However, due to circular imports between this module and the altair.vegalite
# modules, this information is not yet available at this point as altair.vegalite
# is only partially loaded. The draft version which is used is unlikely to
# change often so it's ok to keep this. There is also a test which validates
# that this value is always the same as in the Vega-Lite schema.
_DEFAULT_JSON_SCHEMA_DRAFT_URL: Final = "http://json-schema.org/draft-07/schema#"


# If DEBUG_MODE is True, then schema objects are converted to dict and
# validated at creation time. This slows things down, particularly for
# larger specs, but leads to much more useful tracebacks for the user.
# Individual schema classes can override this by setting the
# class-level _class_is_valid_at_instantiation attribute to False
DEBUG_MODE: bool = True

jsonschema_version_str = importlib_version("jsonschema")


def enable_debug_mode() -> None:
    global DEBUG_MODE
    DEBUG_MODE = True


def disable_debug_mode() -> None:
    global DEBUG_MODE
    DEBUG_MODE = False


@contextlib.contextmanager
def debug_mode(arg: bool) -> Iterator[None]:
    global DEBUG_MODE
    original = DEBUG_MODE
    DEBUG_MODE = arg
    try:
        yield
    finally:
        DEBUG_MODE = original


@overload
def validate_jsonschema(
    spec: Any,
    schema: dict[str, Any],
    rootschema: dict[str, Any] | None = ...,
    *,
    raise_error: Literal[True] = ...,
) -> Never: ...


@overload
def validate_jsonschema(
    spec: Any,
    schema: dict[str, Any],
    rootschema: dict[str, Any] | None = ...,
    *,
    raise_error: Literal[False],
) -> jsonschema.exceptions.ValidationError | None: ...


def validate_jsonschema(
    spec,
    schema: dict[str, Any],
    rootschema: dict[str, Any] | None = None,
    *,
    raise_error: bool = True,
) -> jsonschema.exceptions.ValidationError | None:
    """
    Validates the passed in spec against the schema in the context of the rootschema.

    If any errors are found, they are deduplicated and prioritized
    and only the most relevant errors are kept. Errors are then either raised
    or returned, depending on the value of `raise_error`.
    """
    errors = _get_errors_from_spec(spec, schema, rootschema=rootschema)
    if errors:
        leaf_errors = _get_leaves_of_error_tree(errors)
        grouped_errors = _group_errors_by_json_path(leaf_errors)
        grouped_errors = _subset_to_most_specific_json_paths(grouped_errors)
        grouped_errors = _deduplicate_errors(grouped_errors)

        # Nothing special about this first error but we need to choose one
        # which can be raised
        main_error: Any = next(iter(grouped_errors.values()))[0]
        # All errors are then attached as a new attribute to ValidationError so that
        # they can be used in SchemaValidationError to craft a more helpful
        # error message. Setting a new attribute like this is not ideal as
        # it then no longer matches the type ValidationError. It would be better
        # to refactor this function to never raise but only return errors.
        main_error._all_errors = grouped_errors
        if raise_error:
            raise main_error
        else:
            return main_error
    else:
        return None


def _get_errors_from_spec(
    spec: dict[str, Any],
    schema: dict[str, Any],
    rootschema: dict[str, Any] | None = None,
) -> ValidationErrorList:
    """
    Uses the relevant jsonschema validator to validate the passed in spec against the schema using the rootschema to resolve references.

    The schema and rootschema themselves are not validated but instead considered as valid.
    """
    # We don't use jsonschema.validate as this would validate the schema itself.
    # Instead, we pass the schema directly to the validator class. This is done for
    # two reasons: The schema comes from Vega-Lite and is not based on the user
    # input, therefore there is no need to validate it in the first place. Furthermore,
    # the "uri-reference" format checker fails for some of the references as URIs in
    # "$ref" are not encoded,
    # e.g. '#/definitions/ValueDefWithCondition<MarkPropFieldOrDatumDef,
    # (Gradient|string|null)>' would be a valid $ref in a Vega-Lite schema but
    # it is not a valid URI reference due to the characters such as '<'.

    json_schema_draft_url = _get_json_schema_draft_url(rootschema or schema)
    validator_cls = jsonschema.validators.validator_for(
        {"$schema": json_schema_draft_url}
    )
    validator_kwargs: dict[str, Any] = {}
    if hasattr(validator_cls, "FORMAT_CHECKER"):
        validator_kwargs["format_checker"] = validator_cls.FORMAT_CHECKER

    if _use_referencing_library():
        schema = _prepare_references_in_schema(schema)
        validator_kwargs["registry"] = _get_referencing_registry(
            rootschema or schema, json_schema_draft_url
        )

    else:
        # No resolver is necessary if the schema is already the full schema
        validator_kwargs["resolver"] = (
            jsonschema.RefResolver.from_schema(rootschema)
            if rootschema is not None
            else None
        )

    validator = validator_cls(schema, **validator_kwargs)
    errors = list(validator.iter_errors(spec))
    return errors


def _get_json_schema_draft_url(schema: dict[str, Any]) -> str:
    return schema.get("$schema", _DEFAULT_JSON_SCHEMA_DRAFT_URL)


def _use_referencing_library() -> bool:
    """In version 4.18.0, the jsonschema package deprecated RefResolver in favor of the referencing library."""
    return Version(jsonschema_version_str) >= Version("4.18")


def _prepare_references_in_schema(schema: dict[str, Any]) -> dict[str, Any]:
    # Create a copy so that $ref is not modified in the original schema in case
    # that it would still reference a dictionary which might be attached to
    # an Altair class _schema attribute
    schema = copy.deepcopy(schema)

    def _prepare_refs(d: dict[str, Any]) -> dict[str, Any]:
        """
        Add _VEGA_LITE_ROOT_URI in front of all $ref values.

        This function recursively iterates through the whole dictionary.

        $ref values can only be nested in dictionaries or lists
        as the passed in `d` dictionary comes from the Vega-Lite json schema
        and in json we only have arrays (-> lists in Python) and objects
        (-> dictionaries in Python) which we need to iterate through.
        """
        for key, value in d.items():
            if key == "$ref":
                d[key] = _VEGA_LITE_ROOT_URI + d[key]
            elif isinstance(value, dict):
                d[key] = _prepare_refs(value)
            elif isinstance(value, list):
                prepared_values = []
                for v in value:
                    if isinstance(v, dict):
                        v = _prepare_refs(v)
                    prepared_values.append(v)
                d[key] = prepared_values
        return d

    schema = _prepare_refs(schema)
    return schema


# We do not annotate the return value here as the referencing library is not always
# available and this function is only executed in those cases.
def _get_referencing_registry(
    rootschema: dict[str, Any], json_schema_draft_url: str | None = None
) -> Registry:
    # Referencing is a dependency of newer jsonschema versions, starting with the
    # version that is specified in _use_referencing_library and we therefore
    # can expect that it is installed if the function returns True.
    # We ignore 'import' mypy errors which happen when the referencing library
    # is not installed. That's ok as in these cases this function is not called.
    # We also have to ignore 'unused-ignore' errors as mypy raises those in case
    # referencing is installed.
    import referencing  # type: ignore[import,unused-ignore]
    import referencing.jsonschema  # type: ignore[import,unused-ignore]

    if json_schema_draft_url is None:
        json_schema_draft_url = _get_json_schema_draft_url(rootschema)

    specification = referencing.jsonschema.specification_with(json_schema_draft_url)
    resource = specification.create_resource(rootschema)
    return referencing.Registry().with_resource(
        uri=_VEGA_LITE_ROOT_URI, resource=resource
    )


def _json_path(err: jsonschema.exceptions.ValidationError) -> str:
    """
    Drop in replacement for the .json_path property of the jsonschema ValidationError class.

    This is not available as property for ValidationError with jsonschema<4.0.1.

    More info, see https://github.com/vega/altair/issues/3038.
    """
    path = "$"
    for elem in err.absolute_path:
        if isinstance(elem, int):
            path += "[" + str(elem) + "]"
        else:
            path += "." + elem
    return path


def _group_errors_by_json_path(
    errors: ValidationErrorList,
) -> GroupedValidationErrors:
    """
    Groups errors by the `json_path` attribute of the jsonschema ValidationError class.

    This attribute contains the path to the offending element within
    a chart specification and can therefore be considered as an identifier of an
    'issue' in the chart that needs to be fixed.
    """
    errors_by_json_path = defaultdict(list)
    for err in errors:
        err_key = getattr(err, "json_path", _json_path(err))
        errors_by_json_path[err_key].append(err)
    return dict(errors_by_json_path)


def _get_leaves_of_error_tree(
    errors: ValidationErrorList,
) -> ValidationErrorList:
    """
    For each error in `errors`, it traverses down the "error tree" that is generated by the jsonschema library to find and return all "leaf" errors.

    These are errors which have no further errors that caused it and so they are the most specific errors
    with the most specific error messages.
    """
    leaves: ValidationErrorList = []
    for err in errors:
        if err.context:
            # This means that the error `err` was caused by errors in subschemas.
            # The list of errors from the subschemas are available in the property
            # `context`.
            leaves.extend(_get_leaves_of_error_tree(err.context))
        else:
            leaves.append(err)
    return leaves


def _subset_to_most_specific_json_paths(
    errors_by_json_path: GroupedValidationErrors,
) -> GroupedValidationErrors:
    """
    Removes key (json path), value (errors) pairs where the json path is fully contained in another json path.

    For example if `errors_by_json_path` has two keys, `$.encoding.X` and `$.encoding.X.tooltip`,
    then the first one will be removed and only the second one is returned.

    This is done under the assumption that more specific json paths give more helpful error messages to the user.
    """
    errors_by_json_path_specific: GroupedValidationErrors = {}
    for json_path, errors in errors_by_json_path.items():
        if not _contained_at_start_of_one_of_other_values(
            json_path, list(errors_by_json_path.keys())
        ):
            errors_by_json_path_specific[json_path] = errors
    return errors_by_json_path_specific


def _contained_at_start_of_one_of_other_values(x: str, values: Sequence[str]) -> bool:
    # Does not count as "contained at start of other value" if the values are
    # the same. These cases should be handled separately
    return any(value.startswith(x) for value in values if x != value)


def _deduplicate_errors(
    grouped_errors: GroupedValidationErrors,
) -> GroupedValidationErrors:
    """
    Some errors have very similar error messages or are just in general not helpful for a user.

    This function removes as many of these cases as possible and
    can be extended over time to handle new cases that come up.
    """
    grouped_errors_deduplicated: GroupedValidationErrors = {}
    for json_path, element_errors in grouped_errors.items():
        errors_by_validator = _group_errors_by_validator(element_errors)

        deduplication_functions = {
            "enum": _deduplicate_enum_errors,
            "additionalProperties": _deduplicate_additional_properties_errors,
        }
        deduplicated_errors: ValidationErrorList = []
        for validator, errors in errors_by_validator.items():
            deduplication_func = deduplication_functions.get(validator)
            if deduplication_func is not None:
                errors = deduplication_func(errors)
            deduplicated_errors.extend(_deduplicate_by_message(errors))

        # Removes any ValidationError "'value' is a required property" as these
        # errors are unlikely to be the relevant ones for the user. They come from
        # validation against a schema definition where the output of `alt.value`
        # would be valid. However, if a user uses `alt.value`, the `value` keyword
        # is included automatically from that function and so it's unlikely
        # that this was what the user intended if the keyword is not present
        # in the first place.
        deduplicated_errors = [
            err for err in deduplicated_errors if not _is_required_value_error(err)
        ]

        grouped_errors_deduplicated[json_path] = deduplicated_errors
    return grouped_errors_deduplicated


def _is_required_value_error(err: jsonschema.exceptions.ValidationError) -> bool:
    return err.validator == "required" and err.validator_value == ["value"]


def _group_errors_by_validator(errors: ValidationErrorList) -> GroupedValidationErrors:
    """
    Groups the errors by the json schema "validator" that casued the error.

    For example if the error is that a value is not one of an enumeration in the json schema
    then the "validator" is `"enum"`, if the error is due to an unknown property that
    was set although no additional properties are allowed then "validator" is
    `"additionalProperties`, etc.
    """
    errors_by_validator: defaultdict[str, ValidationErrorList] = defaultdict(list)
    for err in errors:
        # Ignore mypy error as err.validator as it wrongly sees err.validator
        # as of type Optional[Validator] instead of str which it is according
        # to the documentation and all tested cases
        errors_by_validator[err.validator].append(err)  # type: ignore[index]
    return dict(errors_by_validator)


def _deduplicate_enum_errors(errors: ValidationErrorList) -> ValidationErrorList:
    """
    Deduplicate enum errors by removing the errors where the allowed values are a subset of another error.

    For example, if `enum` contains two errors and one has `validator_value` (i.e. accepted values) ["A", "B"] and the
    other one ["A", "B", "C"] then the first one is removed and the final
    `enum` list only contains the error with ["A", "B", "C"].
    """
    if len(errors) > 1:
        # Values (and therefore `validator_value`) of an enum are always arrays,
        # see https://json-schema.org/understanding-json-schema/reference/generic.html#enumerated-values
        # which is why we can use join below
        value_strings = [",".join(err.validator_value) for err in errors]  # type: ignore
        longest_enums: ValidationErrorList = []
        for value_str, err in zip(value_strings, errors):
            if not _contained_at_start_of_one_of_other_values(value_str, value_strings):
                longest_enums.append(err)
        errors = longest_enums
    return errors


def _deduplicate_additional_properties_errors(
    errors: ValidationErrorList,
) -> ValidationErrorList:
    """
    If there are multiple additional property errors it usually means that the offending element was validated against multiple schemas and its parent is a common anyOf validator.

    The error messages produced from these cases are usually
    very similar and we just take the shortest one. For example,
    the following 3 errors are raised for the `unknown` channel option in
    `alt.X("variety", unknown=2)`:
    - "Additional properties are not allowed ('unknown' was unexpected)"
    - "Additional properties are not allowed ('field', 'unknown' were unexpected)"
    - "Additional properties are not allowed ('field', 'type', 'unknown' were unexpected)".
    """
    if len(errors) > 1:
        # Test if all parent errors are the same anyOf error and only do
        # the prioritization in these cases. Can't think of a chart spec where this
        # would not be the case but still allow for it below to not break anything.
        parent = errors[0].parent
        if (
            parent is not None
            and parent.validator == "anyOf"
            # Use [1:] as don't have to check for first error as it was used
            # above to define `parent`
            and all(err.parent is parent for err in errors[1:])
        ):
            errors = [min(errors, key=lambda x: len(x.message))]
    return errors


def _deduplicate_by_message(errors: ValidationErrorList) -> ValidationErrorList:
    """Deduplicate errors by message. This keeps the original order in case it was chosen intentionally."""
    return list({e.message: e for e in errors}.values())


def _subclasses(cls: type[Any]) -> Iterator[type[Any]]:
    """Breadth-first sequence of all classes which inherit from cls."""
    seen = set()
    current_set = {cls}
    while current_set:
        seen |= current_set
        current_set = set.union(*(set(cls.__subclasses__()) for cls in current_set))
        for cls in current_set - seen:
            yield cls


def _from_array_like(obj: Iterable[Any], /) -> list[Any]:
    try:
        ser = nw.from_native(obj, strict=True, series_only=True)
        return ser.to_list()
    except TypeError:
        return list(obj)


def _from_date_datetime(obj: dt.date | dt.datetime, /) -> dict[str, Any]:
    """
    Parse native `datetime.(date|datetime)` into a `DateTime`_ schema.

    .. _DateTime:
        https://vega.github.io/vega-lite/docs/datetime.html
    """
    result: dict[str, Any] = {"year": obj.year, "month": obj.month, "date": obj.day}
    if isinstance(obj, dt.datetime):
        if obj.time() != dt.time.min:
            us = obj.microsecond
            ms = us if us == 0 else us // 1_000
            result.update(
                hours=obj.hour, minutes=obj.minute, seconds=obj.second, milliseconds=ms
            )
        if tzinfo := obj.tzinfo:
            if tzinfo is dt.timezone.utc:
                result["utc"] = True
            else:
                msg = (
                    f"Unsupported timezone {tzinfo!r}.\n"
                    "Only `'UTC'` or naive (local) datetimes are permitted.\n"
                    "See https://altair-viz.github.io/user_guide/generated/core/altair.DateTime.html"
                )
                raise TypeError(msg)
    return result


def _todict(obj: Any, context: dict[str, Any] | None, np_opt: Any, pd_opt: Any) -> Any:  # noqa: C901
    """Convert an object to a dict representation."""
    if np_opt is not None:
        np = np_opt
        if isinstance(obj, np.ndarray):
            return [_todict(v, context, np_opt, pd_opt) for v in obj]
        elif isinstance(obj, np.number):
            return float(obj)
        elif isinstance(obj, np.datetime64):
            result = str(obj)
            if "T" not in result:
                # See https://github.com/vega/altair/issues/1027 for why this is necessary.
                result += "T00:00:00"
            return result
    if isinstance(obj, SchemaBase):
        return obj.to_dict(validate=False, context=context)
    elif isinstance(obj, (list, tuple)):
        return [_todict(v, context, np_opt, pd_opt) for v in obj]
    elif isinstance(obj, dict):
        return {
            k: _todict(v, context, np_opt, pd_opt)
            for k, v in obj.items()
            if v is not Undefined
        }
    elif isinstance(obj, SchemaLike):
        return obj.to_dict()
    elif pd_opt is not None and isinstance(obj, pd_opt.Timestamp):
        return pd_opt.Timestamp(obj).isoformat()
    elif _is_iterable(obj, exclude=(str, bytes)):
        return _todict(_from_array_like(obj), context, np_opt, pd_opt)
    elif isinstance(obj, dt.date):
        return _from_date_datetime(obj)
    else:
        return obj


def _resolve_references(
    schema: dict[str, Any], rootschema: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Resolve schema references until there is no $ref anymore in the top-level of the dictionary."""
    if _use_referencing_library():
        registry = _get_referencing_registry(rootschema or schema)
        # Using a different variable name to show that this is not the
        # jsonschema.RefResolver but instead a Resolver from the referencing
        # library
        referencing_resolver = registry.resolver()
        while "$ref" in schema:
            schema = referencing_resolver.lookup(
                _VEGA_LITE_ROOT_URI + schema["$ref"]
            ).contents
    else:
        resolver = jsonschema.RefResolver.from_schema(rootschema or schema)
        while "$ref" in schema:
            with resolver.resolving(schema["$ref"]) as resolved:
                schema = resolved
    return schema


class SchemaValidationError(jsonschema.ValidationError):
    def __init__(self, obj: SchemaBase, err: jsonschema.ValidationError) -> None:
        """
        A wrapper for ``jsonschema.ValidationError`` with friendlier traceback.

        Parameters
        ----------
        obj
            The instance that failed ``self.validate(...)``.
        err
            The original ``ValidationError``.

        Notes
        -----
        We do not raise `from err` as else the resulting traceback is very long
        as it contains part of the Vega-Lite schema.

        It would also first show the less helpful `ValidationError` instead of
        the more user friendly `SchemaValidationError`.
        """
        super().__init__(**err._contents())
        self.obj = obj
        self._errors: GroupedValidationErrors = getattr(
            err, "_all_errors", {getattr(err, "json_path", _json_path(err)): [err]}
        )
        # This is the message from err
        self._original_message = self.message
        self.message = self._get_message()

    def __str__(self) -> str:
        return self.message

    def _get_message(self) -> str:
        def indent_second_line_onwards(message: str, indent: int = 4) -> str:
            modified_lines: list[str] = []
            for idx, line in enumerate(message.split("\n")):
                if idx > 0 and len(line) > 0:
                    line = " " * indent + line
                modified_lines.append(line)
            return "\n".join(modified_lines)

        error_messages: list[str] = []
        # Only show a maximum of 3 errors as else the final message returned by this
        # method could get very long.
        for errors in list(self._errors.values())[:3]:
            error_messages.append(self._get_message_for_errors_group(errors))

        message = ""
        if len(error_messages) > 1:
            error_messages = [
                indent_second_line_onwards(f"Error {error_id}: {m}")
                for error_id, m in enumerate(error_messages, start=1)
            ]
            message += "Multiple errors were found.\n\n"
        message += "\n\n".join(error_messages)
        return message

    def _get_message_for_errors_group(
        self,
        errors: ValidationErrorList,
    ) -> str:
        if errors[0].validator == "additionalProperties":
            # During development, we only found cases where an additionalProperties
            # error was raised if that was the only error for the offending instance
            # as identifiable by the json path. Therefore, we just check here the first
            # error. However, other constellations might exist in which case
            # this should be adapted so that other error messages are shown as well.
            message = self._get_additional_properties_error_message(errors[0])
        else:
            message = self._get_default_error_message(errors=errors)

        return message.strip()

    def _get_additional_properties_error_message(
        self,
        error: jsonschema.exceptions.ValidationError,
    ) -> str:
        """Output all existing parameters when an unknown parameter is specified."""
        altair_cls = self._get_altair_class_for_error(error)
        param_dict_keys = inspect.signature(altair_cls).parameters.keys()
        param_names_table = self._format_params_as_table(param_dict_keys)

        # Error messages for these errors look like this:
        # "Additional properties are not allowed ('unknown' was unexpected)"
        # Line below extracts "unknown" from this string
        parameter_name = error.message.split("('")[-1].split("'")[0]
        message = f"""\
`{altair_cls.__name__}` has no parameter named '{parameter_name}'

Existing parameter names are:
{param_names_table}
See the help for `{altair_cls.__name__}` to read the full description of these parameters"""
        return message

    def _get_altair_class_for_error(
        self, error: jsonschema.exceptions.ValidationError
    ) -> type[SchemaBase]:
        """
        Try to get the lowest class possible in the chart hierarchy so it can be displayed in the error message.

        This should lead to more informative error messages pointing the user closer to the source of the issue.
        """
        for prop_name in reversed(error.absolute_path):
            # Check if str as e.g. first item can be a 0
            if isinstance(prop_name, str):
                potential_class_name = prop_name[0].upper() + prop_name[1:]
                cls = getattr(vegalite, potential_class_name, None)
                if cls is not None:
                    break
        else:
            # Did not find a suitable class based on traversing the path so we fall
            # back on the class of the top-level object which created
            # the SchemaValidationError
            cls = self.obj.__class__
        return cls

    @staticmethod
    def _format_params_as_table(param_dict_keys: Iterable[str]) -> str:
        """Format param names into a table so that they are easier to read."""
        param_names: tuple[str, ...]
        name_lengths: tuple[int, ...]
        param_names, name_lengths = zip(
            *[
                (name, len(name))
                for name in param_dict_keys
                if name not in {"kwds", "self"}
            ]
        )
        # Worst case scenario with the same longest param name in the same
        # row for all columns
        max_name_length = max(name_lengths)
        max_column_width = 80
        # Output a square table if not too big (since it is easier to read)
        num_param_names = len(param_names)
        square_columns = int(ceil(num_param_names**0.5))
        columns = min(max_column_width // max_name_length, square_columns)

        # Compute roughly equal column heights to evenly divide the param names
        def split_into_equal_parts(n: int, p: int) -> list[int]:
            return [n // p + 1] * (n % p) + [n // p] * (p - n % p)

        column_heights = split_into_equal_parts(num_param_names, columns)

        # Section the param names into columns and compute their widths
        param_names_columns: list[tuple[str, ...]] = []
        column_max_widths: list[int] = []
        last_end_idx: int = 0
        for ch in column_heights:
            param_names_columns.append(param_names[last_end_idx : last_end_idx + ch])
            column_max_widths.append(
                max(len(param_name) for param_name in param_names_columns[-1])
            )
            last_end_idx = ch + last_end_idx

        # Transpose the param name columns into rows to facilitate looping
        param_names_rows: list[tuple[str, ...]] = []
        for li in zip_longest(*param_names_columns, fillvalue=""):
            param_names_rows.append(li)
        # Build the table as a string by iterating over and formatting the rows
        param_names_table: str = ""
        for param_names_row in param_names_rows:
            for num, param_name in enumerate(param_names_row):
                # Set column width based on the longest param in the column
                max_name_length_column = column_max_widths[num]
                column_pad = 3
                param_names_table += "{:<{}}".format(
                    param_name, max_name_length_column + column_pad
                )
                # Insert newlines and spacing after the last element in each row
                if num == (len(param_names_row) - 1):
                    param_names_table += "\n"
        return param_names_table

    def _get_default_error_message(
        self,
        errors: ValidationErrorList,
    ) -> str:
        bullet_points: list[str] = []
        errors_by_validator = _group_errors_by_validator(errors)
        if "enum" in errors_by_validator:
            for error in errors_by_validator["enum"]:
                bullet_points.append(f"one of {error.validator_value}")

        if "type" in errors_by_validator:
            types = [f"'{err.validator_value}'" for err in errors_by_validator["type"]]
            point = "of type "
            if len(types) == 1:
                point += types[0]
            elif len(types) == 2:
                point += f"{types[0]} or {types[1]}"
            else:
                point += ", ".join(types[:-1]) + f", or {types[-1]}"
            bullet_points.append(point)

        # It should not matter which error is specifically used as they are all
        # about the same offending instance (i.e. invalid value), so we can just
        # take the first one
        error = errors[0]
        # Add a summary line when parameters are passed an invalid value
        # For example: "'asdf' is an invalid value for `stack`
        message = f"'{error.instance}' is an invalid value"
        if error.absolute_path:
            message += f" for `{error.absolute_path[-1]}`"

        # Add bullet points
        if len(bullet_points) == 0:
            message += ".\n\n"
        elif len(bullet_points) == 1:
            message += f". Valid values are {bullet_points[0]}.\n\n"
        else:
            # We don't use .capitalize below to make the first letter uppercase
            # as that makes the rest of the message lowercase
            bullet_points = [point[0].upper() + point[1:] for point in bullet_points]
            message += ". Valid values are:\n\n"
            message += "\n".join([f"- {point}" for point in bullet_points])
            message += "\n\n"

        # Add unformatted messages of any remaining errors which were not
        # considered so far. This is not expected to be used but more exists
        # as a fallback for cases which were not known during development.
        it = (
            "\n".join(e.message for e in errors)
            for validator, errors in errors_by_validator.items()
            if validator not in {"enum", "type"}
        )
        message += "".join(it)
        return message


_JSON_VT_co = TypeVar(
    "_JSON_VT_co",
    Literal["string"],
    Literal["object"],
    Literal["array"],
    covariant=True,
)
"""
One of a subset of JSON Schema `primitive types`_:

    ["string", "object", "array"]

.. _primitive types:
    https://json-schema.org/draft-07/json-schema-validation#rfc.section.6.1.1
"""

_TypeMap = TypeAliasType(
    "_TypeMap", Mapping[Literal["type"], _JSON_VT_co], type_params=(_JSON_VT_co,)
)
"""
A single item JSON Schema using the `type`_ keyword.

This may represent **one of**:

    {"type": "string"}
    {"type": "object"}
    {"type": "array"}

.. _type:
    https://json-schema.org/understanding-json-schema/reference/type
"""

# NOTE: Type checkers want opposing things:
# - `mypy`   : Covariant type variable "_JSON_VT_co" used in protocol where invariant one is expected  [misc]
# - `pyright`: Type variable "_JSON_VT_co" used in generic protocol "SchemaLike" should be covariant [reportInvalidTypeVarUse]
# Siding with `pyright` as this is consistent with https://github.com/python/typeshed/blob/9e506eb5e8fc2823db8c60ad561b1145ff114947/stdlib/typing.pyi#L690


@runtime_checkable
class SchemaLike(Generic[_JSON_VT_co], Protocol):  # type: ignore[misc]
    """
    Represents ``altair`` classes which *may* not derive ``SchemaBase``.

    Attributes
    ----------
    _schema
        A single item JSON Schema using the `type`_ keyword.

    Notes
    -----
    Should be kept tightly defined to the **minimum** requirements for:
        - Converting into a form that can be validated by `jsonschema`_.
        - Avoiding calling ``.to_dict()`` on a class external to ``altair``.
    - ``_schema`` is more accurately described as a ``ClassVar``
        - See `discussion`_ for blocking issue.

    .. _jsonschema:
        https://github.com/python-jsonschema/jsonschema
    .. _type:
        https://json-schema.org/understanding-json-schema/reference/type
    .. _discussion:
        https://github.com/python/typing/discussions/1424
    """

    _schema: _TypeMap[_JSON_VT_co]

    def to_dict(self, *args, **kwds) -> Any: ...


@runtime_checkable
class ConditionLike(SchemaLike[Literal["object"]], Protocol):
    """
    Represents the wrapped state of a conditional encoding or property.

    Attributes
    ----------
    condition
        One or more (predicate, statement) pairs which each form a condition.

    Notes
    -----
    - Can be extended with additional conditions.
    - *Does not* define a default value, but can be finalized with one.
    """

    condition: Any
    _schema: _TypeMap[Literal["object"]] = {"type": "object"}


class UndefinedType:
    """A singleton object for marking undefined parameters."""

    __instance = None

    def __new__(cls, *args, **kwargs) -> Self:
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def __repr__(self) -> str:
        return "Undefined"


Undefined = UndefinedType()
T = TypeVar("T")
Optional: TypeAlias = Union[T, UndefinedType]
"""One of ``T`` specified type(s), or the ``Undefined`` singleton.

Examples
--------
The parameters ``short``, ``long`` accept the same range of types::

    # ruff: noqa: UP006, UP007
    from altair.typing import Optional

    def func_1(
        short: Optional[str | bool | float | dict[str, Any] | SchemaBase] = Undefined,
        long: Union[
            str, bool, float, Dict[str, Any], SchemaBase, UndefinedType
        ] = Undefined,
    ): ...

This is distinct from `typing.Optional <https://typing.readthedocs.io/en/latest/spec/historical.html#union-and-optional>`__.

``altair.typing.Optional`` treats ``None`` like any other type::

    # ruff: noqa: UP006, UP007
    from altair.typing import Optional

    def func_2(
        short: Optional[str | float | dict[str, Any] | None | SchemaBase] = Undefined,
        long: Union[
            str, float, Dict[str, Any], None, SchemaBase, UndefinedType
        ] = Undefined,
    ): ...
"""


def is_undefined(obj: Any) -> TypeIs[UndefinedType]:
    """
    Type-safe singleton check for `UndefinedType`.

    Notes
    -----
    - Using `obj is Undefined` does not narrow from `UndefinedType` in a union.
        - Due to the assumption that other `UndefinedType`'s could exist.
    - Current [typing spec advises](https://typing.readthedocs.io/en/latest/spec/concepts.html#support-for-singleton-types-in-unions) using an `Enum`.
        - Otherwise, requires an explicit guard to inform the type checker.
    """
    return obj is Undefined


@overload
def _shallow_copy(obj: _CopyImpl) -> _CopyImpl: ...
@overload
def _shallow_copy(obj: Any) -> Any: ...
def _shallow_copy(obj: _CopyImpl | Any) -> _CopyImpl | Any:
    if isinstance(obj, SchemaBase):
        return obj.copy(deep=False)
    elif isinstance(obj, (list, dict)):
        return obj.copy()
    else:
        return obj


@overload
def _deep_copy(obj: _CopyImpl, by_ref: set[str]) -> _CopyImpl: ...
@overload
def _deep_copy(obj: Any, by_ref: set[str]) -> Any: ...
def _deep_copy(obj: _CopyImpl | Any, by_ref: set[str]) -> _CopyImpl | Any:
    copy = partial(_deep_copy, by_ref=by_ref)
    if isinstance(obj, SchemaBase):
        if copier := getattr(obj, "__deepcopy__", None):
            with debug_mode(False):
                return copier(obj)
        args = (copy(arg) for arg in obj._args)
        kwds = {k: (copy(v) if k not in by_ref else v) for k, v in obj._kwds.items()}
        with debug_mode(False):
            return obj.__class__(*args, **kwds)
    elif isinstance(obj, list):
        return [copy(v) for v in obj]
    elif isinstance(obj, dict):
        return {k: (copy(v) if k not in by_ref else v) for k, v in obj.items()}
    else:
        return obj


class SchemaBase:
    """
    Base class for schema wrappers.

    Each derived class should set the _schema class attribute (and optionally
    the _rootschema class attribute) which is used for validation.
    """

    _schema: ClassVar[dict[str, Any] | Any] = None
    _rootschema: ClassVar[dict[str, Any] | None] = None
    _class_is_valid_at_instantiation: ClassVar[bool] = True

    def __init__(self, *args: Any, **kwds: Any) -> None:
        # Two valid options for initialization, which should be handled by
        # derived classes:
        # - a single arg with no kwds, for, e.g. {'type': 'string'}
        # - zero args with zero or more kwds for {'type': 'object'}
        if self._schema is None:
            msg = (
                f"Cannot instantiate object of type {self.__class__}: "
                "_schema class attribute is not defined."
                ""
            )
            raise ValueError(msg)

        if kwds:
            assert len(args) == 0
        else:
            assert len(args) in {0, 1}

        # use object.__setattr__ because we override setattr below.
        object.__setattr__(self, "_args", args)
        object.__setattr__(self, "_kwds", kwds)

        if DEBUG_MODE and self._class_is_valid_at_instantiation:
            self.to_dict(validate=True)

    def copy(
        self, deep: bool | Iterable[Any] = True, ignore: list[str] | None = None
    ) -> Self:
        """
        Return a copy of the object.

        Parameters
        ----------
        deep : boolean or list, optional
            If True (default) then return a deep copy of all dict, list, and
            SchemaBase objects within the object structure.
            If False, then only copy the top object.
            If a list or iterable, then only copy the listed attributes.
        ignore : list, optional
            A list of keys for which the contents should not be copied, but
            only stored by reference.
        """
        if deep is True:
            return cast("Self", _deep_copy(self, set(ignore) if ignore else set()))
        with debug_mode(False):
            copy = self.__class__(*self._args, **self._kwds)
        if _is_iterable(deep):
            for attr in deep:
                copy[attr] = _shallow_copy(copy._get(attr))
        return copy

    def _get(self, attr, default=Undefined):
        """Get an attribute, returning default if not present."""
        attr = self._kwds.get(attr, Undefined)
        if attr is Undefined:
            attr = default
        return attr

    def __getattr__(self, attr):
        # reminder: getattr is called after the normal lookups
        if attr == "_kwds":
            raise AttributeError()
        if attr in self._kwds:
            return self._kwds[attr]
        else:
            try:
                _getattr = super().__getattr__  # pyright: ignore[reportAttributeAccessIssue]
            except AttributeError:
                _getattr = super().__getattribute__
            return _getattr(attr)

    def __setattr__(self, item, val) -> None:
        self._kwds[item] = val

    def __getitem__(self, item):
        return self._kwds[item]

    def __setitem__(self, item, val) -> None:
        self._kwds[item] = val

    def __repr__(self) -> str:
        name = type(self).__name__
        if kwds := self._kwds:
            it = (f"{k}: {v!r}" for k, v in sorted(kwds.items()) if v is not Undefined)
            args = ",\n".join(it).replace("\n", "\n  ")
            LB, RB = "{", "}"
            return f"{name}({LB}\n  {args}\n{RB})"
        else:
            return f"{name}({self._args[0]!r})"

    def __eq__(self, other: Any) -> bool:
        return (
            type(self) is type(other)
            and self._args == other._args
            and self._kwds == other._kwds
        )

    def to_dict(
        self,
        validate: bool = True,
        *,
        ignore: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Return a dictionary representation of the object.

        Parameters
        ----------
        validate : bool, optional
            If True (default), then validate the result against the schema.
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
        ignore = ignore or []
        opts = _get_optional_modules(np_opt="numpy", pd_opt="pandas")

        if self._args and not self._kwds:
            kwds = self._args[0]
        elif not self._args:
            kwds = self._kwds.copy()
            exclude = {*ignore, "shorthand"}
            if parsed := context.pop("parsed_shorthand", None):
                kwds = _replace_parsed_shorthand(parsed, kwds)
            kwds = {k: v for k, v in kwds.items() if k not in exclude}
            if (mark := kwds.get("mark")) and isinstance(mark, str):
                kwds["mark"] = {"type": mark}
        else:
            msg = f"{type(self)} instance has both a value and properties : cannot serialize to dict"
            raise ValueError(msg)
        result = _todict(kwds, context=context, **opts)
        if validate:
            # NOTE: Don't raise `from err`, see `SchemaValidationError` doc
            try:
                self.validate(result)
            except jsonschema.ValidationError as err:
                raise SchemaValidationError(self, err) from None
        return result

    def to_json(
        self,
        validate: bool = True,
        indent: int | str | None = 2,
        sort_keys: bool = True,
        *,
        ignore: list[str] | None = None,
        context: dict[str, Any] | None = None,
        **kwargs,
    ) -> str:
        """
        Emit the JSON representation for this object as a string.

        Parameters
        ----------
        validate : bool, optional
            If True (default), then validate the result against the schema.
        indent : int, optional
            The number of spaces of indentation to use. The default is 2.
        sort_keys : bool, optional
            If True (default), sort keys in the output.
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
        dct = self.to_dict(validate=validate, ignore=ignore, context=context)
        return json.dumps(dct, indent=indent, sort_keys=sort_keys, **kwargs)

    @classmethod
    def _default_wrapper_classes(cls) -> Iterator[type[SchemaBase]]:
        """Return the set of classes used within cls.from_dict()."""
        return _subclasses(SchemaBase)

    @classmethod
    def from_dict(
        cls: type[TSchemaBase], dct: dict[str, Any], validate: bool = True
    ) -> TSchemaBase:
        """
        Construct class from a dictionary representation.

        Parameters
        ----------
        dct : dictionary
            The dict from which to construct the class
        validate : boolean
            If True (default), then validate the input against the schema.

        Raises
        ------
        jsonschema.ValidationError :
            If ``validate`` and ``dct`` does not conform to the schema
        """
        if validate:
            cls.validate(dct)
        converter = _FromDict(cls._default_wrapper_classes())
        return converter.from_dict(dct, cls)

    @classmethod
    def from_json(
        cls,
        json_string: str,
        validate: bool = True,
        **kwargs: Any,
        # Type hints for this method would get rather complicated
        # if we want to provide a more specific return type
    ) -> ChartType:
        """
        Instantiate the object from a valid JSON string.

        Parameters
        ----------
        json_string : string
            The string containing a valid JSON chart specification.
        validate : boolean
            If True (default), then validate the input against the schema.
        **kwargs :
            Additional keyword arguments are passed to json.loads

        Returns
        -------
        chart : Chart object
            The altair Chart object built from the specification.
        """
        dct: dict[str, Any] = json.loads(json_string, **kwargs)
        return cls.from_dict(dct, validate=validate)  # type: ignore[return-value]

    @classmethod
    def validate(
        cls, instance: dict[str, Any], schema: dict[str, Any] | None = None
    ) -> None:
        """Validate the instance against the class schema in the context of the rootschema."""
        if schema is None:
            schema = cls._schema
        # For the benefit of mypy
        assert schema is not None
        validate_jsonschema(instance, schema, rootschema=cls._rootschema or cls._schema)

    @classmethod
    def resolve_references(cls, schema: dict[str, Any] | None = None) -> dict[str, Any]:
        """Resolve references in the context of this object's schema or root schema."""
        schema_to_pass = schema or cls._schema
        # For the benefit of mypy
        assert schema_to_pass is not None
        return _resolve_references(
            schema=schema_to_pass,
            rootschema=(cls._rootschema or cls._schema or schema),
        )

    @classmethod
    def validate_property(
        cls, name: str, value: Any, schema: dict[str, Any] | None = None
    ) -> None:
        """Validate a property against property schema in the context of the rootschema."""
        opts = _get_optional_modules(np_opt="numpy", pd_opt="pandas")
        value = _todict(value, context={}, **opts)
        props = cls.resolve_references(schema or cls._schema).get("properties", {})
        validate_jsonschema(
            value, props.get(name, {}), rootschema=cls._rootschema or cls._schema
        )

    def __dir__(self) -> list[str]:
        return sorted(chain(super().__dir__(), self._kwds))


def _get_optional_modules(**modules: str) -> dict[str, _OptionalModule]:
    """
    Returns packages only if they have already been imported - otherwise they return `None`.

    This is useful for `isinstance` checks.

    For example, if `pandas` has not been imported, then an object is
    definitely not a `pandas.Timestamp`.

    Parameters
    ----------
    **modules
        Keyword-only binding from `{alias: module_name}`.

    Examples
    --------
    >>> import pandas as pd  # doctest: +SKIP
    >>> import polars as pl  # doctest: +SKIP
    >>> from altair.utils.schemapi import _get_optional_modules  # doctest: +SKIP
    >>>
    >>> _get_optional_modules(pd="pandas", pl="polars", ibis="ibis")  # doctest: +SKIP
    {
        "pd": <module 'pandas' from '...'>,
        "pl": <module 'polars' from '...'>,
        "ibis": None,
    }

    If the user later imports ``ibis``, it would appear in subsequent calls.

    >>> import ibis  # doctest: +SKIP
    >>>
    >>> _get_optional_modules(ibis="ibis")  # doctest: +SKIP
    {
        "ibis": <module 'ibis' from '...'>,
    }
    """
    return {k: sys.modules.get(v) for k, v in modules.items()}


def _replace_parsed_shorthand(
    parsed_shorthand: dict[str, Any], kwds: dict[str, Any]
) -> dict[str, Any]:
    """
    `parsed_shorthand` is added by `FieldChannelMixin`.

    It's used below to replace shorthand with its long form equivalent
    `parsed_shorthand` is removed from `context` if it exists so that it is
    not passed to child `to_dict` function calls.
    """
    # Prevent that pandas categorical data is automatically sorted
    # when a non-ordinal data type is specifed manually
    # or if the encoding channel does not support sorting
    if "sort" in parsed_shorthand and (
        "sort" not in kwds or kwds["type"] not in {"ordinal", Undefined}
    ):
        parsed_shorthand.pop("sort")

    kwds.update(
        (k, v)
        for k, v in parsed_shorthand.items()
        if kwds.get(k, Undefined) is Undefined
    )
    return kwds


TSchemaBase = TypeVar("TSchemaBase", bound=SchemaBase)

_CopyImpl = TypeVar("_CopyImpl", SchemaBase, dict[Any, Any], list[Any])
"""
Types which have an implementation in ``SchemaBase.copy()``.

All other types are returned **by reference**.
"""


def _is_dict(obj: Any | dict[Any, Any]) -> TypeIs[dict[Any, Any]]:
    return isinstance(obj, dict)


def _is_list(obj: Any | list[Any]) -> TypeIs[list[Any]]:
    return isinstance(obj, list)


def _is_iterable(
    obj: Any, *, exclude: type | tuple[type, ...] = (str, bytes)
) -> TypeIs[Iterable[Any]]:
    return not isinstance(obj, exclude) and isinstance(obj, Iterable)


def _passthrough(*args: Any, **kwds: Any) -> Any | dict[str, Any]:
    return args[0] if args else kwds


class _FromDict:
    """
    Class used to construct SchemaBase class hierarchies from a dict.

    The primary purpose of using this class is to be able to build a hash table
    that maps schemas to their wrapper classes. The candidate classes are
    specified in the ``wrapper_classes`` positional-only argument to the constructor.
    """

    _hash_exclude_keys = ("definitions", "title", "description", "$schema", "id")

    def __init__(self, wrapper_classes: Iterable[type[SchemaBase]], /) -> None:
        # Create a mapping of a schema hash to a list of matching classes
        # This lets us quickly determine the correct class to construct
        self.class_dict: dict[int, list[type[SchemaBase]]] = defaultdict(list)
        for tp in wrapper_classes:
            if tp._schema is not None:
                self.class_dict[self.hash_schema(tp._schema)].append(tp)

    @classmethod
    def hash_schema(cls, schema: dict[str, Any], use_json: bool = True) -> int:
        """
        Compute a python hash for a nested dictionary which properly handles dicts, lists, sets, and tuples.

        At the top level, the function excludes from the hashed schema all keys
        listed in `exclude_keys`.

        This implements two methods: one based on conversion to JSON, and one based
        on recursive conversions of unhashable to hashable types; the former seems
        to be slightly faster in several benchmarks.
        """
        if cls._hash_exclude_keys and isinstance(schema, dict):
            schema = {
                key: val
                for key, val in schema.items()
                if key not in cls._hash_exclude_keys
            }
        if use_json:
            s = json.dumps(schema, sort_keys=True)
            return hash(s)
        else:

            def _freeze(val):
                if isinstance(val, dict):
                    return frozenset((k, _freeze(v)) for k, v in val.items())
                elif isinstance(val, set):
                    return frozenset(map(_freeze, val))
                elif isinstance(val, (list, tuple)):
                    return tuple(map(_freeze, val))
                else:
                    return val

            return hash(_freeze(schema))

    @overload
    def from_dict(
        self,
        dct: TSchemaBase,
        tp: None = ...,
        schema: None = ...,
        rootschema: None = ...,
        default_class: Any = ...,
    ) -> TSchemaBase: ...
    @overload
    def from_dict(
        self,
        dct: dict[str, Any] | list[dict[str, Any]],
        tp: Any = ...,
        schema: Any = ...,
        rootschema: Any = ...,
        default_class: type[TSchemaBase] = ...,  # pyright: ignore[reportInvalidTypeVarUse]
    ) -> TSchemaBase: ...
    @overload
    def from_dict(
        self,
        dct: dict[str, Any],
        tp: None = ...,
        schema: dict[str, Any] = ...,
        rootschema: None = ...,
        default_class: Any = ...,
    ) -> SchemaBase: ...
    @overload
    def from_dict(
        self,
        dct: dict[str, Any],
        tp: type[TSchemaBase],
        schema: None = ...,
        rootschema: None = ...,
        default_class: Any = ...,
    ) -> TSchemaBase: ...
    @overload
    def from_dict(
        self,
        dct: dict[str, Any] | list[dict[str, Any]],
        tp: type[TSchemaBase],
        schema: dict[str, Any],
        rootschema: dict[str, Any] | None = ...,
        default_class: Any = ...,
    ) -> Never: ...
    def from_dict(
        self,
        dct: dict[str, Any] | list[dict[str, Any]] | TSchemaBase,
        tp: type[TSchemaBase] | None = None,
        schema: dict[str, Any] | None = None,
        rootschema: dict[str, Any] | None = None,
        default_class: Any = _passthrough,
    ) -> TSchemaBase | SchemaBase:
        """Construct an object from a dict representation."""
        target_tp: Any
        current_schema: dict[str, Any]
        if isinstance(dct, SchemaBase):
            return dct
        elif tp is not None:
            current_schema = tp._schema
            root_schema: dict[str, Any] = rootschema or tp._rootschema or current_schema
            target_tp = tp
        elif schema is not None:
            # If there are multiple matches, we use the first one in the dict.
            # Our class dict is constructed breadth-first from top to bottom,
            # so the first class that matches is the most general match.
            current_schema = schema
            root_schema = rootschema or current_schema
            matches = self.class_dict[self.hash_schema(current_schema)]
            target_tp = matches[0] if matches else default_class
        else:
            msg = "Must provide either `tp` or `schema`, but not both."
            raise ValueError(msg)

        from_dict = partial(self.from_dict, rootschema=root_schema)
        # Can also return a list?
        resolved = _resolve_references(current_schema, root_schema)
        if "anyOf" in resolved or "oneOf" in resolved:
            schemas = resolved.get("anyOf", []) + resolved.get("oneOf", [])
            for possible in schemas:
                try:
                    validate_jsonschema(dct, possible, rootschema=root_schema)
                except jsonschema.ValidationError:
                    continue
                else:
                    return from_dict(dct, schema=possible, default_class=target_tp)

        if _is_dict(dct):
            # TODO: handle schemas for additionalProperties/patternProperties
            props: dict[str, Any] = resolved.get("properties", {})
            kwds = {
                k: (from_dict(v, schema=props[k]) if k in props else v)
                for k, v in dct.items()
            }
            return target_tp(**kwds)
        elif _is_list(dct):
            item_schema: dict[str, Any] = resolved.get("items", {})
            return target_tp([from_dict(k, schema=item_schema) for k in dct])
        else:
            # NOTE: Unsure what is valid here
            return target_tp(dct)


class _PropertySetter:
    def __init__(self, prop: str, schema: dict[str, Any]) -> None:
        self.prop = prop
        self.schema = schema

    def __get__(self, obj, cls):
        self.obj = obj
        self.cls = cls
        # The docs from the encoding class parameter (e.g. `bin` in X, Color,
        # etc); this provides a general description of the parameter.
        self.__doc__ = self.schema["description"].replace("__", "**")
        property_name = f"{self.prop}"[0].upper() + f"{self.prop}"[1:]
        if hasattr(vegalite, property_name):
            altair_prop = getattr(vegalite, property_name)
            # Add the docstring from the helper class (e.g. `BinParams`) so
            # that all the parameter names of the helper class are included in
            # the final docstring
            parameter_index = altair_prop.__doc__.find("Parameters\n")
            if parameter_index > -1:
                self.__doc__ = (
                    altair_prop.__doc__[:parameter_index].replace("    ", "")
                    + self.__doc__
                    + textwrap.dedent(
                        f"\n\n    {altair_prop.__doc__[parameter_index:]}"
                    )
                )
            # For short docstrings such as Aggregate, Stack, et
            else:
                self.__doc__ = (
                    altair_prop.__doc__.replace("    ", "") + "\n" + self.__doc__
                )
            # Add signatures and tab completion for the method and parameter names
            self.__signature__ = inspect.signature(altair_prop)
            self.__wrapped__ = inspect.getfullargspec(altair_prop)
            self.__name__ = altair_prop.__name__
        else:
            # It seems like bandPosition is the only parameter that doesn't
            # have a helper class.
            pass
        return self

    def __call__(self, *args: Any, **kwargs: Any):
        obj = self.obj.copy()
        # TODO: use schema to validate
        obj[self.prop] = args[0] if args else kwargs
        return obj


def with_property_setters(cls: type[TSchemaBase]) -> type[TSchemaBase]:
    """Decorator to add property setters to a Schema class."""
    schema = cls.resolve_references()
    for prop, propschema in schema.get("properties", {}).items():
        setattr(cls, prop, _PropertySetter(prop, propschema))
    return cls
