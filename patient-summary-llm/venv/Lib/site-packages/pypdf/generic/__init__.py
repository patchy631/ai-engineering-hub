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

"""Implementation of generic PDF objects (dictionary, number, string, ...)."""
__author__ = "Mathieu Fenniak"
__author_email__ = "biziqe@mathieu.fenniak.net"

from typing import List, Optional, Tuple, Union

from .._utils import (
    deprecation_with_replacement,
)
from ..constants import OutlineFontFlag
from ._base import (
    BooleanObject,
    ByteStringObject,
    FloatObject,
    IndirectObject,
    NameObject,
    NullObject,
    NumberObject,
    PdfObject,
    TextStringObject,
    encode_pdfdocencoding,
    is_null_or_none,
)
from ._data_structures import (
    ArrayObject,
    ContentStream,
    DecodedStreamObject,
    Destination,
    DictionaryObject,
    EncodedStreamObject,
    Field,
    StreamObject,
    TreeObject,
    read_object,
)
from ._files import EmbeddedFile
from ._fit import Fit
from ._outline import OutlineItem
from ._rectangle import RectangleObject
from ._utils import (
    create_string_object,
    decode_pdfdocencoding,
    hex_to_rgb,
    read_hex_string_from_stream,
    read_string_from_stream,
)
from ._viewerpref import ViewerPreferences

PAGE_FIT = Fit.fit()


class AnnotationBuilder:  # deprecated
    """
    The AnnotationBuilder is deprecated.

    Instead, use the annotation classes in pypdf.annotations.

    See `adding PDF annotations <../user/adding-pdf-annotations.html>`_ for
    its usage combined with PdfWriter.
    """

    from ..generic._rectangle import RectangleObject

    @staticmethod
    def text(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        text: str,
        open: bool = False,
        flags: int = 0,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.text", "pypdf.annotations.Text", "5.0.0"
        )

    @staticmethod
    def free_text(
        text: str,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        font: str = "Helvetica",
        bold: bool = False,
        italic: bool = False,
        font_size: str = "14pt",
        font_color: str = "000000",
        border_color: Optional[str] = "000000",
        background_color: Optional[str] = "ffffff",
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.free_text", "pypdf.annotations.FreeText", "5.0.0"
        )

    @staticmethod
    def popup(
        *,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        flags: int = 0,
        parent: Optional[DictionaryObject] = None,
        open: bool = False,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.popup", "pypdf.annotations.Popup", "5.0.0"
        )

    @staticmethod
    def line(
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        text: str = "",
        title_bar: Optional[str] = None,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.line", "pypdf.annotations.Line", "5.0.0"
        )

    @staticmethod
    def polyline(
        vertices: List[Tuple[float, float]],
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.polyline", "pypdf.annotations.PolyLine", "5.0.0"
        )

    @staticmethod
    def rectangle(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        interiour_color: Optional[str] = None,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.rectangle", "pypdf.annotations.Rectangle", "5.0.0"
        )

    @staticmethod
    def highlight(
        *,
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        quad_points: ArrayObject,
        highlight_color: str = "ff0000",
        printing: bool = False,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.highlight", "pypdf.annotations.Highlight", "5.0.0"
        )

    @staticmethod
    def ellipse(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        interiour_color: Optional[str] = None,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.ellipse", "pypdf.annotations.Ellipse", "5.0.0"
        )

    @staticmethod
    def polygon(vertices: List[Tuple[float, float]]) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.polygon", "pypdf.annotations.Polygon", "5.0.0"
        )

    from ._fit import DEFAULT_FIT

    @staticmethod
    def link(
        rect: Union[RectangleObject, Tuple[float, float, float, float]],
        border: Optional[ArrayObject] = None,
        url: Optional[str] = None,
        target_page_index: Optional[int] = None,
        fit: Fit = DEFAULT_FIT,
    ) -> None:
        deprecation_with_replacement(
            "AnnotationBuilder.link", "pypdf.annotations.Link", "5.0.0"
        )


__all__ = [
    "PAGE_FIT",
    "AnnotationBuilder",
    "ArrayObject",
    "BooleanObject",
    "ByteStringObject",
    "ContentStream",
    "DecodedStreamObject",
    "Destination",
    "DictionaryObject",
    "EmbeddedFile",
    "EncodedStreamObject",
    "Field",
    "Fit",
    "FloatObject",
    "IndirectObject",
    "NameObject",
    "NullObject",
    "NumberObject",
    "OutlineFontFlag",
    "OutlineItem",
    "PdfObject",
    "RectangleObject",
    "StreamObject",
    "TextStringObject",
    "TreeObject",
    "ViewerPreferences",
    # Utility functions
    "create_string_object",
    "decode_pdfdocencoding",
    "encode_pdfdocencoding",
    "hex_to_rgb",
    "is_null_or_none",
    "read_hex_string_from_stream",
    # Data structures core functions
    "read_object",
    "read_string_from_stream",
]
