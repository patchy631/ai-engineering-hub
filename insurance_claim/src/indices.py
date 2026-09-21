import os
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.vector_stores.types import MetadataFilters

# Check for required environment variables
if "LLAMA_ORG_ID" not in os.environ or "LLAMA_API_KEY" not in os.environ:
    raise EnvironmentError("Missing required environment variables: LLAMA_ORG_ID or LLAMA_API_KEY")

# Index for general auto insurance policies
index = LlamaCloudIndex(
    name="auto_insurance_policies_0",
    project_name="Daily_Dose_of_DS",
    organization_id=os.environ["LLAMA_ORG_ID"],
    api_key=os.environ["LLAMA_API_KEY"]
)
retriever = index.as_retriever(rerank_top_n=3)

# Index for declarations pages
declarations_index = LlamaCloudIndex(
    name="auto_insurance_declarations_0",
    project_name="Daily_Dose_of_DS",
    organization_id=os.environ["LLAMA_ORG_ID"],
    api_key=os.environ["LLAMA_API_KEY"]
)

def get_declarations_docs(policy_number: str, top_k: int = 1):
    """
    Retrieve declarations docs for the given policy using metadata filtering.
    
    Args:
        policy_number: The policy number to filter by
        top_k: Number of top results to return (default: 1)
        
    Returns:
        List of retrieved documents that match the policy number
        
    Raises:
        ValueError: If policy_number is empty
        Exception: If retrieval fails
    """
    if not policy_number:
        raise ValueError("Policy number cannot be empty")
        
    filters = MetadataFilters.from_dicts([
        {"key": "policy_number", "value": policy_number}
    ])
    retriever = declarations_index.as_retriever(
        retrieval_mode="files_via_metadata",
        rerank_top_n=top_k,
        filters=filters
    )
    try:
        results = retriever.retrieve(f"declarations page for {policy_number}")
        if not results:
            print(f"Warning: No declarations found for policy number {policy_number}")
        return results
    except Exception as e:
        print(f"Error retrieving declarations: {e}")
        raise