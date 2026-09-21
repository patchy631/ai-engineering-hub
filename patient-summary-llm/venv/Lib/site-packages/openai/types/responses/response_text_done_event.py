# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseTextDoneEvent"]


class ResponseTextDoneEvent(BaseModel):
    content_index: int
    """The index of the content part that the text content is finalized."""

    item_id: str
    """The ID of the output item that the text content is finalized."""

    output_index: int
    """The index of the output item that the text content is finalized."""

    text: str
    """The text content that is finalized."""

    type: Literal["response.output_text.done"]
    """The type of the event. Always `response.output_text.done`."""
