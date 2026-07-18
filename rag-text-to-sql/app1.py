import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core import Settings, SQLDatabase
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import QueryEngineTool
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Configuration
LLAMA_CLOUD_API_KEY = "API-KEY"

# Initialize models with caching
@st.cache_resource
def initialize_models():
    llm = Ollama(model="llama3.2:latest", request_timeout=300.0)
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return llm

# Set up SQL engine (static, cached)
@st.cache_resource
def setup_sql_engine():
    try:
        engine = create_engine("sqlite:///:memory:")
        metadata = MetaData()

        city_stats = Table(
            "city_stats",
            metadata,
            Column("city_name", String(50), primary_key=True),
            Column("population", Integer),
            Column("state", String(50)),
        )
        
        metadata.create_all(engine)

        with engine.begin() as conn:
            conn.execute(insert(city_stats), [
                {"city_name": "New York City", "population": 8336000, "state": "New York"},
                {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                {"city_name": "Miami", "population": 449514, "state": "Florida"},
                {"city_name": "Seattle", "population": 749256, "state": "Washington"},
            ])

        return NLSQLTableQueryEngine(
            sql_database=SQLDatabase(engine),
            tables=["city_stats"],
            llm=initialize_models()
        )
    except Exception as e:
        st.error(f"SQL Engine Error: {str(e)}")
        return None

# Connect to existing index
def connect_to_existing_index():
    try:
        index = LlamaCloudIndex(
            name="<index name>", 
            project_name="<project name>",
            organization_id="<organization_id>",
            api_key=LLAMA_CLOUD_API_KEY
        )
        return index.as_query_engine()
    except Exception as e:
        st.error(f"Index Connection Error: {str(e)}")
        return None

# Create the agent with SQL and RAG tools
def create_agent(sql_engine, rag_engine):
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_engine,
        name="city_stats",
        description="""Useful for translating a natural language query into a SQL query over
        a table containing: city_stats"""
    )

    rag_tool = QueryEngineTool.from_defaults(
        query_engine=rag_engine,
        name="city_info",
        description=f"Useful for answering semantic questions about documents."
    )

    return ReActAgent.from_tools(
        tools=[sql_tool, rag_tool],
        llm=initialize_models(),
        verbose=True,
        #max_iterations=5,
        handle_parsing_errors=True
    )

def main():
    st.title("City Information Assistant")

    # Set up SQL engine (cached)
    if 'sql_engine' not in st.session_state:
        with st.spinner("Setting up SQL database..."):
            st.session_state.sql_engine = setup_sql_engine()
            if st.session_state.sql_engine is None:
                st.error("Failed to set up SQL engine. Please check the logs.")
                return

    # Connect to existing index
    if 'rag_engine' not in st.session_state:
        with st.spinner("Connecting to existing index..."):
            st.session_state.rag_engine = connect_to_existing_index()
            if st.session_state.rag_engine is None:
                st.error("Failed to connect to existing index. Please check the logs.")
                return

    # Create agent with both engines
    if 'agent' not in st.session_state:
        st.session_state.agent = create_agent(st.session_state.sql_engine, st.session_state.rag_engine)

    # User input for queries
    query = st.chat_input("Enter your question to chat:")
    
    if query and 'agent' in st.session_state:
        with st.chat_message("user"):
            st.write(query)
        with st.spinner("Analyzing..."):
            try:
                # Query the agent
                response = st.session_state.agent.query(query)
                
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
