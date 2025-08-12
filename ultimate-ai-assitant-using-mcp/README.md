# MCP-powered Ultimate AI Assistant

A Streamlit application that provides a chat interface for interacting with MCP (Model Context Protocol) servers. This app allows you to configure multiple MCP servers and chat with them using natural language.

Tech stack:
- [mcp-use](https://github.com/mcp-use/mcp-use) to connect LLM to MCP servers
- [Stagehand MCP](https://github.com/browserbase/mcp-server-browserbase) for browser access
- [Firecrawl MCP](https://github.com/mendableai/firecrawl-mcp-server) for scraping
- [Ragie MCP](https://github.com/ragieai/ragie-mcp-server) for multimodal RAG
- [Graphiti MCP](https://github.com/getzep/graphiti/tree/main/mcp_server) as memory
- [Terminal](https://github.com/wonderwhy-er/DesktopCommanderMCP) & [GitIngest](https://github.com/adhikasp/mcp-git-ingest) MCP

## Setup

1. **Install Dependencies**: 
   ```bash
   uv sync 
   ```

2. **Environment Variables**:
   Create a `.env` file with your API keys:
   ```env
   OPENAI_API_KEY=your-openai-api-key
   FIRECRAWL_API_KEY=your-firecrawl-api-key
   RAGIE_API_KEY=your-ragie-api-key
   ```

3. **Setup MCP Servers**

    Go to server.py and update the paths to the MCP servers according to your system.

3. **Run the App**:
   ```bash
   streamlit run mcp_streamlit_app.py
   ```

## Usage

1. **Configure MCP Servers**:
   - Use the sidebar to enter your MCP server configuration in JSON format
   - Click "Load Example Config" to see a sample configuration
   - Click "Activate Configuration" to initialize the MCP client

2. **Chat with MCP Tools**:
   - Once configured, use the chat interface to interact with your MCP servers
   - Ask questions about available tools or request specific actions
   - The agent will use the appropriate MCP tools to respond

## Example Configuration

```json
{
  "mcpServers": {
    "stagehand": {
      "command": "node",
      "args": ["/path/to/stagehand/dist/index.js"],
      "env": {
        "OPENAI_API_KEY": "your-api-key",
        "LOCAL_CDP_URL": "http://localhost:9222"
      }
    },
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "your-firecrawl-key"
      }
    }
  }
}
```

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. 
