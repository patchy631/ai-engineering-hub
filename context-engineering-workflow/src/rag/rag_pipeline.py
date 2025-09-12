import os
from typing import List, Dict, Any, Optional
from src.document_processing import TensorLakeClient, RESEARCH_PAPER_SCHEMA
from src.rag.embeddings import ContextualizedEmbeddings
from src.rag.retriever import MilvusVectorDB
from src.generation import StructuredResponseGen

class RAGPipeline:
    """Unified RAG pipeline combining document parsing, embeddings, and retrieval"""
    def __init__(
        self,
        tensorlake_api_key: Optional[str] = None,
        voyage_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        milvus_db_path: str = "milvus_lite.db",
        collection_name: str = "research_assistant"
    ):
        self.doc_parser = TensorLakeClient(api_key=tensorlake_api_key)
        self.embeddings = ContextualizedEmbeddings(api_key=voyage_api_key)
        self.vector_db = MilvusVectorDB(db_path=milvus_db_path, collection_name=collection_name)
        self.generator = StructuredResponseGen(api_key=openai_api_key)
        
    def process_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        results = {
            "processed_docs": [],
            "total_chunks": 0,
            "structured_data": []
        }
        
        # Upload and parse documents
        file_ids = self.doc_parser.upload(document_paths)
        
        for i, (path, file_id) in enumerate(zip(document_paths, file_ids)):
            parse_id = self.doc_parser.parse_structured(
                file_id=file_id,
                json_schema=RESEARCH_PAPER_SCHEMA,
                labels={"source": path, "doc_index": i}
            )
            
            parse_result = self.doc_parser.get_result(parse_id)
            if parse_result is None:
                raise Exception(f"TensorLake parsing failed for {path}: No result returned")
            
            # Extract chunks and structured data
            chunks = []
            if hasattr(parse_result, 'chunks') and parse_result.chunks:
                for chunk in parse_result.chunks:
                    if chunk and hasattr(chunk, 'content') and hasattr(chunk, 'page_number'):
                        chunks.append({
                            "page": chunk.page_number,
                            "text": chunk.content,
                            "source": path
                        })
            else:
                raise Exception(f"TensorLake parsing failed for {path}: No chunks found in result")
            
            if not chunks:
                raise Exception(f"TensorLake parsing failed for {path}: No valid chunks extracted")
            
            # Generate contextualized embeddings
            chunk_texts = [[chunk["text"] for chunk in chunks]]
            embeddings_result = self.embeddings.embed_document_chunks(chunk_texts)
            
            if not embeddings_result or len(embeddings_result) == 0:
                raise Exception(f"Embedding generation failed for {path}: No embeddings returned")
            
            chunk_embeddings = embeddings_result[0]
            
            if not chunk_embeddings or len(chunk_embeddings) != len(chunks):
                raise Exception(f"Embedding generation failed for {path}: Chunk count mismatch - {len(chunks)} chunks but {len(chunk_embeddings) if chunk_embeddings else 0} embeddings")
            
            # Prepare metadata for each chunk
            chunk_metadata = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    "page_number": chunk.get("page", 0),
                    "chunk_index": i,
                    "source_file": chunk.get("source", path)
                }
                chunk_metadata.append(metadata)
            
            # Store in vector database with metadata
            self.vector_db.insert(
                chunks=[chunk["text"] for chunk in chunks],
                embeddings=chunk_embeddings,
                metadata=chunk_metadata
            )
            
            results["processed_docs"].append({
                "path": path,
                "file_id": file_id,
                "chunks_count": len(chunks),
                "structured_data": parse_result.model_dump()
            })
            results["total_chunks"] += len(chunks)
            results["structured_data"].append(parse_result.model_dump())
            
        return results
    
    def retrieve_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_embedding = self.embeddings.embed_query(query)
        
        # Search vector database
        search_results = self.vector_db.search(
            query_embedding=query_embedding,
            limit=top_k
        )
        
        return search_results
    
    def generate_response(
        self, 
        query: str, 
        context: List[Dict[str, Any]],
        source_used: str = "RAG"
    ) -> Dict[str, Any]:
        context_blocks = [result["text"] for result in context]
        
        response = self.generator.generate(
            query=query,
            context_blocks=context_blocks,
            source_used=source_used
        )
        
        return response
    
    def query(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        context_results = self.retrieve_context(query, top_k=top_k)
        response = self.generate_response(query, context_results)
        
        # Add retrieval metadata for citations
        response["retrieval_metadata"] = {
            "retrieved_chunks": len(context_results),
            "top_scores": [r["score"] for r in context_results]
        }
        
        return response
