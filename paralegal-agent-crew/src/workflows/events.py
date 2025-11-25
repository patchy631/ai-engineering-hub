from typing import List, Optional
from pydantic import BaseModel
from src.retrieval.retriever_rerank import NodeWithScore

class RetrieveEvent(BaseModel):
    """Event containing retrieved nodes from vector database."""
    retrieved_nodes: List[NodeWithScore]
    query: str

class EvaluateEvent(BaseModel): 
    """Event for evaluating RAG response quality."""
    rag_response: str
    retrieved_nodes: List[NodeWithScore]
    query: str

class WebSearchEvent(BaseModel):
    """Event for web search when RAG response is insufficient."""
    rag_response: str
    query: str
    search_results: Optional[str] = None

class SynthesizeEvent(BaseModel):
    """Event for final response synthesis."""
    rag_response: str
    retrieved_nodes: List[NodeWithScore]
    query: str
    web_search_results: Optional[str] = None
    use_web_results: bool = False