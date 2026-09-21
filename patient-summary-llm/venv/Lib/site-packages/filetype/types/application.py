# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .base import Type


class Wasm(Type):
    """Implements the Wasm image type matcher."""

    MIME = 'application/wasm'
    EXTENSION = 'wasm'

    def __init__(self):
        super(Wasm, self).__init__(
            mime=Wasm.MIME,
            extension=Wasm.EXTENSION
        )

    def match(self, buf):
        return buf[:8] == bytearray([0x00, 0x61, 0x73, 0x6d,
                                     0x01, 0x00, 0x00, 0x00])
