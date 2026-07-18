# -*- coding: utf-8 -*-

from __future__ import absolute_import

from .base import Type


class ZippedDocumentBase(Type):
    def match(self, buf):
        # start by checking for ZIP local file header signature
        idx = self.search_signature(buf, 0, 6000)
        if idx != 0:
            return

        return self.match_document(buf)

    def match_document(self, buf):
        raise NotImplementedError

    def compare_bytes(self, buf, subslice, start_offset):
        sl = len(subslice)

        if start_offset + sl > len(buf):
            return False

        return buf[start_offset:start_offset + sl] == subslice

    def search_signature(self, buf, start, rangeNum):
        signature = b"PK\x03\x04"
        length = len(buf)

        end = start + rangeNum
        end = length if end > length else end

        if start >= end:
            return -1

        try:
            return buf.index(signature, start, end)
        except ValueError:
            return -1


class OpenDocument(ZippedDocumentBase):
    def match_document(self, buf):
        # Check if first file in archive is the identifying file
        if not self.compare_bytes(buf, b"mimetype", 0x1E):
            return

        # Check content of mimetype file if it matches current mime
        return self.compare_bytes(buf, bytes(self.mime, "ASCII"), 0x26)


class OfficeOpenXml(ZippedDocumentBase):
    def match_document(self, buf):
        # Check if first file in archive is the identifying file
        ft = self.match_filename(buf, 0x1E)
        if ft:
            return ft

        # Otherwise check that the fist file is one of these
        if (
            not self.compare_bytes(buf, b"[Content_Types].xml", 0x1E)
            and not self.compare_bytes(buf, b"_rels/.rels", 0x1E)
            and not self.compare_bytes(buf, b"docProps", 0x1E)
        ):
            return

        # Loop through next 3 files and check if they match
        # NOTE: OpenOffice/Libreoffice orders ZIP entry differently, so check the 4th file
        # https://github.com/h2non/filetype/blob/d730d98ad5c990883148485b6fd5adbdd378364a/matchers/document.go#L134
        idx = 0
        for i in range(4):
            # Search for next file header
            idx = self.search_signature(buf, idx + 4, 6000)
            if idx == -1:
                return

            # Filename is at file header + 30
            ft = self.match_filename(buf, idx + 30)
            if ft:
                return ft

    def match_filename(self, buf, offset):
        if self.compare_bytes(buf, b"word/", offset):
            return (
                self.mime
                == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        if self.compare_bytes(buf, b"ppt/", offset):
            return (
                self.mime
                == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        if self.compare_bytes(buf, b"xl/", offset):
            return (
                self.mime
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


class Doc(Type):
    """
    Implements the Microsoft Word (Office 97-2003) document type matcher.
    """

    MIME = "application/msword"
    EXTENSION = "doc"

    def __init__(self):
        super(Doc, self).__init__(mime=Doc.MIME, extension=Doc.EXTENSION)

    def match(self, buf):
        if len(buf) > 515 and buf[0:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
            if buf[512:516] == b"\xEC\xA5\xC1\x00":
                return True
            if (
                len(buf) > 2142
                and b"\x00\x0A\x00\x00\x00MSWordDoc\x00\x10\x00\x00\x00Word.Document.8\x00\xF49\xB2q"
                in buf[2075:2142]
            ):
                return True

        return False


class Docx(OfficeOpenXml):
    """
    Implements the Microsoft Word OOXML (Office 2007+) document type matcher.
    """

    MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    EXTENSION = "docx"

    def __init__(self):
        super(Docx, self).__init__(mime=Docx.MIME, extension=Docx.EXTENSION)


class Odt(OpenDocument):
    """
    Implements the OpenDocument Text document type matcher.
    """

    MIME = "application/vnd.oasis.opendocument.text"
    EXTENSION = "odt"

    def __init__(self):
        super(Odt, self).__init__(mime=Odt.MIME, extension=Odt.EXTENSION)


class Xls(Type):
    """
    Implements the Microsoft Excel (Office 97-2003) document type matcher.
    """

    MIME = "application/vnd.ms-excel"
    EXTENSION = "xls"

    def __init__(self):
        super(Xls, self).__init__(mime=Xls.MIME, extension=Xls.EXTENSION)

    def match(self, buf):
        if len(buf) > 520 and buf[0:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
            if buf[512:516] == b"\xFD\xFF\xFF\xFF" and (
                buf[518] == 0x00 or buf[518] == 0x02
            ):
                return True
            if buf[512:520] == b"\x09\x08\x10\x00\x00\x06\x05\x00":
                return True
            if (
                len(buf) > 2095
                and b"\xE2\x00\x00\x00\x5C\x00\x70\x00\x04\x00\x00Calc"
                in buf[1568:2095]
            ):
                return True

        return False


class Xlsx(OfficeOpenXml):
    """
    Implements the Microsoft Excel OOXML (Office 2007+) document type matcher.
    """

    MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    EXTENSION = "xlsx"

    def __init__(self):
        super(Xlsx, self).__init__(mime=Xlsx.MIME, extension=Xlsx.EXTENSION)


class Ods(OpenDocument):
    """
    Implements the OpenDocument Spreadsheet document type matcher.
    """

    MIME = "application/vnd.oasis.opendocument.spreadsheet"
    EXTENSION = "ods"

    def __init__(self):
        super(Ods, self).__init__(mime=Ods.MIME, extension=Ods.EXTENSION)


class Ppt(Type):
    """
    Implements the Microsoft PowerPoint (Office 97-2003) document type matcher.
    """

    MIME = "application/vnd.ms-powerpoint"
    EXTENSION = "ppt"

    def __init__(self):
        super(Ppt, self).__init__(mime=Ppt.MIME, extension=Ppt.EXTENSION)

    def match(self, buf):
        if len(buf) > 524 and buf[0:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1":
            if buf[512:516] == b"\xA0\x46\x1D\xF0":
                return True
            if buf[512:516] == b"\x00\x6E\x1E\xF0":
                return True
            if buf[512:516] == b"\x0F\x00\xE8\x03":
                return True
            if buf[512:516] == b"\xFD\xFF\xFF\xFF" and buf[522:524] == b"\x00\x00":
                return True
            if (
                len(buf) > 2096
                and buf[2072:2096]
                == b"\x00\xB9\x29\xE8\x11\x00\x00\x00MS PowerPoint 97"
            ):
                return True

        return False


class Pptx(OfficeOpenXml):
    """
    Implements the Microsoft PowerPoint OOXML (Office 2007+) document type matcher.
    """

    MIME = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    EXTENSION = "pptx"

    def __init__(self):
        super(Pptx, self).__init__(mime=Pptx.MIME, extension=Pptx.EXTENSION)


class Odp(OpenDocument):
    """
    Implements the OpenDocument Presentation document type matcher.
    """

    MIME = "application/vnd.oasis.opendocument.presentation"
    EXTENSION = "odp"

    def __init__(self):
        super(Odp, self).__init__(mime=Odp.MIME, extension=Odp.EXTENSION)
