import pixeltable as pxt
from mcp.server.fastmcp import FastMCP
from pixeltable.iterators import DocumentSplitter
from pixeltable.functions.huggingface import sentence_transformer

mcp = FastMCP("Pixeltable")

# Base directory for all indexes
DIRECTORY = 'doc_search'

# Registry to hold all document indexes
document_indexes = {}

@mcp.tool()
def setup_document_index(table_name: str) -> str:
    """Set up a document index with the provided name.

    Args:
        table_name: The name of the document index (e.g., 'reports', 'articles').

    Returns:
        A message indicating whether the index was created, already exists, or failed.
    """
    global document_indexes
    try:
        # Construct full table and view names
        full_table_name = f'{DIRECTORY}.{table_name}'
        chunks_view_name = f'{DIRECTORY}.{table_name}_chunks'

        # Check if the table already exists
        existing_tables = pxt.list_tables()
        if full_table_name in existing_tables:
            document_index = pxt.get_table(full_table_name)
            chunks_view = pxt.get_table(chunks_view_name)
            document_indexes[full_table_name] = (document_index, chunks_view)
            return f"Document index '{full_table_name}' already exists and is ready for use."

        # Create directory and table
        pxt.create_dir(DIRECTORY, if_exists='ignore')
        document_index = pxt.create_table(
            full_table_name,
            {'pdf_file': pxt.Document},
            if_exists='ignore'
        )

        # Create view for document chunks
        chunks_view = pxt.create_view(
            chunks_view_name,
            document_index,
            iterator=DocumentSplitter.create(
                document=document_index.pdf_file,
                separators='token_limit',
                limit=300  # Tokens per chunk
            ),
            if_exists='ignore'
        )

        # Define the embedding model and create embedding index
        embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')
        chunks_view.add_embedding_index(
            column='text',
            string_embed=embed_model,
            if_exists='ignore'
        )

        # Store in the registry
        document_indexes[full_table_name] = (document_index, chunks_view)
        return f"Document index '{full_table_name}' created successfully."
    except Exception as e:
        return f"Error setting up document index '{full_table_name}': {str(e)}"

@mcp.tool()
def insert_document(table_name: str, document_location: str) -> str:
    """Insert a document file into the specified document index.

    Args:
        table_name: The name of the document index (e.g., 'reports', 'articles').
        document_location: The URL or path to the document file to insert (e.g., local path or URL).

    Returns:
        A confirmation message indicating success or failure.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in document_indexes:
            return f"Error: Document index '{full_table_name}' not set up. Please call setup_document_index first."
        document_index, _ = document_indexes[full_table_name]
        document_index.insert([{'pdf_file': document_location}])
        return f"Document file '{document_location}' inserted successfully into index '{full_table_name}'."
    except Exception as e:
        return f"Error inserting document file into '{full_table_name}': {str(e)}"

@mcp.tool()
def query_document(table_name: str, query_text: str, top_n: int = 5) -> str:
    """Query the specified document index with a text question.

    Args:
        table_name: The name of the document index (e.g., 'reports', 'articles').
        query_text: The question or text to search for in the document content.
        top_n: Number of top results to return (default is 5).

    Returns:
        A string containing the top matching text chunks and their similarity scores.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in document_indexes:
            return f"Error: Document index '{full_table_name}' not set up. Please call setup_document_index first."
        _, chunks_view = document_indexes[full_table_name]
        
        # Calculate similarity scores
        sim = chunks_view.text.similarity(query_text)

        # Get top results
        results = (chunks_view.order_by(sim, asc=False)
                  .select(chunks_view.text, sim=sim)
                  .limit(top_n)
                  .collect())

        # Format the results
        result_str = f"Query Results for '{query_text}' in '{full_table_name}':\n\n"
        for i, row in enumerate(results.to_pandas().itertuples(), 1):
            result_str += f"{i}. Score: {row.sim:.4f}\n"
            result_str += f"   Text: {row.text}\n\n"
        
        return result_str if result_str else "No results found."
    except Exception as e:
        return f"Error querying document index '{full_table_name}': {str(e)}"

@mcp.tool()
def list_document_tables() -> str:
    """List all document indexes currently available.

    Returns:
        A string listing the current document indexes.
    """
    tables = pxt.list_tables()
    document_tables = [t for t in tables if t.startswith(f'{DIRECTORY}.')]
    return f"Current document indexes: {', '.join(document_tables)}" if document_tables else "No document indexes exist."