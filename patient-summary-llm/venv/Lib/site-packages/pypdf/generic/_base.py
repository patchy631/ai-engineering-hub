# Copyright (c) 2006, Mathieu Fenniak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
import binascii
import codecs
import hashlib
import re
import sys
from binascii import unhexlify
from math import log10
from struct import iter_unpack
from typing import Any, Callable, ClassVar, Dict, Optional, Sequence, Union, cast

if sys.version_info[:2] >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard  # PEP 647

from .._codecs import _pdfdoc_encoding_rev
from .._protocols import PdfObjectProtocol, PdfWriterProtocol
from .._utils import (
    StreamType,
    deprecate_no_replacement,
    logger_warning,
    read_non_whitespace,
    read_until_regex,
)
from ..errors import STREAM_TRUNCATED_PREMATURELY, PdfReadError, PdfStreamError

__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"


class PdfObject(PdfObjectProtocol):
    # function for calculating a hash value
    hash_func: Callable[..., "hashlib._Hash"] = hashlib.sha1
    indirect_reference: Optional["IndirectObject"]

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement .hash_bin() so far"
        )

    def hash_value_data(self) -> bytes:
        return f"{self}".encode()

    def hash_value(self) -> bytes:
        return (
            f"{self.__class__.__name__}:"
            f"{self.hash_func(self.hash_value_data()).hexdigest()}"
        ).encode()

    def replicate(
        self,
        pdf_dest: PdfWriterProtocol,
    ) -> "PdfObject":
        """
        Clone object into pdf_dest (PdfWriterProtocol which is an interface for PdfWriter)
        without ensuring links. This is used in clone_document_from_root with incremental = True.

        Args:
          pdf_dest: Target to clone to.

        Returns:
          The cloned PdfObject

        """
        return self.clone(pdf_dest)

    def clone(
        self,
        pdf_dest: PdfWriterProtocol,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "PdfObject":
        """
        Clone object into pdf_dest (PdfWriterProtocol which is an interface for PdfWriter).

        By default, this method will call ``_reference_clone`` (see ``_reference``).


        Args:
          pdf_dest: Target to clone to.
          force_duplicate: By default, if the object has already been cloned and referenced,
            the copy will be returned; when ``True``, a new copy will be created.
            (Default value = ``False``)
          ignore_fields: List/tuple of field names (for dictionaries) that will be ignored
            during cloning (applies to children duplication as well). If fields are to be
            considered for a limited number of levels, you have to add it as integer, for
            example ``[1,"/B","/TOTO"]`` means that ``"/B"`` will be ignored at the first
            level only but ``"/TOTO"`` on all levels.

        Returns:
          The cloned PdfObject

        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement .clone so far"
        )

    def _reference_clone(
        self, clone: Any, pdf_dest: PdfWriterProtocol, force_duplicate: bool = False
    ) -> PdfObjectProtocol:
        """
        Reference the object within the _objects of pdf_dest only if
        indirect_reference attribute exists (which means the objects was
        already identified in xref/xobjstm) if object has been already
        referenced do nothing.

        Args:
          clone:
          pdf_dest:

        Returns:
          The clone

        """
        try:
            if not force_duplicate and clone.indirect_reference.pdf == pdf_dest:
                return clone
        except Exception:
            pass
        # if hasattr(clone, "indirect_reference"):
        try:
            ind = self.indirect_reference
        except AttributeError:
            return clone
        if (
            pdf_dest.incremental
            and ind is not None
            and ind.pdf == pdf_dest._reader
            and ind.idnum <= len(pdf_dest._objects)
        ):
            i = ind.idnum
        else:
            i = len(pdf_dest._objects) + 1
        if ind is not None:
            if id(ind.pdf) not in pdf_dest._id_translated:
                pdf_dest._id_translated[id(ind.pdf)] = {}
                pdf_dest._id_translated[id(ind.pdf)]["PreventGC"] = ind.pdf  # type: ignore
            if (
                not force_duplicate
                and ind.idnum in pdf_dest._id_translated[id(ind.pdf)]
            ):
                obj = pdf_dest.get_object(
                    pdf_dest._id_translated[id(ind.pdf)][ind.idnum]
                )
                assert obj is not None
                return obj
            pdf_dest._id_translated[id(ind.pdf)][ind.idnum] = i
        try:
            pdf_dest._objects[i - 1] = clone
        except IndexError:
            pdf_dest._objects.append(clone)
            i = len(pdf_dest._objects)
        clone.indirect_reference = IndirectObject(i, 0, pdf_dest)
        return clone

    def get_object(self) -> Optional["PdfObject"]:
        """Resolve indirect references."""
        return self

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        raise NotImplementedError


class NullObject(PdfObject):
    def clone(
        self,
        pdf_dest: PdfWriterProtocol,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "NullObject":
        """Clone object into pdf_dest."""
        return cast(
            "NullObject", self._reference_clone(NullObject(), pdf_dest, force_duplicate)
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__,))

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(b"null")

    @staticmethod
    def read_from_stream(stream: StreamType) -> "NullObject":
        nulltxt = stream.read(4)
        if nulltxt != b"null":
            raise PdfReadError("Could not read Null object")
        return NullObject()

    def __repr__(self) -> str:
        return "NullObject"


class BooleanObject(PdfObject):
    def __init__(self, value: Any) -> None:
        self.value = value

    def clone(
        self,
        pdf_dest: PdfWriterProtocol,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "BooleanObject":
        """Clone object into pdf_dest."""
        return cast(
            "BooleanObject",
            self._reference_clone(BooleanObject(self.value), pdf_dest, force_duplicate),
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self.value))

    def __eq__(self, o: object, /) -> bool:
        if isinstance(o, BooleanObject):
            return self.value == o.value
        elif isinstance(o, bool):
            return self.value == o
        else:
            return False

    def __repr__(self) -> str:
        return "True" if self.value else "False"

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        if self.value:
            stream.write(b"true")
        else:
            stream.write(b"false")

    @staticmethod
    def read_from_stream(stream: StreamType) -> "BooleanObject":
        word = stream.read(4)
        if word == b"true":
            return BooleanObject(True)
        elif word == b"fals":
            stream.read(1)
            return BooleanObject(False)
        else:
            raise PdfReadError("Could not read Boolean object")


class IndirectObject(PdfObject):
    def __init__(self, idnum: int, generation: int, pdf: Any) -> None:  # PdfReader
        self.idnum = idnum
        self.generation = generation
        self.pdf = pdf

    def __hash__(self) -> int:
        return hash((self.idnum, self.generation, id(self.pdf)))

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self.idnum, self.generation, id(self.pdf)))

    def replicate(
        self,
        pdf_dest: PdfWriterProtocol,
    ) -> "PdfObject":
        return IndirectObject(self.idnum, self.generation, pdf_dest)

    def clone(
        self,
        pdf_dest: PdfWriterProtocol,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "IndirectObject":
        """Clone object into pdf_dest."""
        if self.pdf == pdf_dest and not force_duplicate:
            # Already duplicated and no extra duplication required
            return self
        if id(self.pdf) not in pdf_dest._id_translated:
            pdf_dest._id_translated[id(self.pdf)] = {}

        if self.idnum in pdf_dest._id_translated[id(self.pdf)]:
            dup = pdf_dest.get_object(pdf_dest._id_translated[id(self.pdf)][self.idnum])
            if force_duplicate:
                assert dup is not None
                assert dup.indirect_reference is not None
                idref = dup.indirect_reference
                return IndirectObject(idref.idnum, idref.generation, idref.pdf)
        else:
            obj = self.get_object()
            # case observed : a pointed object can not be found
            if obj is None:
                # this normally
                obj = NullObject()
                assert isinstance(self, (IndirectObject,))
                obj.indirect_reference = self
            dup = pdf_dest._add_object(
                obj.clone(pdf_dest, force_duplicate, ignore_fields)
            )
        # asserts added to prevent errors in mypy
        assert dup is not None
        assert dup.indirect_reference is not None
        return dup.indirect_reference

    @property
    def indirect_reference(self) -> "IndirectObject":  # type: ignore[override]
        return self

    def get_object(self) -> Optional["PdfObject"]:
        return self.pdf.get_object(self)

    def __deepcopy__(self, memo: Any) -> "IndirectObject":
        return IndirectObject(self.idnum, self.generation, self.pdf)

    def _get_object_with_check(self) -> Optional["PdfObject"]:
        o = self.get_object()
        # the check is done here to not slow down get_object()
        if isinstance(o, IndirectObject):
            raise PdfStreamError(
                f"{self.__repr__()} references an IndirectObject {o.__repr__()}"
            )
        return o

    def __getattr__(self, name: str) -> Any:
        # Attribute not found in object: look in pointed object
        try:
            return getattr(self._get_object_with_check(), name)
        except AttributeError:
            raise AttributeError(
                f"No attribute {name} found in IndirectObject or pointed object"
            )

    def __getitem__(self, key: Any) -> Any:
        # items should be extracted from pointed Object
        return self._get_object_with_check()[key]  # type: ignore

    def __float__(self) -> str:
        # in this case we are looking for the pointed data
        return self.get_object().__float__()  # type: ignore

    def __int__(self) -> int:
        # in this case we are looking for the pointed data
        return self.get_object().__int__()  # type: ignore

    def __str__(self) -> str:
        # in this case we are looking for the pointed data
        return self.get_object().__str__()

    def __repr__(self) -> str:
        return f"IndirectObject({self.idnum!r}, {self.generation!r}, {id(self.pdf)})"

    def __eq__(self, other: object) -> bool:
        return (
            other is not None
            and isinstance(other, IndirectObject)
            and self.idnum == other.idnum
            and self.generation == other.generation
            and self.pdf is other.pdf
        )

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(f"{self.idnum} {self.generation} R".encode())

    @staticmethod
    def read_from_stream(stream: StreamType, pdf: Any) -> "IndirectObject":  # PdfReader
        idnum = b""
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                break
            idnum += tok
        generation = b""
        while True:
            tok = stream.read(1)
            if not tok:
                raise PdfStreamError(STREAM_TRUNCATED_PREMATURELY)
            if tok.isspace():
                if not generation:
                    continue
                break
            generation += tok
        r = read_non_whitespace(stream)
        if r != b"R":
            raise PdfReadError(
                f"Error reading indirect object reference at byte {hex(stream.tell())}"
            )
        return IndirectObject(int(idnum), int(generation), pdf)


FLOAT_WRITE_PRECISION = 8  # shall be min 5 digits max, allow user adj


class FloatObject(float, PdfObject):
    def __new__(
        cls, value: Any = "0.0", context: Optional[Any] = None
    ) -> "FloatObject":
        try:
            value = float(value)
            return float.__new__(cls, value)
        except Exception as e:
            # If this isn't a valid decimal (happens in malformed PDFs)
            # fallback to 0
            logger_warning(
                f"{e} : FloatObject ({value}) invalid; use 0.0 instead", __name__
            )
            return float.__new__(cls, 0.0)

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "FloatObject":
        """Clone object into pdf_dest."""
        return cast(
            "FloatObject",
            self._reference_clone(FloatObject(self), pdf_dest, force_duplicate),
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self.as_numeric))

    def myrepr(self) -> str:
        if self == 0:
            return "0.0"
        nb = FLOAT_WRITE_PRECISION - int(log10(abs(self)))
        s = f"{self:.{max(1,nb)}f}".rstrip("0").rstrip(".")
        return s

    def __repr__(self) -> str:
        return self.myrepr()  # repr(float(self))

    def as_numeric(self) -> float:
        return float(self)

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(self.myrepr().encode("utf8"))


class NumberObject(int, PdfObject):
    NumberPattern = re.compile(b"[^+-.0-9]")

    def __new__(cls, value: Any) -> "NumberObject":
        try:
            return int.__new__(cls, int(value))
        except ValueError:
            logger_warning(f"NumberObject({value}) invalid; use 0 instead", __name__)
            return int.__new__(cls, 0)

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "NumberObject":
        """Clone object into pdf_dest."""
        return cast(
            "NumberObject",
            self._reference_clone(NumberObject(self), pdf_dest, force_duplicate),
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self.as_numeric()))

    def as_numeric(self) -> int:
        return int(repr(self).encode("utf8"))

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(repr(self).encode("utf8"))

    @staticmethod
    def read_from_stream(stream: StreamType) -> Union["NumberObject", "FloatObject"]:
        num = read_until_regex(stream, NumberObject.NumberPattern)
        if num.find(b".") != -1:
            return FloatObject(num)
        return NumberObject(num)


class ByteStringObject(bytes, PdfObject):
    """
    Represents a string object where the text encoding could not be determined.

    This occurs quite often, as the PDF spec doesn't provide an alternate way to
    represent strings -- for example, the encryption data stored in files (like
    /O) is clearly not text, but is still stored in a "String" object.
    """

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "ByteStringObject":
        """Clone object into pdf_dest."""
        return cast(
            "ByteStringObject",
            self._reference_clone(
                ByteStringObject(bytes(self)), pdf_dest, force_duplicate
            ),
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, bytes(self)))

    @property
    def original_bytes(self) -> bytes:
        """For compatibility with TextStringObject.original_bytes."""
        return self

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(b"<")
        stream.write(binascii.hexlify(self))
        stream.write(b">")

    def __str__(self) -> str:
        charset_to_try = ["utf-16"] + list(NameObject.CHARSETS)
        for enc in charset_to_try:
            try:
                return self.decode(enc)
            except UnicodeDecodeError:
                pass
        raise PdfReadError("Cannot decode ByteStringObject.")


class TextStringObject(str, PdfObject):  # noqa: SLOT000
    """
    A string object that has been decoded into a real unicode string.

    If read from a PDF document, this string appeared to match the
    PDFDocEncoding, or contained a UTF-16BE BOM mark to cause UTF-16 decoding
    to occur.
    """

    autodetect_pdfdocencoding: bool
    autodetect_utf16: bool
    utf16_bom: bytes
    _original_bytes: Optional[bytes] = None

    def __new__(cls, value: Any) -> "TextStringObject":
        org = None
        if isinstance(value, bytes):
            org = value
            value = value.decode("charmap")
        o = str.__new__(cls, value)
        o._original_bytes = org
        o.autodetect_utf16 = False
        o.autodetect_pdfdocencoding = False
        o.utf16_bom = b""
        if o.startswith(("\xfe\xff", "\xff\xfe")):
            assert org is not None  # for mypy
            try:
                o = str.__new__(cls, org.decode("utf-16"))
            except UnicodeDecodeError as exc:
                logger_warning(
                    f"{exc!s}\ninitial string:{exc.object!r}",
                    __name__,
                )
                o = str.__new__(cls, exc.object[: exc.start].decode("utf-16"))
            o._original_bytes = org
            o.autodetect_utf16 = True
            o.utf16_bom = org[:2]
        else:
            try:
                encode_pdfdocencoding(o)
                o.autodetect_pdfdocencoding = True
            except UnicodeEncodeError:
                o.autodetect_utf16 = True
                o.utf16_bom = codecs.BOM_UTF16_BE
        return o

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "TextStringObject":
        """Clone object into pdf_dest."""
        obj = TextStringObject(self)
        obj._original_bytes = self._original_bytes
        obj.autodetect_pdfdocencoding = self.autodetect_pdfdocencoding
        obj.autodetect_utf16 = self.autodetect_utf16
        obj.utf16_bom = self.utf16_bom
        return cast(
            "TextStringObject", self._reference_clone(obj, pdf_dest, force_duplicate)
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self.original_bytes))

    @property
    def original_bytes(self) -> bytes:
        """
        It is occasionally possible that a text string object gets created where
        a byte string object was expected due to the autodetection mechanism --
        if that occurs, this "original_bytes" property can be used to
        back-calculate what the original encoded bytes were.
        """
        if self._original_bytes is not None:
            return self._original_bytes
        else:
            return self.get_original_bytes()

    def get_original_bytes(self) -> bytes:
        # We're a text string object, but the library is trying to get our raw
        # bytes. This can happen if we auto-detected this string as text, but
        # we were wrong. It's pretty common. Return the original bytes that
        # would have been used to create this object, based upon the autodetect
        # method.
        if self.autodetect_utf16:
            if self.utf16_bom == codecs.BOM_UTF16_LE:
                return codecs.BOM_UTF16_LE + self.encode("utf-16le")
            elif self.utf16_bom == codecs.BOM_UTF16_BE:
                return codecs.BOM_UTF16_BE + self.encode("utf-16be")
            else:
                return self.encode("utf-16be")
        elif self.autodetect_pdfdocencoding:
            return encode_pdfdocencoding(self)
        else:
            raise Exception("no information about original bytes")  # pragma: no cover

    def get_encoded_bytes(self) -> bytes:
        # Try to write the string out as a PDFDocEncoding encoded string. It's
        # nicer to look at in the PDF file. Sadly, we take a performance hit
        # here for trying...
        try:
            if self._original_bytes is not None:
                return self._original_bytes
            if self.autodetect_utf16:
                raise UnicodeEncodeError("", "forced", -1, -1, "")
            bytearr = encode_pdfdocencoding(self)
        except UnicodeEncodeError:
            if self.utf16_bom == codecs.BOM_UTF16_LE:
                bytearr = codecs.BOM_UTF16_LE + self.encode("utf-16le")
            elif self.utf16_bom == codecs.BOM_UTF16_BE:
                bytearr = codecs.BOM_UTF16_BE + self.encode("utf-16be")
            else:
                bytearr = self.encode("utf-16be")
        return bytearr

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        bytearr = self.get_encoded_bytes()
        stream.write(b"(")
        for c_ in iter_unpack("c", bytearr):
            c = cast(bytes, c_[0])
            if not c.isalnum() and c != b" ":
                # This:
                #   stream.write(rf"\{c:0>3o}".encode())
                # gives
                #   https://github.com/davidhalter/parso/issues/207
                stream.write(b"\\%03o" % ord(c))
            else:
                stream.write(c)
        stream.write(b")")


class NameObject(str, PdfObject):  # noqa: SLOT000
    delimiter_pattern = re.compile(rb"\s+|[\(\)<>\[\]{}/%]")
    surfix = b"/"
    renumber_table: ClassVar[Dict[str, bytes]] = {
        "#": b"#23",
        "(": b"#28",
        ")": b"#29",
        "/": b"#2F",
        "%": b"#25",
        **{chr(i): f"#{i:02X}".encode() for i in range(33)},
    }

    def clone(
        self,
        pdf_dest: Any,
        force_duplicate: bool = False,
        ignore_fields: Optional[Sequence[Union[str, int]]] = (),
    ) -> "NameObject":
        """Clone object into pdf_dest."""
        return cast(
            "NameObject",
            self._reference_clone(NameObject(self), pdf_dest, force_duplicate),
        )

    def hash_bin(self) -> int:
        """
        Used to detect modified object.

        Returns:
            Hash considering type and value.

        """
        return hash((self.__class__, self))

    def write_to_stream(
        self, stream: StreamType, encryption_key: Union[None, str, bytes] = None
    ) -> None:
        if encryption_key is not None:  # deprecated
            deprecate_no_replacement(
                "the encryption_key parameter of write_to_stream", "5.0.0"
            )
        stream.write(self.renumber())

    def renumber(self) -> bytes:
        out = self[0].encode("utf-8")
        if out != b"/":
            deprecate_no_replacement(
                f"Incorrect first char in NameObject, should start with '/': ({self})",
                "6.0.0",
            )
        for c in self[1:]:
            if c > "~":
                for x in c.encode("utf-8"):
                    out += f"#{x:02X}".encode()
            else:
                try:
                    out += self.renumber_table[c]
                except KeyError:
                    out += c.encode("utf-8")
        return out

    @staticmethod
    def unnumber(sin: bytes) -> bytes:
        i = sin.find(b"#", 0)
        while i >= 0:
            try:
                sin = sin[:i] + unhexlify(sin[i + 1 : i + 3]) + sin[i + 3 :]
                i = sin.find(b"#", i + 1)
            except ValueError:
                # if the 2 characters after # can not be converted to hex
                # we change nothing and carry on
                i = i + 1
        return sin

    CHARSETS = ("utf-8", "gbk", "latin1")

    @staticmethod
    def read_from_stream(stream: StreamType, pdf: Any) -> "NameObject":  # PdfReader
        name = stream.read(1)
        if name != NameObject.surfix:
            raise PdfReadError("Name read error")
        name += read_until_regex(stream, NameObject.delimiter_pattern)
        try:
            # Name objects should represent irregular characters
            # with a '#' followed by the symbol's hex number
            name = NameObject.unnumber(name)
            for enc in NameObject.CHARSETS:
                try:
                    ret = name.decode(enc)
                    return NameObject(ret)
                except Exception:
                    pass
            raise UnicodeDecodeError("", name, 0, 0, "Code Not Found")
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if not pdf.strict:
                logger_warning(
                    f"Illegal character in NameObject ({name!r}), "
                    "you may need to adjust NameObject.CHARSETS",
                    __name__,
                )
                return NameObject(name.decode("charmap"))
            else:
                raise PdfReadError(
                    f"Illegal character in NameObject ({name!r}). "
                    "You may need to adjust NameObject.CHARSETS.",
                ) from e


def encode_pdfdocencoding(unicode_string: str) -> bytes:
    try:
        return bytes([_pdfdoc_encoding_rev[k] for k in unicode_string])
    except KeyError:
        raise UnicodeEncodeError(
            "pdfdocencoding",
            unicode_string,
            -1,
            -1,
            "does not exist in translation table",
        )


def is_null_or_none(x: Any) -> TypeGuard[Union[None, NullObject, IndirectObject]]:
    """
    Returns:
        True if x is None or NullObject.

    """
    return x is None or (
        isinstance(x, PdfObject)
        and (x.get_object() is None or isinstance(x.get_object(), NullObject))
    )
