import os
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.tools import QueryEngineTool

def retrieve_rag_tool():
    """
    Retrieve the RAG tool from the Llama Cloud Index after creating the index 
    for uploaded documents. Uses API credentials stored in environment variables.

    Returns:
        QueryEngineTool: Configured query engine tool instance.
    
    Raises:
        ValueError: If API credentials are missing.
        Exception: If any issue occurs while initializing the Llama Cloud Index.
    """
    # Retrieve API credentials from environment variables
    organization_id = os.getenv("LLAMA_CLOUD_ORG_ID")
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")

    if not organization_id or not api_key:
        raise ValueError("Missing LLAMA_CLOUD_ORG_ID or LLAMA_CLOUD_API_KEY environment variable.")

    # Initialize Llama Cloud Index
    index = LlamaCloudIndex(
        name="text2sql-with-rag", 
        project_name="Default",
        organization_id=organization_id,
        api_key=api_key
    )

    # Convert index to a query engine
    query_engine = index.as_query_engine()

    # Define and return the query tool
    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        description="Useful for answering semantic questions about certain cities in the US.",
        name="llama_cloud_tool"
    )