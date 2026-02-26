import streamlit as st
import os
from typing import Dict, List, Any, Optional
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (critical for Streamlit's environment)
nest_asyncio.apply()

# Handle NumPy/Pandas/SciPy dependency issues
try:
    import pandas as pd
except Exception as e:
    st.error(f"Error with dependencies: {e}")
    st.stop()

# Imports for LlamaIndex and SQL
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, text
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
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

# Threading imports
from threading import Lock

# Create a thread lock for SQLite operations
db_lock = Lock()

# Set page configuration
st.set_page_config(
    page_title="RAG and SQL Router Agent",
    page_icon="🤖",
    layout="wide"
)

# App title and description
st.title("Combining RAG and Text-to-SQL in a Single Query Interface")
st.markdown("""
This app demonstrates a custom agent that can query either a LlamaCloud index for RAG-based retrieval 
or a SQL database as a tool. The example uses Wikipedia pages of US cities and a SQL database 
of their populations and states.

**NOTE**: Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk.
""")

# Show image if available
try:
    st.image("llamacloud_sql_router_img.png", use_container_width=True)
except:
    st.warning("Image file not found. The diagram is not displayed.")

# API Key input section
with st.sidebar:
    st.header("LlamaCloud Settings")
    llama_index_name = st.text_input("Index Name")
    llama_project_name = st.text_input("Project Name")
    llama_org_id = st.text_input("Organization ID")
    llama_api_key = st.text_input("LlamaCloud API Key", type="password")   
    st.caption("Note: You need to create a LlamaCloud index with uploaded PDFs of Wikipedia pages on US cities.")
    st.divider()

    st.header("API Keys")
    openai_api_key = st.text_input("OpenAI API Key", type="password")

    


# Check for OpenAI API key
if not openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = openai_api_key
Settings.llm = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")

@st.cache_resource(show_spinner=False)
def initialize_database():
    """Initialize the database and create query engines."""
    # Create a connection to SQLite database with check_same_thread=False
    engine = create_engine(
        "sqlite:///:memory:", 
        future=True,
        connect_args={"check_same_thread": False}  # Allow cross-thread usage
    )
    
    # Initialize the database
    init_db(engine)
    
    # Create SQL query engine
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    return engine, sql_query_engine

def init_db(engine):
    """Initialize the database with the city_stats table and data."""
    with db_lock:
        with engine.begin() as conn:
            # Create table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS city_stats (
                    city_name VARCHAR(16) PRIMARY KEY,
                    population INTEGER,
                    state VARCHAR(16) NOT NULL
                )
            """))
            
            # Insert data
            data = [
                {"city_name": "New York City", "population": 8336000, "state": "New York"},
                {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                {"city_name": "Miami", "population": 449514, "state": "Florida"},
                {"city_name": "Seattle", "population": 749256, "state": "Washington"},
            ]
            
            for row in data:
                conn.execute(
                    text("INSERT OR REPLACE INTO city_stats (city_name, population, state) VALUES (:city_name, :population, :state)"),
                    row
                )

# Initialize database once
if 'db_engine' not in st.session_state:
    try:
        st.session_state.db_engine, st.session_state.sql_query_engine = initialize_database()
    except Exception as e:
        st.error(f"Error initializing database: {str(e)}")
        st.stop()


# Create SQL tool
sql_tool = QueryEngineTool.from_defaults(
    query_engine=st.session_state.sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/state of"
        " each city located in the USA. ONLY use this tool for questions about"
        " population statistics or which state a city is in."
    ),
    name="sql_tool"
)

# Initialize tools list with SQL tool
tools = [sql_tool]

# Add LlamaCloud tool if credentials are valid
llama_cloud_credentials_valid = False
if llama_index_name and llama_project_name and llama_org_id and llama_api_key:
    try:
        llama_cloud_index = LlamaCloudIndex(
            name=llama_index_name,
            project_name=llama_project_name,
            organization_id=llama_org_id,
            api_key=llama_api_key
        )
        
        llama_cloud_query_engine = llama_cloud_index.as_query_engine(
            similarity_top_k=3,
            response_mode="compact"
        )
        
        llama_cloud_tool = QueryEngineTool.from_defaults(
            query_engine=llama_cloud_query_engine,
            description=(
                "Useful for answering semantic questions about cities in the US."
                " Use this for questions about landmarks (like Space Needle), attractions,"
                " history, culture, transportation, or any information that isn't about" 
                " population numbers or state location."
            ),
            name="llama_cloud_tool"
        )
        
        tools.append(llama_cloud_tool)
        llama_cloud_credentials_valid = True
    except Exception as e:
        st.sidebar.error(f"Error connecting to LlamaCloud: {e}")

# Define router workflow classes
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
        # Important: disable validation during development to avoid errors about events
        super().__init__(timeout=timeout, disable_validation=True, verbose=verbose) 
        
        self.tools: List[BaseTool] = tools
        self.tools_dict: Dict[str, BaseTool] = {tool.metadata.name: tool for tool in self.tools}
        self.llm: LLM = llm or OpenAI(temperature=0, model="gpt-3.5-turbo")
        self.chat_history: List[ChatMessage] = chat_history or []

    def reset(self) -> None:
        """Resets Chat History"""
        self.chat_history = []

    @step()
    async def prepare_chat(self, ev: StartEvent) -> InputEvent:
        message = getattr(ev, "message", None)
        if message is None:
            raise ValueError("'message' field is required.")

        # message = ev.get("message")
        # if message is None:
        #     raise ValueError("'message' field is required.")
        
        # add msg to chat history
        self.chat_history = []  # Make sure to clear history
        self.chat_history.append(ChatMessage(role="user", content=message))
        return InputEvent()

    @step()
    async def chat(self, ev: InputEvent) -> GatherToolsEvent | StopEvent:
        """Appends msg to chat history, then gets tool calls."""
        try:
            # Put msg into LLM with tools included
            chat_res = await self.llm.achat_with_tools(
                self.tools,
                chat_history=self.chat_history,
                verbose=self._verbose
            )
            tool_calls = self.llm.get_tool_calls_from_response(chat_res, error_on_no_tool_call=False)
            
            ai_message = chat_res.message
            self.chat_history.append(ai_message)
            if self._verbose:
                print(f"Chat message: {ai_message.content}")

            # no tool calls, return chat message.
            if not tool_calls:
                return StopEvent(result=ai_message.content or "I don't have an answer for that.")

            return GatherToolsEvent(tool_calls=tool_calls)
        except Exception as e:
            print(f"Error in chat step: {str(e)}")
            return StopEvent(result=f"Error: {str(e)}")

    @step(pass_context=True)
    async def dispatch_calls(self, ctx: Context, ev: GatherToolsEvent) -> None:
        """Dispatches calls."""
        try:
            tool_calls = ev.tool_calls
            await ctx.set("num_tool_calls", len(tool_calls))

            # trigger tool call events
            for tool_call in tool_calls:
                ctx.send_event(ToolCallEvent(tool_call=tool_call))
            
            return None
        except Exception as e:
            print(f"Error in dispatch_calls step: {str(e)}")
            return None
    
    @step()
    async def call_tool(self, ev: ToolCallEvent) -> ToolCallEventResult:
        """Calls tool."""
        try:
            tool_call = ev.tool_call

            # get tool ID and function call
            id_ = tool_call.tool_id
            if self._verbose:
                print(f"Calling function {tool_call.tool_name} with input {tool_call.tool_kwargs}")
            with db_lock:  # Use lock for database 
                # Ensure the tool exists
                tool = self.tools_dict.get(tool_call.tool_name)
                if not tool:
                    raise ValueError(f"Tool '{tool_call.tool_name}' not found.")
                
                # call function and put result into a chat message
                output = await tool.acall(**tool_call.tool_kwargs)
                print("output => ", output)
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
        except Exception as e:
            print(f"Error in call_tool: {str(e)}", e)
            # Still need to return something
            msg = ChatMessage(
                name="error",
                content=f"Error in tool execution: {str(e)}",
                role="tool",
                additional_kwargs={"tool_call_id": id_}
            )
            return ToolCallEventResult(msg=msg)
    
    @step(pass_context=True)
    async def gather(self, ctx: Context, ev: ToolCallEventResult) -> StopEvent:
        """Gathers tool calls."""
        try:
            # wait for all tool call events to finish.
            num_tool_calls = await ctx.get("num_tool_calls")
            
            # Just add the current event to a list instead of using collect_events
            tool_events = [ev]
            
            if not tool_events:
                return StopEvent(result="No tool results were obtained. Please try again.")
            
            for tool_event in tool_events:
                # append tool call chat messages to history
                self.chat_history.append(tool_event.msg)
            
            # Get the final response
            chat_res = await self.llm.achat(messages=self.chat_history)
            self.chat_history.append(chat_res.message)
            
            return StopEvent(result=chat_res.message.content)
        except Exception as e:
            print(f"Error in gather step: {str(e)}")
            return StopEvent(result=f"Error gathering results: {str(e)}")
        
    async def run(self, message: str) -> str:
        """Run the workflow with a message."""
        try:
            wf_output = await super().run(message=message)
            if isinstance(wf_output, str):
                return wf_output
            return wf_output.get("result", "No result was returned from the workflow.")
        except Exception as e:
            return f"Error in workflow: {str(e)}"

# Initialize the workflow
if 'agent_workflow' not in st.session_state or st.session_state.get('last_api_key') != openai_api_key:
    llm = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)
    st.session_state.agent_workflow = RouterOutputAgentWorkflow(
        tools=tools, 
        verbose=True, 
        timeout=60,
        llm=llm
    )
    st.session_state.last_api_key = openai_api_key
    print("st.session_state.agent_workflow => ", st.session_state.agent_workflow)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat interface
st.header("Ask Questions About US Cities")

# Display example questions
if not llama_cloud_credentials_valid:
    st.warning("LlamaCloud credentials not provided. Only SQL queries about city population and state will be available.")
    st.markdown("""
    Example questions:
    - Which city has the highest population?
    - What state is Houston located in?
    - How many people live in Chicago?
    """)
else:
    st.markdown("""
    Example questions:
    - Which city has the highest population? (SQL)
    - What state is Houston located in? (SQL)
    - Tell me about attractions in New York City (RAG)
    - What is the Space Needle? (RAG)
    - How do people in Chicago get around? (RAG)
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about US cities..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.info("Processing query...")
        
        try:
            async def process_query():
                # Reset workflow chat history but maintain the query
                st.session_state.agent_workflow.reset()
                return await st.session_state.agent_workflow.run(message=prompt)
            
            with st.spinner("Thinking..."):
                # Run the query with better error handling
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(process_query())
                    loop.close()
                    
                    if result:
                        message_placeholder.markdown(result)
                        st.session_state.messages.append({"role": "assistant", "content": result})
                    else:
                        message_placeholder.error("No response generated. Please try again.")
                        st.session_state.messages.append({"role": "assistant", "content": "No response generated. Please try again."})
                except Exception as e:
                    message_placeholder.error(f"Error processing query: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error processing query: {str(e)}"})
        except Exception as e:
            error_message = f"Error: {str(e)}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})

# Display database contents with thread safety
with st.expander("View SQL Database Contents"):
    try:
        # Ensure database is initialized
        
        with db_lock, st.session_state.db_engine.connect() as connection:
            # Verify table exists
            result = connection.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='city_stats'"
            ))
            if not result.fetchone():
                # Try to reinitialize the database
                init_db(st.session_state.db_engine)
            
            # Query the table
            result = connection.execute(text("SELECT * FROM city_stats"))
            rows = result.fetchall()
            df = pd.DataFrame(rows, columns=["city_name", "population", "state"])
            st.dataframe(df)
    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        # Try to reinitialize the database
        try:
            init_db(st.session_state.db_engine)
            # st.experimental_rerun()
        except Exception as e2:
            st.error(f"Failed to reinitialize database: {str(e2)}")
