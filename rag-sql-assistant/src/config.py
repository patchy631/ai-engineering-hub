"""
Configuration module for the RAG-SQL Assistant.

This module loads environment variables from the .env file and provides
configuration parameters for the application.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def load_config() -> Dict[str, Any]:
    """
    Load environment variables and configuration parameters for the application.
    
    Returns:
        Dict[str, Any]: Configuration dictionary
    
    Raises:
        ValueError: If required environment variables are missing
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Required environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "LLAMA_CLOUD_API_KEY",
        "LLAMA_CLOUD_ORG_ID",
        "LLAMA_CLOUD_PROJECT",
        "LLAMA_CLOUD_INDEX"
    ]
    
    # Check for missing required variables
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Optional environment variables
    database_url = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    
    # Configure Streamlit page settings
    st.set_page_config(
        page_title="City Assistant: RAG + SQL",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Return config dictionary
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "llama_cloud_api_key": os.getenv("LLAMA_CLOUD_API_KEY"),
        "llama_cloud_org_id": os.getenv("LLAMA_CLOUD_ORG_ID"),
        "llama_cloud_project": os.getenv("LLAMA_CLOUD_PROJECT"),
        "llama_cloud_index": os.getenv("LLAMA_CLOUD_INDEX"),
        "phoenix_api_key": os.getenv("PHOENIX_API_KEY"),  # Optional
        "database_url": database_url,
    }


def get_openai_api_key() -> str:
    """Get the OpenAI API key."""
    return os.getenv("OPENAI_API_KEY", "")


def get_llama_cloud_config() -> Dict[str, str]:
    """
    Get LlamaCloud configuration parameters.
    
    Returns:
        Dict[str, str]: LlamaCloud configuration
    """
    return {
        "api_key": os.getenv("LLAMA_CLOUD_API_KEY", ""),
        "org_id": os.getenv("LLAMA_CLOUD_ORG_ID", ""),
        "project": os.getenv("LLAMA_CLOUD_PROJECT", ""),
        "index": os.getenv("LLAMA_CLOUD_INDEX", ""),
    }


def enable_tracing() -> Optional[str]:
    """
    Enable tracing with LlamaTrace if configured.
    
    Returns:
        Optional[str]: Phoenix API key if available, None otherwise
    """
    phoenix_api_key = os.getenv("PHOENIX_API_KEY")
    if phoenix_api_key:
        # Configure environment variable for Arize Phoenix
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={phoenix_api_key}"
        
        # Import and configure tracing if available
        try:
            import llama_index.core
            llama_index.core.set_global_handler(
                "arize_phoenix", 
                endpoint="https://llamatrace.com/v1/traces"
            )
            return phoenix_api_key
        except ImportError:
            print("Warning: llama_index.core or Arize Phoenix not installed. Tracing disabled.")
    return None


# Export constants for easy access
OPENAI_API_KEY = get_openai_api_key()
LLAMA_CLOUD_CONFIG = get_llama_cloud_config()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
