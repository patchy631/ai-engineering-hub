# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseTextDeltaEvent"]


class ResponseTextDeltaEvent(BaseModel):
    content_index: int
    """The index of the content part that the text delta was added to."""

    delta: str
    """The text delta that was added."""

    item_id: str
    """The ID of the output item that the text delta was added to."""

    output_index: int
    """The index of the output item that the text delta was added to."""

    type: Literal["response.output_text.delta"]
    """The type of the event. Always `response.output_text.delta`."""
