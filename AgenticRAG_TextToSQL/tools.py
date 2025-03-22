from llama_index.core.tools import QueryEngineTool
from query_engines import get_sql_query_engine, get_llama_cloud_query_engine

# Initialize query engines
sql_query_engine = get_sql_query_engine()
llama_cloud_query_engine = get_llama_cloud_query_engine()

# Define SQL Query Engine Tool
sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over "
        "a table containing: city_stats, with population and state data for US cities."
    ),
    name="sql_tool"
)

# Define Llama Cloud Query Engine Tool
llama_cloud_tool = QueryEngineTool.from_defaults(
    query_engine=llama_cloud_query_engine,
    description="Useful for answering semantic questions about certain cities in the US.",
    name="llama_cloud_tool"
)

def get_sql_tool():
    """Returns the SQL query engine tool."""
    return sql_tool

def get_llama_cloud_tool():
    """Returns the Llama Cloud query engine tool."""
    return llama_cloud_tool
