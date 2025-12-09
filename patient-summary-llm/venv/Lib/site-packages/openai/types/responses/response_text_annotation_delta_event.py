# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = [
    "ResponseTextAnnotationDeltaEvent",
    "Annotation",
    "AnnotationFileCitation",
    "AnnotationURLCitation",
    "AnnotationFilePath",
]


class AnnotationFileCitation(BaseModel):
    file_id: str
    """The ID of the file."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_citation"]
    """The type of the file citation. Always `file_citation`."""


class AnnotationURLCitation(BaseModel):
    end_index: int
    """The index of the last character of the URL citation in the message."""

    start_index: int
    """The index of the first character of the URL citation in the message."""

    title: str
    """The title of the web resource."""

    type: Literal["url_citation"]
    """The type of the URL citation. Always `url_citation`."""

    url: str
    """The URL of the web resource."""


class AnnotationFilePath(BaseModel):
    file_id: str
    """The ID of the file."""

    index: int
    """The index of the file in the list of files."""

    type: Literal["file_path"]
    """The type of the file path. Always `file_path`."""


Annotation: TypeAlias = Annotated[
    Union[AnnotationFileCitation, AnnotationURLCitation, AnnotationFilePath], PropertyInfo(discriminator="type")
]


class ResponseTextAnnotationDeltaEvent(BaseModel):
    annotation: Annotation
    """A citation to a file."""

    annotation_index: int
    """The index of the annotation that was added."""

    content_index: int
    """The index of the content part that the text annotation was added to."""

    item_id: str
    """The ID of the output item that the text annotation was added to."""

    output_index: int
    """The index of the output item that the text annotation was added to."""

    type: Literal["response.output_text.annotation.added"]
    """The type of the event. Always `response.output_text.annotation.added`."""
