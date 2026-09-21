import os
import nest_asyncio
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert
)

from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool

from typing import Dict, List, Any, Optional

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
from llama_index.core.tools import FunctionTool


import dotenv
dotenv.load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CLOUD_INDEX_NAME = os.environ.get("CLOUD_INDEX_NAME")
CLOUD_PROJECT_NAME = os.environ.get("CLOUD_PROJECT_NAME")
CLOUD_ORG_ID = os.environ.get("CLOUD_ORG_ID")
CLOUD_API_KEY = os.environ.get("CLOUD_API_KEY")

nest_asyncio.apply()

Settings.llm = OpenAI("gpt-3.5-turbo")

def create_sql_database():
    """Create and populate SQL database, returning the SQL tool"""
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()

    # Create city SQL table
    city_stats_table = Table(
        "city_stats",
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )

    metadata_obj.create_all(engine)

    # Insert data
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]
    
    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)

    # Create SQL database and query engine
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )

    return QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )

index = LlamaCloudIndex(
    name = CLOUD_INDEX_NAME, 
    project_name = CLOUD_PROJECT_NAME,
    organization_id = CLOUD_ORG_ID,
    api_key = CLOUD_API_KEY
)

llama_cloud_query_engine = index.as_query_engine()

cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
llama_cloud_tool = QueryEngineTool.from_defaults(
    query_engine=llama_cloud_query_engine,
    description=(
        f"Useful for answering semantic questions about certain cities in the US."
    ),
    name="llama_cloud_tool"
)

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
        self.llm: LLM = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
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
    

# Run sample query
async def main():
    # Create fresh SQL tool for testing
    sql_tool = create_sql_database()

    # Create workflow with tools
    wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120)

    # Test queries
    result = await wf.run(message="Suggest me some place to visit in Houston.")
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())