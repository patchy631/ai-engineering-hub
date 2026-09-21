import os
import json
import nest_asyncio
from typing import List, Optional
from pydantic import BaseModel, Field
from llama_index.core.vector_stores.types import MetadataInfo, MetadataFilters

nest_asyncio.apply()

class ClaimInfo(BaseModel):
    """Extracted Insurance claim information."""
    claim_number: str
    policy_number: str
    claimant_name: str
    date_of_loss: str
    loss_description: str
    estimated_repair_cost: float
    vehicle_details: Optional[str] = None

#Let's define a class to load the data from indexes and retrieve declarations
class documents:
    policy_index = None
    declarations_index = None
    client = None
    retriever = None

    def __init__(self, policy_index, declarations_index, client): 
        self.policy_index = policy_index
        self.declarations_index = declarations_index
        self.client = client
        
    def load_data_index(self, documents):
        
        person_policy_map = {}
        for k,v in documents.items():
            claim_info = ClaimInfo.model_validate(v[2])
            policy_num = claim_info.policy_number
            person_policy_map[f"{v[1]}-declarations.md"] = policy_num

        pipeline_docs = self.client.pipelines.list_pipeline_documents(self.declarations_index.pipeline.id)
        for doc in pipeline_docs:
            doc.metadata["policy_number"] = person_policy_map[doc.metadata["file_name"]]
        upserted_docs = self.client.pipelines.upsert_batch_pipeline_documents(self.declarations_index.pipeline.id, request=pipeline_docs)

        return upserted_docs


    def get_declarations_docs(self, policy_number: str, top_k: int = 1):
        """Get declarations retriever."""
        self.retriever = self.declarations_index.as_retriever(
            rerank_top_n=top_k, 
        )

        return self.retriever.retrieve(f"{policy_number}")
    
    def get_policy_retriever(self):
        return self.policy_index.as_retriever(rerank_top_n=3)