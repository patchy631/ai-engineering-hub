from llama_index.core import SQLDatabase
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import NLSQLTableQueryEngine
from config.settings import DATABASE_URL

def create_sql_tool():
    sql_database = SQLDatabase.from_uri(
        DATABASE_URL,
        include_tables=["cities"],
        sample_rows_in_table_info=3
    )
    
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["cities"]
    )
    
    return QueryEngineTool(
        query_engine=sql_query_engine,
        metadata=ToolMetadata(
            name="sql_tool",
            description=(
                "Use this tool ONLY for querying factual data about US cities including: "
                "population numbers, state location, and city area. "
                "Available cities: New York City, Los Angeles, Chicago, Houston, Miami, and Seattle. "
                "Do NOT use this tool for historical information, landmarks, or cultural details."
            )
        )
    ) 