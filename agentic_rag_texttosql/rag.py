import os
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from llama_index.core.tools import QueryEngineTool
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Load API Keys
# os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
# os.environ["LLAMA_CLOUD_API_KEY"] = "LLAMA_CLOUD_API_KEY"

# Initialize OpenAI Model
Settings.llm = OpenAI("gpt-3.5-turbo")

# SQL Database Setup
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)

# Insert Data
from sqlalchemy import insert
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

# SQL Query Engine
from llama_index.core.query_engine import NLSQLTableQueryEngine

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, 
    tables=["city_stats"]
)

# Load LlamaCloud Index
index = LlamaCloudIndex(
  name="llama-cloud-index1",
  project_name="Default",
  organization_id="b3288d62-cb4f-42e2-9bc5-63a19c5559ab",
    api_key=os.environ["LLAMA_CLOUD_API_KEY"],
)
llama_cloud_query_engine = index.as_query_engine()

# Create Query Tools
sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
     description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/state of"
        " each city located in the USA."
    ),
    name="sql_tool",
)


cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
llama_cloud_tool = QueryEngineTool.from_defaults(
    query_engine=llama_cloud_query_engine,
     description=(
        f"Useful for answering semantic questions about certain cities in the US."
    ),
    name="llama_cloud_tool",
)


import asyncio
from typing import Dict, List, Any, Optional
from llama_index.core.tools import BaseTool
from llama_index.core.llms import ChatMessage, LLM
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step

class InputEvent(Event): pass
class ToolCallEvent(Event): 
    tool_calls: List[Any]
class ToolCallEventResult(Event): 
    msgs: List[ChatMessage]

class RouterOutputAgentWorkflow(Workflow):
    def __init__(self, tools: List[BaseTool], llm: Optional[LLM] = None, timeout: float = 60):
        super().__init__(timeout=timeout)
        self.tools = {tool.metadata.name: tool for tool in tools}
        self.llm = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.chat_history: List[ChatMessage] = []

    def reset(self):
        """Ensure fresh state for new queries."""
        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        """Prepare chat with user message."""
        message = ev.get("message")
        if not message:
            raise ValueError("Message required.")
        
        self.chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> StopEvent | ToolCallEvent:
        """Call LLM and determine tool usage."""
        chat_res = await self.llm.achat_with_tools(
            list(self.tools.values()), chat_history=self.chat_history
        )
        tool_calls = self.llm.get_tool_calls_from_response(chat_res)

        self.chat_history.append(chat_res.message)
        if not tool_calls:
            return StopEvent(result=chat_res.message.content)

        return ToolCallEvent(tool_calls=tool_calls)

    @step()
    async def call_tools(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """Execute multiple tool calls in parallel."""
        async def call_tool(tool_call):
            tool = self.tools.get(tool_call.tool_name)
            if not tool:
                return ChatMessage(name=tool_call.tool_name, content="Tool not found", role="tool")
            
            output = await tool.acall(**tool_call.tool_kwargs)
            return ChatMessage(name=tool_call.tool_name, content=str(output), role="tool")

        tool_outputs = await asyncio.gather(*[call_tool(tc) for tc in ev.tool_calls])
        return ToolCallEventResult(msgs=tool_outputs)

    @step()
    async def gather(self, ev: ToolCallEventResult) -> StopEvent:
        """Append tool outputs and return response."""
        self.chat_history.extend(ev.msgs)

        # 🔥 Ensure the workflow resets for new queries
        self.reset()
        
        return StopEvent(result="\n".join(msg.content for msg in ev.msgs))

wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], timeout=120)


# Function to process user queries
async def process_query(user_input):
    response = await wf.run(message=user_input)  # Corrected function call
    return (response)
