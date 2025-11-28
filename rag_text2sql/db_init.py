import os
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

from llama_index.core import SQLDatabase, Settings
from llama_index.llms.openai import OpenAI
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
from opik import track

Settings.llm = OpenAI("gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"), timeout=300)


table_name = "city_stats"
@track
def create_db_engine():
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()

    # create city SQL table

    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )

    metadata_obj.create_all(engine)

    from sqlalchemy import insert

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
            cursor = connection.execute(stmt)

    with engine.connect() as connection:
        cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
        print(cursor.fetchall())

    return engine


def create_sql_database(table: str):
    sql_database = SQLDatabase(create_db_engine(), include_tables=[table])
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=[table],
    )

    return sql_query_engine

@track
def create_llama_cloud_index():
    index = LlamaCloudIndex(
        name="competitive-sawfish-2025-03-10",
        project_name="Default",
        organization_id="76e3e4f2-4229-45ca-a4de-300148139d1f",
        api_key=os.getenv("LLAMACLOUD_API_KEY")
    )
    llama_cloud_query_engine = index.as_query_engine()
    return llama_cloud_query_engine

# @track
# def create_llama_cloud_index():
#     index = LlamaCloudIndex(
#         name="index name",
#         project_name="your project name",
#         organization_id="your org id",
#         api_key="your-llamacloud-api-key"
#     )
#     llama_cloud_query_engine = index.as_query_engine()
#     return llama_cloud_query_engine
@track
def create_sql_tool():
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=create_sql_database(table_name),
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool"
    )

    return sql_tool

def create_llama_cloud_tool():
    cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
    llama_cloud_tool = QueryEngineTool.from_defaults(
        query_engine=create_llama_cloud_index(),
        description=(
            f"Useful for answering semantic questions about certain cities in the US."
        ),
        name="llama_cloud_tool"

    )
    return llama_cloud_tool