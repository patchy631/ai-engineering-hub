# Required imports
from sqlalchemy import create_engine
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    SQLDatabase,
    PromptTemplate,
)
from llama_index.core.tools import QueryEngineTool
from llama_index.core.query_engine import NLSQLTableQueryEngine
import qdrant_client
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore


#####################################
# Define Tools for Router Agent
#####################################
def setup_sql_tool():
    """Setup SQL query tool for querying city database."""
    # Setup SQLite database
    db_path = "city_database.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    sql_database = SQLDatabase(engine)

    # Create SQL query engine
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"],
    )

    # Create tool for SQL querying
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for translating a natural language query into a SQL query over"
            " a table containing: city_stats, containing the population/state of"
            " each city located in the USA."
        ),
        name="sql_tool",
    )

    # Return the SQL tool
    return sql_tool


def setup_document_tool(file_dir):
    """Setup document query tool from uploaded documents."""
    # Create a reader and load the data
    loader = SimpleDirectoryReader(
        input_dir=file_dir, required_exts=[".pdf"], recursive=True
    )
    docs = loader.load_data()

    # Creating a vector index over loaded data
    client = qdrant_client.QdrantClient(host="localhost", port=6333)
    vector_store = QdrantVectorStore(client=client, collection_name="rag_and_sql")
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    vector_index = VectorStoreIndex.from_documents(
        docs, show_progress=True, storage_context=storage_context
    )
    # vector_index = VectorStoreIndex.from_documents(docs, show_progress=True)

    # custome prompt template
    template = (
        "You are a knowledgeable assistant helping with information retrieval from documents. "
        "Based on the following context:\n"
        "-----------------------------------------\n"
        "{context_str}\n"
        "-----------------------------------------\n"
        "Please answer the question: {query_str}\n\n"
        "If the answer is not in the context, say 'I don't have enough information to answer this question.' "
        "Be concise and accurate in your response."
    )
    qa_template = PromptTemplate(template)

    # Create a query engine for the vector index
    docs_query_engine = vector_index.as_query_engine(
        text_qa_template=qa_template, similarity_top_k=3, streaming=True
    )

    # Create tool for document querying
    cities = ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"]
    docs_tool = QueryEngineTool.from_defaults(
        query_engine=docs_query_engine,
        description=(
            f"Useful for answering semantic questions about these US cities: {', '.join(cities)}."
        ),
        name="document_tool",
    )

    # Return the document tool
    return docs_tool
