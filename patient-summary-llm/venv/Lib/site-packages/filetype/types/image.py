# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .base import Type
from .isobmff import IsoBmff


class Jpeg(Type):
    """
    Implements the JPEG image type matcher.
    """
    MIME = 'image/jpeg'
    EXTENSION = 'jpg'

    def __init__(self):
        super(Jpeg, self).__init__(
            mime=Jpeg.MIME,
            extension=Jpeg.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 2 and
                buf[0] == 0xFF and
                buf[1] == 0xD8 and
                buf[2] == 0xFF)


class Jpx(Type):
    """
    Implements the JPEG2000 image type matcher.
    """

    MIME = "image/jpx"
    EXTENSION = "jpx"

    def __init__(self):
        super(Jpx, self).__init__(mime=Jpx.MIME, extension=Jpx.EXTENSION)

    def match(self, buf):
        return (
            len(buf) > 50
            and buf[0] == 0x00
            and buf[1] == 0x00
            and buf[2] == 0x00
            and buf[3] == 0x0C
            and buf[16:24] == b"ftypjp2 "
        )


class Apng(Type):
    """
    Implements the APNG image type matcher.
    """
    MIME = 'image/apng'
    EXTENSION = 'apng'

    def __init__(self):
        super(Apng, self).__init__(
            mime=Apng.MIME,
            extension=Apng.EXTENSION
        )

    def match(self, buf):
        if (len(buf) > 8 and
           buf[:8] == bytearray([0x89, 0x50, 0x4e, 0x47,
                                 0x0d, 0x0a, 0x1a, 0x0a])):
            # cursor in buf, skip already readed 8 bytes
            i = 8
            while len(buf) > i:
                data_length = int.from_bytes(buf[i:i+4], byteorder="big")
                i += 4

                chunk_type = buf[i:i+4].decode("ascii", errors='ignore')
                i += 4

                # acTL chunk in APNG should appears first than IDAT
                # IEND is end of PNG
                if (chunk_type == "IDAT" or chunk_type == "IEND"):
                    return False
                elif (chunk_type == "acTL"):
                    return True

                # move to the next chunk by skipping data and crc (4 bytes)
                i += data_length + 4

        return False


class Png(Type):
    """
    Implements the PNG image type matcher.
    """
    MIME = 'image/png'
    EXTENSION = 'png'

    def __init__(self):
        super(Png, self).__init__(
            mime=Png.MIME,
            extension=Png.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x89 and
                buf[1] == 0x50 and
                buf[2] == 0x4E and
                buf[3] == 0x47)


class Gif(Type):
    """
    Implements the GIF image type matcher.
    """
    MIME = 'image/gif'
    EXTENSION = 'gif'

    def __init__(self):
        super(Gif, self).__init__(
            mime=Gif.MIME,
            extension=Gif.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 2 and
                buf[0] == 0x47 and
                buf[1] == 0x49 and
                buf[2] == 0x46)


class Webp(Type):
    """
    Implements the WEBP image type matcher.
    """
    MIME = 'image/webp'
    EXTENSION = 'webp'

    def __init__(self):
        super(Webp, self).__init__(
            mime=Webp.MIME,
            extension=Webp.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 13 and
                buf[0] == 0x52 and
                buf[1] == 0x49 and
                buf[2] == 0x46 and
                buf[3] == 0x46 and
                buf[8] == 0x57 and
                buf[9] == 0x45 and
                buf[10] == 0x42 and
                buf[11] == 0x50 and
                buf[12] == 0x56 and
                buf[13] == 0x50)


class Cr2(Type):
    """
    Implements the CR2 image type matcher.
    """
    MIME = 'image/x-canon-cr2'
    EXTENSION = 'cr2'

    def __init__(self):
        super(Cr2, self).__init__(
            mime=Cr2.MIME,
            extension=Cr2.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 9 and
                ((buf[0] == 0x49 and buf[1] == 0x49 and
                    buf[2] == 0x2A and buf[3] == 0x0) or
                (buf[0] == 0x4D and buf[1] == 0x4D and
                    buf[2] == 0x0 and buf[3] == 0x2A)) and
                buf[8] == 0x43 and buf[9] == 0x52)


class Tiff(Type):
    """
    Implements the TIFF image type matcher.
    """
    MIME = 'image/tiff'
    EXTENSION = 'tif'

    def __init__(self):
        super(Tiff, self).__init__(
            mime=Tiff.MIME,
            extension=Tiff.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 9 and
                ((buf[0] == 0x49 and buf[1] == 0x49 and
                    buf[2] == 0x2A and buf[3] == 0x0) or
                (buf[0] == 0x4D and buf[1] == 0x4D and
                    buf[2] == 0x0 and buf[3] == 0x2A))
                and not (buf[8] == 0x43 and buf[9] == 0x52))


class Bmp(Type):
    """
    Implements the BMP image type matcher.
    """
    MIME = 'image/bmp'
    EXTENSION = 'bmp'

    def __init__(self):
        super(Bmp, self).__init__(
            mime=Bmp.MIME,
            extension=Bmp.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 1 and
                buf[0] == 0x42 and
                buf[1] == 0x4D)


class Jxr(Type):
    """
    Implements the JXR image type matcher.
    """
    MIME = 'image/vnd.ms-photo'
    EXTENSION = 'jxr'

    def __init__(self):
        super(Jxr, self).__init__(
            mime=Jxr.MIME,
            extension=Jxr.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 2 and
                buf[0] == 0x49 and
                buf[1] == 0x49 and
                buf[2] == 0xBC)


class Psd(Type):
    """
    Implements the PSD image type matcher.
    """
    MIME = 'image/vnd.adobe.photoshop'
    EXTENSION = 'psd'

    def __init__(self):
        super(Psd, self).__init__(
            mime=Psd.MIME,
            extension=Psd.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x38 and
                buf[1] == 0x42 and
                buf[2] == 0x50 and
                buf[3] == 0x53)


class Ico(Type):
    """
    Implements the ICO image type matcher.
    """
    MIME = 'image/x-icon'
    EXTENSION = 'ico'

    def __init__(self):
        super(Ico, self).__init__(
            mime=Ico.MIME,
            extension=Ico.EXTENSION,
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x00 and
                buf[1] == 0x00 and
                buf[2] == 0x01 and
                buf[3] == 0x00)


class Heic(IsoBmff):
    """
    Implements the HEIC image type matcher.
    """
    MIME = 'image/heic'
    EXTENSION = 'heic'

    def __init__(self):
        super(Heic, self).__init__(
            mime=Heic.MIME,
            extension=Heic.EXTENSION
        )

    def match(self, buf):
        if not self._is_isobmff(buf):
            return False

        major_brand, minor_version, compatible_brands = self._get_ftyp(buf)
        if major_brand == 'heic':
            return True
        if major_brand in ['mif1', 'msf1'] and 'heic' in compatible_brands:
            return True
        return False


class Dcm(Type):

    MIME = 'application/dicom'
    EXTENSION = 'dcm'
    OFFSET = 128

    def __init__(self):
        super(Dcm, self).__init__(
            mime=Dcm.MIME,
            extension=Dcm.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > Dcm.OFFSET + 4 and
                buf[Dcm.OFFSET + 0] == 0x44 and
                buf[Dcm.OFFSET + 1] == 0x49 and
                buf[Dcm.OFFSET + 2] == 0x43 and
                buf[Dcm.OFFSET + 3] == 0x4D)


class Dwg(Type):
    """Implements the Dwg image type matcher."""

    MIME = 'image/vnd.dwg'
    EXTENSION = 'dwg'

    def __init__(self):
        super(Dwg, self).__init__(
            mime=Dwg.MIME,
            extension=Dwg.EXTENSION
        )

    def match(self, buf):
        return buf[:4] == bytearray([0x41, 0x43, 0x31, 0x30])


class Xcf(Type):
    """Implements the Xcf image type matcher."""

    MIME = 'image/x-xcf'
    EXTENSION = 'xcf'

    def __init__(self):
        super(Xcf, self).__init__(
            mime=Xcf.MIME,
            extension=Xcf.EXTENSION
        )

    def match(self, buf):
        return buf[:10] == bytearray([0x67, 0x69, 0x6d, 0x70, 0x20,
                                      0x78, 0x63, 0x66, 0x20, 0x76])


class Avif(IsoBmff):
    """
    Implements the AVIF image type matcher.
    """
    MIME = 'image/avif'
    EXTENSION = 'avif'

    def __init__(self):
        super(Avif, self).__init__(
            mime=Avif.MIME,
            extension=Avif.EXTENSION
        )

    def match(self, buf):
        if not self._is_isobmff(buf):
            return False

        major_brand, minor_version, compatible_brands = self._get_ftyp(buf)
        if major_brand == 'avif':
            return True
        if major_brand in ['mif1', 'msf1'] and 'avif' in compatible_brands:
            return True
        return False
