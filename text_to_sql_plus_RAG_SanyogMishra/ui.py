import streamlit as st
import sqlite3
import pandas as pd
import time
import sys
import atexit
from sqlalchemy import inspect, text
from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from llama_index.core import Settings, SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import QueryEngineTool

# Import our custom modules
from database import (
    cleanup_resources, 
    create_table_from_csv, 
    is_sql_result_satisfactory
)
from embeddings import (
    create_sample_vector_index, 
    add_csv_rows_to_index
)
from ollama_integration import (
    is_ollama_running,
    get_available_models,
    get_available_embedding_models,
    load_models
)

# ---------------------------------------------------------------------------------
# Streamlit Setup and Initialization
# ---------------------------------------------------------------------------------
st.set_page_config(page_title="RAG + SQL Router", layout="wide")

# Initialize session state variables if they do not exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'index' not in st.session_state:
    st.session_state.index = None
if 'sql_initialized' not in st.session_state:
    st.session_state.sql_initialized = False
if 'fake_docs_loaded' not in st.session_state:
    st.session_state.fake_docs_loaded = False
if 'csv_tables' not in st.session_state:
    st.session_state.csv_tables = []
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Only create these if they don't exist yet
if 'sqlite_connection' not in st.session_state:
    st.session_state.sqlite_connection = sqlite3.connect(':memory:', check_same_thread=False)

if 'db_engine' not in st.session_state:
    st.session_state.db_engine = create_engine(
        'sqlite:///:memory:',
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

def close_app_resources():
    """
    Safely close database connections if they exist in st.session_state.
    """
    try:
        cleanup_resources(
            st.session_state.get('sqlite_connection'), 
            st.session_state.get('db_engine')
        )
    except Exception as e:
        # We just print the exception if needed; 
        # in this example, we ignore it or log it as a minor warning.
        print(f"Ignoring error during resource cleanup: {e}")

atexit.register(close_app_resources)

# ---------------------------------------------------------------------------------
# Sidebar Configuration
# ---------------------------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    if st.button("Close Database Connections"):
        close_app_resources()
        st.success("Database connections closed and will auto-reinitialize if needed.")

    # Ollama Settings
    st.subheader("Ollama Settings")
    ollama_base_url = st.text_input("Ollama Base URL", "http://localhost:11434")
    
    ollama_running = is_ollama_running(ollama_base_url)
    if ollama_running:
        st.subheader("Model Selection")
        available_models = get_available_models(ollama_base_url)
        if not available_models or available_models[0] == "No models found":
            st.warning("No models found in Ollama. Please pull models first.")
        
        qwen_model = st.selectbox("LLM Model", available_models, index=0)
        
        available_embed_models = get_available_embedding_models(ollama_base_url)
        embed_model_name = st.selectbox("Embedding Model", available_embed_models, index=0)
    else:
        st.error("Ollama is not running. Please start Ollama server first.")
        qwen_model = st.selectbox("LLM Model (Ollama not running)", ["Ollama not running"], disabled=True)
        embed_model_name = st.selectbox("Embedding Model (Ollama not running)", ["Ollama not running"], disabled=True)

    st.subheader("Generation Settings")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.1)
    max_new_tokens = st.slider("Max New Tokens", 100, 2000, 512, 50)

    st.subheader("Tool Selection")
    default_tool = st.radio("Default strategy", ["SQL first, then RAG", "Let LLM decide"], index=1)

    if st.button("Load Models"):
        if not ollama_running:
            st.error("Ollama is not running. Please start the Ollama server first.")
        else:
            with st.spinner(f"Loading {qwen_model} and {embed_model_name}..."):
                try:
                    llm, embed_model = load_models(
                        temperature=temperature,
                        max_tokens=max_new_tokens,
                        ollama_base_url=ollama_base_url,
                        model_name=qwen_model,
                        embed_model_name=embed_model_name
                    )
                    st.session_state.llm = llm
                    st.session_state.embed_model = embed_model
                    st.success("Models loaded successfully!")
                except Exception as e:
                    st.error(f"Failed to load models: {str(e)}")

    use_sample_data = st.checkbox("Use sample city information", value=False)
    if use_sample_data and not st.session_state.fake_docs_loaded and 'embed_model' in st.session_state:
        with st.spinner("Loading sample city data..."):
            try:
                st.session_state.index = create_sample_vector_index(st.session_state.embed_model)
                st.session_state.fake_docs_loaded = True
                st.success("Sample city information loaded into the vector index!")
            except Exception as e:
                st.error(f"Error loading sample data: {str(e)}")

    # CSV Upload
    st.subheader("Upload CSV Files for SQL Database")
    uploaded_files = st.file_uploader("Upload CSV files", type=["csv"], accept_multiple_files=True)

    process_files_button = st.button(
        "Process CSV Files",
        disabled=(
            not uploaded_files or 
            'embed_model' not in st.session_state or 
            'llm' not in st.session_state
        )
    )

    if process_files_button and uploaded_files:
        with st.spinner("Processing uploaded CSV files..."):
            for uploaded_file in uploaded_files:
                file_id = f"{uploaded_file.name}_{hash(uploaded_file.getvalue())}"
                if file_id in st.session_state.processed_files:
                    st.info(f"Skipping (already processed): {uploaded_file.name}")
                    continue

                file_name = uploaded_file.name.split('.')[0].lower()
                table_name = file_name.replace(' ', '_').replace('-', '_')

                table_result, df, error_message = create_table_from_csv(
                    st.session_state.db_engine,
                    uploaded_file, 
                    table_name
                )
                if error_message:
                    st.error(error_message)
                else:
                    if table_result not in st.session_state.csv_tables:
                        st.session_state.csv_tables.append(table_result)
                        st.success(f"Loaded {uploaded_file.name} as table '{table_result}'")
                    
                    # Add CSV data to vector index
                    st.session_state.index = add_csv_rows_to_index(
                        df,
                        st.session_state.embed_model,
                        existing_index=st.session_state.index
                    )

                    st.session_state.processed_files.add(file_id)
            
            # Initialize SQL Query Engine
            if st.session_state.csv_tables:
                try:
                    sql_database = SQLDatabase(
                        st.session_state.db_engine,
                        include_tables=st.session_state.csv_tables
                    )
                    st.session_state.sql_query_engine = NLSQLTableQueryEngine(
                        sql_database=sql_database,
                        tables=st.session_state.csv_tables,
                        llm=st.session_state.llm,
                        embed_model=st.session_state.embed_model
                    )
                    st.session_state.sql_initialized = True
                except Exception as e:
                    st.error(f"Error initializing SQL: {str(e)}")

# ---------------------------------------------------------------------------------
# Main Layout
# ---------------------------------------------------------------------------------
col_chat, col_db = st.columns([2, 1])

# Database display in the second column
with col_db:
    st.header("SQL Database")

    if not st.session_state.sql_initialized and not st.session_state.csv_tables:
        st.info("No database tables. Use sample data or upload a CSV.")
        if st.button("Setup Example SQL Database"):
            if 'llm' not in st.session_state or 'embed_model' not in st.session_state:
                st.error("Please load the models first.")
            else:
                with st.spinner("Setting up example SQL data..."):
                    from sqlalchemy import MetaData, Table, Column, String, Integer
                    engine = st.session_state.db_engine
                    metadata_obj = MetaData()
                    table_name = "city_stats"
                    city_stats_table = Table(
                        table_name,
                        metadata_obj,
                        Column("city_name", String(16), primary_key=True),
                        Column("population", Integer),
                        Column("state", String(16), nullable=False),
                    )
                    try:
                        metadata_obj.create_all(engine)
                        rows = [
                            {"city_name": "New York City", "population": 8336000, "state": "New York"},
                            {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                            {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                            {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                            {"city_name": "Miami", "population": 449514, "state": "Florida"},
                            {"city_name": "Seattle", "population": 749256, "state": "Washington"},
                        ]
                        with engine.begin() as connection:
                            # Wrap raw SQL in text() to avoid "Not an executable object" error
                            connection.execute(text("DELETE FROM city_stats"))
                            for row in rows:
                                connection.execute(city_stats_table.insert().values(**row))

                        if table_name not in st.session_state.csv_tables:
                            st.session_state.csv_tables.append(table_name)
                        
                        sql_database = SQLDatabase(
                            engine, 
                            include_tables=st.session_state.csv_tables
                        )
                        st.session_state.sql_query_engine = NLSQLTableQueryEngine(
                            sql_database=sql_database,
                            tables=st.session_state.csv_tables,
                            llm=st.session_state.llm,
                            embed_model=st.session_state.embed_model
                        )
                        st.session_state.sql_initialized = True
                        st.success("Example SQL Database ready!")
                    except Exception as ex:
                        st.error(f"Error setting up DB: {str(ex)}")

    st.subheader("Current Database Tables")
    if st.session_state.csv_tables:
        tabs = st.tabs(st.session_state.csv_tables)
        for i, table_name in enumerate(st.session_state.csv_tables):
            with tabs[i]:
                try:
                    df_table = pd.read_sql_query(f"SELECT * FROM {table_name}", st.session_state.db_engine)
                    st.dataframe(df_table)
                    st.text(f"Schema for {table_name}:")
                    inspector = inspect(st.session_state.db_engine)
                    columns_info = inspector.get_columns(table_name)
                    lines = [f"- {col['name']}: {col['type']}" for col in columns_info]
                    schema_text = "\n".join(lines)
                    st.code(schema_text)
                except Exception as e:
                    st.error(f"Error reading table {table_name}: {str(e)}")
    else:
        st.info("No tables found in the database.")

# Chat interface in the first column
with col_chat:
    st.header("RAG and Text-to-SQL in a Single Query Interface using LlamaIndex and Qwen (via Ollama)")

    def run_query(query):
        if 'index' not in st.session_state or not st.session_state.index:
            return "No document knowledge base. Please load sample data or CSV data first."
        if 'sql_initialized' not in st.session_state or not st.session_state.sql_initialized:
            return "SQL is not initialized. Please load CSV or set up example DB."

        vector_query_engine = st.session_state.index.as_query_engine()

        table_descriptions = ", ".join(st.session_state.csv_tables)
        inspector = inspect(st.session_state.db_engine)
        schema_info = ""
        for table_name in st.session_state.csv_tables:
            schema_info += f"Table {table_name}: "
            columns = inspector.get_columns(table_name)
            column_info = [f"{col['name']} ({col['type']})" for col in columns]
            schema_info += ", ".join(column_info) + "\n"

        sql_tool = QueryEngineTool.from_defaults(
            query_engine=st.session_state.sql_query_engine,
            description=(
                f"Useful for translating natural language into SQL queries on: {table_descriptions}."
            ),
            name="sql_tool"
        )

        rag_tool = QueryEngineTool.from_defaults(
            query_engine=vector_query_engine,
            description=(
                f"Useful for answering questions from vector store documents."
            ),
            name="rag_tool"
        )

        if default_tool == "Let LLM decide":
            chat_messages = []
            for msg in st.session_state.chat_history:
                role = "user" if msg["is_user"] else "assistant"
                chat_messages.append(ChatMessage(role=role, content=msg["text"]))
            
            chat_messages.append(ChatMessage(role="user", content=query))

            system_prompt = (
                "You are an assistant that decides which tool to use. "
                f"1) sql_tool => for SQL queries on: {table_descriptions}\n"
                f"   Schema:\n{schema_info}\n"
                "2) rag_tool => for semantic queries on documents.\n"
                "Return ONLY 'sql_tool' or 'rag_tool'."
            )
            router_prompt = f"{system_prompt}\n\nUser's query: {query}\n\nTool to use:"

            # Decide which tool
            try:
                decision = st.session_state.llm.complete(router_prompt)
                decision_str = str(decision).strip().lower()
                if "sql_tool" in decision_str:
                    chosen_tool = sql_tool
                    st.info("Chosen Tool: SQL")
                elif "rag_tool" in decision_str:
                    chosen_tool = rag_tool
                    st.info("Chosen Tool: RAG")
                else:
                    # Fallback
                    st.warning(f"Unexpected routing decision: {decision_str}")
                    chosen_tool = sql_tool

                result = chosen_tool(query)
                return str(result) if result else ""
            except Exception as ex:
                return f"Error during tool selection: {str(ex)}"
        else:
            # SQL first, then fallback to RAG
            st.info("Attempting SQL tool first, then RAG if needed.")
            sql_response = sql_tool(query)
            if is_sql_result_satisfactory(sql_response):
                return str(sql_response)
            rag_response = rag_tool(query)
            return str(rag_response) if rag_response else ""

    # Show chat history
    st.subheader("Conversation")
    for msg in st.session_state.chat_history:
        if msg["is_user"]:
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**Assistant:** {msg['text']}")
    
    # Define callback for form submission
    def submit_form():
        user_query = st.session_state.user_input
        if user_query:
            st.session_state.user_query = user_query  # Store the query
            st.session_state.submitted = True  # Set the submitted flag
            st.session_state.user_input = ""  # This will work on next rerun

    # Input field with a form
    with st.form(key="query_form"):
        user_query = st.text_input("Ask a question:", key="user_input")
        submit_button = st.form_submit_button("Send", on_click=submit_form)

    # Process the query if it was submitted
    if st.session_state.submitted:
        if 'user_query' in st.session_state:
            user_query = st.session_state.user_query
            if 'llm' not in st.session_state or 'embed_model' not in st.session_state:
                st.error("Please load models first in the sidebar.")
            else:
                st.session_state.chat_history.append({"text": user_query, "is_user": True})
                with st.spinner("Thinking..."):
                    try:
                        answer = run_query(user_query)
                        st.session_state.chat_history.append({"text": answer, "is_user": False})
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            
            # Reset the submitted flag
            st.session_state.submitted = False
            del st.session_state.user_query
            st.rerun()

# ---------------------------------------------------------------------------------
# Footer / Notes
# ---------------------------------------------------------------------------------
st.markdown("""
### About this app
This application demonstrates a combined RAG + Text-to-SQL approach using an LLM from Ollama with a Streamlit interface.

1. RAG for semantic retrieval from documents  
2. Text-to-SQL for structured data queries  
3. Automatic routing based on your query  

### Setup
1. Install and run Ollama  
2. Pull models (if needed) via 'ollama pull <model>'  
3. Use the sidebar to configure and load your selected models  

### Example Queries
- "Which city has the highest population?" (SQL-based)  
- "Tell me about Los Angeles." (RAG-based)  
""")