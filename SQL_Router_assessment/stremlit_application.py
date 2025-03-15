import os
import streamlit as st
import nest_asyncio
import asyncio
from typing import Dict, List, Any, Optional

# LlamaIndex imports
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool, BaseTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
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

# SQLAlchemy imports
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert
)

# Apply nest_asyncio to allow asyncio to work in Streamlit
nest_asyncio.apply()

# Set page configuration
st.set_page_config(
    page_title="LlamaCloud SQL Router",
    page_icon="🦙",
    layout="wide"
)

# App title and description
st.title("🦙 LlamaCloud SQL Router")
st.markdown("""
This application combines RAG and Text-to-SQL in a single query interface. 
It can query either a LlamaCloud index for RAG-based retrieval or a SQL database with city information.
""")

# Sidebar for API keys and configuration
with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    llama_cloud_api_key = st.text_input("LlamaCloud API Key", type="password")
    llama_cloud_index_name = st.text_input("LlamaCloud Index Name", value="your-index-name")
    llama_cloud_project = st.text_input("LlamaCloud Project Name", value="Default")
    llama_cloud_org_id = st.text_input("LlamaCloud Organization ID")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This app demonstrates how to create a custom agent that can:
    - Query a SQL database with city population data
    - Query a LlamaCloud index with semantic information about cities
    - Automatically route queries to the appropriate tool
    """)

# Set OpenAI API key
if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
    Settings.llm = OpenAI("gpt-3.5-turbo")
else:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

# Custom workflow classes
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

        # after all tool calls finish, pass input event back, restart agent loop
        return InputEvent()

# Function to set up the SQL database
@st.cache_resource
def setup_sql_database():
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()
    
    # Create city SQL table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
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
    
    return engine, city_stats_table

# Function to create LlamaCloud index
@st.cache_resource
def setup_llama_cloud_index(_llama_cloud_api_key, _llama_cloud_index_name, _llama_cloud_project, _llama_cloud_org_id):
    if not all([_llama_cloud_api_key, _llama_cloud_index_name, _llama_cloud_project, _llama_cloud_org_id]):
        return None
    
    try:
        index = LlamaCloudIndex(
            name=_llama_cloud_index_name,
            project_name=_llama_cloud_project,
            organization_id=_llama_cloud_org_id,
            api_key=_llama_cloud_api_key
        )
        return index
    except Exception as e:
        st.error(f"Error connecting to LlamaCloud: {str(e)}")
        return None

# Function to create the workflow
@st.cache_resource
def create_workflow(sql_tool, llama_cloud_tool=None):
    tools = [sql_tool]
    if llama_cloud_tool:
        tools.append(llama_cloud_tool)
    
    return RouterOutputAgentWorkflow(tools=tools, verbose=True, timeout=120)

# Main application logic
if openai_api_key:
    # Setup SQL database
    engine, city_stats_table = setup_sql_database()
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Create SQL tool
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )
    
    # Setup LlamaCloud index if credentials are provided
    llama_cloud_tool = None
    if all([llama_cloud_api_key, llama_cloud_index_name, llama_cloud_project, llama_cloud_org_id]):
        index = setup_llama_cloud_index(
            llama_cloud_api_key, 
            llama_cloud_index_name, 
            llama_cloud_project, 
            llama_cloud_org_id
        )
        
        if index:
            llama_cloud_query_engine = index.as_query_engine()
            cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
            llama_cloud_tool = QueryEngineTool.from_defaults(
                query_engine=llama_cloud_query_engine,
                description=(
                    f"Useful for answering semantic questions about certain cities in the US."
                ),
                name="llama_cloud_tool"
            )
            st.success("LlamaCloud index connected successfully!")
    
    # Create workflow
    wf = create_workflow(sql_tool, llama_cloud_tool)
    
    # Chat interface
    st.markdown("## Chat Interface")
    
    # Initialize chat history in session state if it doesn't exist
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about cities..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Run the workflow
            try:
                with st.spinner("Processing..."):
                    # Reset workflow chat history to maintain conversation context
                    if len(wf.chat_history) > 0 and wf.chat_history[0].role != "system":
                        wf.reset()
                        # Add system prompt if needed
                        # wf.chat_history.append(ChatMessage(role="system", content="You are a helpful assistant."))
                        
                        # Add previous messages to workflow chat history
                        for msg in st.session_state.messages:
                            if msg["role"] == "user":
                                wf.chat_history.append(ChatMessage(role="user", content=msg["content"]))
                            elif msg["role"] == "assistant":
                                wf.chat_history.append(ChatMessage(role="assistant", content=msg["content"]))
                    
                    # Run workflow
                    result = asyncio.run(wf.run(message=prompt))
                    
                    # Update placeholder with result
                    message_placeholder.markdown(result)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": result})
            except Exception as e:
                message_placeholder.markdown(f"Error: {str(e)}")
                st.error(f"An error occurred: {str(e)}")
    
    # Display available data
    with st.expander("View SQL Database"):
        st.subheader("City Stats Table")
        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM city_stats")
            rows = result.fetchall()
            
            # Create a DataFrame for display
            import pandas as pd
            df = pd.DataFrame(rows, columns=["City", "Population", "State"])
            st.dataframe(df)
    
    # Example queries
    with st.expander("Example Queries"):
        st.markdown("""
        Try asking questions like:
        - Which city has the highest population?
        - What state is Houston located in?
        - Where is the Space Needle located?
        - List all of the places to visit in Miami.
        - How do people in Chicago get around?
        - What is the historical name of Los Angeles?
        - Which cities have a population over 1 million?
        - Compare the populations of New York City and Los Angeles.
        """)
else:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")
