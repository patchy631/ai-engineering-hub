# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from .response import Response
from ..._models import BaseModel

__all__ = ["ResponseInProgressEvent"]


class ResponseInProgressEvent(BaseModel):
    response: Response
    """The response that is in progress."""

    type: Literal["response.in_progress"]
    """The type of the event. Always `response.in_progress`."""
