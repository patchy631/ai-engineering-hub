import logging
from typing import List, Dict, Any, Optional, Tuple
import json
from pathlib import Path

from pymilvus import MilvusClient, DataType, connections, utility
from src.embeddings.embedding_generator import EmbeddedChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MilvusVectorDB:
    def __init__(
        self, 
        db_path: str = "./milvus_lite.db",
        collection_name: str = "notebook_lm",
        embedding_dim: int = 384
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim
        self.client = None
        self.collection_exists = False
        
        self._initialize_client()
        self._setup_collection()
    
    def _initialize_client(self):
        try:
            self.client = MilvusClient(uri=self.db_path)
            logger.info(f"Milvus client initialized with database: {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Milvus client: {str(e)}")
            raise
    
    def _setup_collection(self):
        try:
            if self.client.has_collection(collection_name=self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                self.collection_exists = True
                return
            
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True  # Allow additional metadata fields
            )
            
            # Primary key field (chunk_id)
            schema.add_field(
                field_name="id",
                datatype=DataType.VARCHAR,
                max_length=128,
                is_primary=True
            )
            
            # Vector field for embeddings
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=self.embedding_dim
            )
            
            # Essential fields for citations and content
            schema.add_field(
                field_name="content",
                datatype=DataType.VARCHAR,
                max_length=8192
            )
            
            schema.add_field(
                field_name="source_file",
                datatype=DataType.VARCHAR,
                max_length=512
            )
            
            schema.add_field(
                field_name="source_type",
                datatype=DataType.VARCHAR,
                max_length=32
            )
            
            schema.add_field(
                field_name="page_number",
                datatype=DataType.INT32
            )
            
            schema.add_field(
                field_name="chunk_index",
                datatype=DataType.INT32
            )
            
            schema.add_field(
                field_name="start_char",
                datatype=DataType.INT32
            )
            
            schema.add_field(
                field_name="end_char", 
                datatype=DataType.INT32
            )
            
            # JSON field for additional metadata
            schema.add_field(
                field_name="metadata",
                datatype=DataType.JSON
            )
            
            schema.add_field(
                field_name="embedding_model",
                datatype=DataType.VARCHAR,
                max_length=128
            )
            
            self.client.create_collection(
                collection_name=self.collection_name,
                schema=schema
            )
            
            logger.info(f"Collection '{self.collection_name}' created successfully")
            self.collection_exists = True
            
        except Exception as e:
            logger.error(f"Error setting up collection: {str(e)}")
            raise
    
    def create_index(
        self,
        use_binary_quantization: bool = False,
        nlist: int = 1024,
        enable_refine: bool = False,
        refine_type: str = "SQ8"
    ):
        try:
            if not self.collection_exists:
                raise Exception("Collection does not exist. Setup collection first.")
            
            index_params = self.client.prepare_index_params()
            
            if use_binary_quantization:
                # IVF_RABITQ with binary quantization
                index_params.add_index(
                    field_name="vector",
                    index_type="IVF_RABITQ",
                    index_name="vector_index",
                    metric_type="L2",
                    params={
                        "nlist": nlist,
                        "refine": enable_refine,
                        "refine_type": refine_type if enable_refine else None
                    }
                )
                logger.info(f"Creating IVF_RABITQ index with nlist={nlist}, refine={enable_refine}")
            else:
                # Fallback to IVF_FLAT if BQ not supported
                index_params.add_index(
                    field_name="vector",
                    index_type="IVF_FLAT", 
                    index_name="vector_index",
                    metric_type="L2",
                    # params={"nlist": nlist}
                )
                logger.info(f"Creating IVF_FLAT index with nlist={nlist}")
            
            self.client.create_index(
                collection_name=self.collection_name,
                index_params=index_params
            )
            
            logger.info("Index created successfully")
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
    
    def insert_embeddings(self, embedded_chunks: List[EmbeddedChunk]) -> List[str]:
        if not embedded_chunks:
            return []
        try:
            data = []
            for embedded_chunk in embedded_chunks:
                chunk_data = embedded_chunk.to_vector_db_format()  
                chunk_data['page_number'] = chunk_data['page_number'] or -1
                chunk_data['start_char'] = chunk_data['start_char'] or -1
                chunk_data['end_char'] = chunk_data['end_char'] or -1
                
                if isinstance(chunk_data['metadata'], dict):
                    chunk_data['metadata'] = chunk_data['metadata']
                
                data.append(chunk_data)
            
            result = self.client.insert(
                collection_name=self.collection_name,
                data=data
            )
            
            inserted_ids = [item['id'] for item in data]
            logger.info(f"Inserted {len(inserted_ids)} embeddings into database")
            
            return inserted_ids
            
        except Exception as e:
            logger.error(f"Error inserting embeddings: {str(e)}")
            raise
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        nprobe: int = 128,
        rbq_query_bits: int = 0,
        refine_k: float = 1.0,
        filter_expr: Optional[str] = None,
        use_binary_quantization: bool = False
    ) -> List[Dict[str, Any]]:
        try:
            if use_binary_quantization:
                search_params = {
                    "params": {
                        "nprobe": nprobe,
                        "rbq_query_bits": rbq_query_bits,
                        "refine_k": refine_k
                    }
                }
            else:
                search_params = {
                    "params": {
                        "nprobe": nprobe
                    }
                }
            
            # Perform vector similarity search
            results = self.client.search(
                collection_name=self.collection_name,
                data=[query_vector],
                anns_field="vector",
                limit=limit,
                search_params=search_params,
                filter=filter_expr,
                output_fields=[
                    "content", "source_file", "source_type", "page_number",
                    "chunk_index", "start_char", "end_char", "metadata", "embedding_model"
                ]
            )
            
            formatted_results = []
            if results and len(results) > 0:
                for result in results[0]:
                    formatted_result = {
                        'id': result['id'],
                        'score': result['distance'],
                        'content': result['entity']['content'],
                        'citation': {
                            'source_file': result['entity']['source_file'],
                            'source_type': result['entity']['source_type'],
                            'page_number': result['entity']['page_number'] if result['entity']['page_number'] != -1 else None,
                            'chunk_index': result['entity']['chunk_index'],
                            'start_char': result['entity']['start_char'] if result['entity']['start_char'] != -1 else None,
                            'end_char': result['entity']['end_char'] if result['entity']['end_char'] != -1 else None,
                        },
                        'metadata': result['entity']['metadata'],
                        'embedding_model': result['entity']['embedding_model']
                    }
                    formatted_results.append(formatted_result)
            
            logger.info(f"Search completed: {len(formatted_results)} results found")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def delete_collection(self):
        try:
            if self.client.has_collection(collection_name=self.collection_name):
                self.client.drop_collection(collection_name=self.collection_name)
                logger.info(f"Collection '{self.collection_name}' deleted")
                self.collection_exists = False
            else:
                logger.info(f"Collection '{self.collection_name}' does not exist")
                
        except Exception as e:
            logger.error(f"Error deleting collection: {str(e)}")
            raise
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        try:
            if not self.collection_exists:
                logger.warning("Collection does not exist")
                return None
            
            logger.info(f"Attempting to retrieve chunk with ID: {chunk_id}")
            
            results = self.client.query(
                collection_name=self.collection_name,
                filter=f'id == "{chunk_id}"',
                output_fields=["id", "content", "metadata", "source_file", "source_type", "page_number", "chunk_index"]
            )
            
            logger.info(f"Query returned {len(results) if results else 0} results")
            
            if results and len(results) > 0:
                chunk_data = results[0]
                logger.info(f"Successfully retrieved chunk: {chunk_data.get('id')}")
                
                metadata = chunk_data.get("metadata", {})
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                return {
                    "id": chunk_data.get("id"),
                    "content": chunk_data.get("content"),
                    "metadata": metadata,
                    "source_file": chunk_data.get("source_file"),
                    "source_type": chunk_data.get("source_type"),
                    "page_number": chunk_data.get("page_number"),
                    "chunk_index": chunk_data.get("chunk_index")
                }
            
            logger.warning(f"No chunk found with ID: {chunk_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving chunk by ID {chunk_id}: {str(e)}")
            logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
            return None
    
    def close(self):
        try:
            if self.client:
                self.client.close()
                logger.info("Milvus client connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")


if __name__ == "__main__":
    from src.document_processing.doc_processor import DocumentProcessor
    from src.embeddings.embedding_generator import EmbeddingGenerator
    
    doc_processor = DocumentProcessor()
    embedding_generator = EmbeddingGenerator()
    vector_db = MilvusVectorDB()
    
    try:
        chunks = doc_processor.process_document("data/raft.pdf")
        embedded_chunks = embedding_generator.generate_embeddings(chunks)
        vector_db.create_index()
        
        inserted_ids = vector_db.insert_embeddings(embedded_chunks)
        print(f"Inserted {len(inserted_ids)} embeddings")
        
        query_text = "What is the main topic?"
        query_vector = embedding_generator.generate_query_embedding(query_text)
        
        search_results = vector_db.search(query_vector.tolist(), limit=5)
        
        for i, result in enumerate(search_results):
            print(f"\nResult {i+1}:")
            print(f"Score: {result['score']:.4f}")
            print(f"Content: {result['content'][:200]}...")
            print(f"Citation: {result['citation']}")
        
    except Exception as e:
        print(f"Error in example: {e}")
    
    finally:
        vector_db.close()