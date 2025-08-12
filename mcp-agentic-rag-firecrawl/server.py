# server.py
from mcp.server.fastmcp import FastMCP
from rag_code import *

# Create an MCP server
mcp = FastMCP("MCP-RAG-app",
              host="127.0.0.1",
              port=8080,
              timeout=30)

@mcp.tool()
def machine_learning_faq_retrieval_tool(query: str) -> str:
    """Retrieve the most relevant documents from the machine learning
       FAQ collection. Use this tool when the user asks about ML.

    Input:
        query: str -> The user query to retrieve the most relevant documents

    Output:
        context: str -> most relevant documents retrieved from a vector DB
    """

    # check type of text
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    
    retriever = Retriever(QdrantVDB("ml_faq_collection"), EmbedData())
    response = retriever.search(query)

    return response


@mcp.tool()
def firecrawl_web_search_tool(query: str) -> list[str]:
    """
    Search for information on a given topic using Firecrawl.
    Use this tool when the user asks about a specific topic or question 
    that is not related to general machine learning.

    Input:
        query: str -> The user query to search for information

    Output:
        context: list[str] -> list of most relevant web search results
    """
    # check type of text
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    
    import requests
    import os
    from dotenv import load_dotenv

    load_dotenv()
    
    url = "https://api.firecrawl.dev/v1/search"
    
    payload = {
    "query": query,
    "limit": 10,
    "lang": "en",
    "country": "us",
    "timeout": 60000,
    "ignoreInvalidURLs": False,
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.text


if __name__ == "__main__":
    print("Starting MCP server at http://127.0.0.1:8080 on port 8080")
    mcp.run()

