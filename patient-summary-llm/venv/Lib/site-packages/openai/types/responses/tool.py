# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .computer_tool import ComputerTool
from .function_tool import FunctionTool
from .web_search_tool import WebSearchTool
from .file_search_tool import FileSearchTool

__all__ = ["Tool"]

Tool: TypeAlias = Annotated[
    Union[FileSearchTool, FunctionTool, ComputerTool, WebSearchTool], PropertyInfo(discriminator="type")
]
