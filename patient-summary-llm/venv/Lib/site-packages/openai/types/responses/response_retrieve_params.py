# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import TypedDict

from .response_includable import ResponseIncludable

__all__ = ["ResponseRetrieveParams"]


class ResponseRetrieveParams(TypedDict, total=False):
    include: List[ResponseIncludable]
    """Additional fields to include in the response.

    See the `include` parameter for Response creation above for more information.
    """
