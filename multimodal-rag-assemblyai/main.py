import os
import glob
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import openai
import sounddevice as sd
import soundfile as sf
import assemblyai as aai
from PyPDF2 import PdfReader
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from crewai.flow.flow import Flow, start, listen

import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize clients
openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
aai.settings.api_key = config.ASSEMBLYAI_API_KEY

# Global variables for caching
_milvus_connection = None
_collection = None

# File patterns
FILE_PATTERNS = ["*.pdf", "*.mp3", "*.wav", "*.m4a", "*.flac", "*.txt", "*.md"]
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.flac'}
TEXT_EXTENSIONS = {'.txt', '.md'}


@dataclass
class DataIngestionState:
    """State for data ingestion flow"""
    collection: Optional[Collection] = None
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    processed_files: List[str] = field(default_factory=list)
    discovered_files: List[str] = field(default_factory=list)


@dataclass
class QueryState:
    """State for query processing flow"""
    query: str = ""
    transcribed_query: str = ""
    search_results: str = ""
    final_response: str = ""
    audio_file: Optional[str] = None


def get_milvus_connection():
    """Get or create Milvus connection"""
    global _milvus_connection
    if _milvus_connection is None:
        try:
            _milvus_connection = connections.connect(host=config.MILVUS_HOST, port=config.MILVUS_PORT)
            logger.info("📡 Connected to Milvus")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise
    return _milvus_connection


def get_collection():
    """Get or create collection"""
    global _collection
    if _collection is None:
        get_milvus_connection()
        _collection = Collection(config.COLLECTION_NAME)
        _collection.load()
    return _collection


def transcribe_audio_file(audio_file: str) -> str:
    """Transcribe audio file using AssemblyAI"""
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript.text


def search_vector_database(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Search vector database for relevant information"""
    try:
        collection = get_collection()
        
        # Generate query embedding
        response = openai_client.embeddings.create(model=config.EMBEDDING_MODEL, input=[query])
        query_embedding = response.data[0].embedding
        
        # Search
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=limit,
            output_fields=["text", "source", "content_type"]
        )
        
        # Format results
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "text": hit.entity.get("text"),
                    "source": hit.entity.get("source"),
                    "content_type": hit.entity.get("content_type"),
                    "score": hit.score
                })
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error searching vector database: {e}")
        return []


def format_search_results(search_results: List[Dict[str, Any]]) -> str:
    """Format search results into readable string"""
    if not search_results:
        return "No relevant documents found."
    
    formatted_results = []
    for result in search_results:
        relevance = (1 - result['score']) * 100
        formatted_results.append(
            f"Source: {result['source']} ({result['content_type']})\n"
            f"Relevance: {relevance:.1f}%\n"
            f"Content: {result['text'][:200]}...\n"
            f"---"
        )
    
    return "\n".join(formatted_results)


class SearchKnowledgeBaseTool(BaseTool):
    """Tool for searching the knowledge base"""
    
    name: str = "search_knowledge_base"
    description: str = "Search the multimodal knowledge base for relevant information"
    
    def _run(self, query: str) -> str:
        """Search the knowledge base and return formatted results"""
        logger.info(f"Searching knowledge base for: {query}")
        search_results = search_vector_database(query)
        return format_search_results(search_results)


class DataIngestionFlow(Flow):
    """CrewAI Flow for data ingestion and vector database setup"""
    
    def __init__(self):
        super().__init__()
    
    @start()
    def discover_files(self) -> DataIngestionState:
        """Discover all files in the data directory"""
        logger.info("🔍 Discovering files in data directory...")
        data_dir = Path(config.DATA_DIR)
        
        if not data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")
        
        discovered_files = []
        for pattern in FILE_PATTERNS:
            files = glob.glob(str(data_dir / pattern))
            discovered_files.extend(files)
        
        discovered_files = sorted(list(set(discovered_files)))
        logger.info(f"📁 Discovered {len(discovered_files)} files")
        return DataIngestionState(discovered_files=discovered_files)
    
    @listen(lambda state: state.discovered_files is not None)
    def setup_vector_database(self, state: DataIngestionState) -> DataIngestionState:
        """Initialize Milvus connection and collection"""
        logger.info("🔧 Setting up vector database...")
        
        get_milvus_connection()
        
        if not utility.has_collection(config.COLLECTION_NAME):
            fields = [
                FieldSchema("id", DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema("text", DataType.VARCHAR, max_length=65535),
                FieldSchema("source", DataType.VARCHAR, max_length=255),
                FieldSchema("content_type", DataType.VARCHAR, max_length=50),
                FieldSchema("embedding", DataType.FLOAT_VECTOR, dim=config.EMBEDDING_DIM)
            ]
            schema = CollectionSchema(fields, "Multimodal RAG collection")
            collection = Collection(config.COLLECTION_NAME, schema)
            collection.create_index("embedding", {"index_type": "IVF_FLAT", "metric_type": "L2", "params": {"nlist": 1024}})
            logger.info("✅ Collection created and indexed")
        else:
            logger.info("✅ Collection already exists")
            collection = Collection(config.COLLECTION_NAME)
        
        collection.load()
        logger.info("✅ Vector database setup completed")
        return DataIngestionState(discovered_files=state.discovered_files, collection=collection)
    
    @listen(lambda state: state.collection is not None)
    def process_multimodal_data(self, state: DataIngestionState) -> DataIngestionState:
        """Process discovered files from the data directory"""
        logger.info(f"📄 Processing {len(state.discovered_files)} discovered files...")
        
        chunks = []
        processed_files = []
        
        for file_path in state.discovered_files:
            file_path = Path(file_path)
            filename = file_path.name
            logger.info(f"🔄 Processing: {filename}")
            
            try:
                # Process different file types
                if file_path.suffix.lower() == '.pdf':
                    with open(file_path, 'rb') as f:
                        reader = PdfReader(f)
                        text = "\n".join(page.extract_text() for page in reader.pages)
                    content_type = "pdf"
                elif file_path.suffix.lower() in AUDIO_EXTENSIONS:
                    text = transcribe_audio_file(str(file_path))
                    content_type = "audio"
                elif file_path.suffix.lower() in TEXT_EXTENSIONS:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    content_type = "text"
                else:
                    logger.warning(f"⚠️ Skipping unsupported file: {filename}")
                    continue
                
                # Create chunks
                chunk_size = 1000
                for i in range(0, len(text), chunk_size):
                    chunk = text[i:i + chunk_size]
                    if chunk.strip():
                        chunks.append({
                            "text": chunk,
                            "source": filename,
                            "content_type": content_type
                        })
                        
                processed_files.append(filename)
                        
            except Exception as e:
                logger.error(f"❌ Error processing {filename}: {e}")
                continue
        
        if not chunks:
            logger.warning("No content extracted from files")
            return DataIngestionState(
                discovered_files=state.discovered_files,
                collection=state.collection,
                chunks=[],
                processed_files=[]
            )
        
        logger.info(f"✅ Processed {len(chunks)} chunks from {len(processed_files)} files")
        return DataIngestionState(
            discovered_files=state.discovered_files,
            collection=state.collection,
            chunks=chunks,
            processed_files=processed_files
        )
    
    @listen(lambda state: len(state.chunks) > 0)
    def generate_embeddings_flow(self, state: DataIngestionState) -> DataIngestionState:
        """Generate embeddings for processed chunks"""
        logger.info(f"🧠 Generating embeddings for {len(state.chunks)} chunks...")
        
        texts = [chunk["text"] for chunk in state.chunks]
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            response = openai_client.embeddings.create(model=config.EMBEDDING_MODEL, input=batch_texts)
            batch_embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(batch_embeddings)
        
        # Assign embeddings to chunks
        updated_chunks = []
        for chunk, embedding in zip(state.chunks, all_embeddings):
            chunk_copy = chunk.copy()
            chunk_copy["embedding"] = embedding
            updated_chunks.append(chunk_copy)
        
        logger.info("✅ Embeddings generation completed")
        return DataIngestionState(
            discovered_files=state.discovered_files,
            collection=state.collection,
            chunks=updated_chunks,
            processed_files=state.processed_files
        )
    
    @listen(lambda state: all(chunk.get("embedding") is not None for chunk in state.chunks))
    def store_in_vector_database(self, state: DataIngestionState) -> DataIngestionState:
        """Insert processed chunks into Milvus"""
        logger.info(f"💾 Inserting {len(state.chunks)} chunks into vector database...")
        
        data = [
            [chunk["text"] for chunk in state.chunks],
            [chunk["source"] for chunk in state.chunks],
            [chunk["content_type"] for chunk in state.chunks],
            [chunk["embedding"] for chunk in state.chunks]
        ]
        
        state.collection.insert(data)
        state.collection.flush()
        logger.info("✅ Data insertion completed")
        return state


class MultimodalRAGFlow(Flow):
    """CrewAI Flow for query processing and response generation"""
    
    def __init__(self):
        super().__init__()
    
    @start()
    def transcribe_audio_if_needed(self, query: str, audio_file: Optional[str] = None) -> QueryState:
        """Transcribe audio if query is audio-based"""
        if audio_file:
            logger.info("🎤 Transcribing audio file...")
            transcribed_query = transcribe_audio_file(audio_file)
            logger.info(f"✅ Transcribed: {transcribed_query}")
        else:
            transcribed_query = query
            logger.info("📝 Using text query directly")
        
        return QueryState(query=query, audio_file=audio_file, transcribed_query=transcribed_query)
    
    @listen(lambda state: state.transcribed_query is not None)
    def search_knowledge_base(self, state: QueryState) -> QueryState:
        """Search the vector database for relevant information"""
        logger.info("🔍 Searching knowledge base...")
        
        search_results = search_vector_database(state.transcribed_query)
        formatted_results = format_search_results(search_results)
        logger.info("✅ Search completed")
        
        return QueryState(
            query=state.query,
            audio_file=state.audio_file,
            transcribed_query=state.transcribed_query,
            search_results=formatted_results
        )
    
    @listen(lambda state: state.search_results is not None)
    def generate_response(self, state: QueryState) -> QueryState:
        """Generate final response using CrewAI agents"""
        logger.info("🤖 Generating response...")
        
        try:
            # Create agents
            research_agent = Agent(
                role="Information Retrieval Specialist",
                goal="Find the most relevant information from the knowledge base to answer user queries",
                backstory="You are an expert at analyzing queries and searching through multimodal knowledge bases to find the most relevant information.",
                tools=[SearchKnowledgeBaseTool()],
                verbose=True,
                allow_delegation=False
            )
            
            response_agent = Agent(
                role="Response Generator",
                goal="Generate comprehensive, accurate, and helpful responses based on retrieved information",
                backstory="You are an expert at synthesizing information from multiple sources and creating clear, informative responses.",
                verbose=True,
                allow_delegation=False
            )
            
            # Create tasks
            research_task = Task(
                description=f"Search for information relevant to: '{state.transcribed_query}'. Use the search_knowledge_base tool to find the most relevant context.",
                agent=research_agent,
                expected_output="Detailed information from the knowledge base with proper citations"
            )
            
            response_task = Task(
                description=f"Based on the research findings, generate a comprehensive response to: '{state.transcribed_query}'.",
                agent=response_agent,
                expected_output="A well-structured, comprehensive response with proper citations"
            )
            
            # Create crew and execute
            crew = Crew(
                agents=[research_agent, response_agent],
                tasks=[research_task, response_task],
                verbose=True,
                memory=False
            )
            
            result = crew.kickoff()
            logger.info("✅ Response generated")
            
            return QueryState(
                query=state.query,
                audio_file=state.audio_file,
                transcribed_query=state.transcribed_query,
                search_results=state.search_results,
                final_response=result
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            fallback_response = f"Based on the search results:\n{state.search_results}\n\nQuery: {state.transcribed_query}"
            return QueryState(
                query=state.query,
                audio_file=state.audio_file,
                transcribed_query=state.transcribed_query,
                search_results=state.search_results,
                final_response=fallback_response
            )


def record_audio(duration: int = 10, sample_rate: int = 16000) -> str:
    """Record audio from microphone and save to temporary file"""
    print(f"🎤 Recording for {duration} seconds... Speak now!")
    print("Press Ctrl+C to stop early")
    
    try:
        audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float64')
        sd.wait()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sf.write(temp_file.name, audio_data, sample_rate)
        
        print("✅ Recording completed!")
        return temp_file.name
        
    except KeyboardInterrupt:
        print("\n⏹️ Recording stopped by user")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sf.write(temp_file.name, audio_data, sample_rate)
        return temp_file.name
    except Exception as e:
        print(f"❌ Recording failed: {e}")
        raise


def process_query(query: str, audio_file: Optional[str] = None) -> str:
    """Process a query through the RAG flow"""
    try:
        rag_flow = MultimodalRAGFlow()
        
        # Start the flow and execute all steps
        initial_state = rag_flow.transcribe_audio_if_needed(query, audio_file)
        
        # Manually execute the remaining steps since Flow isn't auto-executing
        search_state = rag_flow.search_knowledge_base(initial_state)
        final_state = rag_flow.generate_response(search_state)
        
        return final_state.final_response
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"Sorry, I encountered an error while processing your query: {str(e)}"


def check_system_status():
    """Check if the system is ready"""
    try:
        # Check Milvus connection
        get_milvus_connection()
        
        # Check if collection exists and has data
        if utility.has_collection(config.COLLECTION_NAME):
            collection = Collection(config.COLLECTION_NAME)
            collection.load()
            # Check if collection has data
            stats = collection.get_statistics()
            if stats.get("row_count", 0) > 0:
                logger.info("✅ System ready with data")
                return True
            else:
                logger.info("⚠️ Collection exists but is empty")
                return False
        else:
            logger.info("⚠️ Collection does not exist")
            return False
    except Exception as e:
        logger.error(f"❌ System check failed: {e}")
        return False


def main():
    """Main application entry point"""
    print("\n🤖 Welcome to Multimodal Agentic RAG System!")
    print("=" * 50)
    
    # Validate API keys
    if not config.ASSEMBLYAI_API_KEY or not config.OPENAI_API_KEY:
        print("\n❌ Missing API keys!")
        print("Please create a .env file with:")
        print("ASSEMBLYAI_API_KEY=your_key_here")
        print("OPENAI_API_KEY=your_key_here")
        return
    
    # Check system status and setup if needed
    print("🔍 Checking system status...")
    try:
        if check_system_status():
            print("✅ System ready!")
        else:
            print("\n⚠️ System not set up yet. Let's set it up first!")
            print("📡 Connecting to Milvus...")
            
            # Use the DataIngestionFlow to set up the system
            ingestion_flow = DataIngestionFlow()
            initial_state = ingestion_flow.discover_files()
            
            # Manually execute the flow steps
            setup_state = ingestion_flow.setup_vector_database(initial_state)
            process_state = ingestion_flow.process_multimodal_data(setup_state)
            
            if len(process_state.chunks) > 0:
                embed_state = ingestion_flow.generate_embeddings_flow(process_state)
                final_state = ingestion_flow.store_in_vector_database(embed_state)
                print("✅ Setup completed!")
            else:
                print("⚠️ No data to process")
                
    except Exception as e:
        print(f"\n⚠️ Error checking system status: {e}")
        print("Make sure Milvus is running: docker-compose up -d")
        return
    
    # Main interaction loop
    while True:
        print("\nWhat would you like to do?")
        print("1. 💬 Ask a question (text)")
        print("2. 🎤 Record and ask a question")
        print("3. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            query = input("\n💬 Enter your question: ").strip()
            if query:
                print("\n🤔 Processing...")
                response = process_query(query)
                print(f"\n🤖 Response:\n{response}")
            
        elif choice == "2":
            duration = input("\n🎤 Recording duration in seconds (default 10): ").strip()
            duration = int(duration) if duration.isdigit() else 10
            
            audio_file = record_audio(duration)
            if audio_file:
                print("\n🤔 Processing...")
                response = process_query("", audio_file)
                print(f"\n🤖 Response:\n{response}")
                
                try:
                    os.unlink(audio_file)
                except:
                    pass
            
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-3.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc() 