from llama_index.core.vector_stores.types import (
    MetadataInfo,
    MetadataFilters,
)

import os 
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from dotenv import load_dotenv


load_dotenv()

llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")
org_id = os.getenv("ORGANIZATION_ID")


declarations_index = LlamaCloudIndex(
  name="auto_insurance_declarations", 
  project_name="ddods",
  organization_id=org_id,
  api_key=llama_cloud_api_key
)

def get_declarations_docs(policy_number: str, top_k: int = 1):
    """Get declarations retriever."""
    # build retriever and query engine
    filters = MetadataFilters.from_dicts([
        {"key": "policy_number", "value": policy_number}
    ])
    retriever = declarations_index.as_retriever(
        # TODO: do file-level retrieval
        # retrieval_mode="files_via_metadata", 
        rerank_top_n=top_k, 
        filters=filters
    )
    # semantic query matters less here
    return retriever.retrieve(f"declarations page for {policy_number}")