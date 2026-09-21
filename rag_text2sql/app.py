import asyncio

import nest_asyncio
nest_asyncio.apply()
from opik import track
import os
from dotenv import load_dotenv
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from typing import Dict, List, Any, Optional
from llama_index.core.tools import QueryEngineTool
from sqlalchemy import insert
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.base.response.schema import Response
from llama_index.core.tools import FunctionTool
from llama_index.core.llms.llm import ToolSelection, LLM
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
from llama_index.core.workflow import (
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
    Context
)
from db_init import create_sql_tool, create_llama_cloud_tool

load_dotenv()

Settings.llm = OpenAI("gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), timeout=300)
sql_tool = create_sql_tool()
llama_cloud_tool = create_llama_cloud_tool()


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

    def __init__(self,
        tools: List[BaseTool],
        timeout: Optional[float] = 10.0,
        disable_validation: bool = False,
        verbose: bool = False,
        llm: Optional[LLM] = None,
        chat_history: Optional[List[ChatMessage]] = None,
    ):
        """Constructor."""

        super().__init__(timeout=timeout, disable_validation=disable_validation, verbose=verbose)

        self.tools: List[BaseTool] = tools
        self.tools_dict: Optional[Dict[str, BaseTool]] = {tool.metadata.name: tool for tool in self.tools}
        self.llm: LLM = llm or OpenAI(temperature=0, model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"), timeout=300)
        self.chat_history: List[ChatMessage] = chat_history or []
    

    def reset(self) -> None:
        """Resets Chat History"""

        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        message = ev.get("message")
        if message is None:
            raise ValueError("'message' field is required.")
        
        # add msg to chat history
        chat_history = self.chat_history
        chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        """Appends msg to chat history, then gets tool calls."""

        # Put msg into LLM with tools included
        chat_res = await self.llm.achat_with_tools(
            self.tools,
            chat_history=self.chat_history,
            verbose=self._verbose,
            allow_parallel_tool_calls=True
        )
        tool_calls = self.llm.get_tool_calls_from_response(chat_res, error_on_no_tool_call=False)
        
        ai_message = chat_res.message
        self.chat_history.append(ai_message)
        if self._verbose:
            print(f"Chat message: {ai_message.content}")

        # no tool calls, return chat message.
        if not tool_calls:
            return StopEvent(result=ai_message.content)

        return GatherToolsEvent(tool_calls=tool_calls)

    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> ToolCallEvent:
        """Dispatches calls."""

        tool_calls = ev.tool_calls
        await ctx.set("num_tool_calls", len(tool_calls))

        # trigger tool call events
        for tool_call in tool_calls:
            ctx.send_event(ToolCallEvent(tool_call=tool_call))
        
        return None
    
    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """Calls tool."""

        tool_call = ev.tool_call

        # get tool ID and function call
        id_ = tool_call.tool_id

        if self._verbose:
            print(f"Calling function {tool_call.tool_name} with msg {tool_call.tool_kwargs}")

        # call function and put result into a chat message
        tool = self.tools_dict[tool_call.tool_name]
        output = await tool.acall(**tool_call.tool_kwargs)
        msg = ChatMessage(
            name=tool_call.tool_name,
            content=str(output),
            role="tool",
            additional_kwargs={
                "tool_call_id": id_,
                "name": tool_call.tool_name
            }
        )

        return ToolCallEventResult(msg=msg)
    
    @step(pass_context=True)
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> StopEvent | None:
        """Gathers tool calls."""
        # wait for all tool call events to finish.
        tool_events = ctx.collect_events(ev, [ToolCallEventResult] * await ctx.get("num_tool_calls"))
        if not tool_events:
            return None
        
        for tool_event in tool_events:
            # append tool call chat messages to history
            self.chat_history.append(tool_event.msg)
        
        # # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()

    def run_sync(self, message):
        """Synchronous version of run method with custom event loop policy"""
        import asyncio
        import threading

        # Save the original event loop policy
        original_policy = asyncio.get_event_loop_policy()

        try:
            # Create and set a new event loop policy
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

            # Now create a new loop with the fresh policy
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run our async function
            result = loop.run_until_complete(self.run(message=message))

            # Clean up
            loop.close()

            return result
        except Exception as e:
            print(f"Error in run_sync with custom policy: {e}")
            return f"Error: {str(e)}"
        finally:
            # Restore the original event loop policy
            asyncio.set_event_loop_policy(original_policy)

    def reset_chat_history(self):
        """Reset the chat history to a clean state to avoid OpenAI API errors."""
        # Keep only user messages to maintain context without problematic tool calls
        cleaned_history = []
        for msg in self.chat_history:
            if msg.role == "user":
                cleaned_history.append(msg)

        self.chat_history = cleaned_history

# For checking the working condition
async def main():
    wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=300)
    result = await wf.run(message="Which city has the highest population?")
    from IPython.display import display, Markdown

    print(result)

if __name__ == '__main__':
    asyncio.run(main())