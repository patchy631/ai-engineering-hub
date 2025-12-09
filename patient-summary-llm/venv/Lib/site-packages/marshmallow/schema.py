"""The `Schema <marshmallow.Schema>` class, including its metaclass and options (`class Meta <marshmallow.Schema.Meta>`)."""

from __future__ import annotations

import copy
import datetime as dt
import decimal
import functools
import inspect
import json
import operator
import typing
import uuid
import warnings
from abc import ABCMeta
from collections import OrderedDict, defaultdict
from collections.abc import Mapping
from itertools import zip_longest

from marshmallow import base, class_registry, types
from marshmallow import fields as ma_fields
from marshmallow.decorators import (
    POST_DUMP,
    POST_LOAD,
    PRE_DUMP,
    PRE_LOAD,
    VALIDATES,
    VALIDATES_SCHEMA,
)
from marshmallow.error_store import ErrorStore
from marshmallow.exceptions import SCHEMA, StringNotCollectionError, ValidationError
from marshmallow.orderedset import OrderedSet
from marshmallow.utils import (
    EXCLUDE,
    INCLUDE,
    RAISE,
    get_value,
    is_collection,
    is_instance_or_subclass,
    missing,
    set_value,
    validate_unknown_parameter_value,
)
from marshmallow.warnings import RemovedInMarshmallow4Warning

if typing.TYPE_CHECKING:
    from marshmallow.fields import Field


def _get_fields(attrs) -> list[tuple[str, Field]]:
    """Get fields from a class

    :param attrs: Mapping of class attributes
    """
    return [
        (field_name, field_value)
        for field_name, field_value in attrs.items()
        if is_instance_or_subclass(field_value, base.FieldABC)
    ]


# This function allows Schemas to inherit from non-Schema classes and ensures
#   inheritance according to the MRO
def _get_fields_by_mro(klass: SchemaMeta):
    """Collect fields from a class, following its method resolution order. The
    class itself is excluded from the search; only its parents are checked. Get
    fields from ``_declared_fields`` if available, else use ``__dict__``.

    :param klass: Class whose fields to retrieve
    """
    mro = inspect.getmro(klass)
    # Combine fields from all parents
    # functools.reduce(operator.iadd, list_of_lists) is faster than sum(list_of_lists, [])
    # Loop over mro in reverse to maintain correct order of fields
    return functools.reduce(
        operator.iadd,
        (
            _get_fields(
                getattr(base, "_declared_fields", base.__dict__),
            )
            for base in mro[:0:-1]
        ),
        [],
    )


class SchemaMeta(ABCMeta):
    """Metaclass for the Schema class. Binds the declared fields to
    a ``_declared_fields`` attribute, which is a dictionary mapping attribute
    names to field objects. Also sets the ``opts`` class attribute, which is
    the Schema class's `class Meta <marshmallow.Schema.Meta>` options.
    """

    Meta: type
    opts: typing.Any
    OPTIONS_CLASS: type
    _declared_fields: dict[str, Field]

    def __new__(
        mcs,  # noqa: N804
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, typing.Any],
    ) -> SchemaMeta:
        meta = attrs.get("Meta")
        ordered = getattr(meta, "ordered", False)
        if not ordered:
            # Inherit 'ordered' option
            # Warning: We loop through bases instead of MRO because we don't
            # yet have access to the class object
            # (i.e. can't call super before we have fields)
            for base_ in bases:
                if hasattr(base_, "Meta") and hasattr(base_.Meta, "ordered"):
                    ordered = base_.Meta.ordered
                    break
            else:
                ordered = False
        cls_fields = _get_fields(attrs)
        # Remove fields from list of class attributes to avoid shadowing
        # Schema attributes/methods in case of name conflict
        for field_name, _ in cls_fields:
            del attrs[field_name]
        klass = super().__new__(mcs, name, bases, attrs)
        inherited_fields = _get_fields_by_mro(klass)

        meta = klass.Meta
        # Set klass.opts in __new__ rather than __init__ so that it is accessible in
        # get_declared_fields
        klass.opts = klass.OPTIONS_CLASS(meta, ordered=ordered)
        # Add fields specified in the `include` class Meta option
        cls_fields += list(klass.opts.include.items())

        # Assign _declared_fields on class
        klass._declared_fields = mcs.get_declared_fields(  # noqa: SLF001
            klass=klass,
            cls_fields=cls_fields,
            inherited_fields=inherited_fields,
            dict_cls=dict,
        )
        return klass

    @classmethod
    def get_declared_fields(
        mcs,  # noqa: N804
        klass: SchemaMeta,
        cls_fields: list[tuple[str, Field]],
        inherited_fields: list[tuple[str, Field]],
        dict_cls: type[dict] = dict,
    ) -> dict[str, Field]:
        """Returns a dictionary of field_name => `Field` pairs declared on the class.
        This is exposed mainly so that plugins can add additional fields, e.g. fields
        computed from `class Meta <marshmallow.Schema.Meta>` options.

        :param klass: The class object.
        :param cls_fields: The fields declared on the class, including those added
            by the ``include`` `class Meta <marshmallow.Schema.Meta>` option.
        :param inherited_fields: Inherited fields.
        :param dict_cls: dict-like class to use for dict output Default to ``dict``.
        """
        return dict_cls(inherited_fields + cls_fields)

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name and cls.opts.register:
            class_registry.register(name, cls)
        cls._hooks = cls.resolve_hooks()

    def resolve_hooks(cls) -> dict[str, list[tuple[str, bool, dict]]]:
        """Add in the decorated processors

        By doing this after constructing the class, we let standard inheritance
        do all the hard work.
        """
        mro = inspect.getmro(cls)

        hooks: dict[str, list[tuple[str, bool, dict]]] = defaultdict(list)

        for attr_name in dir(cls):
            # Need to look up the actual descriptor, not whatever might be
            # bound to the class. This needs to come from the __dict__ of the
            # declaring class.
            for parent in mro:
                try:
                    attr = parent.__dict__[attr_name]
                except KeyError:
                    continue
                else:
                    break
            else:
                # In case we didn't find the attribute and didn't break above.
                # We should never hit this - it's just here for completeness
                # to exclude the possibility of attr being undefined.
                continue

            try:
                hook_config: dict[str, list[tuple[bool, dict]]] = (
                    attr.__marshmallow_hook__
                )
            except AttributeError:
                pass
            else:
                for tag, config in hook_config.items():
                    # Use name here so we can get the bound method later, in
                    # case the processor was a descriptor or something.
                    hooks[tag].extend(
                        (attr_name, many, kwargs) for many, kwargs in config
                    )

        return hooks


class SchemaOpts:
    """Defines defaults for `marshmallow.Schema.Meta`."""

    def __init__(self, meta: type, ordered: bool = False):  # noqa: FBT001, FBT002
        self.fields = getattr(meta, "fields", ())
        if not isinstance(self.fields, (list, tuple)):
            raise ValueError("`fields` option must be a list or tuple.")
        self.additional = getattr(meta, "additional", ())
        if not isinstance(self.additional, (list, tuple)):
            raise ValueError("`additional` option must be a list or tuple.")
        if self.fields and self.additional:
            raise ValueError(
                "Cannot set both `fields` and `additional` options for the same Schema."
            )
        self.exclude = getattr(meta, "exclude", ())
        if not isinstance(self.exclude, (list, tuple)):
            raise ValueError("`exclude` must be a list or tuple.")
        self.dateformat = getattr(meta, "dateformat", None)
        self.datetimeformat = getattr(meta, "datetimeformat", None)
        self.timeformat = getattr(meta, "timeformat", None)
        if hasattr(meta, "json_module"):
            warnings.warn(
                "The json_module class Meta option is deprecated. Use render_module instead.",
                RemovedInMarshmallow4Warning,
                stacklevel=2,
            )
            render_module = getattr(meta, "json_module", json)
        else:
            render_module = json
        self.render_module = getattr(meta, "render_module", render_module)
        if hasattr(meta, "ordered"):
            warnings.warn(
                "The `ordered` `class Meta` option is deprecated. "
                "Field order is already preserved by default. "
                "Set `Schema.dict_class` to OrderedDict to maintain the previous behavior.",
                RemovedInMarshmallow4Warning,
                stacklevel=2,
            )
        self.ordered = getattr(meta, "ordered", ordered)
        self.index_errors = getattr(meta, "index_errors", True)
        self.include = getattr(meta, "include", {})
        self.load_only = getattr(meta, "load_only", ())
        self.dump_only = getattr(meta, "dump_only", ())
        self.unknown = validate_unknown_parameter_value(getattr(meta, "unknown", RAISE))
        self.register = getattr(meta, "register", True)
        self.many = getattr(meta, "many", False)


class Schema(base.SchemaABC, metaclass=SchemaMeta):
    """Base schema class with which to define schemas.

    Example usage:

    .. code-block:: python

        import datetime as dt
        from dataclasses import dataclass

        from marshmallow import Schema, fields


        @dataclass
        class Album:
            title: str
            release_date: dt.date


        class AlbumSchema(Schema):
            title = fields.Str()
            release_date = fields.Date()


        album = Album("Beggars Banquet", dt.date(1968, 12, 6))
        schema = AlbumSchema()
        data = schema.dump(album)
        data  # {'release_date': '1968-12-06', 'title': 'Beggars Banquet'}

    :param only: Whitelist of the declared fields to select when
        instantiating the Schema. If None, all fields are used. Nested fields
        can be represented with dot delimiters.
    :param exclude: Blacklist of the declared fields to exclude
        when instantiating the Schema. If a field appears in both `only` and
        `exclude`, it is not used. Nested fields can be represented with dot
        delimiters.
    :param many: Should be set to `True` if ``obj`` is a collection
        so that the object will be serialized to a list.
    :param context: Optional context passed to :class:`fields.Method` and
        :class:`fields.Function` fields.
    :param load_only: Fields to skip during serialization (write-only fields)
    :param dump_only: Fields to skip during deserialization (read-only fields)
    :param partial: Whether to ignore missing fields and not require
        any fields declared. Propagates down to ``Nested`` fields as well. If
        its value is an iterable, only missing fields listed in that iterable
        will be ignored. Use dot delimiters to specify nested fields.
    :param unknown: Whether to exclude, include, or raise an error for unknown
        fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.

    .. versionchanged:: 3.0.0
        `prefix` parameter removed.
    """

    TYPE_MAPPING: dict[type, type[Field]] = {
        str: ma_fields.String,
        bytes: ma_fields.String,
        dt.datetime: ma_fields.DateTime,
        float: ma_fields.Float,
        bool: ma_fields.Boolean,
        tuple: ma_fields.Raw,
        list: ma_fields.Raw,
        set: ma_fields.Raw,
        int: ma_fields.Integer,
        uuid.UUID: ma_fields.UUID,
        dt.time: ma_fields.Time,
        dt.date: ma_fields.Date,
        dt.timedelta: ma_fields.TimeDelta,
        decimal.Decimal: ma_fields.Decimal,
    }
    #: Overrides for default schema-level error messages
    error_messages: dict[str, str] = {}

    _default_error_messages: dict[str, str] = {
        "type": "Invalid input type.",
        "unknown": "Unknown field.",
    }

    OPTIONS_CLASS: type = SchemaOpts

    set_class = OrderedSet

    # These get set by SchemaMeta
    opts: typing.Any
    _declared_fields: dict[str, Field] = {}
    _hooks: dict[str, list[tuple[str, bool, dict]]] = {}

    class Meta:
        """Options object for a Schema.

        Example usage: ::

            from marshmallow import Schema


            class MySchema(Schema):
                class Meta:
                    fields = ("id", "email", "date_created")
                    exclude = ("password", "secret_attribute")

        .. admonition:: A note on type checking

            Type checkers will only check the attributes of the `Meta <marshmallow.Schema.Meta>`
            class if you explicitly subclass `marshmallow.Schema.Meta`.

            .. code-block:: python

                from marshmallow import Schema


                class MySchema(Schema):
                    # Not checked by type checkers
                    class Meta:
                        additional = True


                class MySchema2(Schema):
                    # Type checkers will check attributes
                    class Meta(Schema.Opts):
                        additional = True  # Incompatible types in assignment

        .. versionremoved:: 3.0.0b7 Remove ``strict``.
        .. versionadded:: 3.0.0b12 Add `unknown`.
        .. versionchanged:: 3.0.0b17 Rename ``dateformat`` to `datetimeformat`.
        .. versionadded:: 3.9.0 Add `timeformat`.
        .. versionchanged:: 3.26.0 Deprecate `ordered`. Field order is preserved by default.
        """

        fields: typing.ClassVar[tuple[str, ...] | list[str]]
        """Fields to include in the (de)serialized result"""
        additional: typing.ClassVar[tuple[str, ...] | list[str]]
        """Fields to include in addition to the explicitly declared fields.
        `additional <marshmallow.Schema.Meta.additional>` and `fields <marshmallow.Schema.Meta.fields>`
        are mutually-exclusive options.
        """
        include: typing.ClassVar[dict[str, Field]]
        """Dictionary of additional fields to include in the schema. It is
        usually better to define fields as class variables, but you may need to
        use this option, e.g., if your fields are Python keywords.
        """
        exclude: typing.ClassVar[tuple[str, ...] | list[str]]
        """Fields to exclude in the serialized result.
        Nested fields can be represented with dot delimiters.
        """
        many: typing.ClassVar[bool]
        """Whether data should be (de)serialized as a collection by default."""
        dateformat: typing.ClassVar[str]
        """Default format for `Date <marshmallow.fields.Date>` fields."""
        datetimeformat: typing.ClassVar[str]
        """Default format for `DateTime <marshmallow.fields.DateTime>` fields."""
        timeformat: typing.ClassVar[str]
        """Default format for `Time <marshmallow.fields.Time>` fields."""

        # FIXME: Use a more constrained type here.
        # ClassVar[RenderModule] doesn't work.
        render_module: typing.Any
        """ Module to use for `loads <marshmallow.Schema.loads>` and `dumps <marshmallow.Schema.dumps>`.
        Defaults to `json` from the standard library.
        """
        ordered: typing.ClassVar[bool]
        """If `True`, `Schema.dump <marshmallow.Schema.dump>` is a `collections.OrderedDict`."""
        index_errors: typing.ClassVar[bool]
        """If `True`, errors dictionaries will include the index of invalid items in a collection."""
        load_only: typing.ClassVar[tuple[str, ...] | list[str]]
        """Fields to exclude from serialized results"""
        dump_only: typing.ClassVar[tuple[str, ...] | list[str]]
        """Fields to exclude from serialized results"""
        unknown: typing.ClassVar[str]
        """Whether to exclude, include, or raise an error for unknown fields in the data.
        Use `EXCLUDE`, `INCLUDE` or `RAISE`.
        """
        register: typing.ClassVar[bool]
        """Whether to register the `Schema <marshmallow.Schema>` with marshmallow's internal
        class registry. Must be `True` if you intend to refer to this `Schema <marshmallow.Schema>`
        by class name in `Nested` fields. Only set this to `False` when memory
        usage is critical. Defaults to `True`.
        """

    def __init__(
        self,
        *,
        only: types.StrSequenceOrSet | None = None,
        exclude: types.StrSequenceOrSet = (),
        many: bool | None = None,
        context: dict | None = None,
        load_only: types.StrSequenceOrSet = (),
        dump_only: types.StrSequenceOrSet = (),
        partial: bool | types.StrSequenceOrSet | None = None,
        unknown: str | None = None,
    ):
        # Raise error if only or exclude is passed as string, not list of strings
        if only is not None and not is_collection(only):
            raise StringNotCollectionError('"only" should be a list of strings')
        if not is_collection(exclude):
            raise StringNotCollectionError('"exclude" should be a list of strings')
        # copy declared fields from metaclass
        self.declared_fields = copy.deepcopy(self._declared_fields)
        self.many = self.opts.many if many is None else many
        self.only = only
        self.exclude: set[typing.Any] | typing.MutableSet[typing.Any] = set(
            self.opts.exclude
        ) | set(exclude)
        self.ordered = self.opts.ordered
        self.load_only = set(load_only) or set(self.opts.load_only)
        self.dump_only = set(dump_only) or set(self.opts.dump_only)
        self.partial = partial
        self.unknown = (
            self.opts.unknown
            if unknown is None
            else validate_unknown_parameter_value(unknown)
        )
        if context:
            warnings.warn(
                "The `context` parameter is deprecated and will be removed in marshmallow 4.0. "
                "Use `contextvars.ContextVar` to pass context instead.",
                RemovedInMarshmallow4Warning,
                stacklevel=2,
            )
        self.context = context or {}
        self._normalize_nested_options()
        #: Dictionary mapping field_names -> :class:`Field` objects
        self.fields: dict[str, Field] = {}
        self.load_fields: dict[str, Field] = {}
        self.dump_fields: dict[str, Field] = {}
        self._init_fields()
        messages = {}
        messages.update(self._default_error_messages)
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, "error_messages", {}))
        messages.update(self.error_messages or {})
        self.error_messages = messages

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(many={self.many})>"

    @property
    def dict_class(self) -> type[dict]:
        """`dict` type to return when serializing."""
        if self.ordered:
            return OrderedDict
        return dict

    @classmethod
    def from_dict(
        cls,
        fields: dict[str, Field],
        *,
        name: str = "GeneratedSchema",
    ) -> type[Schema]:
        """Generate a `Schema <marshmallow.Schema>` class given a dictionary of fields.

        .. code-block:: python

            from marshmallow import Schema, fields

            PersonSchema = Schema.from_dict({"name": fields.Str()})
            print(PersonSchema().load({"name": "David"}))  # => {'name': 'David'}

        Generated schemas are not added to the class registry and therefore cannot
        be referred to by name in `Nested` fields.


        :param fields: Dictionary mapping field names to field instances.
        :param name: Optional name for the class, which will appear in
            the ``repr`` for the class.

        .. versionadded:: 3.0.0
        """
        Meta = type(
            "GeneratedMeta", (getattr(cls, "Meta", object),), {"register": False}
        )
        return type(name, (cls,), {**fields.copy(), "Meta": Meta})

    ##### Override-able methods #####

    def handle_error(
        self, error: ValidationError, data: typing.Any, *, many: bool, **kwargs
    ):
        """Custom error handler function for the schema.

        :param error: The `ValidationError` raised during (de)serialization.
        :param data: The original input data.
        :param many: Value of ``many`` on dump or load.
        :param partial: Value of ``partial`` on load.

        .. versionchanged:: 3.0.0rc9
            Receives `many` and `partial` (on deserialization) as keyword arguments.
        """

    def get_attribute(self, obj: typing.Any, attr: str, default: typing.Any):
        """Defines how to pull values from an object to serialize.

        .. versionchanged:: 3.0.0a1
            Changed position of ``obj`` and ``attr``.
        """
        return get_value(obj, attr, default)

    ##### Serialization/Deserialization API #####

    @staticmethod
    def _call_and_store(getter_func, data, *, field_name, error_store, index=None):
        """Call ``getter_func`` with ``data`` as its argument, and store any `ValidationErrors`.

        :param getter_func: Function for getting the serialized/deserialized
            value from ``data``.
        :param data: The data passed to ``getter_func``.
        :param field_name: Field name.
        :param index: Index of the item being validated, if validating a collection,
            otherwise `None`.
        """
        try:
            value = getter_func(data)
        except ValidationError as error:
            error_store.store_error(error.messages, field_name, index=index)
            # When a Nested field fails validation, the marshalled data is stored
            # on the ValidationError's valid_data attribute
            return error.valid_data or missing
        return value

    def _serialize(self, obj: typing.Any, *, many: bool = False):
        """Serialize ``obj``.

        :param obj: The object(s) to serialize.
        :param many: `True` if ``data`` should be serialized as a collection.
        :return: A dictionary of the serialized data
        """
        if many and obj is not None:
            return [self._serialize(d, many=False) for d in obj]
        ret = self.dict_class()
        for attr_name, field_obj in self.dump_fields.items():
            value = field_obj.serialize(attr_name, obj, accessor=self.get_attribute)
            if value is missing:
                continue
            key = field_obj.data_key if field_obj.data_key is not None else attr_name
            ret[key] = value
        return ret

    def dump(self, obj: typing.Any, *, many: bool | None = None):
        """Serialize an object to native Python data types according to this
        Schema's fields.

        :param obj: The object to serialize.
        :param many: Whether to serialize `obj` as a collection. If `None`, the value
            for `self.many` is used.
        :return: Serialized data

        .. versionadded:: 1.0.0
        .. versionchanged:: 3.0.0b7
            This method returns the serialized data rather than a ``(data, errors)`` duple.
            A :exc:`ValidationError <marshmallow.exceptions.ValidationError>` is raised
            if ``obj`` is invalid.
        .. versionchanged:: 3.0.0rc9
            Validation no longer occurs upon serialization.
        """
        many = self.many if many is None else bool(many)
        if self._hooks[PRE_DUMP]:
            processed_obj = self._invoke_dump_processors(
                PRE_DUMP, obj, many=many, original_data=obj
            )
        else:
            processed_obj = obj

        result = self._serialize(processed_obj, many=many)

        if self._hooks[POST_DUMP]:
            result = self._invoke_dump_processors(
                POST_DUMP, result, many=many, original_data=obj
            )

        return result

    def dumps(self, obj: typing.Any, *args, many: bool | None = None, **kwargs):
        """Same as :meth:`dump`, except return a JSON-encoded string.

        :param obj: The object to serialize.
        :param many: Whether to serialize `obj` as a collection. If `None`, the value
            for `self.many` is used.
        :return: A ``json`` string

        .. versionadded:: 1.0.0
        .. versionchanged:: 3.0.0b7
            This method returns the serialized data rather than a ``(data, errors)`` duple.
            A :exc:`ValidationError <marshmallow.exceptions.ValidationError>` is raised
            if ``obj`` is invalid.
        """
        serialized = self.dump(obj, many=many)
        return self.opts.render_module.dumps(serialized, *args, **kwargs)

    def _deserialize(
        self,
        data: (
            typing.Mapping[str, typing.Any]
            | typing.Iterable[typing.Mapping[str, typing.Any]]
        ),
        *,
        error_store: ErrorStore,
        many: bool = False,
        partial=None,
        unknown=RAISE,
        index=None,
    ) -> typing.Any | list[typing.Any]:
        """Deserialize ``data``.

        :param data: The data to deserialize.
        :param error_store: Structure to store errors.
        :param many: `True` if ``data`` should be deserialized as a collection.
        :param partial: Whether to ignore missing fields and not require
            any fields declared. Propagates down to ``Nested`` fields as well. If
            its value is an iterable, only missing fields listed in that iterable
            will be ignored. Use dot delimiters to specify nested fields.
        :param unknown: Whether to exclude, include, or raise an error for unknown
            fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.
        :param index: Index of the item being serialized (for storing errors) if
            serializing a collection, otherwise `None`.
        :return: The deserialized data as `dict_class` instance or list of `dict_class`
        instances if `many` is `True`.
        """
        index_errors = self.opts.index_errors
        index = index if index_errors else None
        if many:
            if not is_collection(data):
                error_store.store_error([self.error_messages["type"]], index=index)
                ret_l = []
            else:
                ret_l = [
                    self._deserialize(
                        typing.cast(dict, d),
                        error_store=error_store,
                        many=False,
                        partial=partial,
                        unknown=unknown,
                        index=idx,
                    )
                    for idx, d in enumerate(data)
                ]
            return ret_l
        ret_d = self.dict_class()
        # Check data is a dict
        if not isinstance(data, Mapping):
            error_store.store_error([self.error_messages["type"]], index=index)
        else:
            partial_is_collection = is_collection(partial)
            for attr_name, field_obj in self.load_fields.items():
                field_name = (
                    field_obj.data_key if field_obj.data_key is not None else attr_name
                )
                raw_value = data.get(field_name, missing)
                if raw_value is missing:
                    # Ignore missing field if we're allowed to.
                    if partial is True or (
                        partial_is_collection and attr_name in partial
                    ):
                        continue
                d_kwargs = {}
                # Allow partial loading of nested schemas.
                if partial_is_collection:
                    prefix = field_name + "."
                    len_prefix = len(prefix)
                    sub_partial = [
                        f[len_prefix:] for f in partial if f.startswith(prefix)
                    ]
                    d_kwargs["partial"] = sub_partial
                elif partial is not None:
                    d_kwargs["partial"] = partial

                def getter(
                    val, field_obj=field_obj, field_name=field_name, d_kwargs=d_kwargs
                ):
                    return field_obj.deserialize(
                        val,
                        field_name,
                        data,
                        **d_kwargs,
                    )

                value = self._call_and_store(
                    getter_func=getter,
                    data=raw_value,
                    field_name=field_name,
                    error_store=error_store,
                    index=index,
                )
                if value is not missing:
                    key = field_obj.attribute or attr_name
                    set_value(ret_d, key, value)
            if unknown != EXCLUDE:
                fields = {
                    field_obj.data_key if field_obj.data_key is not None else field_name
                    for field_name, field_obj in self.load_fields.items()
                }
                for key in set(data) - fields:
                    value = data[key]
                    if unknown == INCLUDE:
                        ret_d[key] = value
                    elif unknown == RAISE:
                        error_store.store_error(
                            [self.error_messages["unknown"]],
                            key,
                            (index if index_errors else None),
                        )
        return ret_d

    def load(
        self,
        data: (
            typing.Mapping[str, typing.Any]
            | typing.Iterable[typing.Mapping[str, typing.Any]]
        ),
        *,
        many: bool | None = None,
        partial: bool | types.StrSequenceOrSet | None = None,
        unknown: str | None = None,
    ):
        """Deserialize a data structure to an object defined by this Schema's fields.

        :param data: The data to deserialize.
        :param many: Whether to deserialize `data` as a collection. If `None`, the
            value for `self.many` is used.
        :param partial: Whether to ignore missing fields and not require
            any fields declared. Propagates down to ``Nested`` fields as well. If
            its value is an iterable, only missing fields listed in that iterable
            will be ignored. Use dot delimiters to specify nested fields.
        :param unknown: Whether to exclude, include, or raise an error for unknown
            fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.
            If `None`, the value for `self.unknown` is used.
        :return: Deserialized data

        .. versionadded:: 1.0.0
        .. versionchanged:: 3.0.0b7
            This method returns the deserialized data rather than a ``(data, errors)`` duple.
            A :exc:`ValidationError <marshmallow.exceptions.ValidationError>` is raised
            if invalid data are passed.
        """
        return self._do_load(
            data, many=many, partial=partial, unknown=unknown, postprocess=True
        )

    def loads(
        self,
        json_data: str | bytes | bytearray,
        *,
        many: bool | None = None,
        partial: bool | types.StrSequenceOrSet | None = None,
        unknown: str | None = None,
        **kwargs,
    ):
        """Same as :meth:`load`, except it uses `marshmallow.Schema.Meta.render_module` to deserialize
        the passed string before passing data to :meth:`load`.

        :param json_data: A string of the data to deserialize.
        :param many: Whether to deserialize `obj` as a collection. If `None`, the
            value for `self.many` is used.
        :param partial: Whether to ignore missing fields and not require
            any fields declared. Propagates down to ``Nested`` fields as well. If
            its value is an iterable, only missing fields listed in that iterable
            will be ignored. Use dot delimiters to specify nested fields.
        :param unknown: Whether to exclude, include, or raise an error for unknown
            fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.
            If `None`, the value for `self.unknown` is used.
        :return: Deserialized data

        .. versionadded:: 1.0.0
        .. versionchanged:: 3.0.0b7
            This method returns the deserialized data rather than a ``(data, errors)`` duple.
            A :exc:`ValidationError <marshmallow.exceptions.ValidationError>` is raised
            if invalid data are passed.
        """
        data = self.opts.render_module.loads(json_data, **kwargs)
        return self.load(data, many=many, partial=partial, unknown=unknown)

    def _run_validator(
        self,
        validator_func: types.SchemaValidator,
        output,
        *,
        original_data,
        error_store: ErrorStore,
        many: bool,
        partial: bool | types.StrSequenceOrSet | None,
        pass_original: bool,
        index: int | None = None,
    ):
        try:
            if pass_original:  # Pass original, raw data (before unmarshalling)
                validator_func(output, original_data, partial=partial, many=many)
            else:
                validator_func(output, partial=partial, many=many)
        except ValidationError as err:
            field_name = err.field_name
            data_key: str
            if field_name == SCHEMA:
                data_key = SCHEMA
            else:
                field_obj: Field | None = None
                try:
                    field_obj = self.fields[field_name]
                except KeyError:
                    if field_name in self.declared_fields:
                        field_obj = self.declared_fields[field_name]
                if field_obj:
                    data_key = (
                        field_obj.data_key
                        if field_obj.data_key is not None
                        else field_name
                    )
                else:
                    data_key = field_name
            error_store.store_error(err.messages, data_key, index=index)

    def validate(
        self,
        data: (
            typing.Mapping[str, typing.Any]
            | typing.Iterable[typing.Mapping[str, typing.Any]]
        ),
        *,
        many: bool | None = None,
        partial: bool | types.StrSequenceOrSet | None = None,
    ) -> dict[str, list[str]]:
        """Validate `data` against the schema, returning a dictionary of
        validation errors.

        :param data: The data to validate.
        :param many: Whether to validate `data` as a collection. If `None`, the
            value for `self.many` is used.
        :param partial: Whether to ignore missing fields and not require
            any fields declared. Propagates down to ``Nested`` fields as well. If
            its value is an iterable, only missing fields listed in that iterable
            will be ignored. Use dot delimiters to specify nested fields.
        :return: A dictionary of validation errors.

        .. versionadded:: 1.1.0
        """
        try:
            self._do_load(data, many=many, partial=partial, postprocess=False)
        except ValidationError as exc:
            return typing.cast(dict[str, list[str]], exc.messages)
        return {}

    ##### Private Helpers #####

    def _do_load(
        self,
        data: (
            typing.Mapping[str, typing.Any]
            | typing.Iterable[typing.Mapping[str, typing.Any]]
        ),
        *,
        many: bool | None = None,
        partial: bool | types.StrSequenceOrSet | None = None,
        unknown: str | None = None,
        postprocess: bool = True,
    ):
        """Deserialize `data`, returning the deserialized result.
        This method is private API.

        :param data: The data to deserialize.
        :param many: Whether to deserialize `data` as a collection. If `None`, the
            value for `self.many` is used.
        :param partial: Whether to validate required fields. If its
            value is an iterable, only fields listed in that iterable will be
            ignored will be allowed missing. If `True`, all fields will be allowed missing.
            If `None`, the value for `self.partial` is used.
        :param unknown: Whether to exclude, include, or raise an error for unknown
            fields in the data. Use `EXCLUDE`, `INCLUDE` or `RAISE`.
            If `None`, the value for `self.unknown` is used.
        :param postprocess: Whether to run post_load methods..
        :return: Deserialized data
        """
        error_store = ErrorStore()
        errors: dict[str, list[str]] = {}
        many = self.many if many is None else bool(many)
        unknown = (
            self.unknown
            if unknown is None
            else validate_unknown_parameter_value(unknown)
        )
        if partial is None:
            partial = self.partial
        # Run preprocessors
        if self._hooks[PRE_LOAD]:
            try:
                processed_data = self._invoke_load_processors(
                    PRE_LOAD, data, many=many, original_data=data, partial=partial
                )
            except ValidationError as err:
                errors = err.normalized_messages()
                result: list | dict | None = None
        else:
            processed_data = data
        if not errors:
            # Deserialize data
            result = self._deserialize(
                processed_data,
                error_store=error_store,
                many=many,
                partial=partial,
                unknown=unknown,
            )
            # Run field-level validation
            self._invoke_field_validators(
                error_store=error_store, data=result, many=many
            )
            # Run schema-level validation
            if self._hooks[VALIDATES_SCHEMA]:
                field_errors = bool(error_store.errors)
                self._invoke_schema_validators(
                    error_store=error_store,
                    pass_many=True,
                    data=result,
                    original_data=data,
                    many=many,
                    partial=partial,
                    field_errors=field_errors,
                )
                self._invoke_schema_validators(
                    error_store=error_store,
                    pass_many=False,
                    data=result,
                    original_data=data,
                    many=many,
                    partial=partial,
                    field_errors=field_errors,
                )
            errors = error_store.errors
            # Run post processors
            if not errors and postprocess and self._hooks[POST_LOAD]:
                try:
                    result = self._invoke_load_processors(
                        POST_LOAD,
                        result,
                        many=many,
                        original_data=data,
                        partial=partial,
                    )
                except ValidationError as err:
                    errors = err.normalized_messages()
        if errors:
            exc = ValidationError(errors, data=data, valid_data=result)
            self.handle_error(exc, data, many=many, partial=partial)
            raise exc

        return result

    def _normalize_nested_options(self) -> None:
        """Apply then flatten nested schema options.
        This method is private API.
        """
        if self.only is not None:
            # Apply the only option to nested fields.
            self.__apply_nested_option("only", self.only, "intersection")
            # Remove the child field names from the only option.
            self.only = self.set_class([field.split(".", 1)[0] for field in self.only])
        if self.exclude:
            # Apply the exclude option to nested fields.
            self.__apply_nested_option("exclude", self.exclude, "union")
            # Remove the parent field names from the exclude option.
            self.exclude = self.set_class(
                [field for field in self.exclude if "." not in field]
            )

    def __apply_nested_option(self, option_name, field_names, set_operation) -> None:
        """Apply nested options to nested fields"""
        # Split nested field names on the first dot.
        nested_fields = [name.split(".", 1) for name in field_names if "." in name]
        # Partition the nested field names by parent field.
        nested_options = defaultdict(list)  # type: defaultdict
        for parent, nested_names in nested_fields:
            nested_options[parent].append(nested_names)
        # Apply the nested field options.
        for key, options in iter(nested_options.items()):
            new_options = self.set_class(options)
            original_options = getattr(self.declared_fields[key], option_name, ())
            if original_options:
                if set_operation == "union":
                    new_options |= self.set_class(original_options)
                if set_operation == "intersection":
                    new_options &= self.set_class(original_options)
            setattr(self.declared_fields[key], option_name, new_options)

    def _init_fields(self) -> None:
        """Update self.fields, self.load_fields, and self.dump_fields based on schema options.
        This method is private API.
        """
        if self.opts.fields:
            available_field_names = self.set_class(self.opts.fields)
        else:
            available_field_names = self.set_class(self.declared_fields.keys())
            if self.opts.additional:
                available_field_names |= self.set_class(self.opts.additional)

        invalid_fields = self.set_class()

        if self.only is not None:
            # Return only fields specified in only option
            field_names: typing.AbstractSet[typing.Any] = self.set_class(self.only)

            invalid_fields |= field_names - available_field_names
        else:
            field_names = available_field_names

        # If "exclude" option or param is specified, remove those fields.
        if self.exclude:
            # Note that this isn't available_field_names, since we want to
            # apply "only" for the actual calculation.
            field_names = field_names - self.exclude
            invalid_fields |= self.exclude - available_field_names

        if invalid_fields:
            message = f"Invalid fields for {self}: {invalid_fields}."
            raise ValueError(message)

        fields_dict = self.dict_class()
        for field_name in field_names:
            field_obj = self.declared_fields.get(field_name, ma_fields.Inferred())
            self._bind_field(field_name, field_obj)
            fields_dict[field_name] = field_obj

        load_fields, dump_fields = self.dict_class(), self.dict_class()
        for field_name, field_obj in fields_dict.items():
            if not field_obj.dump_only:
                load_fields[field_name] = field_obj
            if not field_obj.load_only:
                dump_fields[field_name] = field_obj

        dump_data_keys = [
            field_obj.data_key if field_obj.data_key is not None else name
            for name, field_obj in dump_fields.items()
        ]
        if len(dump_data_keys) != len(set(dump_data_keys)):
            data_keys_duplicates = {
                x for x in dump_data_keys if dump_data_keys.count(x) > 1
            }
            raise ValueError(
                "The data_key argument for one or more fields collides "
                "with another field's name or data_key argument. "
                "Check the following field names and "
                f"data_key arguments: {list(data_keys_duplicates)}"
            )
        load_attributes = [obj.attribute or name for name, obj in load_fields.items()]
        if len(load_attributes) != len(set(load_attributes)):
            attributes_duplicates = {
                x for x in load_attributes if load_attributes.count(x) > 1
            }
            raise ValueError(
                "The attribute argument for one or more fields collides "
                "with another field's name or attribute argument. "
                "Check the following field names and "
                f"attribute arguments: {list(attributes_duplicates)}"
            )

        self.fields = fields_dict
        self.dump_fields = dump_fields
        self.load_fields = load_fields

    def on_bind_field(self, field_name: str, field_obj: Field) -> None:
        """Hook to modify a field when it is bound to the `Schema <marshmallow.Schema>`.

        No-op by default.
        """
        return

    def _bind_field(self, field_name: str, field_obj: Field) -> None:
        """Bind field to the schema, setting any necessary attributes on the
        field (e.g. parent and name).

        Also set field load_only and dump_only values if field_name was
        specified in `class Meta <marshmallow.Schema.Meta>`.
        """
        if field_name in self.load_only:
            field_obj.load_only = True
        if field_name in self.dump_only:
            field_obj.dump_only = True
        try:
            field_obj._bind_to_schema(field_name, self)  # noqa: SLF001
        except TypeError as error:
            # Field declared as a class, not an instance. Ignore type checking because
            # we handle unsupported arg types, i.e. this is dead code from
            # the type checker's perspective.
            if isinstance(field_obj, type) and issubclass(field_obj, base.FieldABC):
                msg = (
                    f'Field for "{field_name}" must be declared as a '
                    "Field instance, not a class. "
                    f'Did you mean "fields.{field_obj.__name__}()"?'  # type: ignore[attr-defined]
                )
                raise TypeError(msg) from error
            raise
        self.on_bind_field(field_name, field_obj)

    def _invoke_dump_processors(
        self, tag: str, data, *, many: bool, original_data=None
    ):
        # The pass_many post-dump processors may do things like add an envelope, so
        # invoke those after invoking the non-pass_many processors which will expect
        # to get a list of items.
        data = self._invoke_processors(
            tag, pass_many=False, data=data, many=many, original_data=original_data
        )
        return self._invoke_processors(
            tag, pass_many=True, data=data, many=many, original_data=original_data
        )

    def _invoke_load_processors(
        self,
        tag: str,
        data,
        *,
        many: bool,
        original_data,
        partial: bool | types.StrSequenceOrSet | None,
    ):
        # This has to invert the order of the dump processors, so run the pass_many
        # processors first.
        data = self._invoke_processors(
            tag,
            pass_many=True,
            data=data,
            many=many,
            original_data=original_data,
            partial=partial,
        )
        return self._invoke_processors(
            tag,
            pass_many=False,
            data=data,
            many=many,
            original_data=original_data,
            partial=partial,
        )

    def _invoke_field_validators(self, *, error_store: ErrorStore, data, many: bool):
        for attr_name, _, validator_kwargs in self._hooks[VALIDATES]:
            validator = getattr(self, attr_name)
            field_name = validator_kwargs["field_name"]

            try:
                field_obj = self.fields[field_name]
            except KeyError as error:
                if field_name in self.declared_fields:
                    continue
                raise ValueError(f'"{field_name}" field does not exist.') from error

            data_key = (
                field_obj.data_key if field_obj.data_key is not None else field_name
            )
            if many:
                for idx, item in enumerate(data):
                    try:
                        value = item[field_obj.attribute or field_name]
                    except KeyError:
                        pass
                    else:
                        validated_value = self._call_and_store(
                            getter_func=validator,
                            data=value,
                            field_name=data_key,
                            error_store=error_store,
                            index=(idx if self.opts.index_errors else None),
                        )
                        if validated_value is missing:
                            item.pop(field_name, None)
            else:
                try:
                    value = data[field_obj.attribute or field_name]
                except KeyError:
                    pass
                else:
                    validated_value = self._call_and_store(
                        getter_func=validator,
                        data=value,
                        field_name=data_key,
                        error_store=error_store,
                    )
                    if validated_value is missing:
                        data.pop(field_name, None)

    def _invoke_schema_validators(
        self,
        *,
        error_store: ErrorStore,
        pass_many: bool,
        data,
        original_data,
        many: bool,
        partial: bool | types.StrSequenceOrSet | None,
        field_errors: bool = False,
    ):
        for attr_name, hook_many, validator_kwargs in self._hooks[VALIDATES_SCHEMA]:
            if hook_many != pass_many:
                continue
            validator = getattr(self, attr_name)
            if field_errors and validator_kwargs["skip_on_field_errors"]:
                continue
            pass_original = validator_kwargs.get("pass_original", False)

            if many and not pass_many:
                for idx, (item, orig) in enumerate(zip(data, original_data)):
                    self._run_validator(
                        validator,
                        item,
                        original_data=orig,
                        error_store=error_store,
                        many=many,
                        partial=partial,
                        index=idx,
                        pass_original=pass_original,
                    )
            else:
                self._run_validator(
                    validator,
                    data,
                    original_data=original_data,
                    error_store=error_store,
                    many=many,
                    pass_original=pass_original,
                    partial=partial,
                )

    def _invoke_processors(
        self,
        tag: str,
        *,
        pass_many: bool,
        data,
        many: bool,
        original_data=None,
        **kwargs,
    ):
        for attr_name, hook_many, processor_kwargs in self._hooks[tag]:
            if hook_many != pass_many:
                continue
            # This will be a bound method.
            processor = getattr(self, attr_name)
            pass_original = processor_kwargs.get("pass_original", False)

            if many and not pass_many:
                if pass_original:
                    data = [
                        processor(item, original, many=many, **kwargs)
                        for item, original in zip_longest(data, original_data)
                    ]
                else:
                    data = [processor(item, many=many, **kwargs) for item in data]
            elif pass_original:
                data = processor(data, original_data, many=many, **kwargs)
            else:
                data = processor(data, many=many, **kwargs)
        return data


BaseSchema = Schema  # for backwards compatibility
