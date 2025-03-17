# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["InputItemListParams"]


class InputItemListParams(TypedDict, total=False):
    after: str
    """An item ID to list items after, used in pagination."""

    before: str
    """An item ID to list items before, used in pagination."""

    limit: int
    """A limit on the number of objects to be returned.

    Limit can range between 1 and 100, and the default is 20.
    """

    order: Literal["asc", "desc"]
    """The order to return the input items in. Default is `asc`.

    - `asc`: Return the input items in ascending order.
    - `desc`: Return the input items in descending order.
    """
