"""
Query Processing Module for RAG-SQL Assistant

This module handles the processing of user queries through the router workflow,
coordinating between RAG and SQL tools as needed.
"""

import logging
import asyncio
from typing import Dict, Any

from src.router import RouterWorkflow, create_rag_tool, create_sql_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def _run_workflow_async(query: str) -> str:
    """
    Run the router workflow asynchronously.
    
    Args:
        query: The user's query string
        
    Returns:
        Response string from the workflow
    """
    # Create tools
    rag_tool = create_rag_tool()
    sql_tool = create_sql_tool()
    
    # Initialize router workflow
    router = RouterWorkflow(
        tools=[rag_tool, sql_tool],
        verbose=True,
        llm=None,  # Will use default from config
        chat_history=[]  # Start fresh for each query
    )
    
    # Run the workflow asynchronously
    return await router.run(message=query)

def process_query(query: str) -> Dict[str, Any]:
    """
    Process a user query through the router workflow.
    
    Args:
        query: The user's query string
        
    Returns:
        Dictionary with response content
    """
    try:
        # Run the async function in a new event loop
        result = asyncio.run(_run_workflow_async(query))
        
        return {
            "content": result
        }
    except Exception as e:
        logger.exception(f"Error processing query: {e}")
        return {
            "content": f"I encountered an error processing your query: {str(e)}"
        } 