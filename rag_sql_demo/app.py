import os
import streamlit as st
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
import subprocess
import platform

# Import LlamaIndex components
from llama_index.core import (
    Document,
    Settings,
    VectorStoreIndex,
    SimpleDirectoryReader,
)
from llama_index.core.query_engine import RetrieverQueryEngine, RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.tools import QueryEngineTool
from llama_index.core.indices.struct_store.sql_query import NLSQLTableQueryEngine, SQLDatabase
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.vector_stores import MetadataInfo, MetadataFilters
from llama_index.core.schema import QueryBundle

# Import LLM and embedding models
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface.base import HuggingFaceEmbedding

# Import vector stores
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
import os

# Set page configuration
st.set_page_config(
    page_title="RAG + SQL Router Demo",
    page_icon="🧠",
    layout="wide",
)

# Initialize session state variables if they don't exist
if "initialized" not in st.session_state:
    st.session_state.initialized = False
if "response" not in st.session_state:
    st.session_state.response = None
if "route_taken" not in st.session_state:
    st.session_state.route_taken = None

# Function to check if Ollama is available
def is_ollama_available():
    """Check if Ollama is installed and available."""
    try:
        # Try to run 'ollama -v' to check if Ollama is installed
        result = subprocess.run(['ollama', '-v'], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False

# Function to set up the LLM using Ollama
@st.cache_resource
def get_llm():
    """Initialize and return the LLM from Ollama."""
    if is_ollama_available():
        # Using Llama3 model via Ollama
        try:
            return Ollama(model="llama3", request_timeout=120.0)
        except Exception as e:
            st.warning(f"Error connecting to Ollama: {str(e)}. Using a simple response generator instead.")
            return SimpleLLM()
    else:
        st.warning("Ollama is not available. Using a simple response generator instead.")
        return SimpleLLM()

# Simple LLM class for fallback when Ollama is not available
class SimpleLLM:
    """A simple LLM class that returns predefined responses for different query types."""
    
    def __init__(self):
        self.sql_keywords = ["population", "highest", "lowest", "capital", "state", "founded", "area"]
        
    def complete(self, prompt):
        """Return a simple completion based on the prompt."""
        return "I'm a simple response generator. Please install Ollama for better responses."
    
    def chat(self, messages):
        """Return a simple chat response."""
        if not messages:
            return "No messages provided."
        
        last_message = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])
        
        # Determine if this is likely a SQL or document query
        is_sql_query = any(keyword in last_message.lower() for keyword in self.sql_keywords)
        
        if is_sql_query:
            return "This appears to be a question about city statistics. With a proper LLM, I would query the database for you."
        else:
            return "This appears to be a general question about cities. With a proper LLM, I would search the documents for you."

# Function to set up the embedding model
@st.cache_resource
def get_embedding_model():
    """Initialize and return the embedding model."""
    # Using a smaller model for embeddings to ensure efficiency
    return HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Function to create and populate a sample SQLite database
def setup_database():
    """Create a sample database with city statistics."""
    # Create a SQLite database in memory
    conn = sqlite3.connect('city_stats.db')
    cursor = conn.cursor()
    
    # Create a table for city statistics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS city_stats (
        id INTEGER PRIMARY KEY,
        city TEXT NOT NULL,
        country TEXT NOT NULL,
        population INTEGER NOT NULL,
        area_sqkm REAL NOT NULL,
        founded_year INTEGER,
        is_capital BOOLEAN NOT NULL
    )
    ''')
    
    # Sample data for city statistics
    cities = [
        (1, 'Tokyo', 'Japan', 37400068, 2194.0, 1457, 1),
        (2, 'Delhi', 'India', 31181376, 1484.0, 1052, 0),
        (3, 'Shanghai', 'China', 27795702, 6340.5, 751, 0),
        (4, 'São Paulo', 'Brazil', 22043028, 1521.0, 1554, 0),
        (5, 'Mexico City', 'Mexico', 21782378, 1485.0, 1325, 1),
        (6, 'Cairo', 'Egypt', 21322750, 3085.0, 969, 1),
        (7, 'Mumbai', 'India', 20667656, 603.4, 1507, 0),
        (8, 'Beijing', 'China', 20462610, 16410.5, 1045, 1),
        (9, 'Dhaka', 'Bangladesh', 20283552, 306.4, 1608, 1),
        (10, 'Osaka', 'Japan', 19165340, 2720.0, 645, 0),
        (11, 'New York', 'USA', 18804000, 1213.4, 1624, 0),
        (12, 'Karachi', 'Pakistan', 16093786, 3780.0, 1729, 0),
        (13, 'Buenos Aires', 'Argentina', 15057273, 203.0, 1536, 1),
        (14, 'Chongqing', 'China', 15872179, 82403.0, 1929, 0),
        (15, 'Istanbul', 'Turkey', 15415197, 5461.0, 657, 0),
        (16, 'Kolkata', 'India', 14850066, 205.0, 1690, 0),
        (17, 'Manila', 'Philippines', 14406059, 42.9, 1571, 1),
        (18, 'Lagos', 'Nigeria', 14368332, 1171.0, 1914, 0),
        (19, 'Rio de Janeiro', 'Brazil', 13634274, 1221.0, 1565, 0),
        (20, 'Tianjin', 'China', 13396402, 11946.0, 1404, 0),
        (21, 'Berlin', 'Germany', 3664088, 891.8, 1237, 1)
    ]
    
    # Insert data into the table
    cursor.executemany('''
    INSERT OR REPLACE INTO city_stats (id, city, country, population, area_sqkm, founded_year, is_capital)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', cities)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    return 'city_stats.db'

# Function to create sample documents for RAG
def create_sample_documents() -> List[Document]:
    """Create sample documents about cities for the RAG component."""
    documents = []
    
    # Document about Berlin museums
    berlin_museums = """
    Berlin Museums Guide
    
    Berlin is home to numerous world-class museums that showcase art, history, and culture from around the globe.
    
    Museum Island (Museumsinsel) is a UNESCO World Heritage site in the heart of Berlin. It houses five internationally significant museums:
    1. The Pergamon Museum - Famous for its archaeological collections and reconstructed historic buildings like the Pergamon Altar and the Ishtar Gate of Babylon.
    2. The Bode Museum - Specializes in Byzantine art, sculpture, and coins.
    3. The Neues Museum - Houses the Egyptian collection, including the iconic bust of Nefertiti.
    4. The Alte Nationalgalerie - Contains 19th-century art and paintings.
    5. The Altes Museum - Showcases ancient Greek and Roman artifacts.
    
    Other notable museums in Berlin include:
    - The Jewish Museum - Designed by Daniel Libeskind, it documents Jewish history and culture in Germany.
    - The DDR Museum - An interactive museum about life in former East Germany.
    - The Berlin Wall Memorial and Documentation Center - Preserves a section of the Berlin Wall.
    - The Topography of Terror - Located on the former Gestapo headquarters, it documents Nazi crimes.
    - The Hamburger Bahnhof - A contemporary art museum housed in a former railway station.
    
    Many Berlin museums offer free entry on the first Sunday of each month, and the Museum Pass Berlin provides access to over 30 museums for three consecutive days.
    """
    
    # Document about Tokyo attractions
    tokyo_attractions = """
    Tokyo Attractions Guide
    
    Tokyo, the capital of Japan, offers a blend of ultramodern and traditional attractions that make it a unique destination.
    
    Popular landmarks and attractions include:
    
    - Tokyo Skytree - At 634 meters, it's the tallest structure in Japan and offers panoramic views of the city.
    - Senso-ji Temple - Tokyo's oldest temple, located in Asakusa, featuring a large red lantern and a shopping street.
    - Meiji Shrine - A Shinto shrine dedicated to Emperor Meiji and Empress Shoken, surrounded by a forested area.
    - Shibuya Crossing - One of the busiest pedestrian crossings in the world, where up to 3,000 people cross at once.
    - Shinjuku Gyoen National Garden - A spacious public park with French, English, and Japanese gardens.
    
    Tokyo is also known for its diverse neighborhoods:
    - Akihabara - The center for anime, manga, and electronics.
    - Harajuku - Famous for youth culture and fashion.
    - Ginza - An upscale shopping district with luxury boutiques.
    - Roppongi - Known for its nightlife and art museums.
    
    The city hosts numerous festivals throughout the year, including the Cherry Blossom Festival in spring and the Sumida River Fireworks Festival in summer.
    
    Tokyo's public transportation system, including the JR Yamanote Line and the Tokyo Metro, makes it easy to navigate the city despite its size.
    """
    
    # Document about New York City
    nyc_info = """
    New York City Overview
    
    New York City, often called the "Big Apple," is the most populous city in the United States and a global center for finance, culture, art, and entertainment.
    
    The city consists of five boroughs:
    - Manhattan - The central island and commercial heart of the city, home to skyscrapers, Central Park, and Broadway.
    - Brooklyn - Known for its cultural diversity, brownstone buildings, and hipster neighborhoods.
    - Queens - The largest borough by area and one of the most ethnically diverse urban areas in the world.
    - The Bronx - The only borough located on the mainland, known as the birthplace of hip-hop and home to the Bronx Zoo.
    - Staten Island - The most suburban of the five boroughs, connected to Manhattan by the Staten Island Ferry.
    
    Famous landmarks include:
    - The Statue of Liberty - A symbol of freedom and democracy, located on Liberty Island.
    - Empire State Building - An iconic 102-story skyscraper with observation decks.
    - Times Square - A major commercial intersection known for its bright lights and Broadway theaters.
    - Central Park - An 843-acre urban park that serves as a recreational oasis in Manhattan.
    - The Metropolitan Museum of Art - One of the world's largest and most visited art museums.
    
    New York City's subway system operates 24/7 and is one of the oldest and most extensive public transportation systems in the world.
    
    The city is a melting pot of cultures, with over 800 languages spoken, making it one of the most linguistically diverse cities globally.
    """
    
    # Document about Cairo history
    cairo_history = """
    Cairo Historical Overview
    
    Cairo, the capital of Egypt, is one of the oldest cities in the world with a rich history spanning over a thousand years.
    
    Founded in 969 CE by the Fatimid dynasty, Cairo (Al-Qahira, meaning "The Victorious") was established as an imperial capital. The city has been shaped by various civilizations, including the Fatimids, Ayyubids, Mamluks, Ottomans, and the modern Egyptian state.
    
    Historical landmarks include:
    
    - The Pyramids of Giza - Located on the outskirts of Cairo, these ancient structures were built around 2500 BCE and are the only surviving wonder of the ancient world.
    - The Egyptian Museum - Houses the world's largest collection of Pharaonic antiquities, including treasures from Tutankhamun's tomb.
    - The Citadel of Saladin - A medieval Islamic fortification built by Salah ad-Din (Saladin) in the 12th century to protect the city from Crusaders.
    - Al-Azhar Mosque - Founded in 970 CE, it's one of the oldest universities in the world and a center of Islamic learning.
    - Khan el-Khalili - A historic bazaar dating back to the 14th century, offering traditional crafts, spices, and souvenirs.
    
    Cairo's Old City (Islamic Cairo) is a UNESCO World Heritage site, containing hundreds of historic mosques, madrasas (schools), and monuments dating from the 7th century CE.
    
    The city has experienced significant growth in the modern era, expanding from a population of about 600,000 in the early 20th century to over 20 million in its metropolitan area today, making it the largest city in Africa and the Middle East.
    """
    
    documents.append(Document(text=berlin_museums, metadata={"source": "berlin_guide", "topic": "museums"}))
    documents.append(Document(text=tokyo_attractions, metadata={"source": "tokyo_guide", "topic": "attractions"}))
    documents.append(Document(text=nyc_info, metadata={"source": "nyc_guide", "topic": "overview"}))
    documents.append(Document(text=cairo_history, metadata={"source": "cairo_guide", "topic": "history"}))
    
    return documents

# Function to set up the vector store and index
@st.cache_resource
def setup_vector_store_and_index(_documents):
    """Set up a vector store and create an index from documents."""
    try:
        # Try to use Qdrant if available
        client = QdrantClient(host="localhost", port=6333)
        
        # Create a new collection for our documents if it doesn't exist
        collection_name = "city_guides"
        
        # Get embedding dimension from our model
        embed_model = get_embedding_model()
        
        # List collections to check if ours exists
        collections = client.get_collections().collections
        collection_exists = any(collection.name == collection_name for collection in collections)
        
        if not collection_exists:
            # Get embedding dimension
            sample_embedding = embed_model.get_text_embedding("sample text")
            dim = len(sample_embedding)
            
            # Create new collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config={"size": dim, "distance": "Cosine"}
            )
        
        # Create vector store
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=collection_name,
        )
        
        # Set up global settings with our models
        Settings.llm = get_llm()
        Settings.embed_model = embed_model
        
        # Create and return the index
        index = VectorStoreIndex.from_documents(
            _documents,
            vector_store=vector_store,
        )
        
        st.success("✅ Connected to Qdrant vector database successfully!")
        return index
    except Exception as e:
        st.error(f"Error setting up Qdrant vector store: {str(e)}")
        st.warning("Falling back to in-memory vector store as Qdrant is not available.")
        
        # Set up global settings with our models
        Settings.llm = get_llm()
        Settings.embed_model = get_embedding_model()
        
        # Use default in-memory vector store
        index = VectorStoreIndex.from_documents(
            _documents,
        )
        
        return index

# Function to set up the SQL database engine
@st.cache_resource
def setup_sql_engine(db_path):
    """Set up the SQL database engine for Text-to-SQL queries."""
    # Connect to the SQLite database
    sql_database = SQLDatabase.from_uri(f"sqlite:///{db_path}")
    
    # Set up global settings with our LLM
    Settings.llm = get_llm()
    
    # Create the SQL query engine
    sql_query_engine = NLSQLTableQueryEngine(
        sql_database=sql_database,
        tables=["city_stats"],
    )
    
    return sql_query_engine

# Function to set up the router query engine
def setup_router(vector_index, sql_query_engine):
    """Set up the router query engine that decides between RAG and SQL."""
    # Create query engine tools
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_index.as_query_engine(),
        description=(
            "Useful for answering questions about cities, their attractions, "
            "museums, history, and general information that would be found in travel guides or documents. "
            "Use this for questions about museums in Berlin, attractions in Tokyo, "
            "or historical information about cities."
        ),
        name="CityGuideRetrieval",
    )
    
    sql_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        description=(
            "Useful for answering questions about city statistics like population, area, "
            "founding year, and whether a city is a capital. Use this for questions about "
            "which city has the highest population, the area of specific cities, "
            "or comparing statistics between cities."
        ),
        name="CityStatisticsDB",
    )
    
    # Create the router query engine with LLMSingleSelector
    # This uses the LLM to select which tool to use based on the query
    router = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(
            llm=get_llm(),
        ),
        query_engine_tools=[vector_tool, sql_tool],
        verbose=True,
    )
    
    return router

# Main function to initialize the application
def initialize_app():
    """Initialize the application components."""
    with st.spinner("Setting up the application components..."):
        # Set up the database
        db_path = setup_database()
        
        # Create sample documents
        documents = create_sample_documents()
        
        # Set up the vector store and index
        vector_index = setup_vector_store_and_index(documents)
        
        # Set up the SQL query engine
        sql_query_engine = setup_sql_engine(db_path)
        
        # Set up the router
        router = setup_router(vector_index, sql_query_engine)
        
        return router

# Function to process user query
def process_query(router, query):
    """Process the user query using the router engine."""
    try:
        # Query the router engine
        response = router.query(query)
        
        # Extract the source tool to determine which path was taken
        source_tool = getattr(response, "metadata", {}).get("source", "Unknown")
        
        return response, source_tool
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None, "Error"

# Streamlit UI
def main():
    st.title("🧠 RAG + SQL Router Demo")
    st.markdown("""
    This application demonstrates a combined RAG (Retrieval-Augmented Generation) and Text-to-SQL workflow.
    Enter a natural language query, and an LLM-powered agent will decide whether to retrieve information from 
    unstructured text documents or to query a SQL database for the answer.
    """)
    
    # Check for required dependencies
    if not is_ollama_available():
        st.warning("""
        ⚠️ Ollama is not installed or not running. The application will use a simple response generator with limited functionality.
        
        For the full experience with a local LLM, please:
        1. Download Ollama from [ollama.com/download](https://ollama.com/download)
        2. Install it on your system
        3. Run `ollama pull llama3` in your terminal to download the model
        4. Restart this application
        """)
    
    try:
        # Try to connect to Qdrant
        QdrantClient(host="localhost", port=6333, timeout=5.0).get_collections()
    except Exception:
        st.warning("""
        ⚠️ Qdrant vector database is not available. The application will use an in-memory vector store instead.
        
        For the full experience with persistent vector storage, please:
        1. Install Docker from [docker.com](https://www.docker.com/products/docker-desktop/)
        2. Run `docker run -p 6333:6333 qdrant/qdrant` in your terminal
        3. Restart this application
        """)
    
    # Initialize the application if not already done
    if not st.session_state.initialized:
        with st.spinner("Initializing application..."):
            st.session_state.router = initialize_app()
            st.session_state.initialized = True
    
    # Create tabs for the application
    tab1, tab2, tab3 = st.tabs(["Query Interface", "Sample Questions", "About"])
    
    with tab1:
        st.subheader("Ask a Question")
        
        # User input
        query = st.text_input("Enter your question:", placeholder="e.g., What museums are in Berlin?")
        
        # Process button
        if st.button("Submit Query"):
            if query:
                with st.spinner("Processing your query..."):
                    response, source_tool = process_query(st.session_state.router, query)
                    
                    if response:
                        st.session_state.response = str(response)
                        st.session_state.route_taken = source_tool
                    else:
                        st.session_state.response = "Sorry, I couldn't process your query. Please try again."
                        st.session_state.route_taken = "Error"
        
        # Display the response
        if st.session_state.response:
            st.markdown("### Answer:")
            st.markdown(st.session_state.response)
            
            # Display which path was taken
            if st.session_state.route_taken:
                if "CityGuideRetrieval" in st.session_state.route_taken:
                    st.info("📚 This answer was retrieved from the document database using RAG.")
                elif "CityStatisticsDB" in st.session_state.route_taken:
                    st.info("🔢 This answer was generated by querying the SQL database.")
                else:
                    st.warning("⚠️ The source of this answer could not be determined.")
    
    with tab2:
        st.subheader("Sample Questions")
        st.markdown("""
        Here are some sample questions you can try:
        
        **Questions for the SQL Database:**
        - Which city has the highest population?
        - What is the area of Tokyo in square kilometers?
        - List all capital cities in the database.
        - Which city was founded the earliest?
        - How many cities in the database have a population over 20 million?
        
        **Questions for the Document Retrieval:**
        - What museums can I visit in Berlin?
        - Tell me about attractions in Tokyo.
        - What are the five boroughs of New York City?
        - What is the history of Cairo?
        - What is Museum Island in Berlin?
        
        Click on any question to try it out!
        """)
    
    with tab3:
        st.subheader("About This Application")
        st.markdown("""
        This application demonstrates the integration of two powerful approaches to question answering:
        
        1. **RAG (Retrieval-Augmented Generation)**: Retrieves relevant information from a collection of documents and uses an LLM to generate an answer based on the retrieved content.
        
        2. **Text-to-SQL**: Converts natural language questions into SQL queries to retrieve structured data from a database.
        
        The application uses a router powered by an LLM to decide which approach is more appropriate for each question. This allows it to handle both structured data queries (like statistics and facts) and more general knowledge questions that require context from documents.
        
        **Technologies Used:**
        - **LlamaIndex**: For the core RAG and Text-to-SQL capabilities
        - **Ollama**: To run the LLM locally
        - **Qdrant**: As the vector database for document embeddings
        - **SQLite**: For the structured database
        - **Streamlit**: For the web interface
        
        **Note**: This demo uses a small sample dataset. In a production environment, you would connect to larger databases and document collections.
        """)

if __name__ == "__main__":
    main()
