import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from llama_index.core import Settings
from llama_index.core.indices.struct_store.sql import SQLDatabase
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.objects import SQLTableNodeMapping, SQLTableSchema, ObjectIndex

# Configure LLM and Embedding model
Settings.llm = Ollama(model="llama3.1:70b") 
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")

class TextToSQLRAG:
    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self.sql_db = SQLDatabase(self.engine)

        # Setup Qdrant
        self.qdrant_client = QdrantClient(host="localhost", port=6333)
        self.qdrant_store = QdrantVectorStore(client=self.qdrant_client, collection_name="my_collection")

        # Define table schemas
        self.table_node_mapping = SQLTableNodeMapping(self.sql_db)
        self.table_schema_objs = [
            SQLTableSchema(table_name=table) for table in inspect(self.engine).get_table_names()
        ]

        self.obj_index = ObjectIndex.from_objects(
            self.table_schema_objs,
            self.table_node_mapping,
            vector_store=self.qdrant_store,
        )

        # Query Engine
        self.query_engine = SQLTableRetrieverQueryEngine(
            self.sql_db,
            self.obj_index.as_retriever(
                similarity_top_k=1, embed_model=Settings.embed_model, llm=Settings.llm
            ),
        )

    def query(self, question):
        return self.query_engine.query(question).response
