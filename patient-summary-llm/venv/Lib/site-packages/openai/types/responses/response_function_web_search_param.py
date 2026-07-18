# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ResponseFunctionWebSearchParam"]


class ResponseFunctionWebSearchParam(TypedDict, total=False):
    id: Required[str]
    """The unique ID of the web search tool call."""

    status: Required[Literal["in_progress", "searching", "completed", "failed"]]
    """The status of the web search tool call."""

    type: Required[Literal["web_search_call"]]
    """The type of the web search tool call. Always `web_search_call`."""
