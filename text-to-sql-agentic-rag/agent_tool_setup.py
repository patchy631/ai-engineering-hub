import os
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SQLDatabase

SQL_TABLE_NAME = "city_stats"
LLAMA_CLOUD_INDEX_NAME = "city_index"
LLAMA_CLOUD_ORGANIZATION_ID = "<YOUR_LLAMA_CLOUD_ORGANIZATION_ID>"

# Get API key from environment variables
api_key = os.environ.get('LLAMA_CLOUD_API_KEY')
if not api_key:
    raise ValueError("LLAMA_CLOUD_API_KEY environment variable not set")

def setup_agent_tools(engine):
    # Creating a SQL Tool
    sql_database = SQLDatabase(engine, include_tables=[SQL_TABLE_NAME])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=[SQL_TABLE_NAME],
        verbose=True
    )

    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )

    # Creating a Llama Cloud Tool
    index = LlamaCloudIndex(
        name=LLAMA_CLOUD_INDEX_NAME,
        project_name="Default",
        organization_id=LLAMA_CLOUD_ORGANIZATION_ID,
        api_key=api_key
    )

    llama_cloud_query_engine = index.as_query_engine()

    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=llama_cloud_query_engine,
        description=(
            f"Useful for answering semantic questions about US cities."
        ),
        name="llama_cloud_tool"
    )

    return [sql_tool, llama_cloud_tool]