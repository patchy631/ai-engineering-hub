import os
import json
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class RAGInput(BaseModel):
    """Input schema for RAG search tool"""
    query: str = Field(..., description="The search query for retrieval.")
    top_k: int = Field(default=3, description="Maximum number of retrieved results to fetch.")
    document_paths: List[str] = Field(default=None, description="Optional list of document paths to load. Only needed if no documents are already loaded in the vector database.")


class RAGTool(BaseTool):
    name: str = "rag_search"
    description: str = "Search through research documents for relevant information."
    rag_pipeline: Any = Field(..., description="RAG pipeline instance")
    args_schema: Type[BaseModel] = RAGInput
    
    def _run(self, query: str, top_k: int = 3, document_paths: List[str] = None):
        try:
            doc_count = self.rag_pipeline.vector_db.get_collection_count()
            if doc_count == 0:
                if not document_paths:
                    return json.dumps({
                        "status": "INSUFFICIENT_CONTEXT",
                        "source_used": "RAG",
                        "answer": "No documents have been loaded into the RAG system. Please provide document_paths to load documents first, or ensure documents have been previously loaded.",
                        "citations": [],
                        "confidence": 0.0,
                        "retrieval_metadata": {
                            "retrieved_chunks": 0,
                            "top_scores": [],
                            "document_count": 0
                        }
                    })
                
                # load documents
                load_result = self._load_documents(document_paths)
                if load_result["status"] == "ERROR":
                    return json.dumps(load_result, indent=2)
                
                doc_count = self.rag_pipeline.vector_db.get_collection_count()
                if doc_count == 0:
                    return json.dumps({
                        "status": "INSUFFICIENT_CONTEXT",
                        "source_used": "RAG",
                        "answer": "Failed to load documents into the RAG system.",
                        "citations": [],
                        "confidence": 0.0,
                        "retrieval_metadata": {
                            "retrieved_chunks": 0,
                            "top_scores": [],
                            "document_count": 0
                        }
                    })
            
            # Retrieve relevant context (no generation)
            context_results = self.rag_pipeline.retrieve_context(query, top_k=top_k)
            if not context_results:
                return json.dumps({
                    "status": "INSUFFICIENT_CONTEXT",
                    "source_used": "RAG",
                    "answer": f"No relevant context found for query: '{query}'",
                    "citations": [],
                    "confidence": 0.0,
                    "retrieval_metadata": {
                        "retrieved_chunks": 0,
                        "top_scores": [],
                        "document_count": doc_count
                    }
                })
            
            context_blocks = []
            citations = []
            for i, result in enumerate(context_results):
                chunk_text = result.get("text", "")
                score = result.get("score", 0.0)
                page_number = result.get("page_number", 0)
                chunk_index = result.get("chunk_index", i)
                source_file = result.get("source_file", "unknown")
                
                filename = source_file.split("/")[-1] if source_file != "unknown" else "unknown"
                context_blocks.append(f"**Context {i+1} (Score: {score:.3f}, Page {page_number}, Chunk {chunk_index})**\n{chunk_text[:500]}...")
                citations.append({
                    "label": f"{filename} - Page {page_number}, Chunk {chunk_index}",
                    "locator": f"page_{page_number}_chunk_{chunk_index}",
                    "page_number": page_number,
                    "chunk_index": chunk_index,
                    "source_file": filename,
                    "score": score,
                    "content": chunk_text
                })
            
            answer = "\n\n".join(context_blocks)
            
            return json.dumps({
                "status": "OK",
                "source_used": "RAG",
                "answer": f"Retrieved {len(context_results)} relevant context chunks:\n\n{answer}",
                "citations": citations,
                "confidence": max([r.get("score", 0.0) for r in context_results]),
                "retrieval_metadata": {
                    "retrieved_chunks": len(context_results),
                    "top_scores": [r.get("score", 0.0) for r in context_results],
                    "document_count": doc_count
                },
                "raw_context": context_results  # Include raw context for further processing
            })
            
        except Exception as e:
            return json.dumps({
                "status": "ERROR",
                "source_used": "RAG",
                "answer": f"RAG search failed: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "retrieval_metadata": {
                    "retrieved_chunks": 0,
                    "top_scores": [],
                    "document_count": 0
                },
                "error": str(e)
            })
    
    def _load_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        """Helper method to load documents into the RAG pipeline"""
        try:
            if not document_paths:
                return {
                    "status": "ERROR",
                    "source_used": "RAG",
                    "answer": "No document paths provided",
                    "citations": [],
                    "confidence": 0.0
                }
            
            missing_files = [path for path in document_paths if not os.path.exists(path)]
            if missing_files:
                return {
                    "status": "ERROR",
                    "source_used": "RAG",
                    "answer": f"Missing files: {missing_files}",
                    "citations": [],
                    "confidence": 0.0
                }
            
            results = self.rag_pipeline.process_documents(document_paths)
            return {
                "status": "OK",
                "source_used": "RAG",
                "answer": f"Successfully processed {len(results['processed_docs'])} documents with {results['total_chunks']} total chunks.",
                "citations": [{"label": f"Processed: {doc['path']}", "locator": doc['path']} for doc in results['processed_docs']],
                "confidence": 0.96
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "source_used": "RAG",
                "answer": f"Document processing failed: {str(e)}",
                "citations": [],
                "confidence": 0.0,
                "error": str(e)
            }
