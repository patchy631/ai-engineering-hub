# Required imports
import asyncio
from typing import Dict, List, Any, Optional
from llama_index.core import Settings
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.workflow import (
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
    Context,
)


#####################################
# Define Router Agent Workflow
#####################################
class InputEvent(Event):
    """Input event."""


class GatherToolsEvent(Event):
    """Gather Tools Event"""

    tool_calls: Any


class ToolCallEvent(Event):
    """Tool Call event"""

    tool_call: ToolSelection


class ToolCallEventResult(Event):
    """Tool call event result."""

    msg: ChatMessage


class RouterOutputAgentWorkflow(Workflow):
    """Custom router output agent workflow."""

    def __init__(
        self,
        tools: List[BaseTool],
        timeout: Optional[float] = 10.0,
        disable_validation: bool = False,
        verbose: bool = False,
        llm: Optional[LLM] = None,
        chat_history: Optional[List[ChatMessage]] = None,
    ):
        """Constructor."""
        super().__init__(
            timeout=timeout, disable_validation=disable_validation, verbose=verbose
        )
        self.tools: List[BaseTool] = tools
        self.tools_dict: Optional[Dict[str, BaseTool]] = {
            tool.metadata.name: tool for tool in self.tools
        }
        # Use provided LLM or fall back to Settings.llm
        self.llm: LLM = llm or Settings.llm
        if self.llm is None:
            raise ValueError("No LLM provided and Settings.llm is not initialized")
        self.chat_history: List[ChatMessage] = chat_history or []

    def reset(self) -> None:
        """Resets Chat History"""
        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        message = ev.get("message")
        if message is None:
            raise ValueError("'message' field is required.")

        # Add message to chat history
        chat_history = self.chat_history
        chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        """Appends msg to chat history, then gets tool calls."""
        try:
            # Put message into LLM with tools included
            chat_res = await self.llm.achat_with_tools(
                self.tools,
                chat_history=self.chat_history,
                verbose=self._verbose,
                allow_parallel_tool_calls=True,
            )
            tool_calls = self.llm.get_tool_calls_from_response(
                chat_res, error_on_no_tool_call=False
            )

            ai_message = chat_res.message
            self.chat_history.append(ai_message)
            if self._verbose:
                print(f"Chat message: {ai_message.content}")

            # No tool calls, return chat message.
            if not tool_calls:
                return StopEvent(result=ai_message.content)

            return GatherToolsEvent(tool_calls=tool_calls)
        except asyncio.CancelledError:
            print("Chat operation was cancelled")
            return StopEvent(result="The operation was cancelled. Please try again.")
        except Exception as e:
            error_msg = f"Error during chat: {str(e)}"
            print(error_msg)
            return StopEvent(
                result="I'm sorry, I encountered an issue processing your request. Could you try asking in a different way?"
            )

    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> ToolCallEvent:
        """Dispatches calls."""
        tool_calls = ev.tool_calls
        await ctx.set("num_tool_calls", len(tool_calls))

        # Trigger tool call events
        for tool_call in tool_calls:
            ctx.send_event(ToolCallEvent(tool_call=tool_call))

        return None

    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """Calls tool."""
        try:
            tool_call = ev.tool_call
            # Get tool ID and function call
            id_ = tool_call.tool_id

            if self._verbose:
                print(
                    f"Calling function {tool_call.tool_name} with msg {tool_call.tool_kwargs}"
                )

            # Call function and put result into a chat message
            tool = self.tools_dict[tool_call.tool_name]
            output = await tool.acall(**tool_call.tool_kwargs)
            
            # Check if output is a dictionary (response, trust_score) for document tool
            if isinstance(output, dict) and "response" in output:
                response = output.get("response", "")
                trust_score = output.get("trust_score")
                # Ensure response is a string
                content = str(response) if response is not None else ""
                # Store additional metadata
                additional_kwargs = {
                    "tool_call_id": id_, 
                    "name": tool_call.tool_name,
                    "trust_score": trust_score,
                    "tool_used": tool_call.tool_name
                }
                if self._verbose:
                    print(f"Tool {tool_call.tool_name} returned dict: response='{content}', trust_score={trust_score}")
            else:
                content = str(output) if output is not None else ""
                additional_kwargs = {
                    "tool_call_id": id_, 
                    "name": tool_call.tool_name,
                    "tool_used": tool_call.tool_name
                }
                if self._verbose:
                    print(f"Tool {tool_call.tool_name} returned: '{content}'")
            
            msg = ChatMessage(
                name=tool_call.tool_name,
                content=content,
                role="tool",
                additional_kwargs=additional_kwargs,
            )

            return ToolCallEventResult(msg=msg)
            
        except asyncio.CancelledError:
            print(f"Tool call {tool_call.tool_name} was cancelled")
            # Return a dummy result to avoid workflow breakdown
            msg = ChatMessage(
                name=tool_call.tool_name,
                content="Tool execution was cancelled",
                role="tool",
                additional_kwargs={"tool_call_id": id_, "name": tool_call.tool_name, "tool_used": tool_call.tool_name},
            )
            return ToolCallEventResult(msg=msg)
        except Exception as e:
            print(f"Error in tool call {tool_call.tool_name}: {str(e)}")
            # Return an error result instead of failing
            msg = ChatMessage(
                name=tool_call.tool_name,
                content=f"Error executing tool: {str(e)}",
                role="tool",
                additional_kwargs={"tool_call_id": id_, "name": tool_call.tool_name, "tool_used": tool_call.tool_name},
            )
            return ToolCallEventResult(msg=msg)

    @step(pass_context=True)
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> StopEvent | None:
        """Gathers tool calls."""
        try:
            # Wait for all tool call events to finish.
            tool_events = ctx.collect_events(
                ev, [ToolCallEventResult] * await ctx.get("num_tool_calls")
            )
            if not tool_events:
                return None

            for tool_event in tool_events:
                # Append tool call chat messages to history
                self.chat_history.append(tool_event.msg)

            # After all tool calls finish, pass input event back, restart agent loop
            return InputEvent()
        except Exception as e:
            print(f"Error in gather step: {str(e)}")
            # Return a stop event instead of continuing the loop if there's an error
            return StopEvent(result="I encountered an issue processing the tool responses. Please try again.")
