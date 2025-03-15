"""
Router Workflow Module

This module provides the workflow that routes user queries to appropriate tools.
The workflow determines whether to use the SQL tool or the RAG tool based on the
query content, then gathers and returns the results.
"""

from typing import Dict, List, Any, Optional, Union

from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.workflow import (
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
    Context
)
from llama_index.llms.openai import OpenAI

from src.config import get_openai_api_key


class InputEvent(Event):
    """Input event for the workflow."""


class GatherToolsEvent(Event):
    """Event for gathering tool calls."""
    
    tool_calls: Any


class ToolCallEvent(Event):
    """Event for an individual tool call."""
    
    tool_call: ToolSelection


class ToolCallEventResult(Event):
    """Result event from a tool call."""
    
    msg: ChatMessage


class RouterOutputAgentWorkflow(Workflow):
    """
    Router workflow for determining whether to use SQL or RAG.
    
    This workflow:
    1. Takes a user query and determines which tools to call
    2. Dispatches the appropriate tool calls
    3. Gathers the results
    4. Formats and returns the final response
    """
    
    def __init__(
        self,
        tools: List[BaseTool],
        timeout: Optional[float] = 30.0,
        disable_validation: bool = False,
        verbose: bool = False,
        llm: Optional[LLM] = None,
        chat_history: Optional[List[ChatMessage]] = None,
    ):
        """
        Initialize the router workflow.
        
        Args:
            tools: List of tools to use (SQL and RAG tools)
            timeout: Maximum time to wait for a response
            disable_validation: Whether to disable validation
            verbose: Whether to print verbose output
            llm: LLM to use for routing
            chat_history: Initial chat history
        """
        super().__init__(
            timeout=timeout, 
            disable_validation=disable_validation, 
            verbose=verbose
        )
        
        # Store tools as dictionary for easy lookup
        self.tools: List[BaseTool] = tools
        self.tools_dict: Dict[str, BaseTool] = {
            tool.metadata.name: tool for tool in self.tools
        }
        
        # Initialize LLM and chat history
        api_key = get_openai_api_key()
        self.llm: LLM = llm or OpenAI(
            api_key=api_key,
            temperature=0, 
            model="gpt-3.5-turbo"
        )
        self.chat_history: List[ChatMessage] = chat_history or []
    
    def reset(self) -> None:
        """Reset the chat history."""
        self.chat_history = []
    
    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        """
        Prepare the chat by adding the user message to chat history.
        
        Args:
            ev: Start event containing the user message
            
        Returns:
            InputEvent for the next step
            
        Raises:
            ValueError: If message is not provided
        """
        message = ev.get("message")
        if message is None:
            raise ValueError("'message' field is required.")
        
        # Add user message to chat history
        self.chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()
    
    @step()
    async def chat(self, ev: InputEvent) -> Union[GatherToolsEvent, StopEvent]:
        """
        Determine which tools to call based on the user query.
        
        Args:
            ev: Input event
            
        Returns:
            Either GatherToolsEvent with tool calls or StopEvent with direct response
        """
        # Ask LLM to decide which tools to call
        chat_res = await self.llm.achat_with_tools(
            self.tools,
            chat_history=self.chat_history,
            verbose=self._verbose,
            allow_parallel_tool_calls=True
        )
        
        # Get tool calls from LLM response
        tool_calls = self.llm.get_tool_calls_from_response(
            chat_res, 
            error_on_no_tool_call=False
        )
        
        # Add AI message to chat history
        ai_message = chat_res.message
        self.chat_history.append(ai_message)
        
        if self._verbose:
            print(f"Chat message: {ai_message.content}")
        
        # If no tool calls, return direct response
        if not tool_calls:
            return StopEvent(result=ai_message.content)
        
        # Otherwise, return tool calls for processing
        return GatherToolsEvent(tool_calls=tool_calls)
    
    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> ToolCallEvent:
        """
        Dispatch tool calls to be executed.
        
        Args:
            ctx: Workflow context
            ev: GatherToolsEvent with tool calls
            
        Returns:
            ToolCallEvent for the first tool call
        """
        tool_calls = ev.tool_calls
        
        # Store number of tool calls for later use
        await ctx.set("num_tool_calls", len(tool_calls))
        
        # Send events for each tool call after the first one
        for tool_call in tool_calls[1:] if len(tool_calls) > 1 else []:
            ctx.send_event(ToolCallEvent(tool_call=tool_call))
        
        # Return the first tool call event to satisfy the workflow validation
        if tool_calls:
            return ToolCallEvent(tool_call=tool_calls[0])
        else:
            # This should not happen since we've already checked for tool calls in chat()
            return InputEvent()
    
    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """
        Execute a single tool call.
        
        Args:
            ev: ToolCallEvent with tool to call
            
        Returns:
            ToolCallEventResult with the result message
        """
        tool_call = ev.tool_call
        
        # Get tool ID
        id_ = tool_call.tool_id
        
        if self._verbose:
            print(f"Calling function {tool_call.tool_name} with args {tool_call.tool_kwargs}")
        
        # Call the tool and get result
        tool = self.tools_dict[tool_call.tool_name]
        output = await tool.acall(**tool_call.tool_kwargs)
        
        # Format result as chat message
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
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> Union[StopEvent, InputEvent, None]:
        """
        Gather results from all tool calls.
        
        Args:
            ctx: Workflow context
            ev: ToolCallEventResult to gather
            
        Returns:
            InputEvent to continue workflow or None
        """
        # Wait for all tool calls to finish
        num_tool_calls = await ctx.get("num_tool_calls")
        tool_events = ctx.collect_events(ev, [ToolCallEventResult] * num_tool_calls)
        
        if not tool_events:
            return None
        
        # Add all tool results to chat history
        for tool_event in tool_events:
            self.chat_history.append(tool_event.msg)
        
        # After all tool calls finish, pass input event back, restart agent loop
        return InputEvent()

# Alias RouterWorkflow to RouterOutputAgentWorkflow for compatibility with existing code
RouterWorkflow = RouterOutputAgentWorkflow
