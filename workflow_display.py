from typing import Dict, List, Any, Optional
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.workflow import (
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.core.base.response.schema import Response
# from llama_index.utils.workflow import draw_all_possible_flows
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class UserInputEvent(Event):
    """Handles user input event."""
    pass

class ToolGatherEvent(Event):
    """Event for collecting tool calls."""
    tool_calls: Any

class ToolExecutionEvent(Event):
    """Represents a tool execution event."""
    tool_call: ToolSelection

class ToolExecutionResult(Event):
    """Event for storing tool execution results."""
    msg: ChatMessage

class AdaptiveWorkflow(Workflow):
    """Custom adaptive workflow to manage tool interactions."""

    def __init__(self,
        tools: List[BaseTool],
        timeout: Optional[float] = 10.0,
        verbose: bool = False,
        llm: Optional[LLM] = None,
        chat_history: Optional[List[ChatMessage]] = None,
    ):
        """Initialize workflow with tools and LLM."""
        super().__init__(timeout=timeout, verbose=verbose)
        self.tools = tools
        self.tool_map: Dict[str, BaseTool] = {tool.metadata.name: tool for tool in self.tools}
        self.llm = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.chat_history = chat_history or []

    def reset_history(self) -> None:
        """Clears chat history."""
        self.chat_history = []

    @step()
    async def process_input(self, ev: StartEvent) -> UserInputEvent:
        message = ev.get("message")
        if not message:
            raise ValueError("Message content is required.")
        self.chat_history.append(ChatMessage(role="user", content=message))
        return UserInputEvent()

    @step()
    async def generate_response(self, ev: UserInputEvent) -> ToolGatherEvent | StopEvent:
        """Generate AI response and determine if tools are required."""
        response = await self.llm.achat_with_tools(
            self.tools,
            chat_history=self.chat_history,
            verbose=self._verbose,
            allow_parallel_tool_calls=True
        )
        tool_calls = self.llm.get_tool_calls_from_response(response, error_on_no_tool_call=False)
        self.chat_history.append(response.message)
        if not tool_calls:
            return StopEvent(result=response.message.content)
        return ToolGatherEvent(tool_calls=tool_calls)

    @step(pass_context=True)
    async def manage_tools(self, ctx: Context, ev: ToolGatherEvent) -> ToolExecutionEvent:
        """Manages and triggers tool execution events."""
        await ctx.set("tool_count", len(ev.tool_calls))
        for tool_call in ev.tool_calls:
            ctx.send_event(ToolExecutionEvent(tool_call=tool_call))
        return None

    @step()
    async def execute_tool(self, ev: ToolExecutionEvent) -> ToolExecutionResult:
        """Executes the selected tool and processes its output."""
        tool_call = ev.tool_call
        tool = self.tool_map[tool_call.tool_name]
        output = await tool.acall(**tool_call.tool_kwargs)
        response_msg = ChatMessage(
            name=tool_call.tool_name,
            content=str(output),
            role="tool",
            additional_kwargs={"tool_call_id": tool_call.tool_id, "name": tool_call.tool_name}
        )
        return ToolExecutionResult(msg=response_msg)

    @step(pass_context=True)
    async def collect_results(self, ctx: Context, ev: ToolExecutionResult) -> StopEvent | None:
        """Collects all tool execution results and processes final output."""
        tool_events = ctx.collect_events(ev, [ToolExecutionResult] * await ctx.get("tool_count"))
        if not tool_events:
            return None
        for tool_event in tool_events:
            self.chat_history.append(tool_event.msg)
        return UserInputEvent()

# Visualizing workflow
if __name__ == "__main__":
    import streamlit as st
    st.title("Workflow Visualization")
    with open("task1/workflow_diagram.html", "r") as file:
        html_content = file.read()
    st.components.v1.html(html_content, height=800, scrolling=True)
