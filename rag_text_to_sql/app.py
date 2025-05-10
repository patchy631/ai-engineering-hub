import os
import streamlit as st
import asyncio
from typing import Dict, List, Any, Optional
import nest_asyncio
from dotenv import load_dotenv

# Import necessary components from llama_index
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, BaseTool
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
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

load_dotenv()

# Apply nest_asyncio to allow running asyncio in Streamlit
nest_asyncio.apply()

# Set page configuration
st.set_page_config(
    page_title="City Information Assistant Powered by gpt-4o-mini!",
    page_icon="🏙️",
    layout="centered",
)

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Define the workflow events and classes
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
        self.llm: LLM = llm or OpenAI(temperature=0, model="gpt-4o-mini")
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
        try:
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
        except Exception as e:
            # Handle the error gracefully
            error_msg = f"Error during chat: {str(e)}"
            print(error_msg)
            # Return a simple response instead of failing
            return StopEvent(result="I'm sorry, I encountered an issue processing your request. Could you try asking in a different way?")
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
        
        # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()

# Function to setup SQL database
@st.cache_resource
def setup_sql_database():
    from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
    
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()
    
    # create city SQL table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )
    
    metadata_obj.create_all(engine)
    
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
    
    return engine

# Function to setup query engines and tools
@st.cache_resource
def setup_tools():

    # Setup name, organization_id and api_key
    organization_id = os.environ.get("ORG_ID")
    api_key = os.environ.get("API_KEY")
    name = os.environ.get("NAME")

    # Setup SQL query engine
    engine = setup_sql_database()
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Setup LlamaCloud query engine
    index = LlamaCloudIndex(
        name= name, 
        project_name="Default",
        organization_id= organization_id,
        api_key= api_key
    )
    
    llama_cloud_query_engine = index.as_query_engine()
    
    # Create tools
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )
    
    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=llama_cloud_query_engine,
        description=(
            "Useful for answering semantic questions about certain cities in the US."
        ),
        name="llama_cloud_tool"
    )
    
    return [sql_tool, llama_cloud_tool]

# Function to get workflow
@st.cache_resource
def get_workflow():
    tools = setup_tools()
    return RouterOutputAgentWorkflow(tools=tools, verbose=False, timeout=120)

# Function to process user query
async def process_query(query):
    try:
        workflow = get_workflow()
        result = await workflow.run(message=query)
        return result
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request. Please try a different question."

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# App title
st.title("🏙️ City Information Assistant Powered by gpt-4o-mini!")
st.markdown("""
Ask questions about New York City, Los Angeles, Chicago, Houston, Miami, or Seattle.
You can ask about population statistics or general information about these cities.
""")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_query = st.chat_input("Ask a question about US cities...")

if user_query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_query)
    
    # Display assistant response with a thinking indicator
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = asyncio.run(process_query(user_query))
        st.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})