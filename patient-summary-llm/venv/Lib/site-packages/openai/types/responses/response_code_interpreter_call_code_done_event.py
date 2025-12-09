# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["ResponseCodeInterpreterCallCodeDoneEvent"]


class ResponseCodeInterpreterCallCodeDoneEvent(BaseModel):
    code: str
    """The final code snippet output by the code interpreter."""

    output_index: int
    """The index of the output item that the code interpreter call is in progress."""

    type: Literal["response.code_interpreter_call.code.done"]
    """The type of the event. Always `response.code_interpreter_call.code.done`."""
