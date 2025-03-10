from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from config.settings import (
    LLAMACLOUD_PROJECT_NAME,
    LLAMACLOUD_MODEL_NAME,
    SIMILARITY_TOP_K,
    LLAMACLOUD_API_KEY,
    LLAMACLOUD_INDEX_NAME,
    LLAMACLOUD_ORG_ID
)

def create_rag_tool():
    # Initialize LlamaCloud index
    index = LlamaCloudIndex(
        name=LLAMACLOUD_INDEX_NAME,
        project_name=LLAMACLOUD_PROJECT_NAME,
        organization_id=LLAMACLOUD_ORG_ID,
        api_key=LLAMACLOUD_API_KEY
    )
    
    # Create query engine from the index
    llama_cloud_engine = index.as_query_engine()
    
    return QueryEngineTool(
        query_engine=llama_cloud_engine,
        metadata=ToolMetadata(
            name="llama_cloud_tool",
            description=(
                "Use this tool for querying detailed information about US cities including: "
                "historical names, cultural information, landmarks, tourist attractions, "
                "transportation systems, and other general information from Wikipedia. "
                "Available cities: New York City, Los Angeles, Chicago, Houston, Miami, and Seattle."
            )
        )
    ) 