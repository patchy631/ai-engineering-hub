import pixeltable as pxt
import os
from mcp.server.fastmcp import FastMCP
from pixeltable.functions.openai import vision
from pixeltable.functions.huggingface import sentence_transformer

mcp = FastMCP("Pixeltable")

# Base directory for all indexes
DIRECTORY = 'image_search'

# Registry to hold all image indexes
image_indexes = {}


def _get_openai_api_key() -> str:
    """Get OpenAI API key from environment variables.
    
    Returns:
        The OpenAI API key
        
    Raises:
        ValueError: If the API key is not found
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key


@mcp.tool()
def setup_image_index(table_name: str) -> str:
    """Set up an image index with the provided name and OpenAI API key.

    Args:
        table_name: The name of the image index (e.g., 'photos', 'artwork').

    Returns:
        A message indicating whether the index was created, already exists, or failed.
    """
    global image_indexes

    # Construct full table name
    full_table_name = f'{DIRECTORY}.{table_name}'

    try:
        # Set the API key
        openai_api_key = _get_openai_api_key()
        os.environ['OPENAI_API_KEY'] = openai_api_key

        # Check if the table already exists
        existing_tables = pxt.list_tables()
        if full_table_name in existing_tables:
            image_index = pxt.get_table(full_table_name)
            image_indexes[full_table_name] = image_index
            return f"Image index '{full_table_name}' already exists and is ready for use."

        # Create directory and table
        pxt.create_dir(DIRECTORY, if_exists='ignore')
        image_index = pxt.create_table(
            full_table_name, 
            {'image_file': pxt.Image},
            if_exists='ignore'
        )

        # Add GPT-4 Vision analysis
        image_index.add_computed_column(
            image_description=vision(
                prompt="Describe the image. Be specific on the colors you see.",
                image=image_index.image_file,
                model="gpt-4o-mini"
            )
        )

        # Define the embedding model and create embedding index
        embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')
        image_index.add_embedding_index(
            column='image_description', 
            string_embed=embed_model,
            if_exists='ignore'
        )

        # Store in the registry
        image_indexes[full_table_name] = image_index
        return f"Image index '{full_table_name}' created successfully."
    except Exception as e:
        return f"Error setting up image index '{full_table_name}': {str(e)}"

@mcp.tool()
def insert_image(table_name: str, image_location: str) -> str:
    """Insert an image file into the specified image index.

    Args:
        table_name: The name of the image index (e.g., 'photos', 'artwork').
        image_location: The URL or path to the image file to insert (e.g., local path or URL).

    Returns:
        A confirmation message indicating success or failure.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in image_indexes:
            return f"Error: Image index '{full_table_name}' not set up. Please call setup_image_index first."
        image_index = image_indexes[full_table_name]
        image_index.insert([{'image_file': image_location}])
        return f"Image file '{image_location}' inserted successfully into index '{full_table_name}'."
    except Exception as e:
        return f"Error inserting image file into '{full_table_name}': {str(e)}"

@mcp.tool()
def query_image(table_name: str, query_text: str, top_n: int = 5) -> str:
    """Query the specified image index with a text description.

    Args:
        table_name: The name of the image index (e.g., 'photos', 'artwork').
        query_text: The text description to search for in the image descriptions.
        top_n: Number of top results to return (default is 5).

    Returns:
        A string containing the top matching images and their similarity scores.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in image_indexes:
            return f"Error: Image index '{full_table_name}' not set up. Please call setup_image_index first."
        image_index = image_indexes[full_table_name]
        
        # Calculate similarity scores
        sim = image_index.image_description.similarity(query_text)

        # Get top results
        results = (image_index.order_by(sim, asc=False)
                  .select(image_index.image_file, image_index.image_description, sim=sim)
                  .limit(top_n)
                  .collect())

        # Format the results
        result_str = f"Query Results for '{query_text}' in '{full_table_name}':\n\n"
        for i, row in enumerate(results.to_pandas().itertuples(), 1):
            result_str += f"{i}. Score: {row.sim:.4f}\n"
            result_str += f"   Description: {row.image_description}\n"
            result_str += f"   Image: {row.image_file}\n\n"
        
        return result_str if result_str else "No results found."
    except Exception as e:
        return f"Error querying image index '{full_table_name}': {str(e)}"

@mcp.tool()
def list_image_tables() -> str:
    """List all image indexes currently available.

    Returns:
        A string listing the current image indexes.
    """
    tables = pxt.list_tables()
    image_tables = [t for t in tables if t.startswith(f'{DIRECTORY}.')]
    return f"Current image indexes: {', '.join(image_tables)}" if image_tables else "No image indexes exist."