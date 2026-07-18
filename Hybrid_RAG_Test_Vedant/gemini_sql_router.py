import os
import streamlit as st
from llama_index.llms.gemini import Gemini
from llama_index.core import Settings
from llama_index.core.utilities.sql_wrapper import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.embeddings.gemini import GeminiEmbedding
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert, text, desc, asc, func
import re
from typing import List, Dict, Any, Tuple

# Initialize Streamlit page config
st.set_page_config(page_title="LlamaCloud RAG Demo", page_icon="🦙", layout="wide")

# --- Google API Key ---
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = ""

# --- Database Setup ---
def setup_database():
    """Set up the SQLite database with city information."""
    engine = create_engine("sqlite:///:memory:", future=True)
    metadata_obj = MetaData()

    # Create city SQL table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(16), primary_key=True),
        Column("population", Integer),
        Column("state", String(16), nullable=False),
    )

    metadata_obj.create_all(engine)

    # Insert city data
    rows = [
        {"city_name": "New York City", "population": 8336000, "state": "New York"},
        {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
        {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
        {"city_name": "Houston", "population": 2303000, "state": "Texas"},
        {"city_name": "Miami", "population": 449514, "state": "Florida"},
        {"city_name": "Seattle", "population": 749256, "state": "Washington"},
    ]
    
    for row in rows:
        stmt = insert(city_stats_table).values(**row)
        with engine.begin() as connection:
            connection.execute(stmt)
    
    return engine, city_stats_table

# Add a robust SQL helper class for dynamic querying
class CityQueryEngine:
    def __init__(self, engine):
        self.engine = engine
    
    def execute_query(self, query_text):
        """Execute a raw SQL query and return formatted results"""
        with self.engine.connect() as conn:
            result = conn.execute(text(query_text))
            rows = result.fetchall()
            if not rows:
                return "No matching cities found in the database."
            
            # Format the results
            if len(rows) == 1:
                row = rows[0]
                return f"{row[0]} has a population of {row[1]:,} people and is located in {row[2]}."
            else:
                formatted_rows = "\n".join([f"- {row[0]}: {row[1]:,} people in {row[2]}" for row in rows])
                return f"City information:\n\n{formatted_rows}"
    
    def query_highest_population(self):
        """Query city with highest population"""
        query = "SELECT city_name, population, state FROM city_stats ORDER BY population DESC LIMIT 1"
        return self.execute_query(query)
    
    def query_lowest_population(self):
        """Query city with lowest population"""
        query = "SELECT city_name, population, state FROM city_stats ORDER BY population ASC LIMIT 1"
        return self.execute_query(query)
    
    def query_all_cities_ranked(self):
        """Query all cities ranked by population"""
        query = "SELECT city_name, population, state FROM city_stats ORDER BY population DESC"
        return self.execute_query(query)
    
    def query_by_state(self, state_name):
        """Query cities in a specific state"""
        query_text = text("SELECT city_name, population, state "
                          "FROM city_stats WHERE state LIKE :state_name "
                          "ORDER BY population DESC")
        return self.execute_query(query_text.params(state_name=f'%{state_name}%'))
    def process_population_query(self, query_text):
        """Process a natural language query about population"""
        query_lower = query_text.lower()
        
        # Check for highest/largest/biggest population
        if any(term in query_lower for term in ["highest", "largest", "biggest", "most populous"]):
            return self.query_highest_population()
            
        # Check for lowest/smallest population
        elif any(term in query_lower for term in ["lowest", "smallest", "least populous"]):
            return self.query_lowest_population()
            
        # Check for state-specific queries
        state_match = re.search(r"in\s+([a-zA-Z\s]+)(?:\?)?$", query_lower)
        if state_match:
            state_name = state_match.group(1).strip()
            return self.query_by_state(state_name)
            
        # Check for ranking/listing
        elif any(term in query_lower for term in ["list", "rank", "compare", "all cities"]):
            return self.query_all_cities_ranked()
            
        # Default to highest if just asking about population
        elif "population" in query_lower:
            return self.query_highest_population()
            
        return None  # No match found

# --- Main Application ---
def main():
    st.title("🦙 LlamaCloud RAG Demo")
    st.markdown("""
    This demo showcases Retrieval-Augmented Generation (RAG) using LlamaCloud for document retrieval.
    Ask questions about cities like New York, Los Angeles, Chicago, Houston, Miami, or Seattle!
    """)
    
    # API key input (in sidebar)
    with st.sidebar:
        st.title("API Settings")
        api_key = st.text_input("Enter your Google API Key:", type="password", 
                               value=st.session_state.GOOGLE_API_KEY)
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            os.environ["GOOGLE_API_KEY"] = api_key
        
        st.divider()
        
        st.subheader("LlamaCloud Settings")
        llamacloud_api_key = st.text_input("LlamaCloud API Key:", type="password",
                                          value="llx-CssfMkf0ENH0TTeU6xCxZC9hmOYm656gHu7fkexPHsu2hACz")
        llamacloud_org_id = st.text_input("Organization ID:",
                                         value="ea3321f4-0226-41b8-9929-5f5f8c396086")
        llamacloud_project = st.text_input("Project Name:",
                                          value="Default")
        llamacloud_index = st.text_input("Index Name:",
                                        value="overwhelming-felidae-2025-03-13")
        
        st.subheader("RAG Components")
        st.markdown("""
        1. **Document Retrieval**
        - LlamaCloud for document storage
        - Pre-indexed city documents
        
        2. **Structured Data**  
        - SQL database for city statistics
        - Population and state information
        
        3. **Generation**
        - Gemini 2.0 Flash model
        - Context-aware responses
        """)
    
    # Initialize chat if API key present
    if not st.session_state.GOOGLE_API_KEY:
        st.warning("Please enter your Google API Key in the sidebar to continue.")
        return
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Set up structured data (SQL database)
    engine, city_stats_table = setup_database()
    
    # Initialize Gemini model and embeddings
    gemini_model = Gemini(
        model="models/gemini-2.0-flash",
        api_key=st.session_state.GOOGLE_API_KEY,
        temperature=0.2
    )
    
    gemini_embed_model = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key=st.session_state.GOOGLE_API_KEY
    )
    
    # Configure global settings
    Settings.llm = gemini_model
    Settings.embed_model = gemini_embed_model
    
    # Create SQL database wrapper
    sql_database = SQLDatabase(engine, include_tables=["city_stats"])
    
    # Create SQL query engine using direct instantiation
    try:
        sql_query_engine = NLSQLTableQueryEngine(
            sql_database=sql_database,
                tables=["city_stats"],
                synthesize_response=True,
                context_query_kwargs={
                    "schema_context": "Table 'city_stats' has columns: city_name (String, primary key), population (Integer), state (String)"
                }
            )
    except Exception as e:
        st.error(f"Error setting up SQL query engine: {str(e)}")
        sql_query_engine = None
    
    # Initialize query engines
    have_llamacloud = False
    vector_query_engine = None
    
    # Connect to LlamaCloud if credentials are provided
    if all([llamacloud_api_key, llamacloud_org_id, llamacloud_project, llamacloud_index]):
        try:
            index = LlamaCloudIndex(
                name=llamacloud_index,
                project_name=llamacloud_project,
                organization_id=llamacloud_org_id,
                api_key=llamacloud_api_key
            )
            
            vector_query_engine = index.as_query_engine()
            have_llamacloud = True
            st.sidebar.success("✅ Connected to LlamaCloud")
        except Exception as e:
            st.sidebar.error(f"Error connecting to LlamaCloud: {str(e)}")
    else:
        st.sidebar.warning("⚠️ LlamaCloud credentials not fully provided. Only SQL queries will work.")
    
    # Get user input
    if prompt := st.chat_input("Ask about US cities..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process query and generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                message_placeholder = st.empty()
                
                try:
                    # Create the query engine
                    city_query_engine = CityQueryEngine(engine)
                    
                    # Check if this is a population query
                    if any(word in prompt.lower() for word in ['population', 'populous', 'big city', 'large city', 'small city']):
                        # Try direct SQL approach first
                        result = city_query_engine.process_population_query(prompt)
                        if result:
                            message_placeholder.markdown(f"{result}\n\n*Source: Database (Direct SQL)*")
                            st.session_state.messages.append({"role": "assistant", "content": f"{result}\n\n*Source: Database (Direct SQL)*"})
                        else:
                            # Fall back to LLM-based SQL
                            response = sql_query_engine.query(prompt)
                            message_placeholder.markdown(f"{str(response)}\n\n*Source: Database*")
                            st.session_state.messages.append({"role": "assistant", "content": f"{str(response)}\n\n*Source: Database*"})
                    elif have_llamacloud:
                        # For general information, use LlamaCloud
                        response = vector_query_engine.query(prompt)
                        message_placeholder.markdown(f"{str(response)}\n\n*Source: LlamaCloud*")
                        st.session_state.messages.append({"role": "assistant", "content": f"{str(response)}\n\n*Source: LlamaCloud*"})
                    else:
                        # If neither available
                        message_placeholder.markdown("I'm unable to answer that question with the current configuration.")
                        st.session_state.messages.append({"role": "assistant", "content": "I'm unable to answer that question with the current configuration."})
                
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    message_placeholder.markdown("I encountered an error processing your question. Please try rephrasing or asking something else.")
                    st.session_state.messages.append({"role": "assistant", "content": "I encountered an error processing your question. Please try rephrasing or asking something else."})

if __name__ == "__main__":
    main()