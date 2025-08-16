import asyncio
import os
import sys
from pathlib import Path
from loguru import logger
import warnings
warnings.filterwarnings("ignore")

sys.path.append(str(Path(__file__).parent.parent))

from src.embeddings.embed_data import EmbedData
from src.indexing.milvus_vdb import MilvusVDB
from src.retrieval.retriever_rerank import Retriever
from src.generation.rag import RAG
from src.workflows.agent_workflow import ParalegalAgentWorkflow
from pypdf import PdfReader
from config.settings import settings

def get_citations(retriever, query, top_k=3, snippet_chars=300):
    """Return retrieval results as simple citation dicts."""
    results = retriever.search_with_scores(query, top_k=top_k)
    citations = []
    for rank, item in enumerate(results, start=1):
        context = (item.get("context") or "").strip()
        snippet = (context[:snippet_chars] + ("…" if len(context) > snippet_chars else "")) if context else ""
        citations.append({
            "rank": rank,
            "node_id": item.get("node_id"),
            "score": item.get("score"),
            "snippet": snippet,
            "metadata": item.get("metadata") or {},
        })
    return citations

def print_citations(citations):
    if not citations:
        print("\n(No citations available)")
        return
    print("\nCITATIONS (top matches)")
    print("-" * 60)
    for c in citations:
        score_str = f"{float(c.get("score")):.3f}"
        node_id = c.get("node_id")
        snippet = c.get("snippet") or ""
        print(f"[{c['rank']}] score={score_str} id={node_id}")
        if snippet:
            print(f"    \u201c{snippet}\u201d")
    print("-" * 60)

async def main():
    logger.info("Starting Enhanced RAG Pipeline Demo")
    
    required_env_vars = ["OPENAI_API_KEY"]
    for var in required_env_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            return
    
    try:
        # Step 1: Load and process document
        logger.info("Step 1: Loading document...")
        
        docs_path = settings.docs_path
        if not docs_path or not Path(docs_path).exists():
            logger.error("Invalid PDF path provided")
            return
        
        # Load and split documents
        reader = PdfReader(docs_path)
        pages_text = []
        for page in reader.pages:
            pages_text.append(page.extract_text() or "")
        full_text = "\n".join(pages_text)
        words = full_text.split()
        text_chunks = []
        chunk_size = 512
        overlap = 50
        step = max(1, chunk_size - overlap)
        i = 0
        while i < len(words):
            segment = words[i : i + chunk_size]
            text_chunks.append(" ".join(segment))
            i += step
        logger.info(f"Created {len(text_chunks)} text chunks")
        
        # Step 2: Create embeddings
        logger.info("Step 2: Creating embeddings...")
        
        embed_data = EmbedData(
            embed_model_name=settings.embedding_model,
            batch_size=settings.batch_size
        )
        
        # Generate embeddings with binary quantization
        embed_data.embed(text_chunks)
        logger.info("Embeddings created successfully")
        
        # Step 3: Setup vector database
        logger.info("Step 3: Setting up vector database...")
        
        vector_db = MilvusVDB(
            collection_name=settings.collection_name,
            vector_dim=settings.vector_dim,
            batch_size=settings.batch_size,
            db_file=settings.milvus_db_path
        )
        
        # Initialize database and create collection
        vector_db.initialize_client()
        vector_db.create_collection()
        
        # Ingest data
        vector_db.ingest_data(embed_data)
        logger.info("Vector database setup completed")
        
        # Step 4: Setup retrieval system
        logger.info("Step 4: Setting up retrieval system...")
        
        retriever = Retriever(
            vector_db=vector_db,
            embed_data=embed_data,
            top_k=settings.top_k
        )
        
        # Step 5: Setup RAG system
        logger.info("Step 5: Setting up RAG system...")
        
        rag_system = RAG(
            retriever=retriever,
            llm_model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Step 6: Setup workflow
        logger.info("Step 6: Setting up agentic workflow...")
        
        workflow = ParalegalAgentWorkflow(
            retriever=retriever,
            rag_system=rag_system,
            firecrawl_api_key=os.getenv("FIRECRAWL_API_KEY"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        logger.info("Setup completed! Ready for queries.")
        
        print("\n" + "="*60)
        print("Pipeline Ready!")
        print("Type 'quit' to exit, 'help' for commands")
        print("="*60)
        
        while True:
            try:
                query = input("\nEnter your question: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    break
                elif not query:
                    continue
                
                logger.info(f"Processing query: {query}")
                
                # Run the workflow
                result = await workflow.run_workflow(query)
                
                # Display results
                print("\n" + "-"*60)
                print("ANSWER:")
                print(result["answer"])
                
                if result.get("web_search_used", False):
                    print(f"\n🌐 Web search was used to enhance the response")
                else:
                    print(f"\n📚 Response based on document knowledge")
                    # Show citations grounding the answer
                    try:
                        citations = get_citations(retriever, query, top_k=min(3, settings.top_k))
                        print_citations(citations)
                    except Exception as e:
                        logger.warning(f"Could not fetch citations: {e}")
                
                print("-"*60)
                
                show_details = input("\nShow detailed results? (y/n): ").strip().lower()
                if show_details == 'y':
                    print_detailed_results(result)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"Error: {e}")
        
        # Cleanup
        logger.info("Cleaning up...")
        vector_db.close()
        logger.info("Demo completed")
        
    except Exception as e:
        logger.error(f"Pipeline setup failed: {e}")
        print(f"Setup failed: {e}")

def print_detailed_results(result):
    print("\n" + "="*60)
    print("DETAILED RESULTS")
    print("="*60)
    
    print(f"\nOriginal Query: {result['query']}")
    
    if result.get('rag_response'):
        print(f"\nRAG Response:")
        print(result['rag_response'])
    
    if result.get('web_search_used') and result.get('web_results'):
        print(f"\nWeb Search Results:")
        print(result['web_results'][:500] + "..." if len(result['web_results']) > 500 else result['web_results'])
    
    if result.get('error'):
        print(f"\nError: {result['error']}")
    
    print("="*60)

async def test_retrieval():
    # Test retrieval pipeline
    logger.info("Running retrieval test...")

    test_text = [
        "This is a test document about artificial intelligence.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers."
    ]
    
    # Test embedding
    embed_data = EmbedData()
    embed_data.embed(test_text)
    
    # Test vector database
    vector_db = MilvusVDB(collection_name="test_collection")
    vector_db.initialize_client()
    vector_db.create_collection()
    vector_db.ingest_data(embed_data)
    
    # Test retrieval
    retriever = Retriever(vector_db, embed_data)
    results = retriever.search("What is machine learning?")
    
    logger.info(f"Test completed. Retrieved {len(results)} results")

    # Test citations
    citations = get_citations(retriever, "What is machine learning?", top_k=3)
    print(citations)
    
    # Cleanup
    vector_db.close()
    
    return True

if __name__ == "__main__":
    asyncio.run(main())