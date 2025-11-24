import streamlit as st
import os
import time
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core import Settings, SQLDatabase
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.readers.file import PDFReader
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
import tempfile

# Configuration
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Initialize models with caching
@st.cache_resource
def initialize_models():
    llm = Ollama(model="deepseek-r1:14b", request_timeout=300.0)
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return llm

# Set up SQL engine (static, cached)
@st.cache_resource
def setup_sql_engine():
    try:
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()

        stats = Table(
            "sql_stats",
            metadata,
            Column("city_name", String(50), primary_key=True),
            Column("population", Integer),
            Column("state", String(50)),
        )
        
        metadata.create_all(engine)

        with engine.begin() as conn:
            conn.execute(insert(stats), [
                {"city_name": "New York City", "population": 8336000, "state": "New York"},
                {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                {"city_name": "Miami", "population": 449514, "state": "Florida"},
                {"city_name": "Seattle", "population": 749256, "state": "Washington"},
            ])

        return NLSQLTableQueryEngine(
            sql_database=SQLDatabase(engine),
            tables=["stats"],
            llm=initialize_models()
        )
    except Exception as e:
        st.error(f"SQL Engine Error: {str(e)}")
        return None

# Create RAG index from a file path (not cached, as it depends on the uploaded file)
def create_rag_index_from_file(file_path):
    try:
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        reader = PDFReader()
        documents = reader.load_data(file=pdf_path)

        index = LlamaCloudIndex.from_documents(
            documents,
            name=f"index-{int(time.time())}",
            project_name="<project-name>",
            api_key=LLAMA_CLOUD_API_KEY,
            embedding_config={
                "type": "HUGGINGFACE_API_EMBEDDING",
                "component": {
                    "token": "<hf_token>",
                    "model_name": "BAAI/bge-small-en-v1.5"
                }
            },
            transform_config={
                "mode": "auto",
                "config": {"chunk_size": 1024, "chunk_overlap": 20}
            }
        )
        return index.as_query_engine()
    except Exception as e:
        st.error(f"RAG Index Error: {str(e)}")
        return None

# Create the agent with SQL and RAG tools
def create_agent(sql_engine, rag_engine):
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_engine,
        name="stats",
        description="""Useful for translating a natural language query into a SQL query over
        a table containing: stats"""
    )

    rag_tool = QueryEngineTool.from_defaults(
        query_engine=rag_engine,
        name="info",
        description="Useful for answering semantic questions about the document."
    )

    return ReActAgent.from_tools(
        tools=[sql_tool, rag_tool],
        llm=initialize_models(),
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True
    )

def main():
    st.title("RAG-SQL Agent")
    
    # Set up SQL engine (cached)
    if 'sql_engine' not in st.session_state:
        with st.spinner("Setting up SQL database..."):
            st.session_state.sql_engine = setup_sql_engine()
            if st.session_state.sql_engine is None:
                st.error("Failed to set up SQL engine. Please check the logs.")
                return

    # File uploader for PDF
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    # Process the uploaded file
    if uploaded_file is not None:
        # Check if the file has changed (to avoid reprocessing the same file)
        if 'last_uploaded_file' not in st.session_state or st.session_state.last_uploaded_file != uploaded_file:
            st.session_state.last_uploaded_file = uploaded_file
            with st.spinner("Processing uploaded PDF..."):
                # Save the uploaded file to a temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                
                # Create RAG index from the temporary file
                rag_engine = create_rag_index_from_file(tmp_file_path)
                if rag_engine:
                    st.session_state.rag_engine = rag_engine
                    # Create agent with both engines
                    st.session_state.agent = create_agent(st.session_state.sql_engine, rag_engine)
                    st.success("PDF processed and index created!")
                else:
                    st.error("Failed to create RAG index from the uploaded PDF.")
                    return
    else:
        st.info("Please upload a PDF file to enable queries.")
        return

    # # User input for queries
    # query = st.chat_input("Enter your question about US cities:")
    
    # if query and 'agent' in st.session_state:
    #     with st.chat_message("user"):
    #         st.write(query)
    #     with st.spinner("Analyzing..."):
    #         try:
    #             # response = st.session_state.agent.query(query)
    #             # final_answer = response.response.split('</think>')[-1].strip()
    #             # with st.chat_message("assistant"):
    #             #     st.write(final_answer)
    #             response = st.session_state.agent.query(query)
    #             final_answer = response.response.split('</think>')[-1].strip()
    #             st.write(final_answer)
    #         except Exception as e:
    #             st.error(f"Query failed: {str(e)}")

    query = st.chat_input("Enter your question :")
    
    if query and 'agent' in st.session_state:
        with st.chat_message("user"):
            st.write(query)
        with st.spinner("Analyzing..."):
            try:
                # Query the agent
                response = st.session_state.agent.query(query)
                
                # Temporarily display the full response for debugging (remove this later)
               
                
                # Robust parsing: extract text after the last </think> if present
                if '</think>' in response.response:
                    final_answer = response.response.split('</think>')[-1].strip()
                else:
                    # Fallback: use the entire response if no </think> is found
                    final_answer = response.response.strip()
                
                # Display the final answer
                with st.chat_message("assistant"):
                    st.write(final_answer)
            except Exception as e:
                st.error(f"Query failed: {str(e)}")

if __name__ == "__main__":
    main()
