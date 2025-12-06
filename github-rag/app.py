import os
import gc
import tempfile
import uuid
import pandas as pd
from typing import Optional, Dict, Any
import logging
from functools import wraps
import time

from gitingest import ingest
from llama_index.core import Settings, PromptTemplate, VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser
import streamlit as st
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Constants
MAX_REPO_SIZE = 100 * 1024 * 1024  # 100MB
SUPPORTED_REPO_TYPES = ['.py', '.md', '.ipynb', '.js', '.ts', '.json']
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

class GitHubRAGError(Exception):
    """Base exception for GitHub RAG application errors"""
    pass

class ValidationError(GitHubRAGError):
    """Raised when input validation fails"""
    pass

class ProcessingError(GitHubRAGError):
    """Raised when repository processing fails"""
    pass

class QueryEngineError(GitHubRAGError):
    """Raised when query engine creation or operation fails"""
    pass

class SessionError(GitHubRAGError):
    """Raised when session management fails"""
    pass

def retry_on_error(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """Decorator for retrying operations on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying...")
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

def validate_github_url(url: str) -> bool:
    """Validate GitHub repository URL"""
    if not url:
        raise ValidationError("Repository URL cannot be empty")
    if not url.startswith(('https://github.com/', 'http://github.com/')):
        raise ValidationError("Invalid GitHub URL format. URL must start with 'https://github.com/' or 'http://github.com/'")
    return True

def get_repo_name(url: str) -> str:
    """Extract repository name from URL"""
    try:
        parts = url.split('/')
        if len(parts) < 5:
            raise ValidationError("Invalid repository URL format")
        repo_name = parts[-1].replace('.git', '')
        if not repo_name:
            raise ValidationError("Could not extract repository name from URL")
        return repo_name
    except Exception as e:
        raise ValidationError(f"Failed to extract repository name: {str(e)}")

def cleanup_session():
    """Clean up session resources"""
    try:
        if hasattr(st.session_state, 'file_cache'):
            for key, value in st.session_state.file_cache.items():
                try:
                    del value
                except Exception as e:
                    logger.warning(f"Failed to cleanup cache entry {key}: {str(e)}")
            st.session_state.file_cache.clear()
        gc.collect()
        logger.info("Session cleanup completed successfully")
    except Exception as e:
        logger.error(f"Error during session cleanup: {str(e)}")
        raise SessionError(f"Failed to cleanup session: {str(e)}")

def reset_chat():
    """Reset chat session and clean up resources"""
    try:
        st.session_state.messages = []
        st.session_state.context = None
        cleanup_session()
        logger.info("Chat session reset successfully")
    except Exception as e:
        logger.error(f"Error resetting chat: {str(e)}")
        raise SessionError("Failed to reset chat session")

@retry_on_error()
def process_with_gitingets(github_url: str) -> tuple:
    """Process GitHub repository using gitingest"""
    try:
        summary, tree, content = ingest(github_url)
        if not all([summary, tree, content]):
            raise ProcessingError("Failed to process repository: Missing data")
        return summary, tree, content
    except Exception as e:
        logger.error(f"Error processing repository: {str(e)}")
        raise ProcessingError(f"Failed to process repository: {str(e)}")

def create_query_engine(content_path: str, repo_name: str) -> Any:
    """Create and configure query engine"""
    try:
        loader = SimpleDirectoryReader(input_dir=content_path)
        docs = loader.load_data()
        node_parser = MarkdownNodeParser()
        index = VectorStoreIndex.from_documents(
            documents=docs, 
            transformations=[node_parser], 
            show_progress=True
        )

        qa_prompt_tmpl_str = """
        You are an AI assistant specialized in analyzing GitHub repositories.

        Repository structure:
        {tree}
        ---------------------

        Context information from the repository:
        {context_str}
        ---------------------

        Given the repository structure and context above, provide a clear and precise answer to the query. 
        Focus on the repository's content, code structure, and implementation details. 
        If the information is not available in the context, respond with 'I don't have enough information about that aspect of the repository.'

        Query: {query_str}
        Answer: """
        
        qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)
        query_engine = index.as_query_engine(streaming=True)
        query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
        )
        return query_engine
    except Exception as e:
        logger.error(f"Error creating query engine: {str(e)}")
        raise QueryEngineError(f"Failed to create query engine: {str(e)}")

def initialize_session_state():
    """Initialize or reset session state variables"""
    try:
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'context' not in st.session_state:
            st.session_state.context = None
        if 'file_cache' not in st.session_state:
            st.session_state.file_cache = {}
        if 'current_repo' not in st.session_state:
            st.session_state.current_repo = None
        if 'query_engine' not in st.session_state:
            st.session_state.query_engine = None
        logger.info("Session state initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing session state: {str(e)}")
        raise SessionError("Failed to initialize session state")

def handle_repository_loading(github_url: str) -> None:
    """Handle repository loading process with proper error handling"""
    try:
        validate_github_url(github_url)
        repo_name = get_repo_name(github_url)
        
        with st.spinner(f"Processing repository {repo_name}..."):
            summary, tree, content = process_with_gitingets(github_url)
            
            # Create temporary directory for repository content
            with tempfile.TemporaryDirectory() as temp_dir:
                content_path = os.path.join(temp_dir, repo_name)
                os.makedirs(content_path, exist_ok=True)
                
                # Save repository content
                for file_path, file_content in content.items():
                    file_dir = os.path.dirname(os.path.join(content_path, file_path))
                    os.makedirs(file_dir, exist_ok=True)
                    with open(os.path.join(content_path, file_path), 'w', encoding='utf-8') as f:
                        f.write(file_content)
                
                # Create query engine
                query_engine = create_query_engine(content_path, repo_name)
                
                # Update session state
                st.session_state.query_engine = query_engine
                st.session_state.current_repo = repo_name
                st.session_state.context = {
                    'summary': summary,
                    'tree': tree,
                    'content': content
                }
                
                st.success(f"Successfully loaded repository: {repo_name}")
                logger.info(f"Repository {repo_name} loaded successfully")
                
    except ValidationError as e:
        st.error(f"Validation error: {str(e)}")
        logger.warning(f"Validation error for URL {github_url}: {str(e)}")
    except ProcessingError as e:
        st.error(f"Processing error: {str(e)}")
        logger.error(f"Error processing repository {github_url}: {str(e)}")
    except QueryEngineError as e:
        st.error(f"Query engine error: {str(e)}")
        logger.error(f"Error creating query engine for {github_url}: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error processing {github_url}: {str(e)}")
    finally:
        cleanup_session()

def handle_chat_message(prompt: str) -> None:
    """Handle chat message processing with proper error handling"""
    try:
        if not st.session_state.query_engine:
            raise QueryEngineError("Please load a repository first!")
        
        if not prompt.strip():
            raise ValidationError("Please enter a non-empty message")
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get response from query engine
        response = st.session_state.query_engine.query(prompt)
        
        # Format and display response
        full_response = f"Repository: {st.session_state.current_repo}\n\n{response}"
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        logger.info(f"Successfully processed chat message for repository {st.session_state.current_repo}")
        
    except ValidationError as e:
        st.error(f"Validation error: {str(e)}")
        logger.warning(f"Chat validation error: {str(e)}")
    except QueryEngineError as e:
        st.error(f"Query engine error: {str(e)}")
        logger.error(f"Error in chat processing: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in chat: {str(e)}")

def main():
    """Main application function"""
    st.title("GitHub Repository RAG")
    
    try:
        # Initialize session state
        initialize_session_state()
        
        # Sidebar for repository input
        with st.sidebar:
            st.header("Repository Settings")
            github_url = st.text_input("Enter GitHub Repository URL")
            
            if st.button("Load Repository"):
                if github_url:
                    handle_repository_loading(github_url)
                else:
                    st.warning("Please enter a GitHub repository URL")
            
            if st.button("Reset Chat"):
                reset_chat()
        
        # Main chat interface
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        if prompt := st.chat_input("Ask a question about the repository"):
            handle_chat_message(prompt)
            
    except SessionError as e:
        st.error(f"Session error: {str(e)}")
        logger.error(f"Session error in main: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in main: {str(e)}")

if __name__ == "__main__":
    main()