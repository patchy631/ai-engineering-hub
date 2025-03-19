import os
import nest_asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert,
    text,
)

from llama_index.core import SQLDatabase, Settings
from llama_index.core.tools import BaseTool, QueryEngineTool
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
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert

# Import Groq LLM (alternative to OpenAI)
from llama_index.llms.groq import Groq

# Apply nest_asyncio to allow nested event loops (needed for async in notebooks/Streamlit)
nest_asyncio.apply()

# Load environment variables
load_dotenv()

# Required environment variables:
# - GROQ_API_KEY: API key for Groq
# - LLAMA_CLOUD_API_KEY: API key for LlamaCloud
# - LLAMA_CLOUD_INDEX_NAME: Name of your LlamaCloud index
# - LLAMA_CLOUD_PROJECT_NAME: Name of your LlamaCloud project
# - LLAMA_CLOUD_ORG_ID: Your LlamaCloud organization ID


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
        self.llm: LLM = llm or Groq(temperature=0, model="llama3-70b-8192")
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
            allow_parallel_tool_calls=True,
        )
        tool_calls = self.llm.get_tool_calls_from_response(
            chat_res, error_on_no_tool_call=False
        )

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
            print(
                f"Calling function {tool_call.tool_name} with msg {tool_call.tool_kwargs}"
            )

        # call function and put result into a chat message
        tool = self.tools_dict[tool_call.tool_name]
        output = await tool.acall(**tool_call.tool_kwargs)
        msg = ChatMessage(
            name=tool_call.tool_name,
            content=str(output),
            role="tool",
            additional_kwargs={"tool_call_id": id_, "name": tool_call.tool_name},
        )

        return ToolCallEventResult(msg=msg)

    @step(pass_context=True)
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> StopEvent | None:
        """Gathers tool calls."""
        # wait for all tool call events to finish.
        tool_events = ctx.collect_events(
            ev, [ToolCallEventResult] * await ctx.get("num_tool_calls")
        )
        if not tool_events:
            return None

        for tool_event in tool_events:
            # append tool call chat messages to history
            self.chat_history.append(tool_event.msg)

        # # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()


from sqlalchemy import text  # Add this import at the top


def create_sql_database(db_path="city_stats.db"):
    """Load an existing SQLite database file"""
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    table_name = "city_stats"

    # Verify the table exists and has data
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM city_stats")).fetchall()
        print("Loaded city_stats table contents:", result)

    return engine, table_name


async def setup_hybrid_rag():
    """Setup the hybrid RAG system with SQL and LlamaCloud components"""
    # Set up the LLM (Groq)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")

    llm = Groq(api_key=groq_api_key, model="llama3-70b-8192")
    Settings.llm = llm
    embed_model = HuggingFaceEmbedding(
        model_name="baai/bge-small-en-v1.5",
        token=os.getenv("HUGGINGFACE_API_KEY"),
    )
    Settings.embed_model = embed_model

    # Load the SQL database from file
    engine, table_name = create_sql_database(db_path="city_stats.db")
    sql_database = SQLDatabase(engine, include_tables=[table_name])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database, tables=[table_name]
    )

    # Create LlamaCloud query engine
    llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    llama_cloud_index_name = os.getenv("LLAMA_CLOUD_INDEX_NAME")
    llama_cloud_project_name = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
    llama_cloud_org_id = os.getenv("LLAMA_CLOUD_ORG_ID")

    if not all(
        [
            llama_cloud_api_key,
            llama_cloud_index_name,
            llama_cloud_project_name,
            llama_cloud_org_id,
        ]
    ):
        raise ValueError("All LlamaCloud environment variables are required")

    index = LlamaCloudIndex(
        name=llama_cloud_index_name,
        project_name=llama_cloud_project_name,
        organization_id=llama_cloud_org_id,
        api_key=llama_cloud_api_key,
    )

    llama_cloud_query_engine = index.as_query_engine()

    # Create query engine tools
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

    # Create the workflow
    wf = RouterOutputAgentWorkflow(
        tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120, llm=llm
    )

    return wf


async def query_hybrid_rag(workflow, query):
    """Run a query through the hybrid RAG system"""
    try:
        # Run the workflow with the provided query
        result = await workflow.run(message=query)
        return result
    except Exception as e:
        # Handle any exceptions during the workflow execution
        error_message = f"Error processing query: {str(e)}"
        return error_message
