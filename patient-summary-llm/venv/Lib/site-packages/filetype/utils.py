# -*- coding: utf-8 -*-

# Python 2.7 workaround
try:
    import pathlib
except ImportError:
    pass


_NUM_SIGNATURE_BYTES = 8192


def get_signature_bytes(path):
    """
    Reads file from disk and returns the first 8192 bytes
    of data representing the magic number header signature.

    Args:
        path: path string to file.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    with open(path, 'rb') as fp:
        return bytearray(fp.read(_NUM_SIGNATURE_BYTES))


def signature(array):
    """
    Returns the first 8192 bytes of the given bytearray
    as part of the file header signature.

    Args:
        array: bytearray to extract the header signature.

    Returns:
        First 8192 bytes of the file content as bytearray type.
    """
    length = len(array)
    index = _NUM_SIGNATURE_BYTES if length > _NUM_SIGNATURE_BYTES else length

    return array[:index]


def get_bytes(obj):
    """
    Infers the input type and reads the first 8192 bytes,
    returning a sliced bytearray.

    Args:
        obj: path to readable, file-like object(with read() method), bytes,
        bytearray or memoryview

    Returns:
        First 8192 bytes of the file content as bytearray type.

    Raises:
        TypeError: if obj is not a supported type.
    """
    if isinstance(obj, bytearray):
        return signature(obj)

    if isinstance(obj, str):
        return get_signature_bytes(obj)

    if isinstance(obj, bytes):
        return signature(obj)

    if isinstance(obj, memoryview):
        return bytearray(signature(obj).tolist())

    if isinstance(obj, pathlib.PurePath):
        return get_signature_bytes(obj)

    if hasattr(obj, 'read'):
        if hasattr(obj, 'tell') and hasattr(obj, 'seek'):
            start_pos = obj.tell()
            obj.seek(0)
            magic_bytes = obj.read(_NUM_SIGNATURE_BYTES)
            obj.seek(start_pos)
            return get_bytes(magic_bytes)
        return get_bytes(obj.read(_NUM_SIGNATURE_BYTES))

    raise TypeError('Unsupported type as file input: %s' % type(obj))
