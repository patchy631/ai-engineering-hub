from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from database import get_database_engine
import os 
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

#LlamaCloud_TOKEN_KEY
LlamaCloud_TOKEN_KEY = os.getenv('LlamaCloud_TOKEN_KEY')

# Initialize SQL Database Engine
engine = get_database_engine()
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

# Create SQL Query Engine
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"]
)

# Initialize Llama Cloud Index
index = LlamaCloudIndex(
    name="sumit-TextToSql-2025-03-09", 
    project_name="Default",
    organization_id="70ad601c-65ec-4354-a2cf-3d5de8aff7b5",
    api_key=LlamaCloud_TOKEN_KEY # Replace with actual API key
)

# Create Llama Cloud Query Engine
llama_cloud_query_engine = index.as_query_engine()

def get_sql_query_engine():
    """Returns the SQL Query Engine."""
    return sql_query_engine

def get_llama_cloud_query_engine():
    """Returns the Llama Cloud Query Engine."""
    return llama_cloud_query_engine

