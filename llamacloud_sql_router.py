# -*- coding: utf-8 -*-
"""llamacloud_sql_router.py"""

# Standard library imports
import asyncio
import os
import sys
import logging

# Third-party imports
from sentence_transformers import SentenceTransformer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import VectorStoreIndex, Settings, SQLDatabase
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, text
from llama_index.readers.file import PDFReader
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step
from typing import List, Optional
import streamlit as st

# Set up logging
log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Ensure compatibility with Windows event loop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load the Hugging Face model
model_path = "E:/huggingface_models/all-MiniLM-L6-v2"  # Use local path
try:
    hf_model = SentenceTransformer(model_path)
    Settings.embed_model = HuggingFaceEmbedding(model_name=model_path)
    logger.info("✅ Hugging Face model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Error loading Hugging Face model: {e}")
    sys.exit(1)

# Load Ollama model with retry logic
async def load_ollama_model(max_retries=3, retry_delay=5):
    retries = 0
    while retries < max_retries:
        try:
            Settings.llm = Ollama(model="mistral", request_timeout=300)
            logger.info("✅ Ollama model loaded successfully!")
            return True
        except Exception as e:
            retries += 1
            logger.error(f"❌ Error loading Ollama model (attempt {retries}/{max_retries}): {e}")
            if retries >= max_retries:
                logger.error("Make sure Ollama is running and the Mistral model is available.")
                return False
            logger.info(f"Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
    return False

# Run Ollama loading
if not asyncio.run(load_ollama_model()):
    sys.exit(1)

logger.info("✅ Model Loaded Successfully!")

# Create SQL Database in Memory
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

# Create city SQL table
city_stats_table = Table(
    "city_stats",
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

# Create the table
try:
    metadata_obj.create_all(engine)
    logger.info("✅ 'city_stats' table created successfully!")
except Exception as e:
    logger.error(f"❌ Error creating 'city_stats' table: {e}")
    sys.exit(1)

# Insert Data using bulk insert
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]

try:
    with engine.begin() as connection:
        connection.execute(insert(city_stats_table), rows)
    logger.info("✅ Data inserted into 'city_stats' table successfully!")
except Exception as e:
    logger.error(f"❌ Error inserting data into 'city_stats' table: {e}")
    sys.exit(1)

# Verify table exists using SQLAlchemy
from sqlalchemy import inspect

inspector = inspect(engine)
if "city_stats" not in inspector.get_table_names():
    logger.error("❌ Error: 'city_stats' table not found in SQL database.")
    sys.exit(1)
else:
    logger.info("✅ 'city_stats' table verified in the database.")

# SQL Query Engine
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])

# Test SQL Query
test_query = "SELECT * FROM city_stats;"
try:
    with engine.connect() as connection:
        result = connection.execute(text(test_query)).fetchall()
        logger.info(f"✅ Test SQL query executed successfully. Result: {result}")
except Exception as e:
    logger.error(f"❌ Error executing test SQL query: {e}")
    sys.exit(1)

# Define the absolute paths to the PDF files
pdf_files = [
    r"E:\rag and sql\New York City - Wikipedia.pdf",
    r"E:\rag and sql\Chicago - Wikipedia.pdf",
    r"E:\rag and sql\Houston - Wikipedia.pdf",
    r"E:\rag and sql\Seattle - Wikipedia.pdf",
    r"E:\rag and sql\Miami - Wikipedia.pdf"
]

# Load PDF Documents
documents = []
pdf_reader = PDFReader()
for pdf in pdf_files:
    if os.path.exists(pdf):
        logger.info(f"Loading PDF: {pdf}")
        try:
            documents.extend(pdf_reader.load_data(pdf))
        except Exception as e:
            logger.error(f"❌ Error loading PDF {pdf}: {e}")
    else:
        logger.warning(f"⚠️ PDF file not found: {pdf}")

# Log the number of documents loaded
logger.info(f"✅ Loaded {len(documents)} documents.")

# Create Local Vector Index
if documents:
    index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model)
    llama_cloud_query_engine = index.as_query_engine()
    logger.info(f"✅ Vector index created with {len(documents)} documents")
else:
    logger.warning("⚠️ No documents loaded. Creating an empty index.")
    index = VectorStoreIndex.from_documents([], embed_model=Settings.embed_model)
    llama_cloud_query_engine = index.as_query_engine()

# Create Tools
sql_tool = QueryEngineTool.from_defaults(query_engine=sql_query_engine, name="sql_tool")
llama_cloud_tool = QueryEngineTool.from_defaults(query_engine=llama_cloud_query_engine, name="llama_cloud_tool")

# Custom Agent Workflow
class RouterOutputAgentWorkflow(Workflow):
    """Custom router output agent workflow."""

    def __init__(self, tools: List[QueryEngineTool], timeout: Optional[float] = 10.0, verbose: bool = False):
        """Constructor."""
        super().__init__(timeout=timeout, verbose=verbose)
        self.tools = tools
        self.tools_dict = {tool.metadata.name: tool for tool in self.tools}
        self.llm = Settings.llm
        self.chat_history = []

    @step()
    async def chat(self, ev: StartEvent) -> StopEvent:
        """Retrieve relevant data from SQL or RAG and return a response."""
        try:
            if not self.chat_history:
                self.chat_history.append(ChatMessage(role="user", content=ev.message))

            query = self.chat_history[-1].content

            # Route the query to the appropriate tool
            if "population" in query.lower() or "state" in query.lower():
                logger.info(f"Routing query to SQL tool: {query}")
                try:
                    result = await self.tools_dict["sql_tool"].query_engine.aquery(query)
                    logger.info(f"SQL query result: {result}")
                except Exception as e:
                    logger.error(f"❌ Error executing SQL query: {e}")
                    result = f"Error: Failed to retrieve data from the database. Details: {e}"
            else:
                logger.info(f"Routing query to RAG tool: {query}")
                try:
                    result = await self.tools_dict["llama_cloud_tool"].query_engine.aquery(query)
                    logger.info(f"RAG query result: {result}")
                except Exception as e:
                    logger.error(f"❌ Error executing RAG query: {e}")
                    result = f"Error: Failed to retrieve data from the knowledge base. Details: {e}"

            self.chat_history.append(ChatMessage(role="assistant", content=str(result)))
            return StopEvent(result=str(result))
        except Exception as e:
            logger.error(f"❌ Error in chat step: {e}")
            return StopEvent(result=f"Error: An unexpected error occurred. Details: {e}")

# Create and run the Workflow
verbose = os.environ.get("VERBOSE", "False").lower() == "true"
wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=verbose, timeout=600)

# Streamlit App
def main():
    st.set_page_config(page_title="RAG and Text-to-SQL", page_icon="📊", layout="wide")

    # Sidebar for instructions and query history
    with st.sidebar:
        st.header("Combining RAG and Text-to-SQL in a Single Query Interface")
        st.write("Ask any question, and AI will answer.")
        st.markdown("---")
        if "query_history" not in st.session_state:
            st.session_state.query_history = []
        if st.session_state.query_history:
            st.subheader("📜 Query History")
            for i, q in enumerate(st.session_state.query_history[-5:]):
                st.text(f"{i+1}. {q}")
        st.markdown("---")
        if st.button("Clear History"):
            st.session_state.query_history = []

    # Main content
    st.title("RAG and Text-to-SQL")
    query = st.text_input("💡 Enter your query:")

    async def get_response(query):
        if query:
            result = await wf.run(message=query)
            return result
        return None

    # Display response when button is clicked
    col1, col2 = st.columns([3, 1])
    with col2:
        get_answer = st.button("🚀 Get Answer")

    if get_answer:
        if query.strip():
            st.session_state.query_history.append(query)
            with st.spinner("🤖 Thinking..."):
                response = asyncio.run(get_response(query))
                if response:
                    st.toast("✅ Answered successfully")
                    st.write(response)
                else:
                    st.warning("⚠️ No data available for this query.")
        else:
            st.warning("⚠️ Please enter a query.")

if __name__ == "__main__":
    main()