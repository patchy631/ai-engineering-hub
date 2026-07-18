# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import TypeAlias

from .computer_tool_param import ComputerToolParam
from .function_tool_param import FunctionToolParam
from .web_search_tool_param import WebSearchToolParam
from .file_search_tool_param import FileSearchToolParam
from ..chat.chat_completion_tool_param import ChatCompletionToolParam

__all__ = ["ToolParam"]

ToolParam: TypeAlias = Union[FileSearchToolParam, FunctionToolParam, ComputerToolParam, WebSearchToolParam]

ParseableToolParam: TypeAlias = Union[ToolParam, ChatCompletionToolParam]
