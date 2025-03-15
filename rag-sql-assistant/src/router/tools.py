"""
Query Tools Module

This module provides tools for querying both SQL and RAG information sources.
"""
from typing import List

from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SQLDatabase

from src.database.city_stats import CityStatsDB
from src.rag.cloud_index import LlamaCloudRAG


def get_sql_tool(city_stats_db: CityStatsDB) -> QueryEngineTool:
    """
    Create a QueryEngineTool for SQL queries.
    
    Args:
        city_stats_db: CityStatsDB instance
        
    Returns:
        QueryEngineTool: Tool for executing SQL queries
    """
    # Get the SQL database
    sql_database = city_stats_db.get_llama_index_sql_database()
    
    # Create a natural language SQL query engine
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"]
    )
    
    # Create a tool from the query engine
    return QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )


def get_rag_tool(llama_cloud_rag: LlamaCloudRAG) -> QueryEngineTool:
    """
    Create a QueryEngineTool for RAG queries.
    
    Args:
        llama_cloud_rag: LlamaCloudRAG instance
        
    Returns:
        QueryEngineTool: Tool for executing RAG queries
    """
    # The cities we have information about
    cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
    
    # Get query engine from RAG instance
    query_engine = llama_cloud_rag.query_engine
    
    # Create a tool for the RAG query engine
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        description=(
            f"Useful for answering semantic questions about certain cities in the US."
        ),
        name="llama_cloud_tool"
    )


def get_all_tools(city_stats_db: CityStatsDB, llama_cloud_rag: LlamaCloudRAG) -> List[QueryEngineTool]:
    """
    Get all query tools.
    
    Args:
        city_stats_db: CityStatsDB instance
        llama_cloud_rag: LlamaCloudRAG instance
        
    Returns:
        List[QueryEngineTool]: List of all query tools
    """
    sql_tool = get_sql_tool(city_stats_db)
    rag_tool = get_rag_tool(llama_cloud_rag)
    
    return [sql_tool, rag_tool]


def create_sql_tool() -> QueryEngineTool:
    """
    Create a QueryEngineTool for SQL queries with default configuration.
    
    This function initializes a CityStatsDB instance and uses it to create an SQL tool.
    
    Returns:
        QueryEngineTool: Tool for executing SQL queries
    """
    # Initialize the database with default settings
    city_stats_db = CityStatsDB()
    
    # Create and return the SQL tool
    return get_sql_tool(city_stats_db)


def create_rag_tool() -> QueryEngineTool:
    """
    Create a QueryEngineTool for RAG queries with default configuration.
    
    This function initializes a LlamaCloudRAG instance and uses it to create a RAG tool.
    
    Returns:
        QueryEngineTool: Tool for executing RAG queries
    """
    # Initialize the RAG system with default settings
    llama_cloud_rag = LlamaCloudRAG()
    
    # Create and return the RAG tool
    return get_rag_tool(llama_cloud_rag)
