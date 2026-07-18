# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseFunctionCallArgumentsDoneEvent"]


class ResponseFunctionCallArgumentsDoneEvent(BaseModel):
    arguments: str
    """The function-call arguments."""

    item_id: str
    """The ID of the item."""

    output_index: int
    """The index of the output item."""

    type: Literal["response.function_call_arguments.done"]
