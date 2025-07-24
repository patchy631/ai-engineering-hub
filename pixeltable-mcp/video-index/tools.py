import pixeltable as pxt
import os
from mcp.server.fastmcp import FastMCP
from pixeltable.functions import openai
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter
from pixeltable.iterators.string import StringSplitter
from datetime import datetime

mcp = FastMCP("Pixeltable")

# Base directory for all indexes
DIRECTORY = 'video_index'

# Registry to hold all video indexes
video_indexes = {}


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
def setup_video_index(table_name: str) -> str:
    """Set up a video index with the provided name and OpenAI API key.

    Args:
        table_name: The name of the video index (e.g., 'lectures', 'interviews').

    Returns:
        A message indicating whether the index was created, already exists, or failed.
    """
    global video_indexes

    # Construct full table and view names
    full_table_name = f'{DIRECTORY}.{table_name}'
    chunks_view_name = f'{DIRECTORY}.{table_name}_chunks'
    sentences_view_name = f'{DIRECTORY}.{table_name}_sentence_chunks'
    
    try:
        # Set the API key
        openai_api_key = _get_openai_api_key()
        os.environ['OPENAI_API_KEY'] = openai_api_key

        # Check if the table already exists
        existing_tables = pxt.list_tables()
        if full_table_name in existing_tables:
            video_index = pxt.get_table(full_table_name)
            chunks_view = pxt.get_table(chunks_view_name)
            sentences_view = pxt.get_table(sentences_view_name)
            video_indexes[full_table_name] = (video_index, chunks_view, sentences_view)
            return f"Video index '{full_table_name}' already exists and is ready for use."

        # Create directory and table
        pxt.create_dir(DIRECTORY, if_exists='ignore')
        video_index = pxt.create_table(
            full_table_name, 
            {'video_file': pxt.Video, 'uploaded_at': pxt.Timestamp},
            if_exists='ignore'
        )

        # Extract audio from video
        video_index.add_computed_column(
            audio_extract=extract_audio(video_index.video_file, format='mp3')
        )

        # Create view for audio chunks
        chunks_view = pxt.create_view(
            chunks_view_name,
            video_index,
            iterator=AudioSplitter.create(
                audio=video_index.audio_extract,
                chunk_duration_sec=30.0,
                overlap_sec=2.0,
                min_chunk_duration_sec=5.0
            ),
            if_exists='ignore'
        )

        # Add transcription to chunks
        chunks_view.add_computed_column(
            transcription=openai.transcriptions(audio=chunks_view.audio_chunk, model='whisper-1')
        )

        # Create view that chunks transcriptions into sentences
        sentences_view = pxt.create_view(
            sentences_view_name,
            chunks_view,
            iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
            if_exists='ignore'
        )

        # Define the embedding model and create embedding index
        embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')
        sentences_view.add_embedding_index(column='text', string_embed=embed_model)

        # Store in the registry
        video_indexes[full_table_name] = (video_index, chunks_view, sentences_view)
        return f"Video index '{full_table_name}' created successfully."
    except Exception as e:
        return f"Error setting up video index '{full_table_name}': {str(e)}"

@mcp.tool()
def insert_video(table_name: str, video_location: str) -> str:
    """Insert a video file into the specified video index.

    Args:
        table_name: The name of the video index (e.g., 'lectures', 'interviews').
        video_location: The URL or path to the video file to insert (e.g., local path or S3 URL).

    Returns:
        A confirmation message indicating success or failure.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in video_indexes:
            return f"Error: Video index '{full_table_name}' not set up. Please call setup_video_index first."
        video_index, _, _ = video_indexes[full_table_name]
        video_index.insert([{'video_file': video_location, 'uploaded_at': datetime.now()}])
        return f"Video file '{video_location}' inserted successfully into index '{full_table_name}'."
    except Exception as e:
        return f"Error inserting video file into '{full_table_name}': {str(e)}"

@mcp.tool()
def query_video(table_name: str, query_text: str, top_n: int = 5) -> str:
    """Query the specified video index with a text question.

    Args:
        table_name: The name of the video index (e.g., 'lectures', 'interviews').
        query_text: The question or text to search for in the video content.
        top_n: Number of top results to return (default is 5).

    Returns:
        A string containing the top matching sentences and their similarity scores.
    """
    full_table_name = f'{DIRECTORY}.{table_name}'
    try:
        if full_table_name not in video_indexes:
            return f"Error: Video index '{full_table_name}' not set up. Please call setup_video_index first."
        _, _, sentences_view = video_indexes[full_table_name]
        # Calculate similarity scores between query and sentences
        sim = sentences_view.text.similarity(query_text)

        # Get top results
        results = (sentences_view.order_by(sim, asc=False)
                  .select(sentences_view.text, sim=sim, video_file=sentences_view.video_file, 
                         uploaded_at=sentences_view.uploaded_at)
                  .limit(top_n)
                  .collect())

        # Format the results
        result_str = f"Query Results for '{query_text}' in '{full_table_name}':\n\n"
        for i, row in enumerate(results.to_pandas().itertuples(), 1):
            result_str += f"{i}. Score: {row.sim:.4f}\n"
            result_str += f"   Text: {row.text}\n"
            result_str += f"   From video: {row.video_file}\n"
            result_str += f"   Uploaded: {row.uploaded_at}\n\n"
        
        return result_str if result_str else "No results found."
    except Exception as e:
        return f"Error querying video index '{full_table_name}': {str(e)}"

@mcp.tool()
def list_video_tables() -> str:
    """List all video indexes currently available.

    Returns:
        A string listing the current video indexes.
    """
    tables = pxt.list_tables()
    video_tables = [t for t in tables if t.startswith(f'{DIRECTORY}.')]
    return f"Current video indexes: {', '.join(video_tables)}" if video_tables else "No video indexes exist."