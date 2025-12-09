# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Union
from typing_extensions import Literal, Annotated, TypeAlias

from ..._utils import PropertyInfo
from ..._models import BaseModel

__all__ = ["ResponseCodeInterpreterToolCall", "Result", "ResultLogs", "ResultFiles", "ResultFilesFile"]


class ResultLogs(BaseModel):
    logs: str
    """The logs of the code interpreter tool call."""

    type: Literal["logs"]
    """The type of the code interpreter text output. Always `logs`."""


class ResultFilesFile(BaseModel):
    file_id: str
    """The ID of the file."""

    mime_type: str
    """The MIME type of the file."""


class ResultFiles(BaseModel):
    files: List[ResultFilesFile]

    type: Literal["files"]
    """The type of the code interpreter file output. Always `files`."""


Result: TypeAlias = Annotated[Union[ResultLogs, ResultFiles], PropertyInfo(discriminator="type")]


class ResponseCodeInterpreterToolCall(BaseModel):
    id: str
    """The unique ID of the code interpreter tool call."""

    code: str
    """The code to run."""

    results: List[Result]
    """The results of the code interpreter tool call."""

    status: Literal["in_progress", "interpreting", "completed"]
    """The status of the code interpreter tool call."""

    type: Literal["code_interpreter_call"]
    """The type of the code interpreter tool call. Always `code_interpreter_call`."""
