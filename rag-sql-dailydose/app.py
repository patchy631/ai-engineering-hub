import streamlit as st
import os
import nest_asyncio
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings, SQLDatabase
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core.tools import QueryEngineTool
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from workflow import RouterOutputAgentWorkflow  # Import the workflow from your script
from dotenv import load_dotenv
import google.generativeai as genai
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.core.indices.struct_store.sql_query import NLSQLTableQueryEngine
import asyncio

# Apply nest_asyncio for running in Jupyter or interactive environments
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Get API key from environment
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY environment variable")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Configure Gemini LLM and Embeddings
def configure_gemini():
    llm = Gemini(model="models/gemini-1.5-flash")
    Settings.llm = llm
    embed_model = GeminiEmbedding(model="text-embedding-004")
    Settings.embed_model = embed_model

# Set up SQL database in memory
def setup_sql_database():
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()

    # Define table schema
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )

    # Create the table in memory
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
            stmt = insert(city_stats_table).values(**row)
            connection.execute(stmt)

    return engine

# Create SQL Query Engine
def create_sql_query_engine(engine):
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    return QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description="Query population data for US cities",
        name="sql_tool"
    )

# Connect to LlamaCloud
def connect_to_llama_cloud():
    index = LlamaCloudIndex(
        name=os.environ.get("LLAMA_CLOUD_INDEX_NAME"),
        project_name=os.environ.get("LLAMA_CLOUD_PROJECT_NAME"),
        organization_id=os.environ.get("LLAMA_CLOUD_ORG_ID"),
        api_key=os.environ.get("LLAMA_CLOUD_API_KEY")
    )

    if not all([os.environ.get("LLAMA_CLOUD_INDEX_NAME"), 
                os.environ.get("LLAMA_CLOUD_PROJECT_NAME"),
                os.environ.get("LLAMA_CLOUD_ORG_ID"),
                os.environ.get("LLAMA_CLOUD_API_KEY")]):
        raise ValueError("Missing required LlamaCloud environment variables")

    llama_cloud_query_engine = index.as_query_engine()
    return QueryEngineTool.from_defaults(
        query_engine=llama_cloud_query_engine,
        description="Semantic search for city information",
        name="llama_cloud_tool"
    )

# Initialize workflow
def initialize_workflow():
    engine = setup_sql_database()
    sql_tool = create_sql_query_engine(engine)
    llama_cloud_tool = connect_to_llama_cloud()
    return RouterOutputAgentWorkflow(
        tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120
    )

# Function to run async code
async def get_workflow_response(query):
    wf = initialize_workflow()
    response = await wf.run(message=query)
    return response

def run_async(coroutine):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

# Custom CSS for chat interface
st.markdown("""
<style>
    .chat-container {
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 10px;
        display: flex;
        flex-direction: column;
    }
    .user-container {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
        align-self: flex-end;
        margin-left: 20%;
    }
    .bot-container {
        background-color: #f0f2f5;
        border-left: 5px solid #52c41a;
        align-self: flex-start;
        margin-right: 20%;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    .main-header {
        text-align: center;
        color: #1890ff;
        margin-bottom: 30px;
    }
    .thinking {
        color: #999;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Streamlit UI
st.markdown("<h1 class='main-header'>🌍 CityGPT - AI City Assistant</h1>", unsafe_allow_html=True)

# Display chat messages from history
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"<div class='chat-container user-container'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-container bot-container'><strong>CityGPT:</strong> {message['content']}</div>", unsafe_allow_html=True)

# Add a welcome message if the chat is empty
if len(st.session_state.messages) == 0:
    with st.container():
        st.markdown("""
        <div class='chat-container bot-container'>
            <strong>CityGPT:</strong> Hello! I'm your AI assistant for city information. 
            You can ask me questions about US cities such as:
            <ul>
                <li>What's the population of New York City?</li>
                <li>Which city has the largest population?</li>
                <li>Tell me about cities in California</li>
                <li>Compare the populations of Chicago and Houston</li>
            </ul>
            How can I help you today?
        </div>
        """, unsafe_allow_html=True)

# User input at the bottom of the page
with st.container():
    # Create a form for the chat input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="user_input", placeholder="Ask about US cities...")
        submit_button = st.form_submit_button("Send")

        # Process user input when form is submitted
        if submit_button and user_input.strip():
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Rerun to display the user message immediately
            st.rerun()

# Process the last user message if it exists and hasn't been answered
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    user_query = st.session_state.messages[-1]["content"]
    
    # Show thinking indicator
    with st.container():
        thinking_placeholder = st.markdown("<div class='chat-container bot-container thinking'><strong>CityGPT:</strong> Thinking...</div>", unsafe_allow_html=True)
    
    # Get response from the workflow
    try:
        response = run_async(get_workflow_response(user_query))
        
        # Add bot response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Remove thinking indicator and rerun to show the response
        thinking_placeholder.empty()
        st.rerun()
    except Exception as e:
        # Handle errors gracefully
        error_message = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        thinking_placeholder.empty()
        st.rerun()

# Add a sidebar with additional information
with st.sidebar:
    st.title("About CityGPT")
    st.write("CityGPT combines Gemini's AI capabilities with a city database to provide you with accurate information about US cities.")
    
    st.subheader("Available Data")
    st.write("This demo contains information about:")
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]
    for city in rows:
        st.write(f"• {city['city_name']}, {city['state']}")
    
    st.subheader("Clear Chat")
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()