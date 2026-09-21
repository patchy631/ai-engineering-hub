# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .response_output_item import ResponseOutputItem

__all__ = ["ResponseOutputItemAddedEvent"]


class ResponseOutputItemAddedEvent(BaseModel):
    item: ResponseOutputItem
    """The output item that was added."""

    output_index: int
    """The index of the output item that was added."""

    type: Literal["response.output_item.added"]
    """The type of the event. Always `response.output_item.added`."""
