from typing import List, Dict, Any
from pymilvus import MilvusClient, DataType

class MilvusVectorDB:
    def __init__(self, db_path: str = "milvus_lite.db", collection_name: str = "research_assistant"):
        self.client = MilvusClient(db_path)
        self.collection_name = collection_name
        self._ensure_collection()

    def _ensure_collection(self, dim: int = 1024):
        if self.client.has_collection(collection_name=self.collection_name):
            print(f"Dropping existing collection: {self.collection_name}")
            self.client.drop_collection(collection_name=self.collection_name)

        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_fields=True,
        )
        schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=dim)
        schema.add_field("text", DataType.VARCHAR, max_length=65535)
        schema.add_field("page_number", DataType.INT64)
        schema.add_field("chunk_index", DataType.INT64)
        schema.add_field("source_file", DataType.VARCHAR, max_length=500)

        index_params = self.client.prepare_index_params()
        index_params.add_index("embedding", index_type="IVF_FLAT", metric_type="COSINE")

        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )

    def insert(self, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        assert len(chunks) == len(embeddings), "Mismatch between chunks and embeddings"
        
        if metadata:
            assert len(chunks) == len(metadata), "Mismatch between chunks and metadata"

        data = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            entry = {
                "text": chunk,
                "embedding": emb,
            }
            if metadata and i < len(metadata):
                meta = metadata[i]
                entry["page_number"] = meta.get("page_number", 0)
                entry["chunk_index"] = meta.get("chunk_index", i)
                entry["source_file"] = meta.get("source_file", "unknown")
            else:
                entry["page_number"] = 0
                entry["chunk_index"] = i
                entry["source_file"] = "unknown"
            
            data.append(entry)

        self.client.insert(
            collection_name=self.collection_name,
            data=data
        )
        self.client.flush(collection_name=self.collection_name)

    def get_collection_count(self) -> int:
        try:
            stats = self.client.get_collection_stats(collection_name=self.collection_name)
            return stats.get('row_count', 0)
        except:
            return 0

    def search(
        self,
        query_embedding: List[float],
        limit: int = 3,
        nprobe: int = 10,
        metric: str = "COSINE"
    ) -> List[Dict[str, Any]]:
        
        search_params = {"metric_type": metric, "params": {"nprobe": nprobe}}

        results = self.client.search(
            collection_name=self.collection_name,
            data=[query_embedding],
            anns_field="embedding",
            search_params=search_params,
            limit=limit,
            output_fields=["text", "page_number", "chunk_index", "source_file"],
        )

        hits = []
        for hit in results[0]:
            hits.append({
                "text": hit.entity.get("text"),
                "score": hit.score,
                "page_number": hit.entity.get("page_number", 0),
                "chunk_index": hit.entity.get("chunk_index", 0),
                "source_file": hit.entity.get("source_file", "unknown")
            })

        return hits