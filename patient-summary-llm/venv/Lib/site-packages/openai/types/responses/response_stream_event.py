# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union
from typing_extensions import Annotated, TypeAlias

from ..._utils import PropertyInfo
from .response_error_event import ResponseErrorEvent
from .response_failed_event import ResponseFailedEvent
from .response_created_event import ResponseCreatedEvent
from .response_completed_event import ResponseCompletedEvent
from .response_text_done_event import ResponseTextDoneEvent
from .response_audio_done_event import ResponseAudioDoneEvent
from .response_incomplete_event import ResponseIncompleteEvent
from .response_text_delta_event import ResponseTextDeltaEvent
from .response_audio_delta_event import ResponseAudioDeltaEvent
from .response_in_progress_event import ResponseInProgressEvent
from .response_refusal_done_event import ResponseRefusalDoneEvent
from .response_refusal_delta_event import ResponseRefusalDeltaEvent
from .response_output_item_done_event import ResponseOutputItemDoneEvent
from .response_content_part_done_event import ResponseContentPartDoneEvent
from .response_output_item_added_event import ResponseOutputItemAddedEvent
from .response_content_part_added_event import ResponseContentPartAddedEvent
from .response_audio_transcript_done_event import ResponseAudioTranscriptDoneEvent
from .response_text_annotation_delta_event import ResponseTextAnnotationDeltaEvent
from .response_audio_transcript_delta_event import ResponseAudioTranscriptDeltaEvent
from .response_web_search_call_completed_event import ResponseWebSearchCallCompletedEvent
from .response_web_search_call_searching_event import ResponseWebSearchCallSearchingEvent
from .response_file_search_call_completed_event import ResponseFileSearchCallCompletedEvent
from .response_file_search_call_searching_event import ResponseFileSearchCallSearchingEvent
from .response_web_search_call_in_progress_event import ResponseWebSearchCallInProgressEvent
from .response_file_search_call_in_progress_event import ResponseFileSearchCallInProgressEvent
from .response_function_call_arguments_done_event import ResponseFunctionCallArgumentsDoneEvent
from .response_function_call_arguments_delta_event import ResponseFunctionCallArgumentsDeltaEvent
from .response_code_interpreter_call_code_done_event import ResponseCodeInterpreterCallCodeDoneEvent
from .response_code_interpreter_call_completed_event import ResponseCodeInterpreterCallCompletedEvent
from .response_code_interpreter_call_code_delta_event import ResponseCodeInterpreterCallCodeDeltaEvent
from .response_code_interpreter_call_in_progress_event import ResponseCodeInterpreterCallInProgressEvent
from .response_code_interpreter_call_interpreting_event import ResponseCodeInterpreterCallInterpretingEvent

__all__ = ["ResponseStreamEvent"]

ResponseStreamEvent: TypeAlias = Annotated[
    Union[
        ResponseAudioDeltaEvent,
        ResponseAudioDoneEvent,
        ResponseAudioTranscriptDeltaEvent,
        ResponseAudioTranscriptDoneEvent,
        ResponseCodeInterpreterCallCodeDeltaEvent,
        ResponseCodeInterpreterCallCodeDoneEvent,
        ResponseCodeInterpreterCallCompletedEvent,
        ResponseCodeInterpreterCallInProgressEvent,
        ResponseCodeInterpreterCallInterpretingEvent,
        ResponseCompletedEvent,
        ResponseContentPartAddedEvent,
        ResponseContentPartDoneEvent,
        ResponseCreatedEvent,
        ResponseErrorEvent,
        ResponseFileSearchCallCompletedEvent,
        ResponseFileSearchCallInProgressEvent,
        ResponseFileSearchCallSearchingEvent,
        ResponseFunctionCallArgumentsDeltaEvent,
        ResponseFunctionCallArgumentsDoneEvent,
        ResponseInProgressEvent,
        ResponseFailedEvent,
        ResponseIncompleteEvent,
        ResponseOutputItemAddedEvent,
        ResponseOutputItemDoneEvent,
        ResponseRefusalDeltaEvent,
        ResponseRefusalDoneEvent,
        ResponseTextAnnotationDeltaEvent,
        ResponseTextDeltaEvent,
        ResponseTextDoneEvent,
        ResponseWebSearchCallCompletedEvent,
        ResponseWebSearchCallInProgressEvent,
        ResponseWebSearchCallSearchingEvent,
    ],
    PropertyInfo(discriminator="type"),
]
