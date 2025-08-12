from mcp.server.fastmcp import FastMCP
from main import clear_index, ingest_data, retrieve_data, chunk_video

mcp = FastMCP("ragie")

@mcp.tool()
def ingest_data_tool(directory: str) -> None:
    """
    Loads data from a directory into the Ragie index. Wait until the data is fully ingested before continuing.

    Args:
        directory (str): The directory to load data from.

    Returns:
        str: A message indicating that the data was loaded successfully.
    """
    try:
        clear_index()
        ingest_data(directory)
        return "Data loaded successfully"   
    except Exception as e:
        return f"Failed to load data: {str(e)}"

@mcp.tool()
def retrieve_data_tool(query: str) -> list[dict]:
    """
    Retrieves data from the Ragie index based on the query. The data is returned as a list of dictionaries, each containing the following keys:
    - text: The text of the retrieved chunk
    - document_name: The name of the document the chunk belongs to
    - start_time: The start time of the chunk
    - end_time: The end time of the chunk

    Args:
        query (str): The query to retrieve data from the Ragie index.

    Returns:
        list[dict]: The retrieved data.
    """
    try:
        content = retrieve_data(query)
        return content
    except Exception as e:
        return f"Failed to retrieve data: {str(e)}"

@mcp.tool()
def show_video_tool(document_name: str, start_time: float, end_time: float) -> str:
    """
    Creates and saves a video chunk based on the document name, start time, and end time of the chunk.
    Returns a message indicating that the video chunk was created successfully.

    Args:
        document_name (str): The name of the document the chunk belongs to
        start_time (float): The start time of the chunk
        end_time (float): The end time of the chunk

    Returns:
        str: A message indicating that the video chunk was created successfully
    """
    try:
        chunk_video(document_name, start_time, end_time)
        return "Video chunk created successfully"
    except Exception as e:
        return f"Failed to create video chunk: {str(e)}"

# Run the server locally
if __name__ == "__main__":
    mcp.run(transport='stdio')