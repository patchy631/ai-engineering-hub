import os
import asyncio
import pandas as pd
import nest_asyncio
import streamlit as st
from typing import Dict, List, Any, Optional
import traceback

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    insert
)

from llama_index.core import SQLDatabase, Settings
from llama_index.core.llms import ChatMessage
from llama_index.core.llms.llm import ToolSelection, LLM
from llama_index.core.tools import BaseTool, QueryEngineTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.workflow import (
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    Context,
    step,
)
from llama_index.llms.openai import OpenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Apply nest_asyncio to allow asyncio to work in Streamlit
nest_asyncio.apply()

# Set page config
st.set_page_config(page_title="RAG ⇄ Text-to-SQL Orchestrator Agent", layout="wide")
st.title("RAG ⇄ Text-to-SQL Orchestrator Agent 🤖")

# Define workflow events
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

        toolname = 'RAG tool' if tool_call.tool_name == 'llama_cloud_tool' else 'Text-to-SQL tool'
        
        message_placeholder = st.empty()
        message_placeholder.text(f'🔧 Using {toolname} to find answer..')
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
        message_placeholder.empty()

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

# Function to initialize query engines and tools
def initialize_tools(engine, openai_api_key, llama_api_key):
    """Initialize the SQL and LlamaCloud tools."""
    # Initialize LLM settings
    Settings.llm = OpenAI(api_key=openai_api_key, model="gpt-3.5-turbo")
    
    # Create SQL query engine
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Create LlamaCloud index and query engine
    index = LlamaCloudIndex(
        name="homely-scorpion-2025-03-12", 
        project_name="Default",
        organization_id="af059f26-47ec-4d5a-9f43-9dc9ed3db91c",
        api_key=llama_api_key
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

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "api_keys_submitted" not in st.session_state:
        st.session_state.api_keys_submitted = False
    
    if "openai_api_key" not in st.session_state:
        st.session_state.openai_api_key = ""
    
    if "llama_api_key" not in st.session_state:
        st.session_state.llama_api_key = ""

def render_sidebar():
    """Render the sidebar UI elements."""
    # API key inputs section
    st.sidebar.title("API Keys")
    
    # Form for submitting API keys
    with st.sidebar.form(key="api_key_form"):
        openai_api_key = st.text_input(
            "OpenAI API Key:", 
            type="password",
            value=st.session_state.openai_api_key
        )
        
        llama_api_key = st.text_input(
            "Llama Cloud API Key:", 
            type="password",
            value=st.session_state.llama_api_key
        )
        
        submit_button = st.form_submit_button(label="Submit Keys")
        
        if submit_button:
            st.session_state.openai_api_key = openai_api_key
            st.session_state.llama_api_key = llama_api_key
            st.session_state.api_keys_submitted = True
            st.rerun()

async def process_question(question, wf):
    """Process a question and display the response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": question})
    
    # Display user message
    with st.chat_message("user"):
        st.write(question)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.text("Thinking...")
        
        try:
            with st.spinner():
                result = await wf.run(message=question)
            
            # Extract content and tools
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                # tools_used = result.get("tools_used", [])
            else:
                content = result
                # tools_used = wf.get_tools_used()
            
            # Display content
            message_placeholder.write(content)
            
            # Save message
            st.session_state.messages.append({
                "role": "assistant", 
                "content": content,
                # "tools_used": tools_used
            })
        except Exception as e:
            error_details = traceback.format_exc()
            message_placeholder.error(f"Error: {str(e)}\n{error_details}")

async def main():
    """Main application entry point."""
    try:
        # Initialize session state
        init_session_state()
        

        # """Initialize the SQLite database with city data."""
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
                cursor = connection.execute(stmt)

        with engine.connect() as connection:
            cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
            print(cursor.fetchall())
        
        # Render sidebar
        render_sidebar()
        
        # Main content area
        st.subheader("Ask questions about US cities")
        
        # Check if API keys are provided
        if st.session_state.api_keys_submitted and st.session_state.openai_api_key and st.session_state.llama_api_key:
            # Initialize tools with API keys
            os.environ["OPENAI_API_KEY"] = st.session_state.openai_api_key

            tools = initialize_tools(
                engine, 
                st.session_state.openai_api_key, 
                st.session_state.llama_api_key
            )
            
            wf = RouterOutputAgentWorkflow(
                tools=tools, 
                verbose=True, 
                timeout=120
            )

            st.success("✅ API Key is valid!")
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

            # Clear chat button
            if st.sidebar.button("Clear Chat"):
                st.session_state.messages = []
                st.rerun()

            # Chat input
            if prompt := st.chat_input("Enter your question"):
                await process_question(prompt, wf)
        else:
            # Show message if API keys are not provided
            st.info("Please enter your API keys in the sidebar to start using the application.")
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please check your API keys and try again.")

if __name__ == "__main__":
    asyncio.run(main())