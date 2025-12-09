# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Any, List, Type, Union, Iterable, Optional, cast
from functools import partial
from typing_extensions import Literal, overload

import httpx

from ... import _legacy_response
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import (
    is_given,
    required_args,
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import to_streamed_response_wrapper, async_to_streamed_response_wrapper
from .input_items import (
    InputItems,
    AsyncInputItems,
    InputItemsWithRawResponse,
    AsyncInputItemsWithRawResponse,
    InputItemsWithStreamingResponse,
    AsyncInputItemsWithStreamingResponse,
)
from ..._streaming import Stream, AsyncStream
from ...lib._tools import PydanticFunctionTool, ResponsesPydanticFunctionTool
from ..._base_client import make_request_options
from ...types.responses import response_create_params, response_retrieve_params
from ...lib._parsing._responses import (
    TextFormatT,
    parse_response,
    type_to_text_format_param as _type_to_text_format_param,
)
from ...types.shared.chat_model import ChatModel
from ...types.responses.response import Response
from ...types.responses.tool_param import ToolParam, ParseableToolParam
from ...types.shared_params.metadata import Metadata
from ...types.shared_params.reasoning import Reasoning
from ...types.responses.parsed_response import ParsedResponse
from ...lib.streaming.responses._responses import ResponseStreamManager, AsyncResponseStreamManager
from ...types.responses.response_includable import ResponseIncludable
from ...types.responses.response_input_param import ResponseInputParam
from ...types.responses.response_stream_event import ResponseStreamEvent
from ...types.responses.response_text_config_param import ResponseTextConfigParam

__all__ = ["Responses", "AsyncResponses"]


class Responses(SyncAPIResource):
    @cached_property
    def input_items(self) -> InputItems:
        return InputItems(self._client)

    @cached_property
    def with_raw_response(self) -> ResponsesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return ResponsesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ResponsesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return ResponsesWithStreamingResponse(self)

    @overload
    def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        stream: Literal[True],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        stream: bool,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | Stream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input", "model"], ["input", "model", "stream"])
    def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | Stream[ResponseStreamEvent]:
        return self._post(
            "/responses",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "include": include,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "metadata": metadata,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "reasoning": reasoning,
                    "store": store,
                    "stream": stream,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=Stream[ResponseStreamEvent],
        )

    def stream(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        text_format: type[TextFormatT] | NotGiven = NOT_GIVEN,
        tools: Iterable[ParseableToolParam] | NotGiven = NOT_GIVEN,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ResponseStreamManager[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")

            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        api_request: partial[Stream[ResponseStreamEvent]] = partial(
            self.create,
            input=input,
            model=model,
            tools=tools,
            include=include,
            instructions=instructions,
            max_output_tokens=max_output_tokens,
            metadata=metadata,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            store=store,
            stream=True,
            temperature=temperature,
            text=text,
            tool_choice=tool_choice,
            reasoning=reasoning,
            top_p=top_p,
            truncation=truncation,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return ResponseStreamManager(
            api_request,
            text_format=text_format,
            input_tools=tools,
        )

    def parse(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        text_format: type[TextFormatT] | NotGiven = NOT_GIVEN,
        tools: Iterable[ParseableToolParam] | NotGiven = NOT_GIVEN,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ParsedResponse[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")

            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        def parser(raw_response: Response) -> ParsedResponse[TextFormatT]:
            return parse_response(
                input_tools=tools,
                text_format=text_format,
                response=raw_response,
            )

        return self._post(
            "/responses",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "include": include,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "metadata": metadata,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "reasoning": reasoning,
                    "store": store,
                    "stream": stream,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                post_parser=parser,
            ),
            # we turn the `Response` instance into a `ParsedResponse`
            # in the `parser` function above
            cast_to=cast(Type[ParsedResponse[TextFormatT]], Response),
        )

    def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response:
        """
        Retrieves a model response with the given ID.

        Args:
          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return self._get(
            f"/responses/{response_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"include": include}, response_retrieve_params.ResponseRetrieveParams),
            ),
            cast_to=Response,
        )

    def delete(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a model response with the given ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/responses/{response_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncResponses(AsyncAPIResource):
    @cached_property
    def input_items(self) -> AsyncInputItems:
        return AsyncInputItems(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncResponsesWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/openai/openai-python#accessing-raw-response-data-eg-headers
        """
        return AsyncResponsesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncResponsesWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/openai/openai-python#with_streaming_response
        """
        return AsyncResponsesWithStreamingResponse(self)

    @overload
    async def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        stream: Literal[True],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @overload
    async def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        stream: bool,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        """Creates a model response.

        Provide
        [text](https://platform.openai.com/docs/guides/text) or
        [image](https://platform.openai.com/docs/guides/images) inputs to generate
        [text](https://platform.openai.com/docs/guides/text) or
        [JSON](https://platform.openai.com/docs/guides/structured-outputs) outputs. Have
        the model call your own
        [custom code](https://platform.openai.com/docs/guides/function-calling) or use
        built-in [tools](https://platform.openai.com/docs/guides/tools) like
        [web search](https://platform.openai.com/docs/guides/tools-web-search) or
        [file search](https://platform.openai.com/docs/guides/tools-file-search) to use
        your own data as input for the model's response.

        Args:
          input: Text, image, or file inputs to the model, used to generate a response.

              Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Image inputs](https://platform.openai.com/docs/guides/images)
              - [File inputs](https://platform.openai.com/docs/guides/pdf-files)
              - [Conversation state](https://platform.openai.com/docs/guides/conversation-state)
              - [Function calling](https://platform.openai.com/docs/guides/function-calling)

          model: Model ID used to generate the response, like `gpt-4o` or `o1`. OpenAI offers a
              wide range of models with different capabilities, performance characteristics,
              and price points. Refer to the
              [model guide](https://platform.openai.com/docs/models) to browse and compare
              available models.

          stream: If set to true, the model response data will be streamed to the client as it is
              generated using
              [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events#Event_stream_format).
              See the
              [Streaming section below](https://platform.openai.com/docs/api-reference/responses-streaming)
              for more information.

          include: Specify additional output data to include in the model response. Currently
              supported values are:

              - `file_search_call.results`: Include the search results of the file search tool
                call.
              - `message.input_image.image_url`: Include image urls from the input message.
              - `computer_call_output.output.image_url`: Include image urls from the computer
                call output.

          instructions: Inserts a system (or developer) message as the first item in the model's
              context.

              When using along with `previous_response_id`, the instructions from a previous
              response will be not be carried over to the next response. This makes it simple
              to swap out system (or developer) messages in new responses.

          max_output_tokens: An upper bound for the number of tokens that can be generated for a response,
              including visible output tokens and
              [reasoning tokens](https://platform.openai.com/docs/guides/reasoning).

          metadata: Set of 16 key-value pairs that can be attached to an object. This can be useful
              for storing additional information about the object in a structured format, and
              querying for objects via API or the dashboard.

              Keys are strings with a maximum length of 64 characters. Values are strings with
              a maximum length of 512 characters.

          parallel_tool_calls: Whether to allow the model to run tool calls in parallel.

          previous_response_id: The unique ID of the previous response to the model. Use this to create
              multi-turn conversations. Learn more about
              [conversation state](https://platform.openai.com/docs/guides/conversation-state).

          reasoning: **o-series models only**

              Configuration options for
              [reasoning models](https://platform.openai.com/docs/guides/reasoning).

          store: Whether to store the generated model response for later retrieval via API.

          temperature: What sampling temperature to use, between 0 and 2. Higher values like 0.8 will
              make the output more random, while lower values like 0.2 will make it more
              focused and deterministic. We generally recommend altering this or `top_p` but
              not both.

          text: Configuration options for a text response from the model. Can be plain text or
              structured JSON data. Learn more:

              - [Text inputs and outputs](https://platform.openai.com/docs/guides/text)
              - [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs)

          tool_choice: How the model should select which tool (or tools) to use when generating a
              response. See the `tools` parameter to see how to specify which tools the model
              can call.

          tools: An array of tools the model may call while generating a response. You can
              specify which tool to use by setting the `tool_choice` parameter.

              The two categories of tools you can provide the model are:

              - **Built-in tools**: Tools that are provided by OpenAI that extend the model's
                capabilities, like
                [web search](https://platform.openai.com/docs/guides/tools-web-search) or
                [file search](https://platform.openai.com/docs/guides/tools-file-search).
                Learn more about
                [built-in tools](https://platform.openai.com/docs/guides/tools).
              - **Function calls (custom tools)**: Functions that are defined by you, enabling
                the model to call your own code. Learn more about
                [function calling](https://platform.openai.com/docs/guides/function-calling).

          top_p: An alternative to sampling with temperature, called nucleus sampling, where the
              model considers the results of the tokens with top_p probability mass. So 0.1
              means only the tokens comprising the top 10% probability mass are considered.

              We generally recommend altering this or `temperature` but not both.

          truncation: The truncation strategy to use for the model response.

              - `auto`: If the context of this response and previous ones exceeds the model's
                context window size, the model will truncate the response to fit the context
                window by dropping input items in the middle of the conversation.
              - `disabled` (default): If a model response will exceed the context window size
                for a model, the request will fail with a 400 error.

          user: A unique identifier representing your end-user, which can help OpenAI to monitor
              and detect abuse.
              [Learn more](https://platform.openai.com/docs/guides/safety-best-practices#end-user-ids).

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        ...

    @required_args(["input", "model"], ["input", "model", "stream"])
    async def create(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response | AsyncStream[ResponseStreamEvent]:
        return await self._post(
            "/responses",
            body=await async_maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "include": include,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "metadata": metadata,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "reasoning": reasoning,
                    "store": store,
                    "stream": stream,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Response,
            stream=stream or False,
            stream_cls=AsyncStream[ResponseStreamEvent],
        )

    def stream(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        text_format: type[TextFormatT] | NotGiven = NOT_GIVEN,
        tools: Iterable[ParseableToolParam] | NotGiven = NOT_GIVEN,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncResponseStreamManager[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")

            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        api_request = self.create(
            input=input,
            model=model,
            tools=tools,
            include=include,
            instructions=instructions,
            max_output_tokens=max_output_tokens,
            metadata=metadata,
            parallel_tool_calls=parallel_tool_calls,
            previous_response_id=previous_response_id,
            store=store,
            stream=True,
            temperature=temperature,
            text=text,
            tool_choice=tool_choice,
            reasoning=reasoning,
            top_p=top_p,
            truncation=truncation,
            user=user,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        return AsyncResponseStreamManager(
            api_request,
            text_format=text_format,
            input_tools=tools,
        )

    async def parse(
        self,
        *,
        input: Union[str, ResponseInputParam],
        model: Union[str, ChatModel],
        text_format: type[TextFormatT] | NotGiven = NOT_GIVEN,
        tools: Iterable[ParseableToolParam] | NotGiven = NOT_GIVEN,
        include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN,
        instructions: Optional[str] | NotGiven = NOT_GIVEN,
        max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        metadata: Optional[Metadata] | NotGiven = NOT_GIVEN,
        parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN,
        previous_response_id: Optional[str] | NotGiven = NOT_GIVEN,
        reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN,
        store: Optional[bool] | NotGiven = NOT_GIVEN,
        stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        text: ResponseTextConfigParam | NotGiven = NOT_GIVEN,
        tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ParsedResponse[TextFormatT]:
        if is_given(text_format):
            if not text:
                text = {}

            if "format" in text:
                raise TypeError("Cannot mix and match text.format with text_format")

            text["format"] = _type_to_text_format_param(text_format)

        tools = _make_tools(tools)

        def parser(raw_response: Response) -> ParsedResponse[TextFormatT]:
            return parse_response(
                input_tools=tools,
                text_format=text_format,
                response=raw_response,
            )

        return await self._post(
            "/responses",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "include": include,
                    "instructions": instructions,
                    "max_output_tokens": max_output_tokens,
                    "metadata": metadata,
                    "parallel_tool_calls": parallel_tool_calls,
                    "previous_response_id": previous_response_id,
                    "reasoning": reasoning,
                    "store": store,
                    "stream": stream,
                    "temperature": temperature,
                    "text": text,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                    "truncation": truncation,
                    "user": user,
                },
                response_create_params.ResponseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                post_parser=parser,
            ),
            # we turn the `Response` instance into a `ParsedResponse`
            # in the `parser` function above
            cast_to=cast(Type[ParsedResponse[TextFormatT]], Response),
        )

    async def retrieve(
        self,
        response_id: str,
        *,
        include: List[ResponseIncludable] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Response:
        """
        Retrieves a model response with the given ID.

        Args:
          include: Additional fields to include in the response. See the `include` parameter for
              Response creation above for more information.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        return await self._get(
            f"/responses/{response_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"include": include}, response_retrieve_params.ResponseRetrieveParams
                ),
            ),
            cast_to=Response,
        )

    async def delete(
        self,
        response_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a model response with the given ID.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not response_id:
            raise ValueError(f"Expected a non-empty value for `response_id` but received {response_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/responses/{response_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ResponsesWithRawResponse:
    def __init__(self, responses: Responses) -> None:
        self._responses = responses

        self.create = _legacy_response.to_raw_response_wrapper(
            responses.create,
        )
        self.retrieve = _legacy_response.to_raw_response_wrapper(
            responses.retrieve,
        )
        self.delete = _legacy_response.to_raw_response_wrapper(
            responses.delete,
        )

    @cached_property
    def input_items(self) -> InputItemsWithRawResponse:
        return InputItemsWithRawResponse(self._responses.input_items)


class AsyncResponsesWithRawResponse:
    def __init__(self, responses: AsyncResponses) -> None:
        self._responses = responses

        self.create = _legacy_response.async_to_raw_response_wrapper(
            responses.create,
        )
        self.retrieve = _legacy_response.async_to_raw_response_wrapper(
            responses.retrieve,
        )
        self.delete = _legacy_response.async_to_raw_response_wrapper(
            responses.delete,
        )

    @cached_property
    def input_items(self) -> AsyncInputItemsWithRawResponse:
        return AsyncInputItemsWithRawResponse(self._responses.input_items)


class ResponsesWithStreamingResponse:
    def __init__(self, responses: Responses) -> None:
        self._responses = responses

        self.create = to_streamed_response_wrapper(
            responses.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            responses.retrieve,
        )
        self.delete = to_streamed_response_wrapper(
            responses.delete,
        )

    @cached_property
    def input_items(self) -> InputItemsWithStreamingResponse:
        return InputItemsWithStreamingResponse(self._responses.input_items)


class AsyncResponsesWithStreamingResponse:
    def __init__(self, responses: AsyncResponses) -> None:
        self._responses = responses

        self.create = async_to_streamed_response_wrapper(
            responses.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            responses.retrieve,
        )
        self.delete = async_to_streamed_response_wrapper(
            responses.delete,
        )

    @cached_property
    def input_items(self) -> AsyncInputItemsWithStreamingResponse:
        return AsyncInputItemsWithStreamingResponse(self._responses.input_items)


def _make_tools(tools: Iterable[ParseableToolParam] | NotGiven) -> List[ToolParam] | NotGiven:
    if not is_given(tools):
        return NOT_GIVEN

    converted_tools: List[ToolParam] = []
    for tool in tools:
        if tool["type"] != "function":
            converted_tools.append(tool)
            continue

        if "function" not in tool:
            # standard Responses API case
            converted_tools.append(tool)
            continue

        function = cast(Any, tool)["function"]  # pyright: ignore[reportUnnecessaryCast]
        if not isinstance(function, PydanticFunctionTool):
            raise Exception(
                "Expected Chat Completions function tool shape to be created using `openai.pydantic_function_tool()`"
            )

        assert "parameters" in function
        new_tool = ResponsesPydanticFunctionTool(
            {
                "type": "function",
                "name": function["name"],
                "description": function.get("description"),
                "parameters": function["parameters"],
                "strict": function.get("strict") or False,
            },
            function.model,
        )

        converted_tools.append(new_tool.cast())

    return converted_tools
