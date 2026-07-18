import os
from sqlalchemy import create_engine
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.llms.openai import OpenAI

#Set API Keys
os.environ["OPENAI_API_KEY"] = "sk-proj-xxxxxx" # Replace with your actual key
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-xxxxxx"  # Replace with your actual key

#Connect to SQLite Database (Text-to-SQL)
engine = create_engine("sqlite:///city_data.db", future=True)
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])

#Connect to LlamaCloud Index (RAG Retrieval)
index = LlamaCloudIndex(
    name="confidential-xxx-xxx-xxx", #Replace with your actual value
    project_name="xxxx", #Replace with your actual value
    organization_id="xxxxxxxx", #Replace with your actual value
    api_key=os.environ["LLAMA_CLOUD_API_KEY"]
)

llama_cloud_query_engine = index.as_query_engine()

#Define function to handle queries
def query_backend(user_query):
    "Routes queries to either SQL or RAG-based retrieval and provides metadata."
    response_details = {}

    if "population" in user_query.lower() or "state" in user_query.lower():
        result = sql_query_engine.query(user_query)
        response_details["source"] = "SQL Database"
        response_details["query"] = result.metadata.get("sql_query", "Generated SQL Query Not Available")
    else:
        result = llama_cloud_query_engine.query(user_query)
        response_details["source"] = "LlamaCloud (RAG Retrieval)"
        response_details["retrieved_documents"] = [doc.metadata for doc in result.source_nodes] if hasattr(result, "source_nodes") else "No documents retrieved"

    # Extract readable response text
    response_text = result.response if hasattr(result, "response") else str(result)
    response_details["final_answer"] = response_text

    return response_details  # Now returns a dictionary with extra details


