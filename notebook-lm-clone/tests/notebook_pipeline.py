import os
import logging
from pathlib import Path

from src.document_processing.doc_processor import DocumentProcessor
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.vector_database.milvus_vector_db import MilvusVectorDB
from src.generation.rag import RAGGenerator
from src.memory.memory_layer import NotebookMemoryLayer
from src.audio_processing.audio_transcriber import AudioTranscriber
from src.web_scraping.web_scraper import WebScraper

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NotebookLMPipeline:
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        self.firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        self.zep_key = os.getenv("ZEP_API_KEY")
        
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        logger.info("Initializing NotebookLM Pipeline...")
        
        self.doc_processor = DocumentProcessor()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_db = MilvusVectorDB()
        self.rag_generator = RAGGenerator(
            embedding_generator=self.embedding_generator,
            vector_db=self.vector_db,
            openai_api_key=self.openai_key,
            model_name="gpt-4o-mini",
            temperature=0.1
        )
        
        self.audio_transcriber = AudioTranscriber(self.assemblyai_key) if self.assemblyai_key else None
        self.web_scraper = WebScraper(self.firecrawl_key) if self.firecrawl_key else None
        
        self.memory = None
        if self.zep_key:
            self.memory = NotebookMemoryLayer(
                user_id="test_user",
                session_id="test_session",
                create_new_session=True
            )
        
        logger.info("Pipeline initialized successfully!")
    
    def process_documents(self, file_paths):
        logger.info(f"Processing {len(file_paths)} documents...")
        
        all_chunks = []
        for file_path in file_paths:
            try:
                chunks = self.doc_processor.process_document(file_path)
                all_chunks.extend(chunks)
                logger.info(f"✓ Processed {file_path}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"✗ Failed to process {file_path}: {e}")
        
        if not all_chunks:
            logger.error("No documents processed successfully!")
            return False
        
        logger.info("Generating embeddings...")
        embedded_chunks = self.embedding_generator.generate_embeddings(all_chunks)
        
        logger.info("Setting up vector database...")
        self.vector_db.create_index(use_binary_quantization=False)
        
        logger.info("Inserting embeddings...")
        self.vector_db.insert_embeddings(embedded_chunks)
        
        logger.info(f"✓ Successfully processed {len(all_chunks)} chunks from {len(file_paths)} documents")
        return True
    
    def process_audio(self, audio_path):
        if not self.audio_transcriber:
            logger.warning("Audio transcriber not available (missing ASSEMBLYAI_API_KEY)")
            return False
        
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            chunks = self.audio_transcriber.transcribe_audio(audio_path)
            
            if chunks:
                embedded_chunks = self.embedding_generator.generate_embeddings(chunks)
                self.vector_db.insert_embeddings(embedded_chunks)
                logger.info(f"✓ Audio processed: {len(chunks)} chunks")
                return True
            
        except Exception as e:
            logger.error(f"✗ Audio processing failed: {e}")
        
        return False
    
    def process_url(self, url):
        if not self.web_scraper:
            logger.warning("Web scraper not available (missing FIRECRAWL_API_KEY)")
            return False
        
        try:
            logger.info(f"Scraping URL: {url}")
            chunks = self.web_scraper.scrape_url(url)
            
            if chunks:
                embedded_chunks = self.embedding_generator.generate_embeddings(chunks)
                self.vector_db.insert_embeddings(embedded_chunks)
                logger.info(f"✓ URL processed: {len(chunks)} chunks")
                return True
            
        except Exception as e:
            logger.error(f"✗ URL processing failed: {e}")
        
        return False
    
    def ask_question(self, question):
        logger.info(f"Processing question: {question}")
        
        try:
            result = self.rag_generator.generate_response(question)
            if self.memory:
                self.memory.save_conversation_turn(result)
            
            return result
            
        except Exception as e:
            logger.error(f"✗ Question processing failed: {e}")
            return None
    
    def cleanup(self):
        try:
            self.vector_db.close()
            logger.info("Pipeline cleaned up")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


def test_pipeline():
    logger.info("=" * 60)
    logger.info("STARTING NOTEBOOKLM PIPELINE TEST")
    logger.info("=" * 60)
    
    try:
        pipeline = NotebookLMPipeline()
        
        # Test 1: Document Processing
        logger.info("\n📄 TEST 1: Document Processing")
        test_documents = [
            # Add paths to your test files here
            # "sample.pdf",
            # "document.txt"
        ]
        
        if test_documents:
            success = pipeline.process_documents(test_documents)
            if not success:
                logger.warning("Document processing failed - creating sample data")
                # Create a simple test document
                test_file = Path("test_sample.txt")
                test_file.write_text("This is a sample document for testing the NotebookLM pipeline. It contains information about artificial intelligence and machine learning.")
                pipeline.process_documents([str(test_file)])
                test_file.unlink()
        else:
            logger.info("No test documents provided - skipping document test")
        
        # Test 2: Audio Processing
        logger.info("\n🎵 TEST 2: Audio Processing")
        # pipeline.process_audio("sample_audio.mp3")
        logger.info("Audio test skipped (no sample file)")
        
        # Test 3: Web Scraping
        logger.info("\n🌐 TEST 3: Web Scraping")
        # pipeline.process_url("https://example.com")
        logger.info("Web scraping test skipped")
        
        # Test 4: Question Answering
        logger.info("\n❓ TEST 4: Question Answering")
        
        test_questions = [
            "What is the main topic discussed in the documents?",
            "Can you summarize the key points?",
            "What information is available about artificial intelligence?"
        ]
        
        for question in test_questions:
            logger.info(f"\nQ: {question}")
            result = pipeline.ask_question(question)
            
            if result:
                logger.info(f"A: {result.response}")
                logger.info(f"Sources: {len(result.sources_used)} documents used")
                
                if result.sources_used:
                    logger.info("Citations:")
                    for i, source in enumerate(result.sources_used[:3], 1):
                        source_info = f"  [{i}] {source.get('source_file', 'Unknown')}"
                        if source.get('page_number'):
                            source_info += f" (Page {source['page_number']})"
                        logger.info(source_info)
            else:
                logger.error("Failed to get response")
        
        # Test 5: Memory Context
        if pipeline.memory:
            logger.info("\n🧠 TEST 5: Memory Context")
            context = pipeline.memory.get_conversation_context()
            logger.info(f"Memory context available: {bool(context)}")
            if context:
                logger.info(f"Context preview: {context[:200]}...")
        
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE TEST COMPLETED SUCCESSFULLY! ✅")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Pipeline test failed: {e}")
        logger.info("\n" + "=" * 60)
        logger.info("PIPELINE TEST FAILED ❌")
        logger.info("=" * 60)
    
    finally:
        if 'pipeline' in locals():
            pipeline.cleanup()


if __name__ == "__main__":
    required_keys = ["OPENAI_API_KEY"]
    optional_keys = ["ASSEMBLYAI_API_KEY", "FIRECRAWL_API_KEY", "ZEP_API_KEY"]
    
    logger.info("Environment Check:")
    for key in required_keys:
        status = "✅" if os.getenv(key) else "❌ REQUIRED"
        logger.info(f"  {key}: {status}")
    
    for key in optional_keys:
        status = "✅" if os.getenv(key) else "⚠️  Optional"
        logger.info(f"  {key}: {status}")
    
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("Missing required OPENAI_API_KEY - cannot proceed")
        exit(1)
    
    logger.info("")
    test_pipeline()