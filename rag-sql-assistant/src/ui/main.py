"""
Main UI Components for RAG-SQL Assistant

This module provides the main Streamlit UI components for the RAG-SQL Assistant,
including page configuration, sidebar, and layout.
"""

import os
import streamlit as st
import base64
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="RAG-SQL Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar():
    """Render the sidebar with API status and about information."""
    
    with st.sidebar:
        
        # About section
        st.markdown("""
        ### About This Project
        
        This assistant intelligently routes your questions to:
        
        1. **SQL Database**: City stats (population, state) for NYC, LA, Chicago, Houston, Miami, and Seattle
        
        2. **LlamaCloud RAG**: Wikipedia content about these cities
        
        Ask about population figures or explore detailed information like history, attractions, and more. The system automatically chooses the right data source.
        
        **Source Code**: [GitHub Repository](https://github.com/patchy631/ai-engineering-hub)
        """)
        
        st.markdown("""
        ---
        
        ## 📬 Stay Updated with Daily Dose of Data Science!
        
        **Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science 
        when you subscribe to our newsletter!
        
        [Subscribe now!](https://join.dailydoseofds.com)
        """)

def render_header():
    """Render the application header with logo."""
    try:
        # Define base assets directory
        assets_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent / "assets"
        
        # Define possible paths for the logos
        openai_possible_paths = [
            os.path.join("assets", "openai-logo.png"),
            "repo-to-submit-pr/rag-sql-assistant/assets/openai-logo.png",
            "rag-sql-assistant/assets/openai-logo.png",
            str(assets_dir / "openai-logo.png")
        ]
        
        llama_cloud_possible_paths = [
            os.path.join("assets", "llama-cloud.png"),
            "repo-to-submit-pr/rag-sql-assistant/assets/llama-cloud.png",
            "rag-sql-assistant/assets/llama-cloud.png",
            str(assets_dir / "llama-cloud.png")
        ]
        
        # Find OpenAI logo
        openai_logo_path = None
        for path in openai_possible_paths:
            if os.path.exists(path):
                openai_logo_path = path
                break
        
        # Find LlamaCloud logo
        llama_cloud_logo_path = None
        for path in llama_cloud_possible_paths:
            if os.path.exists(path):
                llama_cloud_logo_path = path
                break
        
        # Display header with logos if found
        col1, col2 = st.columns([6, 1])
        
        with col1:
            if openai_logo_path and llama_cloud_logo_path:
                # Both logos found
                st.markdown("""
                # RAG-SQL Assistant powered by <img src="data:image/png;base64,{}" style="height: 0.9em; vertical-align: middle; padding-left: 5px; padding-right: 5px;"> and <img src="data:image/png;base64,{}" style="height: 0.9em; vertical-align: middle; padding-left: 5px;">
                """.format(
                    base64.b64encode(open(openai_logo_path, "rb").read()).decode(),
                    base64.b64encode(open(llama_cloud_logo_path, "rb").read()).decode()
                ), unsafe_allow_html=True)
            else:
                # Fallback to text if logos not found
                st.header("RAG-SQL Assistant powered by OpenAI and LlamaCloud")
        
        with col2:
            from src.ui.chat import reset_chat
            st.button("Clear ↺", on_click=reset_chat)
            
    except Exception as e:
        logger.exception(f"Error loading logos: {e}")
        st.header("RAG-SQL Assistant powered by OpenAI and LlamaCloud")

def render_main_ui(process_query_func):
    """
    Render the main UI components including chat interface.
    
    Args:
        process_query_func: Function to process user queries
    """
    from src.ui.chat import initialize_chat_state, display_chat_history, add_user_message, add_assistant_message
    from src.ui.utils import stream_text_with_cursor
    
    # Initialize chat state
    initialize_chat_state()
    
    # Check if this is a new session (no messages yet) and add a welcome message
    if not st.session_state.get("messages", []):
        welcome_message = (
            "👋 Hi there! I'm your RAG-SQL Assistant. Ask me anything about New York City, Los Angeles, "
            "Chicago, Houston, Miami, or Seattle!\n\n"
            "I can tell you about population figures, which states they're in, or dive into details "
            "about history, attractions, transportation, and more. What would you like to know?"
        )
        add_assistant_message(welcome_message)
    
    # Display chat history
    display_chat_history()
    
    # Accept user input
    if prompt := st.chat_input("Ask a question using natural language..."):
        # Add user message to chat history
        add_user_message(prompt)
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Processing your query..."):
                # Process the query
                response = process_query_func(prompt)
                full_response = str(response["content"])
                
                # Display the response with streaming effect and red cursor
                stream_text_with_cursor(full_response)
            
            # Add assistant response to chat history
            add_assistant_message(full_response)