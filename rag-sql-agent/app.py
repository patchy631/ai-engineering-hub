import asyncio
import nest_asyncio

# Ensure an event loop exists before applying nest_asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

nest_asyncio.apply()

import streamlit as st
import qdrant_client
import base64
import io
import gc
import uuid
import time
from pathlib import Path
from contextlib import redirect_stdout
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings, StorageContext, SQLDatabase
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sqlalchemy import insert, inspect, create_engine, MetaData, Table, Column, String, Integer
from sqlalchemy.pool import StaticPool
from workflow import RouterOutputAgentWorkflow


# Set up page configuration
st.set_page_config(
    page_title="RAG & Text-to-SQL Agent",
    layout="wide",
)

# Initialize session state variables
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    
if "workflow" not in st.session_state:
    st.session_state.workflow = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "workflow_logs" not in st.session_state:
    st.session_state.workflow_logs = []

session_id = st.session_state.id

system_prompt = """
You MUST follow these rules:
1. You must ALWAYS use tools for factual questions
2. Use sql_tool ONLY for population/state/statistics questions
3. Use semantic_search_tool for other city info
4. Never answer any question directly without tool usage
5. If the question is specifically not related to the context, politely refuse to answer."
"""

@st.cache_resource
def load_llm():
    try:
        llm = Ollama(model="mistral:7b", system_prompt=system_prompt, request_timeout=120.0)
        return llm
    except Exception as e:
        st.error(f"Ollama Error: {str(e)}")
        st.stop()

def reset_chat():
    st.session_state.messages = []
    st.session_state.workflow_logs = []
    st.session_state.workflow = None
    gc.collect()

# SQL Database Initialization
@st.cache_resource
def initialize_sql_database():
    # Use shared in-memory database with connection pooling
    engine = create_engine(
        "sqlite:///file:memdb1?mode=memory&cache=shared",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False}
    )
    metadata_obj = MetaData()

    # Create table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name, 
        metadata_obj,
        Column("city_name", String(16)),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )
    with engine.connect() as conn:
        metadata_obj.create_all(conn)

        # Insert data
        rows = [
            {"city_name": "New York City", "population": 8336000, "state": "New York"},
            {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
            {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
            {"city_name": "Houston", "population": 2303000, "state": "Texas"},
            {"city_name": "Miami", "population": 449514, "state": "Florida"},
            {"city_name": "Seattle", "population": 749256, "state": "Washington"},
            {"city_name": "Mumbai", "population": 12691836, "state": "Maharashtra"},
            {"city_name": "Delhi", "population": 10927986, "state": "Delhi"},
            {"city_name": "Ahmedabad", "population": 3719710, "state": "Gujarat"},
            {"city_name": "Hyderabad", "population": 3597816, "state": "Telangana"},
            {"city_name": "Bengaluru", "population": 5104047, "state": "Karnataka"},
        ]

        for row in rows:
            conn.execute(insert(city_stats_table).values(**row))
        conn.commit()

    return SQLDatabase(engine, include_tables=["city_stats"])

# Document Loading and Vector Store Initialization
@st.cache_data(show_spinner="Loading city knowledge base...")
def initialize_city_data():
    with st.spinner("📂 Loading city documents..."):
        docs_dir = Path("./docs")
        if not docs_dir.exists():
            docs_dir.mkdir()
            st.error("Docs directory not found! Created empty directory.")
            return None

        documents = SimpleDirectoryReader("./docs").load_data()
        if not documents:
            st.error("No documents found in /docs directory!")
            return None

        with st.spinner("🧠 Initializing vector database..."):
            client = qdrant_client.QdrantClient(":memory:")
            # client = qdrant_client.QdrantClient(url="http://localhost:6333", prefer_grpc=True)
            vector_store = QdrantVectorStore(client=client, collection_name="city_docs")
            embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
            
            Settings.embed_model = embed_model
            Settings.llm = load_llm()
            
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            return VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
                show_progress=True
            )

@st.cache_resource
def initialize_workflow(_index, _sql_database):
    with st.spinner("🚀 Starting query engines..."):
        # SQL Query Engine
        sql_context = """The table 'city_stats' contains:
        - city_name (string)
        - population (integer)
        - state (string)
        Use EXACT values from the city_stats table for numerical queries."""
        
        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
            tables=["city_stats"],
            # context=sql_context,
        )

        # Store SQL engine for fallback access
        st.session_state.sql_query_engine = sql_query_engine

        # Semantic Search Engine
        search_query_engine = _index.as_query_engine(
            llm=load_llm(),
        )

        # Define Tools
        sql_tool = QueryEngineTool.from_defaults(
            name="sql_tool",
            description=f"""Useful for translating a natural language query into a SQL query over
                a table containing: city_stats, containing the population/state of cities""",
            query_engine=sql_query_engine,
        )

        semantic_search_tool = QueryEngineTool.from_defaults(
            name="semantic_search_tool",
            description=f"Useful for answering semantic questions about certain cities in the USA and India.",
            query_engine=search_query_engine,
        )

        # Create Workflow
        workflow = RouterOutputAgentWorkflow(
            tools=[sql_tool, semantic_search_tool],
            verbose=True, 
            timeout=120,
            llm=load_llm()
        )
        
        return workflow
    
# Helper Functions
async def run_workflow(query):
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            result = await st.session_state.workflow.run(message=query)
        except Exception as e:
            st.error(f"Query Error: {str(e)}")
            result = f"Could not process query: {str(e)}"
            # Add SQL schema verification
            try:
                inspector = inspect(sql_database.engine)
                tables = inspector.get_table_names()
                st.error(f"Existing tables: {tables}")
            except Exception as db_error:
                st.error(f"Database connection error: {str(db_error)}")

    logs = f.getvalue()
    if logs:
        st.session_state.workflow_logs.append(logs)
    
    return result

# Initialize Components
sql_database = initialize_sql_database()
city_index = initialize_city_data()
if city_index and not st.session_state.workflow:
    st.session_state.workflow = initialize_workflow(city_index, sql_database)

# Sidebar Configuration
with st.sidebar:
    st.header("🌐 City Configuration")
    
    # Supported Cities
    st.subheader("Currently supported Cities")
    predefined_cities = [
        "New York City", "Los Angeles", "Chicago", "Houston",
        "Miami", "Seattle", "Mumbai", "Delhi",
        "Ahmedabad", "Hyderabad", "Bengaluru"
    ]
    
    for city in predefined_cities:
        st.markdown(f"- {city}")
    
    if city_index:
        try:
            doc_cities = [f.stem.replace('_', ' ').title() for f in Path("./docs").glob("*.pdf")]
        except Exception as e:
            st.error(f"Error loading document cities: {str(e)}")
    
    st.divider()
    st.subheader("➕ Add More Cities")
    st.markdown("""
    1. For numerical data:
       - Contact admin to add to SQL database
    2. For general info:
       - Add city PDF files to `/docs` (preferably from wikipedia)
       - Format: `City_Name.pdf`
       - Include sections for history, culture, landmarks
    3. Restart the app
    """)
    
# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown("<h1 style='color: #0066cc;'>🕵️ RAG & Text-to-SQL Agent</h1>", unsafe_allow_html=True)

    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; margin-top: -10px;'>
        <span style='font-size: 28px; color: #666;'>Powered by LlamaIndex
        <img src='data:image/png;base64,{}' width='40'> Qdrant
        <img src='data:image/png;base64,{}' width='40'> Ollama
        <img src='data:image/png;base64,{}' width='40'></span>
    </div>
    """.format(
        base64.b64encode(open("./assets/llamaindex.jpeg", "rb").read()).decode(),
        base64.b64encode(open("./assets/qdrant.png", "rb").read()).decode(),
        base64.b64encode(open("./assets/ollama.png", "rb").read()).decode()
    ), unsafe_allow_html=True)

with col2:
    st.button("Clear chat", on_click=reset_chat)

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! Ask me anything about cities."}
    ]

# Display chat history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
    if message["role"] == "user" and "log_index" in message and i < len(st.session_state.messages) - 1:
        log_index = message["log_index"]
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("View Workflow Execution Logs", expanded=False):
                st.code(st.session_state.workflow_logs[log_index], language="text")

if prompt := st.chat_input("Ask me something about cities..."):
    if not st.session_state.workflow:
        st.error("Workflow not initialized! Check documents and SQL data.")
        st.stop()

    log_index = len(st.session_state.workflow_logs)
    st.session_state.messages.append({"role": "user", "content": prompt, "log_index": log_index})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.workflow:
        with st.spinner("Thinking..."):
            result = asyncio.run(run_workflow(prompt))
        
        st.session_state.messages.append({"role": "assistant", "content": result})
        
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("View Execution Details", expanded=False):
                st.code(st.session_state.workflow_logs[log_index], language="text")
        
        # Display assistant response with streaming
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Stream response word by word
            for chunk in result.split(): 
                full_response += chunk + " "
                time.sleep(0.05)  
                message_placeholder.markdown(full_response + "▌")
                
            # Final display without cursor
            message_placeholder.markdown(full_response)

# Performance Notes
st.sidebar.markdown("---")
st.sidebar.caption("ℹ️ Initial load may take 1-2 minutes for model initialization")