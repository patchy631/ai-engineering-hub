import streamlit as st
import os
import tempfile
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
import pandas as pd
from typing import List, Dict
import json
import openai

# Set page config
st.set_page_config(
    page_title="AI Agent Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e6f3ff;
        border: 1px solid #b3d7ff;
    }
    .assistant-message {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    /* Style for API key input */
    .stTextInput > div > div > input[type="password"] {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 0.5rem;
        font-family: monospace;
    }
    /* Style for message content */
    .chat-message > div:nth-child(2) {
        margin: 0.5rem 0;
        line-height: 1.5;
        color: #2c3e50;
    }
    /* Style for timestamps */
    .chat-message > div:last-child {
        color: #6c757d;
        font-size: 0.8rem;
        margin-top: 0.5rem;
    }
    /* Style for role labels */
    .chat-message > div:first-child {
        color: #495057;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 AI Agent Assistant")
st.markdown("""
    This application uses an intelligent agent to answer your questions based on the uploaded documents.
    The agent automatically determines the best way to answer your question using RAG or SQL capabilities.
""")

# Initialize session state variables
if 'index' not in st.session_state:
    st.session_state.index = None
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'uploaded_files' not in st.session_state:
    st.session_state.uploaded_files = []
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = None

def get_llm():
    """Get OpenAI LLM with API key."""
    if not st.session_state.openai_api_key:
        raise ValueError("OpenAI API key not set. Please add your API key in the sidebar.")
    
    # Set the API key globally
    openai.api_key = st.session_state.openai_api_key
    
    return OpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        api_key=st.session_state.openai_api_key
    )

def process_documents(directory: str) -> VectorStoreIndex:
    """Process documents and create a vector index."""
    try:
        # Set up embedding model
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Set up OpenAI LLM
        llm = get_llm()
        
        # Create node parser
        node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
        
        # Load documents
        documents = SimpleDirectoryReader(directory).load_data()
        
        # Create index with components directly
        index = VectorStoreIndex.from_documents(
            documents,
            llm=llm,
            embed_model=embed_model,
            transformations=[node_parser]
        )
        
        return index
    except Exception as e:
        st.error(f"Error processing documents: {str(e)}")
        return None

def add_to_chat_history(role: str, content: str):
    """Add a message to the chat history."""
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def display_chat_history():
    """Display the chat history with proper formatting."""
    for message in st.session_state.chat_history:
        message_class = "user-message" if message["role"] == "user" else "assistant-message"
        st.markdown(f"""
            <div class="chat-message {message_class}">
                <div style="font-weight: bold;">{message['role'].title()}</div>
                <div style="white-space: pre-wrap;">{message['content']}</div>
                <div style="font-size: 0.8em; color: #666;">{message['timestamp']}</div>
            </div>
        """, unsafe_allow_html=True)

# Sidebar for file upload and processing
with st.sidebar:
    st.header("⚙️ Settings")
    
    # OpenAI API Key input with better styling
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <h4 style="margin-bottom: 0.5rem;">🔑 OpenAI API Key</h4>
            <p style="font-size: 0.8rem; color: #6c757d; margin-bottom: 0.5rem;">
                Enter your OpenAI API key to enable AI features. Your key is stored securely and never shared.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    api_key = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.openai_api_key if st.session_state.openai_api_key else "",
        help="Enter your OpenAI API key to enable the AI features."
    )
    
    if api_key:
        st.session_state.openai_api_key = api_key
        # Set the API key globally
        openai.api_key = api_key
        st.success("✅ OpenAI API key set successfully!")
    
    st.markdown("---")
    st.header("📁 Document Management")
    
    # Option to select an existing directory or upload files
    option = st.radio("Choose an option:", ["Upload PDF files", "Select directory"])
    
    if option == "Select directory":
        directory = st.text_input("Enter the directory path containing PDFs:")
        
        if directory and os.path.isdir(directory):
            st.success(f"Directory selected: {directory}")
            
            if st.button("Process PDFs"):
                with st.spinner("Processing PDFs..."):
                    st.session_state.index = process_documents(directory)
                    if st.session_state.index is not None:
                        st.session_state.processed = True
                        st.success("PDFs processed successfully!")
    else:
        uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            if st.button("Process Uploaded PDFs"):
                with tempfile.TemporaryDirectory() as temp_dir:
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(temp_dir, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    with st.spinner("Processing PDFs..."):
                        st.session_state.index = process_documents(temp_dir)
                        if st.session_state.index is not None:
                            st.session_state.processed = True
                            st.success("PDFs processed successfully!")

# Main chat interface
if st.session_state.processed and st.session_state.index is not None:
    st.header("💬 Ask Your Questions")
    
    # Display chat history
    display_chat_history()
    
    # Query interface
    st.markdown("---")
    query = st.text_input("Your question:", key="query_input")
    
    # Only process if query is new and not empty
    if query and query != st.session_state.last_query:
        st.session_state.last_query = query
        add_to_chat_history("user", query)
        
        with st.spinner("Thinking..."):
            try:
                # Get a fresh LLM instance for the query
                llm = get_llm()
                query_engine = st.session_state.index.as_query_engine(llm=llm)
                response = query_engine.query(query)
                answer = response.response
                
                add_to_chat_history("assistant", answer)
                st.rerun()  # Rerun to update the UI
                
            except Exception as e:
                error_message = f"Error generating answer: {str(e)}"
                st.error(error_message)
                add_to_chat_history("assistant", error_message)
                st.rerun()  # Rerun to update the UI
else:
    if not st.session_state.openai_api_key:
        st.warning("⚠️ Please add your OpenAI API key in the sidebar to enable AI features.")
    st.info("👈 Please upload and process PDFs using the sidebar to start asking questions!")
