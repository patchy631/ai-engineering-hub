import streamlit as st
import os
import nest_asyncio
from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool

# Set up API key (Ensure to store securely in production)
os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>"
# Apply Nest Asyncio for Streamlit compatibility
nest_asyncio.apply()

# Configure OpenAI LLM
Settings.llm = OpenAI("gpt-3.5-turbo")

# Create SQLite in-memory database
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# Define city statistics table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)
metadata_obj.create_all(engine)

# Insert sample data
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]
for row in rows:
    stmt = sqlite_insert(city_stats_table).values(**row)
    stmt = stmt.on_conflict_do_update(index_elements=['city_name'], set_=row)
    with engine.begin() as connection:
        connection.execute(stmt)

# Set up SQL Database query engine
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])

sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description="Query city statistics using natural language.",
    name="sql_tool"
)

# Streamlit UI
st.title("RAG and Text-to-SQL")
st.write("Ask questions about city populations and states!")

user_query = st.text_input("Enter your query:", "Which city has the highest population?")

if st.button("Get Answer"):
    with st.spinner("Processing..."):
        response = sql_query_engine.query(user_query)
        st.write("### Answer:")
        st.write(response.response)
