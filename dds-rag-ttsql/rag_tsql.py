#!/usr/bin/env python
# coding: utf-8

import os
import nest_asyncio
import openai
import asyncio

# Retrieve the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")
nest_asyncio.apply()

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

Settings.llm = OpenAI("gpt-3.5-turbo")

engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# create city SQL table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)

from sqlalchemy import insert

rows = [
    {"city": "New York City", "population": 8336000, "state": "New York"},
    {"city": "Los Angeles", "population": 3822000, "state": "California"},
    {"city": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city": "Houston", "population": 2303000, "state": "Texas"},
    {"city": "Miami", "population": 449514, "state": "Florida"},
    {"city": "Seattle", "population": 749256, "state": "Washington"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

with engine.connect() as connection:
    cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
    print(cursor.fetchall())

# Create a query engine based on SQL database.
from llama_index.core.query_engine import NLSQLTableQueryEngine

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"]
)

# ## LlamaCloud Index
# Create an index and a query engine around the index you've created.
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import logging

# Step 1: Suppress PyPDF2 and other unnecessary logs
logging.getLogger("pypdf").setLevel(logging.ERROR)  # Suppress PyPDF2 warnings
logging.getLogger("llama_index").setLevel(logging.ERROR)  # Suppress llama_index debug/info logs
logging.basicConfig(level=logging.INFO)  # Keep only INFO and above for your app

# Step 1: Define paths and settings
PDF_DIRECTORY = "./pdf"  # Directory containing your 5 PDFs
PERSIST_DIR = "./storage"  # Directory to save the index locally (optional persistence)

# Step 2: Load PDFs from local directory
def load_documents():
    if not os.path.exists(PDF_DIRECTORY):
        os.makedirs(PDF_DIRECTORY)
        raise ValueError(f"Directory {PDF_DIRECTORY} created. Please place your 5 PDFs in this folder and rerun.")
    documents = SimpleDirectoryReader(PDF_DIRECTORY).load_data()
    if not documents:
        raise ValueError(f"No PDFs found in {PDF_DIRECTORY}. Please add your PDFs and rerun.")
    return documents

# Step 3: Set up local embedding model
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Step 4: Create or load the index
def get_or_create_index():
    # Check if the storage directory exists and contains the required files
    if os.path.exists(PERSIST_DIR) and os.path.exists(os.path.join(PERSIST_DIR, "docstore.json")):
        # Load existing index if it exists and is valid
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context, embed_model=embed_model)
        print("Loaded existing index from storage.")
    else:
        # Create a new index from PDFs if no valid index exists
        documents = load_documents()
        index = VectorStoreIndex.from_documents(documents, embed_model=embed_model)
        # Persist the index to disk for reuse
        if not os.path.exists(PERSIST_DIR):
            os.makedirs(PERSIST_DIR)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
        print("Created and saved new index.")
    return index

# Step 5: Initialize the index and query engine
index = get_or_create_index()
local_query_engine = index.as_query_engine()

from llama_index.core.tools import QueryEngineTool

sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over "
        "a table named 'city_stats' with columns: 'city' (string), 'population' (integer), "
        "'state' (string). Use 'city_name' to refer to the city."
    ),
    name="sql_tool"
)

# Step 6: Define the QueryEngineTool for local PDFs
cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
local_pdf_tool = QueryEngineTool.from_defaults(
    query_engine=local_query_engine,
    description=(
        f"Useful for answering semantic questions about content in the local PDFs."
    ),
    name="local_pdf_tool"
)

# ## Creating an Agent Around the Query Engines
# We'll create a workflow that acts as an agent around the two query engines. In this workflow, we need four events:
# 1. `GatherToolsEvent`: Gets all tools that need to be called (which is determined by the LLM).
# 2. `ToolCallEvent`: An individual tool call. Multiple of these events will be triggered at the same time.
# 3. `ToolCallEventResult`: Gets result from a tool call.
# 4. `GatherEvent`: Returned from dispatcher that triggers the `ToolCallEvent`.
#
# This workflow consists of the following steps:
# 1. `chat()`: Appends the message to the chat history. This chat history is fed into the LLM, along with the given tools, and the LLM determines which tools to call. This returns a `GatherToolsEvent`.
# 2. `dispatch_calls()`: Triggers a `ToolCallEvent` for each tool call given in the `GatherToolsEvent` using `send_event()`. Returns a `GatherEvent` with the number of tool calls.
# 3. `call_tool()`: Calls an individual tool. This step will run multiple times if there is more than one tool call. This step calls the tool and appends the result as a chat message to the chat history. It returns a `ToolCallEventResult` with the result of the tool call.
# 4. `gather()`: Gathers the results from all tool calls using `collect_events()`. Waits for all tool calls to finish, then feeds chat history (following all tool calls) into the LLM. Returns the response from the LLM.
from typing import Dict, List, Any, Optional

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
from llama_index.core.base.response.schema import Response
from llama_index.core.tools import FunctionTool

class InputEvent(Event):
    """Input event."""
    pass

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
        print("Chat history sent to OpenAI:")
        for msg in self.chat_history:
            content = msg.content if msg.content is not None else "[No content]"
            print(f"{msg.role}: {content[:50]}...")
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
        id_ = tool_call.tool_id
        if self._verbose:
            print(f"Calling function {tool_call.tool_name} with msg {tool_call.tool_kwargs}")
        # Attempt to call the tool, handle any exceptions
        try:
            tool = self.tools_dict[tool_call.tool_name]
            output = await tool.acall(**tool_call.tool_kwargs)
            content = str(output)
        except Exception as e:
            content = f"Error: {str(e)}"  # Provide error info if tool call fails
        # Create tool response message, even on failure
        msg = ChatMessage(
            name=tool_call.tool_name,
            content=content,
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
        # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()

wf = RouterOutputAgentWorkflow(tools=[sql_tool, local_pdf_tool], verbose=True, timeout=120)

async def get_agent_response(query):
    """Asynchronously run the agent workflow with the given query."""
    try:
        result = await wf.run(message=query)
        return str(result)  # Convert result to string for Streamlit
    except Exception as e:
        return f"Error: {str(e)}"

def get_response(message: str) -> str:
    """Synchronously fetches the response by running the async function."""
    return asyncio.run(get_agent_response(message))