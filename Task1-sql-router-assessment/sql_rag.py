import os
import nest_asyncio
import asyncio
import streamlit as st
from llama_index.core import SQLDatabase, Settings, set_global_handler
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool
from tool_workflow import RouterOutputAgentWorkflow
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert


def get_api_keys():
    """Retrieve API keys from environment variables."""
    keys = {}
    required_keys = ["PHOENIX_API_KEY", "OPENAI_API_KEY", "LLAMA_CLOUD_API_KEY", "ORGANIZATION_ID"]
    for key in required_keys:
        keys[key] = os.getenv(key)
        if keys[key] is None:
            raise ValueError(f"Missing required environment variable: {key}")
    return keys


def setup_logging(api_key):
    """Setup Arize Phoenix logging for tracing."""
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={api_key}"
    set_global_handler("arize_phoenix", endpoint="https://llamatrace.com/v1/traces")


def initialize_llama_index(organization_id):
    """Initialize LlamaCloudIndex and return a query engine."""
    try:
        index = LlamaCloudIndex(
            name="thirsty-finch-2025-03-09",
            project_name="Default",
            organization_id=organization_id
        )
        return index.as_query_engine()
    except Exception as e:
        raise RuntimeError(f"Failed to initialize LlamaCloudIndex: {e}")


def setup_database():
    """Setup SQLite in-memory database and populate it with city data."""
    try:
        engine = create_engine("sqlite:///:memory:", future=True)
        metadata_obj = MetaData()
        city_stats_table = Table(
            "city_stats",
            metadata_obj,
            Column("city_name", String(16), primary_key=True),
            Column("population", Integer),
            Column("state", String(16), nullable=False),
        )
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
            for row in rows:
                connection.execute(insert(city_stats_table).values(**row))

        return engine, city_stats_table
    except Exception as e:
        raise RuntimeError(f"Failed to set up database: {e}")


def setup_query_engines(engine):
    """Setup SQL query engine for querying city data."""
    try:
        sql_database = SQLDatabase(engine, include_tables=["city_stats"])
        sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])
        return QueryEngineTool.from_defaults(
            query_engine=sql_query_engine,
            description="Useful for querying city population and state information in the USA.",
            name="sql_tool"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to setup SQL query engine: {e}")


def initialize_workflow(sql_tool, llama_cloud_tool):
    """Initialize the RouterOutputAgentWorkflow with query tools."""
    try:
        return RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=120)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize workflow: {e}")


async def run_query(query, workflow):
    """Run a query asynchronously using the workflow."""
    try:
        return await workflow.run(message=query)
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")


def main():
    """Main function to run the Streamlit app."""
    try:
        # Retrieve API keys
        api_keys = get_api_keys()
        setup_logging(api_keys["PHOENIX_API_KEY"])
        nest_asyncio.apply()

        # Set default LLM model
        Settings.llm = OpenAI("gpt-4o-mini")

        # Initialize LlamaCloud Query Engine
        llama_cloud_query_engine = initialize_llama_index(api_keys["ORGANIZATION_ID"])
        engine, _ = setup_database()
        sql_tool = setup_query_engines(engine)
        llama_cloud_tool = QueryEngineTool.from_defaults(
            query_engine=llama_cloud_query_engine,
            description="Useful for answering semantic questions about US cities.",
            name="llama_cloud_tool"
        )
        wf = initialize_workflow(sql_tool, llama_cloud_tool)

        # Streamlit UI
        st.title("Agentic RAG Integrating SQL Databases & Semantic Search")
        query = st.text_input("Enter your query:")
        if st.button("Submit") and query:
            try:
                response = asyncio.run(run_query(query, wf))
                st.write("### Response:")
                st.write(str(response))
            except Exception as e:
                st.error(f"An error occurred: {e}")
    except Exception as e:
        st.error(f"Application failed to start: {e}")


if __name__ == "__main__":
    main()
