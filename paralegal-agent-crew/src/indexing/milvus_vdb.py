from typing import List
from loguru import logger
from pymilvus import MilvusClient, DataType
from src.embeddings.embed_data import EmbedData, batch_iterate
from config.settings import settings

class MilvusVDB:
    """Milvus vector database with binary quantization support."""
    def __init__(
        self,
        collection_name: str = None,
        vector_dim: int = None,
        batch_size: int = None,
        db_file: str = None
    ):
        self.collection_name = collection_name or settings.collection_name
        self.vector_dim = vector_dim or settings.vector_dim
        self.batch_size = batch_size or settings.batch_size
        self.db_file = db_file or settings.milvus_db_path
        self.client = None

    def initialize_client(self):
        try:
            self.client = MilvusClient(self.db_file)
            logger.info(f"Initialized Milvus Lite client with database: {self.db_file}")
        except Exception as e:
            logger.error(f"Failed to initialize Milvus client: {e}")
            raise e

    def create_collection(self):
        """Create collection with binary vector support."""
        if not self.client:
            raise RuntimeError("Milvus client not initialized. Call initialize_client() first.")
        
        # Drop existing collection if it exists
        if self.client.has_collection(collection_name=self.collection_name):
            self.client.drop_collection(collection_name=self.collection_name)
            logger.info(f"Dropped existing collection: {self.collection_name}")

        # Create schema for binary vectors
        schema = self.client.create_schema(
            auto_id=True,
            enable_dynamic_fields=True,
        )

        # Add fields to schema
        schema.add_field(
            field_name="id", 
            datatype=DataType.INT64, 
            is_primary=True, 
            auto_id=True
        )
        schema.add_field(
            field_name="context", 
            datatype=DataType.VARCHAR, 
            max_length=65535
        )
        schema.add_field(
            field_name="binary_vector", 
            datatype=DataType.BINARY_VECTOR, 
            dim=self.vector_dim
        )

        # Create index parameters for binary vectors
        index_params = self.client.prepare_index_params()
        index_params.add_index(
            field_name="binary_vector",
            index_name="binary_vector_index",
            index_type="BIN_FLAT",  # Exact search for binary vectors
            metric_type="HAMMING"   # Hamming distance for binary vectors
        )

        # Create collection with schema and index
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params
        )

        logger.info(f"Created collection '{self.collection_name}' with binary vectors (dim={self.vector_dim})")

    def ingest_data(self, embed_data: EmbedData):
        """Ingest embedded data into the vector database."""
        if not self.client:
            raise RuntimeError("Milvus client not initialized. Call initialize_client() first.")
        
        logger.info(f"Ingesting {len(embed_data.contexts)} documents...")

        total_inserted = 0
        for batch_context, batch_binary_embeddings in zip(
            batch_iterate(embed_data.contexts, self.batch_size),
            batch_iterate(embed_data.binary_embeddings, self.batch_size)
        ):
            # Prepare data for insertion
            data_batch = []
            for context, binary_embedding in zip(batch_context, batch_binary_embeddings):
                data_batch.append({
                    "context": context,
                    "binary_vector": binary_embedding
                })

            # Insert batch
            self.client.insert(
                collection_name=self.collection_name,
                data=data_batch
            )

            total_inserted += len(batch_context)
            logger.info(f"Inserted batch: {len(batch_context)} documents")

        logger.info(f"Successfully ingested {total_inserted} documents with binary quantization")

    def search(
        self, 
        binary_query: bytes, 
        top_k: int = None,
        output_fields: List[str] = None
    ):
        if not self.client:
            raise RuntimeError("Milvus client not initialized. Call initialize_client() first.")
        
        top_k = top_k or settings.top_k
        output_fields = output_fields or ["context"]

        # Perform similarity search using MilvusClient
        search_results = self.client.search(
            collection_name=self.collection_name,
            data=[binary_query],
            anns_field="binary_vector",
            search_params={"metric_type": "HAMMING", "params": {}},
            limit=top_k,
            output_fields=output_fields
        )

        # Format results
        formatted_results = []
        for result in search_results[0]:
            formatted_results.append({
                "id": result["id"],
                "score": 1.0 / (1.0 + result["distance"]),  # Convert Hamming distance to similarity
                "payload": {"context": result["entity"]["context"]}
            })

        return formatted_results

    def collection_exists(self):
        if not self.client:
            return False
        return self.client.has_collection(collection_name=self.collection_name)

    def get_collection_info(self):
        if not self.client:
            raise RuntimeError("Milvus client not initialized. Call initialize_client() first.")
        
        if not self.collection_exists():
            return {"exists": False}
        
        # Get collection statistics
        stats = self.client.get_collection_stats(collection_name=self.collection_name)
        return {
            "exists": True,
            "row_count": stats["row_count"],
            "collection_name": self.collection_name
        }

    # Close the database connection
    def close(self):
        if self.client:
            self.client.close()
            logger.info("Closed Milvus client connection")