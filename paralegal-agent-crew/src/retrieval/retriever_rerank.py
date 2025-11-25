from typing import Optional
from loguru import logger
from pydantic import BaseModel, Field
from src.indexing.milvus_vdb import MilvusVDB
from src.embeddings.embed_data import EmbedData
from config.settings import settings

class TextNode(BaseModel):
    text: str
    id_: str
    metadata: dict | None = Field(default=None)

class NodeWithScore(BaseModel):
    node: TextNode
    score: float

class Retriever:
    def __init__(
        self, 
        vector_db: MilvusVDB, 
        embed_data: EmbedData, 
        top_k: int = None
    ):
        self.vector_db = vector_db
        self.embed_data = embed_data
        self.top_k = top_k or settings.top_k

    def search(self, query: str, top_k: Optional[int] = None):
        """Search for relevant documents using vector similarity."""
        if top_k is None:
            top_k = self.top_k

        # Generate query embedding and convert to binary
        query_embedding = self.embed_data.get_query_embedding(query)
        binary_query = self.embed_data.binary_quantize_query(query_embedding)

        # Perform vector search
        search_results = self.vector_db.search(
            binary_query=binary_query,
            top_k=top_k,
            output_fields=["context"]
        )

        # Convert to NodeWithScore objects
        nodes_with_scores = []
        for result in search_results:
            node = TextNode(
                text=result["payload"]["context"],
                id_=str(result["id"])
            )
            node_with_score = NodeWithScore(
                node=node,
                score=result["score"]
            )
            nodes_with_scores.append(node_with_score)

        # logger.info(f"Retrieved {len(nodes_with_scores)} results for query")
        return nodes_with_scores

    def get_contexts(self, query: str, top_k: Optional[int] = None):
        nodes_with_scores = self.search(query, top_k)
        return [node.node.text for node in nodes_with_scores]

    def get_combined_context(self, query: str, top_k: Optional[int] = None):
        contexts = self.get_contexts(query, top_k)
        return "\n\n---\n\n".join(contexts)

    def search_with_scores(self, query: str, top_k: Optional[int] = None):
        nodes_with_scores = self.search(query, top_k)
        
        results = []
        for node_with_score in nodes_with_scores:
            results.append({
                "context": node_with_score.node.text,
                "score": node_with_score.score,
                "node_id": node_with_score.node.id_,
                "metadata": node_with_score.node.metadata or {}
            })
        
        return results

    def get_citations(self, query: str, top_k: int = 3, snippet_chars: int = 300):
        # Return top-k retrieval results formatted as citation dicts
        results = self.search_with_scores(query, top_k)
        citations = []
        for rank, item in enumerate(results, start=1):
            context = (item.get("context") or "").strip()
            if context:
                snippet = context[:snippet_chars]
                if len(context) > snippet_chars:
                    snippet += "…"
            else:
                snippet = ""

            citations.append({
                "rank": rank,
                "node_id": item.get("node_id"),
                "score": item.get("score"),
                "snippet": snippet,
                "metadata": item.get("metadata") or {},
            })
        return citations