# -*- coding: utf-8 -*-

from __future__ import absolute_import

import struct

from .base import Type


class Epub(Type):
    """
    Implements the EPUB archive type matcher.
    """
    MIME = 'application/epub+zip'
    EXTENSION = 'epub'

    def __init__(self):
        super(Epub, self).__init__(
            mime=Epub.MIME,
            extension=Epub.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 57 and
                buf[0] == 0x50 and buf[1] == 0x4B and
                buf[2] == 0x3 and buf[3] == 0x4 and
                buf[30] == 0x6D and buf[31] == 0x69 and
                buf[32] == 0x6D and buf[33] == 0x65 and
                buf[34] == 0x74 and buf[35] == 0x79 and
                buf[36] == 0x70 and buf[37] == 0x65 and
                buf[38] == 0x61 and buf[39] == 0x70 and
                buf[40] == 0x70 and buf[41] == 0x6C and
                buf[42] == 0x69 and buf[43] == 0x63 and
                buf[44] == 0x61 and buf[45] == 0x74 and
                buf[46] == 0x69 and buf[47] == 0x6F and
                buf[48] == 0x6E and buf[49] == 0x2F and
                buf[50] == 0x65 and buf[51] == 0x70 and
                buf[52] == 0x75 and buf[53] == 0x62 and
                buf[54] == 0x2B and buf[55] == 0x7A and
                buf[56] == 0x69 and buf[57] == 0x70)


class Zip(Type):
    """
    Implements the Zip archive type matcher.
    """
    MIME = 'application/zip'
    EXTENSION = 'zip'

    def __init__(self):
        super(Zip, self).__init__(
            mime=Zip.MIME,
            extension=Zip.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x50 and buf[1] == 0x4B and
                (buf[2] == 0x3 or buf[2] == 0x5 or
                    buf[2] == 0x7) and
                (buf[3] == 0x4 or buf[3] == 0x6 or
                    buf[3] == 0x8))


class Tar(Type):
    """
    Implements the Tar archive type matcher.
    """
    MIME = 'application/x-tar'
    EXTENSION = 'tar'

    def __init__(self):
        super(Tar, self).__init__(
            mime=Tar.MIME,
            extension=Tar.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 261 and
                buf[257] == 0x75 and
                buf[258] == 0x73 and
                buf[259] == 0x74 and
                buf[260] == 0x61 and
                buf[261] == 0x72)


class Rar(Type):
    """
    Implements the RAR archive type matcher.
    """
    MIME = 'application/x-rar-compressed'
    EXTENSION = 'rar'

    def __init__(self):
        super(Rar, self).__init__(
            mime=Rar.MIME,
            extension=Rar.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 6 and
                buf[0] == 0x52 and
                buf[1] == 0x61 and
                buf[2] == 0x72 and
                buf[3] == 0x21 and
                buf[4] == 0x1A and
                buf[5] == 0x7 and
                (buf[6] == 0x0 or
                    buf[6] == 0x1))


class Gz(Type):
    """
    Implements the GZ archive type matcher.
    """
    MIME = 'application/gzip'
    EXTENSION = 'gz'

    def __init__(self):
        super(Gz, self).__init__(
            mime=Gz.MIME,
            extension=Gz.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 2 and
                buf[0] == 0x1F and
                buf[1] == 0x8B and
                buf[2] == 0x8)


class Bz2(Type):
    """
    Implements the BZ2 archive type matcher.
    """
    MIME = 'application/x-bzip2'
    EXTENSION = 'bz2'

    def __init__(self):
        super(Bz2, self).__init__(
            mime=Bz2.MIME,
            extension=Bz2.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 2 and
                buf[0] == 0x42 and
                buf[1] == 0x5A and
                buf[2] == 0x68)


class SevenZ(Type):
    """
    Implements the SevenZ (7z) archive type matcher.
    """
    MIME = 'application/x-7z-compressed'
    EXTENSION = '7z'

    def __init__(self):
        super(SevenZ, self).__init__(
            mime=SevenZ.MIME,
            extension=SevenZ.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 5 and
                buf[0] == 0x37 and
                buf[1] == 0x7A and
                buf[2] == 0xBC and
                buf[3] == 0xAF and
                buf[4] == 0x27 and
                buf[5] == 0x1C)


class Pdf(Type):
    """
    Implements the PDF archive type matcher.
    """
    MIME = 'application/pdf'
    EXTENSION = 'pdf'

    def __init__(self):
        super(Pdf, self).__init__(
            mime=Pdf.MIME,
            extension=Pdf.EXTENSION
        )

    def match(self, buf):
        # Detect BOM and skip first 3 bytes
        if (len(buf) > 3 and
            buf[0] == 0xEF and
            buf[1] == 0xBB and
            buf[2] == 0xBF):  # noqa E129
            buf = buf[3:]

        return (len(buf) > 3 and
                buf[0] == 0x25 and
                buf[1] == 0x50 and
                buf[2] == 0x44 and
                buf[3] == 0x46)


class Exe(Type):
    """
    Implements the EXE archive type matcher.
    """
    MIME = 'application/x-msdownload'
    EXTENSION = 'exe'

    def __init__(self):
        super(Exe, self).__init__(
            mime=Exe.MIME,
            extension=Exe.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 1 and
                buf[0] == 0x4D and
                buf[1] == 0x5A)


class Swf(Type):
    """
    Implements the SWF archive type matcher.
    """
    MIME = 'application/x-shockwave-flash'
    EXTENSION = 'swf'

    def __init__(self):
        super(Swf, self).__init__(
            mime=Swf.MIME,
            extension=Swf.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 2 and
                (buf[0] == 0x43 or
                    buf[0] == 0x46) and
                buf[1] == 0x57 and
                buf[2] == 0x53)


class Rtf(Type):
    """
    Implements the RTF archive type matcher.
    """
    MIME = 'application/rtf'
    EXTENSION = 'rtf'

    def __init__(self):
        super(Rtf, self).__init__(
            mime=Rtf.MIME,
            extension=Rtf.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 4 and
                buf[0] == 0x7B and
                buf[1] == 0x5C and
                buf[2] == 0x72 and
                buf[3] == 0x74 and
                buf[4] == 0x66)


class Nes(Type):
    """
    Implements the NES archive type matcher.
    """
    MIME = 'application/x-nintendo-nes-rom'
    EXTENSION = 'nes'

    def __init__(self):
        super(Nes, self).__init__(
            mime=Nes.MIME,
            extension=Nes.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x4E and
                buf[1] == 0x45 and
                buf[2] == 0x53 and
                buf[3] == 0x1A)


class Crx(Type):
    """
    Implements the CRX archive type matcher.
    """
    MIME = 'application/x-google-chrome-extension'
    EXTENSION = 'crx'

    def __init__(self):
        super(Crx, self).__init__(
            mime=Crx.MIME,
            extension=Crx.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x43 and
                buf[1] == 0x72 and
                buf[2] == 0x32 and
                buf[3] == 0x34)


class Cab(Type):
    """
    Implements the CAB archive type matcher.
    """
    MIME = 'application/vnd.ms-cab-compressed'
    EXTENSION = 'cab'

    def __init__(self):
        super(Cab, self).__init__(
            mime=Cab.MIME,
            extension=Cab.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                ((buf[0] == 0x4D and
                    buf[1] == 0x53 and
                    buf[2] == 0x43 and
                    buf[3] == 0x46) or
                    (buf[0] == 0x49 and
                        buf[1] == 0x53 and
                        buf[2] == 0x63 and
                        buf[3] == 0x28)))


class Eot(Type):
    """
    Implements the EOT archive type matcher.
    """
    MIME = 'application/octet-stream'
    EXTENSION = 'eot'

    def __init__(self):
        super(Eot, self).__init__(
            mime=Eot.MIME,
            extension=Eot.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 35 and
                buf[34] == 0x4C and
                buf[35] == 0x50 and
                ((buf[8] == 0x02 and
                    buf[9] == 0x00 and
                    buf[10] == 0x01) or
                (buf[8] == 0x01 and
                    buf[9] == 0x00 and
                    buf[10] == 0x00) or
                    (buf[8] == 0x02 and
                        buf[9] == 0x00 and
                        buf[10] == 0x02)))


class Ps(Type):
    """
    Implements the PS archive type matcher.
    """
    MIME = 'application/postscript'
    EXTENSION = 'ps'

    def __init__(self):
        super(Ps, self).__init__(
            mime=Ps.MIME,
            extension=Ps.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 1 and
                buf[0] == 0x25 and
                buf[1] == 0x21)


class Xz(Type):
    """
    Implements the XS archive type matcher.
    """
    MIME = 'application/x-xz'
    EXTENSION = 'xz'

    def __init__(self):
        super(Xz, self).__init__(
            mime=Xz.MIME,
            extension=Xz.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 5 and
                buf[0] == 0xFD and
                buf[1] == 0x37 and
                buf[2] == 0x7A and
                buf[3] == 0x58 and
                buf[4] == 0x5A and
                buf[5] == 0x00)


class Sqlite(Type):
    """
    Implements the Sqlite DB archive type matcher.
    """
    MIME = 'application/x-sqlite3'
    EXTENSION = 'sqlite'

    def __init__(self):
        super(Sqlite, self).__init__(
            mime=Sqlite.MIME,
            extension=Sqlite.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x53 and
                buf[1] == 0x51 and
                buf[2] == 0x4C and
                buf[3] == 0x69)


class Deb(Type):
    """
    Implements the DEB archive type matcher.
    """
    MIME = 'application/x-deb'
    EXTENSION = 'deb'

    def __init__(self):
        super(Deb, self).__init__(
            mime=Deb.MIME,
            extension=Deb.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 20 and
                buf[0] == 0x21 and
                buf[1] == 0x3C and
                buf[2] == 0x61 and
                buf[3] == 0x72 and
                buf[4] == 0x63 and
                buf[5] == 0x68 and
                buf[6] == 0x3E and
                buf[7] == 0x0A and
                buf[8] == 0x64 and
                buf[9] == 0x65 and
                buf[10] == 0x62 and
                buf[11] == 0x69 and
                buf[12] == 0x61 and
                buf[13] == 0x6E and
                buf[14] == 0x2D and
                buf[15] == 0x62 and
                buf[16] == 0x69 and
                buf[17] == 0x6E and
                buf[18] == 0x61 and
                buf[19] == 0x72 and
                buf[20] == 0x79)


class Ar(Type):
    """
    Implements the AR archive type matcher.
    """
    MIME = 'application/x-unix-archive'
    EXTENSION = 'ar'

    def __init__(self):
        super(Ar, self).__init__(
            mime=Ar.MIME,
            extension=Ar.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 6 and
                buf[0] == 0x21 and
                buf[1] == 0x3C and
                buf[2] == 0x61 and
                buf[3] == 0x72 and
                buf[4] == 0x63 and
                buf[5] == 0x68 and
                buf[6] == 0x3E)


class Z(Type):
    """
    Implements the Z archive type matcher.
    """
    MIME = 'application/x-compress'
    EXTENSION = 'Z'

    def __init__(self):
        super(Z, self).__init__(
            mime=Z.MIME,
            extension=Z.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 1 and
                ((buf[0] == 0x1F and
                    buf[1] == 0xA0) or
                (buf[0] == 0x1F and
                    buf[1] == 0x9D)))


class Lzop(Type):
    """
    Implements the Lzop archive type matcher.
    """
    MIME = 'application/x-lzop'
    EXTENSION = 'lzo'

    def __init__(self):
        super(Lzop, self).__init__(
            mime=Lzop.MIME,
            extension=Lzop.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 7 and
                buf[0] == 0x89 and
                buf[1] == 0x4C and
                buf[2] == 0x5A and
                buf[3] == 0x4F and
                buf[4] == 0x00 and
                buf[5] == 0x0D and
                buf[6] == 0x0A and
                buf[7] == 0x1A)


class Lz(Type):
    """
    Implements the Lz archive type matcher.
    """
    MIME = 'application/x-lzip'
    EXTENSION = 'lz'

    def __init__(self):
        super(Lz, self).__init__(
            mime=Lz.MIME,
            extension=Lz.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x4C and
                buf[1] == 0x5A and
                buf[2] == 0x49 and
                buf[3] == 0x50)


class Elf(Type):
    """
    Implements the Elf archive type matcher
    """
    MIME = 'application/x-executable'
    EXTENSION = 'elf'

    def __init__(self):
        super(Elf, self).__init__(
            mime=Elf.MIME,
            extension=Elf.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 52 and
                buf[0] == 0x7F and
                buf[1] == 0x45 and
                buf[2] == 0x4C and
                buf[3] == 0x46)


class Lz4(Type):
    """
    Implements the Lz4 archive type matcher.
    """
    MIME = 'application/x-lz4'
    EXTENSION = 'lz4'

    def __init__(self):
        super(Lz4, self).__init__(
            mime=Lz4.MIME,
            extension=Lz4.EXTENSION
        )

    def match(self, buf):
        return (len(buf) > 3 and
                buf[0] == 0x04 and
                buf[1] == 0x22 and
                buf[2] == 0x4D and
                buf[3] == 0x18)


class Br(Type):
    """Implements the Br image type matcher."""

    MIME = 'application/x-brotli'
    EXTENSION = 'br'

    def __init__(self):
        super(Br, self).__init__(
            mime=Br.MIME,
            extension=Br.EXTENSION
        )

    def match(self, buf):
        return buf[:4] == bytearray([0xce, 0xb2, 0xcf, 0x81])


class Dcm(Type):
    """Implements the Dcm image type matcher."""

    MIME = 'application/dicom'
    EXTENSION = 'dcm'

    def __init__(self):
        super(Dcm, self).__init__(
            mime=Dcm.MIME,
            extension=Dcm.EXTENSION
        )

    def match(self, buf):
        return buf[128:131] == bytearray([0x44, 0x49, 0x43, 0x4d])


class Rpm(Type):
    """Implements the Rpm image type matcher."""

    MIME = 'application/x-rpm'
    EXTENSION = 'rpm'

    def __init__(self):
        super(Rpm, self).__init__(
            mime=Rpm.MIME,
            extension=Rpm.EXTENSION
        )

    def match(self, buf):
        return buf[:4] == bytearray([0xed, 0xab, 0xee, 0xdb])


class Zstd(Type):
    """
    Implements the Zstd archive type matcher.
    https://github.com/facebook/zstd/blob/dev/doc/zstd_compression_format.md
    """
    MIME = 'application/zstd'
    EXTENSION = 'zst'
    MAGIC_SKIPPABLE_START = 0x184D2A50
    MAGIC_SKIPPABLE_MASK = 0xFFFFFFF0

    def __init__(self):
        super(Zstd, self).__init__(
            mime=Zstd.MIME,
            extension=Zstd.EXTENSION
        )

    @staticmethod
    def _to_little_endian_int(buf):
        # return int.from_bytes(buf, byteorder='little')
        return struct.unpack('<L', buf)[0]

    def match(self, buf):
        # Zstandard compressed data is made of one or more frames.
        # There are two frame formats defined by Zstandard:
        # Zstandard frames and Skippable frames.
        # See more details from
        # https://tools.ietf.org/id/draft-kucherawy-dispatch-zstd-00.html#rfc.section.2
        is_zstd = (
            len(buf) > 3 and
            buf[0] in (0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28) and
            buf[1] == 0xb5 and
            buf[2] == 0x2f and
            buf[3] == 0xfd)
        if is_zstd:
            return True
        # skippable frames
        if len(buf) < 8:
            return False
        magic = self._to_little_endian_int(buf[:4]) & Zstd.MAGIC_SKIPPABLE_MASK
        if magic == Zstd.MAGIC_SKIPPABLE_START:
            user_data_len = self._to_little_endian_int(buf[4:8])
            if len(buf) < 8 + user_data_len:
                return False
            next_frame = buf[8 + user_data_len:]
            return self.match(next_frame)
        return False
