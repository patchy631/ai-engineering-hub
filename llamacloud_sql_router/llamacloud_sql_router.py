#!/usr/bin/env python


import asyncio
import streamlit as st

import logging
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")



import nest_asyncio

nest_asyncio.apply()



# setup Arize Phoenix for logging/observability
import llama_index.core
import os

PHOENIX_API_KEY = os.getenv("ARIZE_PHOENIX_API_KEY")
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
llama_index.core.set_global_handler(
    "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
)



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
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)



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
# 
# Create an index and a query engine around the index you've created.


from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

index = LlamaCloudIndex(
    name="yummy-meerkat-2025-03-05", 
    project_name="Default",
    organization_id="a17977ff-6c02-4b74-ab89-2e2396d01310",
    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
    timeout=30
)

llama_cloud_query_engine = index.as_query_engine()


# Create a query engine tool around these query engines.


from llama_index.core.tools import QueryEngineTool

sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/state of"
        " each city located in the USA."
    ),
    name="sql_tool"
)

cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
llama_cloud_tool = QueryEngineTool.from_defaults(
    query_engine=llama_cloud_query_engine,
    description=(
        f"Useful for answering semantic questions about certain cities in the US."
    ),
    name="llama_cloud_tool"
)


# ## Creating an Agent Around the Query Engines
# 
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
    Context
)
from llama_index.core.base.response.schema import Response
from llama_index.core.tools import FunctionTool


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


# Create the workflow instance.


logging.getLogger("llama_index").setLevel(logging.ERROR)  # Hide LlamaIndex logs
logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Hide asyncio warnings
logging.getLogger("streamlit").setLevel(logging.ERROR)   # Hide Streamlit warnings

wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120)


# #### Visualize Workflow





from llama_index.utils.workflow import draw_all_possible_flows

# ## Example Queries


# Ensure your workflow is properly defined
async def run_workflow(query_text):
    """Run the async workflow properly."""
    try:
        # Pass the query as a message parameter in a dictionary
        result = await wf.run(message=query_text)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {str(e)}"

# Define the Streamlit UI
st.title("Combining RAG and Text-to-SQL")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Import image handling
from PIL import Image
import os
import base64

# Function to convert image to base64 for inline display
def get_image_as_base64(image_path):
    if not os.path.exists(image_path):
        return ""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Define image paths for icons (adjust these paths to your actual images)
USER_ICON = "user_icon.png"  # Replace with your user icon path
AI_ICON = "ai_icon.png"      # Replace with your AI icon path
QUERY_ICON = "query_icon.png"  # Replace with your query icon path

# Add global CSS for disabled text areas to show normal cursor
st.markdown(
    """
    <style>
    /* Fix cursor for disabled text areas to show normal text cursor instead of "not-allowed" */
    .stTextArea textarea:disabled {
        cursor: text !important;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

# Display chat history
for message in st.session_state.chat_history:
    col1, col2 = st.columns([1, 10])
    
    with col1:
        if message['role'] == 'user':
            if os.path.exists(USER_ICON):
                st.image(USER_ICON, width=50)
            else:
                st.markdown("👤")
        else:
            if os.path.exists(AI_ICON):
                st.image(AI_ICON, width=50)
            else:
                st.markdown("🤖")
    
    with col2:
        # Get message index for truly unique keys
        msg_idx = st.session_state.chat_history.index(message)
        
        # Calculate appropriate height based on content
        # Count newlines and estimate chars per line for word wrapping
        lines = message['content'].split('\n')
        # Base height + line count + extra space for word wrapping based on content length
        content_len = sum(len(line) for line in lines)
        line_estimate = max(1, len(lines) + (content_len // 50))  # Assume ~50 chars per line before wrapping
        # Ensure minimum 68px height (Streamlit requirement) with 24px per line
        height = max(68, 20 + (line_estimate * 24))
        
        if message['role'] == 'user':
            st.text_area("User message", message['content'], disabled=True, label_visibility="hidden", 
                        key=f"user_{msg_idx}", height=height)
        else:
            st.text_area("AI response", message['content'], disabled=True, label_visibility="hidden", 
                        key=f"ai_{msg_idx}", height=height)

# Initialize key counter if not exists
if 'form_key' not in st.session_state:
    st.session_state.form_key = 0

# Create a form with a unique key that changes on each submission to force reset
form_key = f"query_form_{st.session_state.form_key}"
with st.form(key=form_key):
    # Use a direct empty string for the input
    query = st.text_input("Enter your query:", key=f"query_input_{st.session_state.form_key}")
    
    # Split into input and button columns
    input_col, button_col = st.columns([10, 1])
    
    # Place submit button in button column
    with button_col:
        if os.path.exists(QUERY_ICON):
            # Get base64 image for embedded use
            query_icon_b64 = get_image_as_base64(QUERY_ICON)
            
            # Create a unique key for this button instance
            button_id = str(id(query_icon_b64))[-6:]
            
            # Create button with an arrow emoji
            submit_button = st.form_submit_button(label="➡️")
            
            # Style the button to be compact
            st.markdown(
                """
                <style>
                /* Make the button compact */
                form div.row-widget.stButton > button {
                    width: 40px !important;
                    height: 40px !important;
                    padding: 0 !important;
                    min-width: unset !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                
                /* Make the emoji slightly larger */
                form div.row-widget.stButton > button span {
                    font-size: 20px !important;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )
        else:
            # Fallback to text button
            submit_button = st.form_submit_button("Send")

if submit_button and query.strip():  # Only process if there's actual query content
    try:
        # Add user query to chat history
        st.session_state.chat_history.append({'role': 'user', 'content': query})
        
        # Create and set an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the workflow and get the result
        result = loop.run_until_complete(run_workflow(query))
        
        # Display the result and save to chat history
        if result:
            st.session_state.chat_history.append({'role': 'assistant', 'content': result})
        else:
            st.error("No result returned from the workflow.")
        
        # Increment the form key to force a new form with empty input on next render
        st.session_state.form_key += 1
        
        # Force a rerun to create a new form and update chat history
        st.rerun()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")






