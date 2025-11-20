# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .match import match
from .types import TYPES, Type

# Expose supported matchers types
types = TYPES


def guess(obj):
    """
    Infers the type of the given input.

    Function is overloaded to accept multiple types in input
    and peform the needed type inference based on it.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched type instance. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    return match(obj) if obj else None


def guess_mime(obj):
    """
    Infers the file type of the given input
    and returns its MIME type.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched MIME type as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.mime if kind else kind


def guess_extension(obj):
    """
    Infers the file type of the given input
    and returns its RFC file extension.

    Args:
        obj: path to file, bytes or bytearray.

    Returns:
        The matched file extension as string. Otherwise None.

    Raises:
        TypeError: if obj is not a supported type.
    """
    kind = guess(obj)
    return kind.extension if kind else kind


def get_type(mime=None, ext=None):
    """
    Returns the file type instance searching by
    MIME type or file extension.

    Args:
        ext: file extension string. E.g: jpg, png, mp4, mp3
        mime: MIME string. E.g: image/jpeg, video/mpeg

    Returns:
        The matched file type instance. Otherwise None.
    """
    for kind in types:
        if kind.extension == ext or kind.mime == mime:
            return kind
    return None


def add_type(instance):
    """
    Adds a new type matcher instance to the supported types.

    Args:
        instance: Type inherited instance.

    Returns:
        None
    """
    if not isinstance(instance, Type):
        raise TypeError('instance must inherit from filetype.types.Type')

    types.insert(0, instance)
