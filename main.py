import asyncio
import nest_asyncio
from sqlalchemy import Float, insert
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
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
from llama_index.core.tools import FunctionTool, QueryEngineTool
from dotenv import load_dotenv
import os
import csv
import streamlit as st

# Load environment variables
load_dotenv()

# Apply nest_asyncio to allow multiple event loop runs
nest_asyncio.apply()

def workflow(engine):
    Settings.llm = OpenAI("gpt-3.5-turbo")

    # Define the path to the CSV file inside the data directory
    csv_file_name = next((f for f in os.listdir('data') if f.endswith('.csv')), None)
    if not csv_file_name:
        raise FileNotFoundError("No CSV file found in the 'data' directory.")

    csv_file_path = os.path.join('data', csv_file_name)

    # Create SQLAlchemy metadata object
    metadata_obj = MetaData()

    # Read CSV to infer column types
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        columns = []
        first_row = next(reader)  # Read first row for type inference

        for column_name in reader.fieldnames:
            sample_value = first_row[column_name]
            if sample_value.isdigit():
                column_type = Integer
            else:
                try:
                    float(sample_value)
                    column_type = Float
                except ValueError:
                    column_type = String(50)
            columns.append(Column(column_name, column_type))

    table_name = "input_tables"
    input_tables = Table(
        table_name,
        metadata_obj,
        *columns
    )

    metadata_obj.create_all(engine)

    # Insert data into the SQL table
    rows = [first_row] + [row for row in reader]  # Include first row again
    with engine.begin() as connection:
        connection.execute(insert(input_tables), rows)

    # Debugging: Print table contents
    with engine.connect() as connection:
        cursor = connection.exec_driver_sql(f"SELECT * FROM {table_name}")
        print(cursor.fetchall())

    # Initialize SQLDatabase and Query Engine
    sql_database = SQLDatabase(engine, include_tables=[table_name])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=[table_name]
    )

    # Llama Cloud Index (Fix: Remove tuple assignment)
    LLAMA_CLOUD_INDEX_NAME = os.getenv("LLAMA_CLOUD_INDEX_NAME")
    LLAMA_CLOUD_PROJECT_NAME = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
    LLAMA_CLOUD_ORGANIZATION_ID = os.getenv("LLAMA_CLOUD_ORGANIZATION_ID")
    LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

    index = LlamaCloudIndex(
        name=LLAMA_CLOUD_INDEX_NAME,
        project_name=LLAMA_CLOUD_PROJECT_NAME,
        organization_id=LLAMA_CLOUD_ORGANIZATION_ID,
        api_key=LLAMA_CLOUD_API_KEY
    )

    llama_cloud_query_engine = index.as_query_engine()

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

        def __init__(self, tools: List[BaseTool], timeout: Optional[float] = 10.0,
                     disable_validation: bool = False, verbose: bool = False,
                     llm: Optional[LLM] = None, chat_history: Optional[List[ChatMessage]] = None):
            super().__init__(timeout=timeout, disable_validation=disable_validation, verbose=verbose)

            self.tools: List[BaseTool] = tools
            self.tools_dict: Dict[str, BaseTool] = {tool.metadata.name: tool for tool in self.tools}
            self.llm: LLM = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
            self.chat_history: List[ChatMessage] = chat_history or []

        def reset(self) -> None:
            """Resets Chat History"""
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
            """Processes user query and determines tool calls."""
            chat_res = await self.llm.achat_with_tools(
                self.tools,
                chat_history=self.chat_history,
                verbose=self._verbose,
                allow_parallel_tool_calls=True
            )
            tool_calls = self.llm.get_tool_calls_from_response(chat_res, error_on_no_tool_call=False)

            ai_message = chat_res.message
            self.chat_history.append(ai_message)

            if not tool_calls:
                return StopEvent(result=ai_message.content)

            return GatherToolsEvent(tool_calls=tool_calls)

        @step(pass_context=True)
        async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> None:
            """Dispatches tool calls."""
            tool_calls = ev.tool_calls
            await ctx.set("num_tool_calls", len(tool_calls))

            for tool_call in tool_calls:
                ctx.send_event(ToolCallEvent(tool_call=tool_call))

        @step()
        async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
            """Executes tool call."""
            tool = self.tools_dict[ev.tool_call.tool_name]
            output = await tool.acall(**ev.tool_call.tool_kwargs)

            return ToolCallEventResult(
                msg=ChatMessage(
                    name=ev.tool_call.tool_name,
                    content=str(output),
                    role="tool",
                    additional_kwargs={"tool_call_id": ev.tool_call.tool_id}
                )
            )

    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description="Useful for translating a natural language query into SQL.",
        name="sql_tool"
    )
    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=llama_cloud_query_engine,
        description="Useful for answering semantic questions about certain cities.",
        name="llama_cloud_tool"
    )

    return RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120)

async def main(query: str, engine) -> str:
    agent = workflow(engine)
    sql_query = await agent.run(message=query)
    return sql_query

if __name__ == "__main__":
    engine = create_engine("sqlite:///:memory:", future=True)
    asyncio.run(main("What is the population of New York City?", engine))
