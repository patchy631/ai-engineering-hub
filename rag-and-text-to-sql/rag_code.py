import json
import re
from pydantic_core.core_schema import AnySchema
from qdrant_client import models
from qdrant_client import QdrantClient
import qdrant_client
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.sambanovasystems import SambaNovaCloud
from llama_index.llms.ollama import Ollama
import assemblyai as aai
from typing import List, Dict
from llama_index.core.tools import QueryEngineTool
from llama_index.core import Settings
from llama_index.core.llms.function_calling import FunctionCallingLLM, ToolSelection
from llama_index.core.base.llms.types import (
    ChatMessage,
    MessageRole,
)
import nest_asyncio
from IPython.display import Markdown, display
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from llama_index.core.llms.llm import LLM
import ollama
import asyncio
from openai import OpenAI  
import qdrant_client
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.indices.vector_store.base import VectorStoreIndex  
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Float
from llama_index.core import SQLDatabase
import pandas as pd
from llama_index.core.query_engine import NLSQLTableQueryEngine
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from sqlalchemy.sql import text 


nest_asyncio.apply()
def batch_iterate(lst, batch_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]

class Tool:
    def __init__(self, name, description, tool_id, tool_args=None, execute_fn=None):
        self.name = name
        self.description = description
        self.t_id = tool_id
        self.arguments = tool_args
        self.execute_fn = execute_fn  # Store function to execute tool

    async def acall(self, **kwargs):
        """Asynchronously call the tool with given arguments."""
        if self.execute_fn:
            return await self.execute_fn(**kwargs)
        raise ValueError(f"Tool {self.name} does not have an execution function.")

class EmbedData:

    def __init__(self, embed_model_name="BAAI/bge-large-en-v1.5", batch_size = 32):
        self.embed_model_name = embed_model_name
        self.embed_model = self._load_embed_model()
        self.batch_size = batch_size
        self.embeddings = []
        
    def _load_embed_model(self):
        embed_model = (FastEmbedEmbedding(model_name=self.embed_model_name) if self.embed_model_name != "BAAI/bge-large-en-v1.5" else HuggingFaceEmbedding(model_name=self.embed_model_name, trust_remote_code=True, cache_folder='./hf_cache'))
        Settings.embed_model = embed_model
        return embed_model

    def generate_embedding(self, context):
        return self.embed_model.get_text_embedding_batch(context)
        
    def embed(self, contexts):
        
        self.contexts = contexts
        
        for batch_context in batch_iterate(contexts, self.batch_size):
            batch_embeddings = self.generate_embedding(batch_context)
            self.embeddings.extend(batch_embeddings)
        
class QdrantVectoreDBHandler:
    def __init__(self, collection_name, url="https://190f1475-3b3e-4e8b-b6ad-ff884b16eefb.eu-central-1-0.aws.cloud.qdrant.io", api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.JjPkzVLE7tNrtZR_X2YG1TaaAe6t7YE-y2RBmIQzGVs"):
        self.collection_name = collection_name
        self.url = url
        self.api_key = api_key
        self.client = None
        self.aclient = None
        self.index = None

    def define_client(self):
        """Defines the Qdrant client connection."""
        self.client = qdrant_client.QdrantClient(
            url=self.url,
            api_key=self.api_key,
            prefer_grpc=True
        )
        self.aclient =  qdrant_client.AsyncQdrantClient(
            url=self.url,
            api_key=self.api_key,
            prefer_grpc=True
        )

    def ingest_data(self, documents):
        """Ingests vectorized data into Qdrant."""
        vector_store = QdrantVectorStore(client=self.client, aclient=self.aclient, collection_name=self.collection_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        embed_model = EmbedData(embed_model_name="BAAI/bge-base-en-v1.5")._load_embed_model()
        Settings.embed_mode = embed_model
        index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, embed_model = embed_model,use_async=True)
        self.index = index
        return index

    async def query_data(self, query):
        """Queries the indexed data using a custom LLM."""
        query_engine = self.index.as_query_engine(llm=OllamaLLM()._load_llm_model(), use_async=True)
        response = await query_engine.aquery(query)
        return response
        
class StructuredDataSQLHandler:
    def __init__(self):
        """Initialize an in-memory SQL database for investment portfolio storage."""
        self.engine = create_engine("sqlite:///:memory:", future=True)
        self.async_engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)  
        self.metadata = MetaData()
        self.sql_database = None
        self.table_name = "investment_portfolio"
        self.table = None
        self.async_session = sessionmaker(
            bind=self.async_engine, class_=AsyncSession, expire_on_commit=False
        )

    def create_table(self, df: pd.DataFrame):
        """Dynamically creates a table based on uploaded CSV/Excel headers."""
        columns = [Column("id", Integer, primary_key=True, autoincrement=True)]
        
        # Define columns dynamically based on DataFrame headers
        for col in df.columns:
            if df[col].dtype == 'int64':
                columns.append(Column(col, Integer))
            elif df[col].dtype == 'float64':
                columns.append(Column(col, Float))
            else:
                columns.append(Column(col, String))

        # Create table dynamically
        self.table = Table(self.table_name, self.metadata, *columns)
        self.metadata.create_all(self.engine)
      

    def insert_data(self, df: pd.DataFrame):
        """Inserts uploaded data into the dynamically created SQL table."""
        if self.table is None:
            self.create_table(df)  # Ensure table is created

        # Convert DataFrame to dictionary format for insertion
        with self.engine.connect() as connection:
            connection.execute(self.table.insert(), df.to_dict(orient="records"))
            connection.commit()

        # Initialize SQLDatabase for querying
        self.sql_database = SQLDatabase(self.engine)

    def query_data(self, sql_query: str):
        """Executes a SQL query and returns the result."""
        if self.sql_database:
            return self.sql_database.run_sql(sql_query)
        return "No data available. Please upload a file first."
    
    async def sql_tool(self, user_question: str):
        """Takes a natural language query and returns SQL query results."""
        if self.sql_database is None:
            self.sql_database = SQLDatabase(self.engine, include_tables=[self.table_name])

        # Creating an instance of the NLSQLTableQueryEngine
        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=self.sql_database,
            tables=[self.table_name],
            llm = OllamaLLM()._load_llm_model(),
            embed_model = EmbedData()._load_embed_model()
        )

        # Execute the query
        result = sql_query_engine.query(user_question)
        
        return result

    async def async_sql_tool(self, query: str):
        """Asynchronously executes a SQL query and fetches results."""
        async with self.async_session() as session:
            result = await session.execute(select(self.table).where(text(query)))
            return result.fetchall()
    def fetch_schema(self):
        """Fetches and returns the database schema."""
        inspector = inspect(self.engine)
        schema_info = {}
        
        for column in inspector.get_columns(self.table_name):
            schema_info[column['name']] = {
                'type': str(column['type']),
                'nullable': column['nullable']
            }
        
        return schema_info

class OllamaLLM:
    """Custom LLM Wrapper for Ollama"""

    def __init__(self, model="Meta-Llama-3.1-8B-Instruct"):
        self.client = OpenAI(
            base_url="https://api.sambanova.ai/v1",
            api_key=api_key
        )
        self.model = model
        self.llm_model = SambaNovaCloud(
                        model="Meta-Llama-3.1-405B-Instruct",
                        temperature=0.7,
                        context_window=100000,
                        api_key=os.environ["SAMBANOVA_API_KEY"]
                    )
        # self.llm_model = Ollama(model=self.llm_name,
        #               temperature=0.7,
        #               context_window=100000,
        #             )

    def _load_llm_model(self):
        """Loads the custom LLM instance."""
        return self.llm_model

    async def achat_with_tools(self,tools, chat_history,verbose=False,allow_parallel_tool_calls=False):  # Make this async
        """Asynchronous chat method using OpenAI API."""
       
        # Construct the prompt with tool descriptions

        tool_descriptions = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])

        prompt = f"""
          You are an AI assistant with tool-calling capabilities. 
          Available tools:
          {tool_descriptions}

          Chat History:
          {chat_history[-5:]}

          User Query:
          {chat_history[-1].content}

          If a tool is required, return JSON in format JSON```(.*?)``` like: JSON```{{"tool_name": "<name>", "tool_args": {{...}}}}```
          
          Otherwise, provide a direct answer.
        """

        response = self.client.chat.completions.create(  # Use await here
            model=self.model,
            messages=chat_history+[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def get_tool_calls_from_response(self, chat_res, error_on_no_tool_call=False):
        """Extracts tool calls from a response (dummy implementation)."""
        
        def extract_tool_calls(response_text):
            """Extracts tool calls from the LLM response JSON string."""
            # Remove backticks (`) and extract JSON content
            matches = re.findall(r'```(.*?)```', response_text, re.DOTALL)
            
            tool_calls = []
            for match in matches:
                try:
                    tool_call = json.loads(match.strip())  # Convert JSON string to dictionary
                    if "tool_name" in tool_call and "tool_args" in tool_call:
                        tool_calls.append(tool_call)
                except json.JSONDecodeError:
                    continue  # Skip invalid JSON
                
            return tool_calls

        # Extract tool calls
        chat_res = extract_tool_calls(chat_res)
        # print("Extracted tool call = ", chat_res)
        try:
            tool_call_data = []
            for tool in chat_res:
                tool_call_data += [ToolSelection(
                    tool_id=tool.get("tool_id", "default_tool_id"),  # Ensure tool_id exists
                    tool_name=tool["tool_name"], 
                    tool_kwargs=tool.get("tool_args", {})  # Default to empty dict if missing
                )]
            return tool_call_data
        except json.JSONDecodeError:
            if error_on_no_tool_call:
                raise ValueError("Invalid tool response format")
        return []
    
    async def chatbot_tool(self, **kwargs):  # Accept dynamic arguments
        """Asynchronous chat method"""

        # Extract the user query dynamically
        user_query = kwargs.get("input_text") or kwargs.get("query") or kwargs.get("question")  # Handle different keys

        if not user_query:
            return "Error: No valid user query found."

        # Construct the prompt
        prompt = f"""
          You are an AI assistant that replies to user questions.
          reply the user question - {user_query}
        """

        # Await the response properly
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content
    
    async def asummarizer(self, chat_history, verbose=False):  
        """Asynchronous summarizer using OpenAI API."""
             
        # Construct the prompt for summarization
        prompt = f"""
        You are an AI assistant that provides concise summaries of conversations.

         Chat History:
        {chat_history[-5:]}

        User Query:
        {chat_history[-1].content}
        
        Note :- Your response should only be focused on reply of user question. Based on the chat history provied. 
        
        Don't mention tools just use the information provided to answer user question.

        **Task:** 
        Summarize the conversation in a clear and concise manner, keeping key points and responses intact.
        """

        try:
          response = self.client.chat.completions.create(
              model=self.model,
              messages=[{"role": "user", "content": prompt}]
          )
          return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            # Handle the error appropriately, e.g., return an empty summary or retry
            return "Hi I am facing error with the llm call"
        # Call OpenAI API asynchronously
        
        # Extract summarized content
        summary = response.choices[0].message.content
        
        return summary
    