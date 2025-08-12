# Graphiti MCP Demo

We are implementing an MCP server and AI agent integration to leverage Zep's Graphiti for persistent memory and context continuity across Cursor and Claude. This will allow AI agents hosted on Cursor and Claude to connect to the MCP for dynamic tool discovery, select the optimal tool for a given query, and formulate responses informed by past interactions, all while Graphiti ensures consistent context across both client platforms.

We use:

- Graphiti by [Zep AI](https://www.getzep.com/) as a memory layer for an AI agent
- Cursor and Claude (as MCP Hosts)

## Set Up

Follow these steps to set up the project before running the MCP server.

### Clone GitHub Repository

```bash
git clone https://github.com/getzep/graphiti.git
cd graphiti/mcp_server
```

### Install Dependencies

```bash
uv sync
```

### Configuration

Before running the MCP server, you need to configure the environment variables. Here's a look at the `.env` file you need to create in the `graphiti/mcp_server` directory:

```dotenv
# Neo4j Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=demodemo

# OpenAI API Configuration
OPENAI_API_KEY=<your_openai_api_key>
MODEL_NAME=gpt-4.1-mini
```

## Use MCP Server

Graphiti MCP server can be run using Docker or directly with Python. Docker is recommended for use, while direct Python execution is useful for troubleshooting.

### Run MCP Server

Docker deployment will start both the Neo4j database and the Graphiti MCP server.

Start the services using Docker Compose:

```bash
docker compose up
```

**Note**: When running the Docker Compose for both the Neo4j database and the Graphiti MCP server, if you encounter the `No server info found` error in the MCP logs, try running the server directly using Python to troubleshoot the issue.

```bash
uv run graphiti_mcp_server.py --model gpt-4.1-mini --transport sse
```

### Integrate MCP Clients

- **Cursor**: Here's the configuration of the `mcp.json` file to integrate the MCP server with Cursor:

```json
{
  "mcpServers": {
    "Graphiti": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

- **Claude**: Here's the configuration of `claude_desktop_config.json` file to integrate the MCP server with Claude:

```json
{
  "mcpServers": {
    "graphiti": {
      "transport": "stdio",
      "command": "/Users/avichawla/.local/bin/uv",
      "args": [
        "run",
        "--isolated",
        "--directory",
        "/Users/avichawla/Desktop/posts/graphiti/mcp_server",
        "--project",
        ".",
        "graphiti_mcp_server.py",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
