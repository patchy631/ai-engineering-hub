"""
RAG-SQL Assistant

This application provides a Streamlit interface for the RAG-SQL Assistant,
which combines RAG and Text-to-SQL capabilities in a single interface.
"""

import uuid
import gc
import logging
import streamlit as st
from dotenv import load_dotenv

# Import from local modules
from src.ui import setup_page_config, render_sidebar, render_header, render_main_ui
from src.query_processor import process_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize session state for file cache if needed
if "chat_id" not in st.session_state:
    st.session_state.chat_id = uuid.uuid4()
    st.session_state.file_cache = {}

def main():
    """Main application entry point."""
    # Configure the page
    setup_page_config()
    
    # Render sidebar with API status and about info
    render_sidebar()
    
    # Render header with logo
    render_header()
    
    # Render main UI with chat interface
    render_main_ui(process_query)

if __name__ == "__main__":
    main()
