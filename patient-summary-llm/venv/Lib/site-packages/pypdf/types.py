"""Helpers for working with PDF types."""

import sys
from typing import List, Literal, Union

if sys.version_info[:2] >= (3, 10):
    # Python 3.10+: https://www.python.org/dev/peps/pep-0484
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias

from .generic._base import NameObject, NullObject, NumberObject
from .generic._data_structures import ArrayObject, Destination
from .generic._outline import OutlineItem

BorderArrayType: TypeAlias = List[Union[NameObject, NumberObject, ArrayObject]]
OutlineItemType: TypeAlias = Union[OutlineItem, Destination]
FitType: TypeAlias = Literal[
    "/XYZ", "/Fit", "/FitH", "/FitV", "/FitR", "/FitB", "/FitBH", "/FitBV"
]
# Those go with the FitType: They specify values for the fit
ZoomArgType: TypeAlias = Union[NumberObject, NullObject, float]
ZoomArgsType: TypeAlias = List[ZoomArgType]

# Recursive types like the following are not yet supported by mypy:
#    OutlineType = List[Union[Destination, "OutlineType"]]
# See https://github.com/python/mypy/issues/731
# Hence use this for the moment:
OutlineType = List[Union[Destination, List[Union[Destination, List[Destination]]]]]

LayoutType: TypeAlias = Literal[
    "/NoLayout",
    "/SinglePage",
    "/OneColumn",
    "/TwoColumnLeft",
    "/TwoColumnRight",
    "/TwoPageLeft",
    "/TwoPageRight",
]
PagemodeType: TypeAlias = Literal[
    "/UseNone",
    "/UseOutlines",
    "/UseThumbs",
    "/FullScreen",
    "/UseOC",
    "/UseAttachments",
]
AnnotationSubtype: TypeAlias = Literal[
    "/Text",
    "/Link",
    "/FreeText",
    "/Line",
    "/Square",
    "/Circle",
    "/Polygon",
    "/PolyLine",
    "/Highlight",
    "/Underline",
    "/Squiggly",
    "/StrikeOut",
    "/Caret",
    "/Stamp",
    "/Ink",
    "/Popup",
    "/FileAttachment",
    "/Sound",
    "/Movie",
    "/Screen",
    "/Widget",
    "/PrinterMark",
    "/TrapNet",
    "/Watermark",
    "/3D",
    "/Redact",
    "/Projection",
    "/RichMedia",
]
