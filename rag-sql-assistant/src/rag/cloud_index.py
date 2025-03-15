"""
LlamaCloud RAG Module

This module provides functionality to connect to LlamaCloud and perform
semantic search on indexed documents (Wikipedia pages about various US cities).
"""
from typing import Any

from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import QueryEngineTool

from src.config import get_llama_cloud_config, get_openai_api_key


class LlamaCloudRAG:
    """Class to manage retrieval-augmented generation with LlamaCloud."""
    
    def __init__(self):
        """
        Initialize the LlamaCloud RAG component using environment variables.
        """
        # Set LLM in Settings
        api_key = get_openai_api_key()
        if api_key:
            Settings.llm = OpenAI(api_key=api_key)
        
        # Initialize the LlamaCloud index using environment variables
        config = get_llama_cloud_config()
        print(config)
        
        self.index = LlamaCloudIndex(
            name=config["index"],
            project_name=config["project"],
            organization_id=config["org_id"],
            api_key=config["api_key"]
        )
        
        # Create query engine
        self.query_engine = self.index.as_query_engine()
        
        # Create tool for use in agent
        self.tool = QueryEngineTool.from_defaults(
            query_engine=self.query_engine,
            description="Useful for answering semantic questions about certain cities in the US.",
            name="llama_cloud_tool"
        )
    
    def query(self, query_text: str) -> Any:
        """
        Query the LlamaCloud index with a natural language query.
        
        Args:
            query_text: The natural language query text
            
        Returns:
            Any: The response from the query engine
        """
        return self.query_engine.query(query_text)
