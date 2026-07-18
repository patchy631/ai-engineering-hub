"""Abstract base classes.

These are necessary to avoid circular imports between schema.py and fields.py.

.. warning::

    This module is deprecated. Users should not import from this module.
    Use `marshmallow.fields.Field` and `marshmallow.schema.Schema` as base classes instead.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class FieldABC(ABC):
    """Abstract base class from which all Field classes inherit."""

    @abstractmethod
    def serialize(self, attr, obj, accessor=None):
        pass

    @abstractmethod
    def deserialize(self, value):
        pass

    @abstractmethod
    def _serialize(self, value, attr, obj, **kwargs):
        pass

    @abstractmethod
    def _deserialize(self, value, attr, data, **kwargs):
        pass


class SchemaABC(ABC):
    """Abstract base class from which all Schemas inherit."""

    @abstractmethod
    def dump(self, obj, *, many: bool | None = None):
        pass

    @abstractmethod
    def dumps(self, obj, *, many: bool | None = None):
        pass

    @abstractmethod
    def load(self, data, *, many: bool | None = None, partial=None, unknown=None):
        pass

    @abstractmethod
    def loads(
        self,
        json_data,
        *,
        many: bool | None = None,
        partial=None,
        unknown=None,
        **kwargs,
    ):
        pass
