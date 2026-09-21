# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .base import Type
from .isobmff import IsoBmff


class Mp4(IsoBmff):
    """
    Implements the MP4 video type matcher.
    """
    MIME = 'video/mp4'
    EXTENSION = 'mp4'

    def __init__(self):
        super(Mp4, self).__init__(
            mime=Mp4.MIME,
            extension=Mp4.EXTENSION
        )

    def match(self, buf):
        if not self._is_isobmff(buf):
            return False

        major_brand, minor_version, compatible_brands = self._get_ftyp(buf)
        for brand in compatible_brands:
            if brand in ['mp41', 'mp42', 'isom']:
                return True
        return major_brand in ['mp41', 'mp42', 'isom']


class M4v(Type):
    """
    Implements the M4V video type matcher.
    """
    MIME = 'video/x-m4v'
    EXTENSION = 'm4v'

    def __init__(self):
        super(M4v, self).__init__(
            mime=M4v.MIME,
            extension=M4v.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 10 and
                buf[0] == 0x0 and buf[1] == 0x0 and
                buf[2] == 0x0 and buf[3] == 0x1C and
                buf[4] == 0x66 and buf[5] == 0x74 and
                buf[6] == 0x79 and buf[7] == 0x70 and
                buf[8] == 0x4D and buf[9] == 0x34 and
                buf[10] == 0x56)


class Mkv(Type):
    """
    Implements the MKV video type matcher.
    """
    MIME = 'video/x-matroska'
    EXTENSION = 'mkv'

    def __init__(self):
        super(Mkv, self).__init__(
            mime=Mkv.MIME,
            extension=Mkv.EXTENSION
        )

    def match(self, buf):
        contains_ebml_element = buf.startswith(b'\x1A\x45\xDF\xA3')
        contains_doctype_element = buf.find(b'\x42\x82\x88matroska') > -1
        return contains_ebml_element and contains_doctype_element


class Webm(Type):
    """
    Implements the WebM video type matcher.
    """
    MIME = 'video/webm'
    EXTENSION = 'webm'

    def __init__(self):
        super(Webm, self).__init__(
            mime=Webm.MIME,
            extension=Webm.EXTENSION
        )

    def match(self, buf):
        contains_ebml_element = buf.startswith(b'\x1A\x45\xDF\xA3')
        contains_doctype_element = buf.find(b'\x42\x82\x84webm') > -1
        return contains_ebml_element and contains_doctype_element


class Mov(IsoBmff):
    """
    Implements the MOV video type matcher.
    """
    MIME = 'video/quicktime'
    EXTENSION = 'mov'

    def __init__(self):
        super(Mov, self).__init__(
            mime=Mov.MIME,
            extension=Mov.EXTENSION
        )

    def match(self, buf):
        if not self._is_isobmff(buf):
            return False

        major_brand, minor_version, compatible_brands = self._get_ftyp(buf)
        return major_brand == 'qt  '


class Avi(Type):
    """
    Implements the AVI video type matcher.
    """
    MIME = 'video/x-msvideo'
    EXTENSION = 'avi'

    def __init__(self):
        super(Avi, self).__init__(
            mime=Avi.MIME,
            extension=Avi.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 11 and
                buf[0] == 0x52 and
                buf[1] == 0x49 and
                buf[2] == 0x46 and
                buf[3] == 0x46 and
                buf[8] == 0x41 and
                buf[9] == 0x56 and
                buf[10] == 0x49 and
                buf[11] == 0x20)


class Wmv(Type):
    """
    Implements the WMV video type matcher.
    """
    MIME = 'video/x-ms-wmv'
    EXTENSION = 'wmv'

    def __init__(self):
        super(Wmv, self).__init__(
            mime=Wmv.MIME,
            extension=Wmv.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 9 and
                buf[0] == 0x30 and
                buf[1] == 0x26 and
                buf[2] == 0xB2 and
                buf[3] == 0x75 and
                buf[4] == 0x8E and
                buf[5] == 0x66 and
                buf[6] == 0xCF and
                buf[7] == 0x11 and
                buf[8] == 0xA6 and
                buf[9] == 0xD9)


class Flv(Type):
    """
    Implements the FLV video type matcher.
    """
    MIME = 'video/x-flv'
    EXTENSION = 'flv'

    def __init__(self):
        super(Flv, self).__init__(
            mime=Flv.MIME,
            extension=Flv.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x46 and
                buf[1] == 0x4C and
                buf[2] == 0x56 and
                buf[3] == 0x01)


class Mpeg(Type):
    """
    Implements the MPEG video type matcher.
    """
    MIME = 'video/mpeg'
    EXTENSION = 'mpg'

    def __init__(self):
        super(Mpeg, self).__init__(
            mime=Mpeg.MIME,
            extension=Mpeg.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x0 and
                buf[1] == 0x0 and
                buf[2] == 0x1 and
                buf[3] >= 0xb0 and
                buf[3] <= 0xbf)


class M3gp(Type):
    """Implements the 3gp image type matcher."""

    MIME = 'video/3gpp'
    EXTENSION = '3gp'

    def __init__(self):
        super(M3gp, self).__init__(
            mime=M3gp.MIME,
            extension=M3gp.EXTENSION
        )

    def match(self, buf):
        return buf[:7] == bytearray([0x66, 0x74, 0x79, 0x70, 0x33, 0x67, 0x70])
