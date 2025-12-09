# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel
from .response_code_interpreter_tool_call import ResponseCodeInterpreterToolCall

__all__ = ["ResponseCodeInterpreterCallCompletedEvent"]


class ResponseCodeInterpreterCallCompletedEvent(BaseModel):
    code_interpreter_call: ResponseCodeInterpreterToolCall
    """A tool call to run code."""

    output_index: int
    """The index of the output item that the code interpreter call is in progress."""

    type: Literal["response.code_interpreter_call.completed"]
    """The type of the event. Always `response.code_interpreter_call.completed`."""
