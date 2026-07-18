import streamlit as st
import asyncio
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from llama_index.core import SQLDatabase, VectorStoreIndex, Document
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool
from pathlib import Path

from sql_router import (
    RouterOutputAgentWorkflow,
    llama_cloud_tool,
    create_llama_tool
)

# Default database setup
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# Create city stats table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)

# Insert initial data
cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
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

# Create default SQL tool
sql_database = SQLDatabase(engine, include_tables=[table_name])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=[table_name]
)

default_sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/state of"
        " each city located in the USA."
    ),
    name="sql_tool"
)

st.title("City Information Query System")

# Display default interface
st.header("Available Cities")
st.write(", ".join(cities))
sql_tool = default_sql_tool
llama_tool = llama_cloud_tool

# Display sample queries
st.header("Sample Queries")
sample_queries = [
    "Which city has the highest population?",
    "List all places to visit in Miami.",
    "How do people in Chicago get around?",
    "What is the historical name of Los Angeles?"
]
st.write("\n".join(f"- {query}" for query in sample_queries))

# User input
user_query = st.text_input("Enter your query:")

async def get_response(query):
    try:
        wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_tool], verbose=True, timeout=120)
        response = await wf.run(message=query)
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}"

if st.button("Get Answer"):
    if user_query:
        with st.spinner("Processing your query..."):
            try:
                import nest_asyncio
                nest_asyncio.apply()
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(get_response(user_query))
                loop.close()
                
                if isinstance(result, str) and result.startswith("Error"):
                    st.error(result)
                else:
                    st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a query.")