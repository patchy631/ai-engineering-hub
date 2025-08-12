from dotenv import load_dotenv
from linkup import LinkupClient
from mcp.server.fastmcp import FastMCP

load_dotenv()

mcp = FastMCP('linkup-server', port=8080)
client = LinkupClient()

@mcp.tool()
def web_search(query: str = "") -> str:
    """Search the web for the given query."""
    search_response = client.search(
        query=query,
        depth="standard",  # "standard" or "deep"
        output_type="sourcedAnswer",  # "searchResults" or "sourcedAnswer" or "structured"
        structured_output_schema=None,  # must be filled if output_type is "structured"
    )
    return str(search_response)

if __name__ == "__main__":
   mcp.run(transport="sse")