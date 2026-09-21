import os
from typing import Dict, List, Any, Optional

from llama_index.llms.ollama import Ollama
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step, Context
from llama_index.core.base.response.schema import Response
from llama_index.core.tools import FunctionTool
from llama_index.core import Settings

import opik
from llama_index.core import global_handler, set_global_handler



##### Configure Opik (Local) #####


set_global_handler("opik")
opik.configure(use_local=True)
os.environ["OPIK_BASE_URL"] = "http://localhost:5173/api"



##### Define Ollama LLM #####

Settings.llm = Ollama(model="qwen2.5:7b", temperature=0, request_timeout=60.0*5)



##### Custom Workflow #####


### Set Up Various Event of the Workflow ###

class InputEvent(Event):
    """Input event. For every new user message."""

class GatherToolsEvent(Event):
    """Gather Tools Event. Checks if LLM has choosen any tools and gather them."""

    tool_calls: Any

class ToolCallEvent(Event):
    """Tool Call event. Calls the above gathered Tool"""

    tool_call: ToolSelection

class ToolCallEventResult(Event):
    """Tool call event result. Output from the above tool call."""

    msg: ChatMessage


### Set Up Custom Workflow using above events and LLamaIndex WorkFlow ###

class RouterOutputAgentWorkflow(Workflow):
    """
    Accepts user input --> LLM selects none or some tools -->
    tools are collected and run --> tools result are appended
    --> final LLM reply based on all the above appended context
    """

    def __init__(self,
        tools: List[BaseTool],
        timeout: Optional[float] = 60.0*20,
        disable_validation: bool = False,
        verbose: bool = True,
        llm: Optional[LLM] = Ollama(model="qwen2.5:0.5b", temperature=0, request_timeout=60.0*5),
        chat_history: Optional[List[ChatMessage]] = None,
    ):
        """Constructor."""

        super().__init__(timeout=timeout, disable_validation=disable_validation, verbose=verbose)

        self.tools: List[BaseTool] = tools
        self.tools_dict: Optional[Dict[str, BaseTool]] = {tool.metadata.name: tool for tool in self.tools}
        self.llm: LLM = llm
        self.chat_history: List[ChatMessage] = chat_history or []


    def reset(self) -> None:
        """Resets Chat History"""

        self.chat_history = []

    
    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        """
        Receives user query and append them to the Chat History
        """
        
        message = ev.get("message")
        if message is None:
            raise ValueError("'message' field is required.")

        # add msg to chat history
        chat_history = self.chat_history
        chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    
    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        """
        Sends the any new user message to LLM having access to tools.
        Based on user query it selects relevant tool
        """

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
        print(self.chat_history)
        if self._verbose:
            print(f"Chat message: {ai_message.content}")

        # no tool calls, return chat message.
        if not tool_calls:
            return StopEvent(result=ai_message.content)

        return GatherToolsEvent(tool_calls=tool_calls)

    
    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> ToolCallEvent:
        """
        Calls the selected tool and returns their individual output
        """

        tool_calls = ev.tool_calls
        await ctx.set("num_tool_calls", len(tool_calls))

        # trigger tool call events
        for tool_call in tool_calls:
            ctx.send_event(ToolCallEvent(tool_call=tool_call))

        return None

    
    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """
        Calls the selected tool and returns their individual output
        """

        tool_call = ev.tool_call

        # get tool ID and function call
        id_ = tool_call.tool_id

        if self._verbose:
            print(f"Calling function {tool_call.tool_name} with msg {tool_call.tool_kwargs}")

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
        """
        Appends any tool call results from the above function to the chat history.
        Now LLM can reply as per the enhance context provided by those tools.
        """

        # wait for all tool call events to finish.
        tool_events = ctx.collect_events(ev, [ToolCallEventResult] * await ctx.get("num_tool_calls"))
        if not tool_events:
            return None

        for tool_event in tool_events:
            # append tool call chat messages to history
            self.chat_history.append(tool_event.msg)

        # # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()
    

