import os
import nest_asyncio
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core.workflow.context import Context
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step
from llama_index.core.base.response.schema import Response
from typing import Dict, List, Any, Optional

# Set up API keys
os.environ["OPENAI_API_KEY"] = "<openai-api-key>"

# Apply nest_asyncio
nest_asyncio.apply()

## Initialize SQL Database
from llama_index.core import SQLDatabase
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert

engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# Define the table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(50), primary_key=True),  # Increased String size
    Column("population", Integer),
    Column("state", String(50), nullable=False),
)

metadata_obj.create_all(engine)

# Insert sample data
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]
with engine.begin() as connection:
    for row in rows:
        connection.execute(insert(city_stats_table).values(**row))

# Ensure SQLDatabase is properly initialized
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["city_stats"]
)


# Create SQL Query Engine
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])

# LlamaCloud settings
LLAMA_CLOUD_API_KEY = "<llama-cloud-api-key>"
LLAMA_CLOUD_ORG_ID = "<llama-cloud-org-id>"

# Create LlamaCloud Index
index = LlamaCloudIndex(
    name="ds-assignment",
    project_name="Default",
    organization_id=LLAMA_CLOUD_ORG_ID,
    api_key=LLAMA_CLOUD_API_KEY
)
llama_cloud_query_engine = index.as_query_engine()

# Create tools
sql_tool = QueryEngineTool.from_defaults(query_engine=sql_query_engine, name="sql_tool")
llama_cloud_tool = QueryEngineTool.from_defaults(query_engine=llama_cloud_query_engine, name="llama_cloud_tool")

# Define Workflow and Event classes
class InputEvent(Event): pass
class GatherToolsEvent(Event): tool_calls: Any
class ToolCallEvent(Event): tool_call: ToolSelection
class ToolCallEventResult(Event): msg: ChatMessage

class RouterOutputAgentWorkflow(Workflow):
    def __init__(self, tools: List[BaseTool], llm: Optional[LLM] = None):
        super().__init__(timeout=300, disable_validation=False, verbose=True)
        self.tools = tools
        self.tools_dict = {tool.metadata.name: tool for tool in self.tools}
        self.llm = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.chat_history = []

    def reset(self):
        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        message = ev.get("message")
        if not message:
            raise ValueError("'message' field is required.")
        self.chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        chat_res = await self.llm.achat_with_tools(self.tools, chat_history=self.chat_history, allow_parallel_tool_calls=True)
        tool_calls = self.llm.get_tool_calls_from_response(chat_res, error_on_no_tool_call=False)
        self.chat_history.append(chat_res.message)
        return GatherToolsEvent(tool_calls=tool_calls) if tool_calls else StopEvent(result=chat_res.message.content)

    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> ToolCallEvent:
        await ctx.set("num_tool_calls", len(ev.tool_calls))
        for tool_call in ev.tool_calls:
            ctx.send_event(ToolCallEvent(tool_call=tool_call))

    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """Calls tool."""

        tool_call = ev.tool_call
        tool = self.tools_dict[tool_call.tool_name]
        
        output = await tool.acall(**tool_call.tool_kwargs)

        msg = ChatMessage(
            name=tool_call.tool_name,
            content=str(output),
            role="tool",
            additional_kwargs={
                "tool_call_id": tool_call.tool_id,  # Ensure tool_call_id is included
                "name": tool_call.tool_name
            }
    )

        return ToolCallEventResult(msg=msg)

    @step(pass_context=True)
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> StopEvent | None:
        tool_events = ctx.collect_events(ev, [ToolCallEventResult] * await ctx.get("num_tool_calls"))
        if tool_events:
            self.chat_history.extend(event.msg for event in tool_events)
            return InputEvent()

# Create workflow instance
wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool])

# Example Queries
async def run_queries():
    queries = [
        # "Which city has the highest population?"
        # "What is the historical name of Los Angeles?"
        "How do people in Chicago get around?"
    ]
    for query in queries:
        result = await wf.run(message=query)
        print(result)

# Run the script if executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_queries())