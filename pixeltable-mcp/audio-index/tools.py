import os
import logging
from typing import Tuple, Dict, Any, Optional

import pixeltable as pxt
from mcp.server.fastmcp import FastMCP
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators import AudioSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('audio_index')

# Initialize MCP server
mcp = FastMCP("Pixeltable Audio Index")

# Constants
DIRECTORY = 'audio_index'
DEFAULT_CHUNK_DURATION = 30.0
DEFAULT_OVERLAP_DURATION = 2.0
DEFAULT_MIN_CHUNK_DURATION = 5.0
DEFAULT_EMBEDDING_MODEL = 'intfloat/e5-large-v2'
DEFAULT_WHISPER_MODEL = 'base.en'

# Registry to hold all audio indexes
# Format: {full_table_name: (audio_index, chunks_view, sentences_view)}
audio_indexes: Dict[str, Tuple[Any, Any, Any]] = {}


def _get_table_names(table_name: str) -> Tuple[str, str, str]:
    """Generate the full table and view names for a given table name.
    
    Args:
        table_name: Base name for the audio index
        
    Returns:
        Tuple of (full_table_name, chunks_view_name, sentences_view_name)
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    chunks_view_name = f'{DIRECTORY}.{table_name}_chunks'
    sentences_view_name = f'{DIRECTORY}.{table_name}_sentence_chunks'
    return full_table_name, chunks_view_name, sentences_view_name


def _load_existing_index(full_table_name: str, chunks_view_name: str, 
                         sentences_view_name: str) -> bool:
    """Load an existing audio index into the registry.
    
    Args:
        full_table_name: Full name of the audio index table
        chunks_view_name: Name of the chunks view
        sentences_view_name: Name of the sentences view
        
    Returns:
        True if the index was loaded successfully, False otherwise
    """
    try:
        audio_index = pxt.get_table(full_table_name)
        chunks_view = pxt.get_view(chunks_view_name)
        sentences_view = pxt.get_view(sentences_view_name)
        audio_indexes[full_table_name] = (audio_index, chunks_view, sentences_view)
        logger.info(f"Loaded existing audio index '{full_table_name}'")
        return True
    except Exception as e:
        logger.error(f"Failed to load existing audio index '{full_table_name}': {str(e)}")
        return False


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
def setup_audio_index(table_name: str) -> str:
    """Set up an audio index with the provided name and OpenAI API key.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').

    Returns:
        A message indicating whether the index was created, already exists, or failed.
    """
    global audio_indexes
    
    # Generate table names
    full_table_name, chunks_view_name, sentences_view_name = _get_table_names(table_name)
    
    try:
        # Set the API key
        openai_api_key = _get_openai_api_key()
        os.environ['OPENAI_API_KEY'] = openai_api_key
        logger.info(f"Setting up audio index '{full_table_name}'")

        # Check if the table already exists
        existing_tables = pxt.list_tables()
        if full_table_name in existing_tables:
            if _load_existing_index(full_table_name, chunks_view_name, sentences_view_name):
                return f"Audio index '{full_table_name}' already exists and is ready for use."
            else:
                return f"Audio index '{full_table_name}' exists but could not be loaded."

        # Create directory and table
        pxt.create_dir(DIRECTORY, if_exists='ignore')
        audio_index = pxt.create_table(full_table_name, {'audio_file': pxt.Audio}, if_exists='ignore')
        logger.info(f"Created audio index table '{full_table_name}'")

        # Create view for audio chunks
        chunks_view = pxt.create_view(
            chunks_view_name,
            audio_index,
            iterator=AudioSplitter.create(
                audio=audio_index.audio_file,
                chunk_duration_sec=DEFAULT_CHUNK_DURATION,
                overlap_sec=DEFAULT_OVERLAP_DURATION,
                min_chunk_duration_sec=DEFAULT_MIN_CHUNK_DURATION
            ),
            if_exists='ignore'
        )
        logger.info(f"Created audio chunks view '{chunks_view_name}'")

        # Add transcription to chunks
        chunks_view.add_computed_column(
            transcription=whisper.transcribe(audio=chunks_view.audio_chunk, model=DEFAULT_WHISPER_MODEL)
        )
        logger.info("Added transcription column to chunks view")

        # Create view that chunks transcriptions into sentences
        sentences_view = pxt.create_view(
            sentences_view_name,
            chunks_view,
            iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
            if_exists='ignore'
        )
        logger.info(f"Created sentence chunks view '{sentences_view_name}'")

        # Define the embedding model and create embedding index
        embed_model = sentence_transformer.using(model_id=DEFAULT_EMBEDDING_MODEL)
        sentences_view.add_embedding_index(column='text', string_embed=embed_model)
        logger.info("Added embedding index to sentence chunks view")

        # Store in the registry
        audio_indexes[full_table_name] = (audio_index, chunks_view, sentences_view)
        return f"Audio index '{full_table_name}' created successfully."
    except Exception as e:
        logger.error(f"Error setting up audio index '{full_table_name}': {str(e)}")
        return f"Error setting up audio index '{full_table_name}': {str(e)}"


@mcp.tool()
def insert_audio(table_name: str, audio_location: str) -> str:
    """Insert an audio file into the specified audio index.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').
        audio_location: The URL or path to the audio file to insert (e.g., local path or S3 URL).

    Returns:
        A confirmation message indicating success or failure.
    """
    full_table_name, _, _ = _get_table_names(table_name)
    
    try:
        if full_table_name not in audio_indexes:
            logger.warning(f"Audio index '{full_table_name}' not set up")
            return f"Error: Audio index '{full_table_name}' not set up. Please call setup_audio_index first."
            
        audio_index, _, _ = audio_indexes[full_table_name]
        audio_index.insert([{'audio_file': audio_location}])
        logger.info(f"Inserted audio file '{audio_location}' into index '{full_table_name}'")
        return f"Audio file '{audio_location}' inserted successfully into index '{full_table_name}'."
    except Exception as e:
        logger.error(f"Error inserting audio file into '{full_table_name}': {str(e)}")
        return f"Error inserting audio file into '{full_table_name}': {str(e)}"


@mcp.tool()
def query_audio(table_name: str, query_text: str, top_n: int = 5) -> str:
    """Query the specified audio index with a text question.

    Args:
        table_name: The name of the audio index (e.g., 'podcasts', 'interviews').
        query_text: The question or text to search for in the audio content.
        top_n: Number of top results to return (default is 5).

    Returns:
        A string containing the top matching sentences and their similarity scores.
    """
    full_table_name, _, _ = _get_table_names(table_name)
    
    try:
        if full_table_name not in audio_indexes:
            logger.warning(f"Audio index '{full_table_name}' not set up")
            return f"Error: Audio index '{full_table_name}' not set up. Please call setup_audio_index first."
            
        _, _, sentences_view = audio_indexes[full_table_name]
        
        # Calculate similarity scores between query and sentences
        logger.info(f"Querying '{full_table_name}' with: '{query_text}'")
        sim = sentences_view.text.similarity(query_text)

        # Get top results
        results = (sentences_view.order_by(sim, asc=False)
                  .select(sentences_view.text, sim=sim, audio_file=sentences_view.audio_file)
                  .limit(top_n)
                  .collect())

        # Format the results
        result_str = f"Query Results for '{query_text}' in '{full_table_name}':\n\n"
        for i, row in enumerate(results.to_pandas().itertuples(), 1):
            result_str += f"{i}. Score: {row.sim:.4f}\n"
            result_str += f"   Text: {row.text}\n"
            result_str += f"   From audio: {row.audio_file}\n\n"
        
        return result_str if len(results) > 0 else "No results found."
    except Exception as e:
        logger.error(f"Error querying audio index '{full_table_name}': {str(e)}")
        return f"Error querying audio index '{full_table_name}': {str(e)}"


@mcp.tool()
def list_audio_tables(random_string: str = "") -> str:
    """List all audio indexes currently available.

    Returns:
        A string listing the current audio indexes.
    """
    try:
        tables = pxt.list_tables()
        audio_tables = [t for t in tables if t.startswith(f'{DIRECTORY}.') and not (
            t.endswith('_chunks') or t.endswith('_sentence_chunks')
        )]
        
        if not audio_tables:
            return "No audio indexes exist."
            
        # Load any tables that exist but aren't in our registry
        for table in audio_tables:
            if table not in audio_indexes:
                table_name = table.split('.')[-1]
                _, chunks_view_name, sentences_view_name = _get_table_names(table_name)
                _load_existing_index(table, chunks_view_name, sentences_view_name)
                
        return f"Current audio indexes: {', '.join(audio_tables)}"
    except Exception as e:
        logger.error(f"Error listing audio indexes: {str(e)}")
        return f"Error listing audio indexes: {str(e)}"