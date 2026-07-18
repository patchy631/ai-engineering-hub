import logging, sys, os

from llama_index.core import SQLDatabase, Settings, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.core.query_engine import NLSQLTableQueryEngine
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert

import qdrant_client
from qdrant_client import models
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding

from llama_index.core.tools import QueryEngineTool


##### Get LLM #####

llm = Settings.llm



##### Create SQL DB #####


engine = create_engine("sqlite:///city_stats.sqlite", future=True)
metadata_obj = MetaData()

# create city SQL table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)

if os.path.exists('city_stats.sqlite'):
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]
    try:
        for row in rows:
            stmt = insert(city_stats_table).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)
    except Exception as e:
        # print('Error while inserting data in sql: ',e)
        pass


##### Set Up Embedding Model #####

# use any supported FastEmbedding model
Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")



##### Create SQL Query Engine #####


sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"],
    llm=Settings.llm,
    embed_model = Settings.embed_model,
    verbose=True,
    use_async = True)



##### Set Up async RAG Query Engine (Qdrant) #####


documents = SimpleDirectoryReader("./data/cities/").load_data()

aclient = qdrant_client.AsyncQdrantClient(
    # host="localhost",
    # port=6333,
    location=":memory:"
)

vectors_config=models.VectorParams(size=768,
                                   distance=models.Distance.DOT,
                                    on_disk=True)

quantization_config=models.BinaryQuantization(
              binary=models.BinaryQuantizationConfig(always_ram=True)),

vector_store = QdrantVectorStore(
    collection_name="cities",
    aclient=aclient,
    batch_size = 4,
    dense_config = vectors_config,
    quantization_config = quantization_config,
    prefer_grpc=True
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    use_async=True,
)

rag_query_engine = index.as_query_engine(llm=Settings.llm, use_async=True, verbose=True)



##### Create Tools for LLM #####


sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        f"""call this tool when you want to get the value of population of a US city.
        you will provide a SQL query for a table named city_stats containing city_name, population, state as its columns."""
    ),
    name="sql_tool"
)


rag_tool = QueryEngineTool.from_defaults(
    query_engine = rag_query_engine,
    description=(
        f"Whenever user asks about any US cities then call this function to get relevant information about the city as per the user query."
    ),
    name="city_information_tool"
)
