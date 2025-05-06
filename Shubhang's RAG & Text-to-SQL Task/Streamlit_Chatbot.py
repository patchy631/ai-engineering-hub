import streamlit as st
import os
import nest_asyncio
import time
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, inspect

# Import from llama_index with correct module paths
import llama_index.core
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool

# Import API keys
from config import OPENAI_API_KEY, PHOENIX_API_KEY, LLAMA_CLOUD_API_KEY, LLAMA_ORGANIZATION_ID, LLAMA_NAME

# Set environment variables
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
os.environ["PHOENIX_API_KEY"] = PHOENIX_API_KEY
os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_CLOUD_API_KEY

# Setup Phoenix for logging/observability
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"
llama_index.core.set_global_handler(
    "arize_phoenix", endpoint="https://llamatrace.com/v1/traces"
)

# Apply nest_asyncio to allow nested asyncio event loops
nest_asyncio.apply()

# Configure page
st.set_page_config(
    page_title="City Explorer - RAG Text-to-SQL",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E88E5;
        margin-bottom: 20px;
        text-align: center;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #64B5F6;
        font-weight: 600;
        margin-top: 1rem;
    }
    .app-description {
        text-align: center;
        margin-bottom: 20px;
    }
    .stDataFrame {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# App header with larger, more visible styling
st.markdown('<h1 class="main-header">🏙️ City Explorer: RAG & Text-to-SQL Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-description">This application combines SQL database queries with semantic search to answer questions about cities. Ask about city statistics or general knowledge questions about US cities!</p>', unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
    
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    
if 'engine' not in st.session_state:
    st.session_state.engine = None
    
if 'sql_query_engine' not in st.session_state:
    st.session_state.sql_query_engine = None
    
if 'llama_cloud_query_engine' not in st.session_state:
    st.session_state.llama_cloud_query_engine = None

# Setup database and tools
def initialize_resources():
    # Set OpenAI as the default LLM
    Settings.llm = OpenAI("gpt-4o-mini")
    
    # Create file-based SQLite database
    db_path = os.path.join(os.path.dirname(__file__), "city_stats.db")
    engine = create_engine(f"sqlite:///{db_path}", future=True)
    metadata_obj = MetaData()
    
    # Create city_stats table if it doesn't exist
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )
    
    # Use inspect to check if table exists
    inspector = inspect(engine)
    if not inspector.has_table(table_name):
        metadata_obj.create_all(engine)
        
        # Insert data into the table
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
    
    # Create SQL query engine
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Create LlamaCloud index using config variables
    index = LlamaCloudIndex(
        name=LLAMA_NAME,
        project_name="Default",
        organization_id=LLAMA_ORGANIZATION_ID,
        api_key=LLAMA_CLOUD_API_KEY
    )
    
    llama_cloud_query_engine = index.as_query_engine()
    
    return sql_query_engine, llama_cloud_query_engine, engine

# Initialize with loading spinner
with st.spinner("Setting up the city database and knowledge base..."):
    if not st.session_state.initialized:
        sql_query_engine, llama_cloud_query_engine, engine = initialize_resources()
        st.session_state.sql_query_engine = sql_query_engine
        st.session_state.llama_cloud_query_engine = llama_cloud_query_engine
        st.session_state.engine = engine
        st.session_state.initialized = True

# Function to process the user's question
def process_question(question):
    if not question.strip():
        return
    
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": question})
    
    # Determine which tool to use
    if any(keyword in question.lower() for keyword in ["population", "highest", "lowest", "how many", "statistics"]):
        with st.spinner("Querying city database..."):
            response = st.session_state.sql_query_engine.query(question)
            tool_used = "SQL Database"
    else:
        with st.spinner("Searching knowledge base..."):
            response = st.session_state.llama_cloud_query_engine.query(question)
            tool_used = "Semantic Search"
    
    # Add assistant response to chat history
    response_text = str(response)
    st.session_state.chat_history.append({"role": "assistant", "content": response_text, "tool": tool_used})

# Create main layout
col1, col2 = st.columns([3, 2])  # Adjust ratio to give more space to chat

with col1:
    st.markdown('<p class="sub-header">Chat with City Explorer</p>', unsafe_allow_html=True)
    
    # Use chat_input which handles Enter key presses automatically
    user_question = st.chat_input("Ask a question about US cities:")
    
    if user_question:
        process_question(user_question)
    
    # Display "Conversation History" heading
    st.markdown("### Conversation History")
    
    # Display chat messages in reverse order (newest first)
    for message_pair in reversed(list(zip(st.session_state.chat_history[::2], st.session_state.chat_history[1::2]))):
        user_message = message_pair[0]
        assistant_message = message_pair[1]
        
        # Display the user message
        with st.chat_message("user"):
            st.write(user_message["content"])
        
        # Display the assistant message
        with st.chat_message("assistant"):
            st.write(assistant_message["content"])
            if "tool" in assistant_message:
                st.caption(f"Tool used: {assistant_message['tool']}")
        
        # Add a separator between conversation pairs
        st.markdown("---")

with col2:
    st.markdown('<p class="sub-header">City Database</p>', unsafe_allow_html=True)
    
    # Display database content
    try:
        with st.session_state.engine.connect() as connection:
            cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
            results = cursor.fetchall()
            
            # Create a DataFrame for display
            df = pd.DataFrame(results, columns=["City", "Population", "State"])
            st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error accessing database: {e}")
    
    st.markdown('<p class="sub-header">Example Questions</p>', unsafe_allow_html=True)
    st.markdown("""
    - Which city has the highest population?
    - What state is Houston located in?
    - Where is the Space Needle located?
    - List places to visit in Miami.
    - How do people in Chicago get around?
    - What is the historical name of Los Angeles?
    """)
    
    # Add tool information in a dropdown
    st.markdown('<p class="sub-header">How It Works</p>', unsafe_allow_html=True)
    with st.expander("Click to learn more about the tools"):
        st.markdown("""
        This app uses two powerful tools:
        
        **SQL Tool**: Answers questions about city statistics by querying a database containing information about population and state for major US cities.
        
        **Semantic Search Tool**: Answers general knowledge questions about US cities using LlamaCloud's semantic search capabilities.
        
        The app automatically selects the appropriate tool based on your question!
        """)

# Add footer
st.markdown("---")
st.markdown("Built with Streamlit, LlamaIndex, and OpenAI")