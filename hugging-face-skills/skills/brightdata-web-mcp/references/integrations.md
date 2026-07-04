# Bright Data MCP Integrations

Complete integration guides for AI tools and frameworks.

## Supported Clients

| Client | Method | Best For |
|--------|--------|----------|
| Claude Desktop | Local MCP | Desktop AI assistant |
| Claude Code | Local MCP | Coding assistant |
| Codex | Remote MCP | OpenAI coding agent |
| Cursor | Local MCP | IDE integration |
| VS Code | Local MCP | IDE integration |
| ChatGPT | Remote MCP | Chat interface |
| LangChain | SDK | Python agents |
| LlamaIndex | SDK | RAG pipelines |
| CrewAI | SDK | Multi-agent systems |
| Google ADK | SDK | Gemini agents |
| OpenAI SDK | SDK | Custom agents |
| n8n | Remote MCP | Workflow automation |

---

## Claude Desktop

Add to `claude_desktop_config.json`:

**Location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## Claude Code

Same configuration as Claude Desktop:

```json
{
  "mcpServers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## Codex (OpenAI)

Add to `.codex/config.toml` in your project root:

```toml
[mcp_servers.brightdata]
command = "npx"
args = ["mcp-remote", "https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN"]
```

### With Pro Mode (All Tools)

```toml
[mcp_servers.brightdata]
command = "npx"
args = ["mcp-remote", "https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN&pro=1"]
```

### With Tool Groups

```toml
[mcp_servers.brightdata]
command = "npx"
args = ["mcp-remote", "https://mcp.brightdata.com/mcp?token=YOUR_API_TOKEN&groups=ecommerce,social"]
```

> **Note:** Codex uses `mcp-remote` to connect to remote MCP servers via the Streamable HTTP endpoint (`/mcp`).

---

## Cursor

Settings → Gear Icon → Tools & Integrations → Add Custom MCP:

```json
{
  "mcpServers": {
    "brightdata-mcp": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## VS Code

Add to workspace or user settings:

```json
{
  "mcp.servers": {
    "brightdata": {
      "command": "npx",
      "args": ["-y", "@brightdata/mcp"],
      "env": {
        "API_TOKEN": "<your-token>"
      }
    }
  }
}
```

---

## ChatGPT

Use remote MCP URL in ChatGPT's MCP settings:

```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN
```

Or with Pro mode:
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&pro=1
```

---

## LangChain

### Installation

```bash
pip install langchain-mcp-adapters langchain-openai langgraph python-dotenv
```

### Basic Setup

```python
import asyncio
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os

load_dotenv()

async def main():
    # Configure MCP client
    client = MultiServerMCPClient({
        "bright_data": {
            "url": "https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN",
            "transport": "sse",
        }
    })

    # Get available tools
    tools = await client.get_tools()
    print("Available tools:", [tool.name for tool in tools])

    # Configure LLM
    llm = ChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-4o"
    )

    # System prompt for web search agent
    system_prompt = """
    You are a web search agent with comprehensive scraping capabilities. Your tools include:
    - **search_engine**: Get search results from Google/Bing/Yandex
    - **scrape_as_markdown**: Extract content from any webpage with bot detection bypass
    - **Structured extractors**: Fast, reliable data from major platforms
    - **Browser automation**: Navigate, click, type, screenshot for complex interactions

    Guidelines:
    - Use structured web_data_* tools for supported platforms when possible
    - Use general scraping for other sites
    - Handle errors gracefully and respect rate limits
    """

    # Create ReAct agent
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt
    )

    # Test the agent
    result = await agent.ainvoke({
        "messages": [("human", "Search for the latest news about AI developments")]
    })

    print("\nAgent Response:")
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
```

### Environment Variables

Create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## LlamaIndex

### Installation

```bash
pip install llama-index llama-index-tools-mcp
```

### Basic Setup

```python
from llama_index.tools.mcp import MCPToolSpec

tool_spec = MCPToolSpec(
    server_url="https://mcp.brightdata.com/sse",
    api_key="YOUR_API_TOKEN"
)

# Get tools for use with LlamaIndex agents
tools = tool_spec.to_tool_list()
```

---

## CrewAI

### Installation

```bash
pip install crewai crewai-tools
```

### Basic Setup

```python
from crewai import Agent, Task, Crew
from crewai_tools import MCPServerAdapter
import os

server_params = {
    "url": "https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN",
    "transport": "sse"
}

try:
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"Available tools: {[tool.name for tool in mcp_tools]}")
        
        my_agent = Agent(
            role="Web Scraping Specialist",
            goal="Extract data from websites using Bright Data tools",
            backstory="I am an expert at web scraping and data extraction using MCP tools.",
            tools=mcp_tools,
            verbose=True,
            llm="gpt-4o-mini",
        )
        
        task = Task(
            description="Search for flights from New York to San Francisco and provide a summary.",
            expected_output="A clear summary of available flights with key details.",
            agent=my_agent
        )
        
        crew = Crew(
            agents=[my_agent],
            tasks=[task],
            verbose=True
        )
        
        result = crew.kickoff()
        print("\n=== RESULT ===")
        print(result)
        
except Exception as e:
    print(f"Error connecting to MCP server: {e}")
```

---

## Google ADK

### Installation

```bash
pip install google-adk
```

### Remote MCP Setup

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="brightdata_agent",
    instruction="Help users access web data using Bright Data",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url=f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_API_TOKEN}",
            ),
        )
    ],
)
```

### Local MCP Setup

```python
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters

BRIGHTDATA_API_TOKEN = "YOUR_BRIGHTDATA_API_TOKEN"

root_agent = Agent(
    model="gemini-2.5-pro",
    name="brightdata_agent",
    instruction="Help users access web data using Bright Data",
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@brightdata/mcp"],
                    env={
                        "API_TOKEN": BRIGHTDATA_API_TOKEN,
                        "PRO_MODE": "true",
                    }
                ),
                timeout=300,
            ),
        )
    ],
)
```

---

## OpenAI SDK

```python
from openai import OpenAI
from mcp import MCPClient

client = OpenAI()
mcp = MCPClient("https://mcp.brightdata.com/sse", api_key="YOUR_API_TOKEN")

# Get tools and use with OpenAI function calling
tools = mcp.list_tools()

# Convert to OpenAI function format
functions = [
    {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.inputSchema
    }
    for tool in tools
]

# Use with chat completions
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Search for AI news"}],
    functions=functions,
    function_call="auto"
)
```

---

## n8n

1. Add MCP node to workflow
2. Set server URL: `https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN`
3. Configure authentication with API token
4. Select tools to use in workflow

For Pro mode:
```
https://mcp.brightdata.com/sse?token=YOUR_API_TOKEN&pro=1
```

---

## Remote vs Local

| Aspect | Remote | Local |
|--------|--------|-------|
| Setup | URL only | `npx @brightdata/mcp` |
| Updates | Automatic | Manual |
| Latency | Slightly higher | Lower |
| Offline | No | Yes (after install) |
| Configuration | URL parameters | Environment variables |

**Recommendation:** 
- Use **Remote** for simplicity and automatic updates
- Use **Local** for lower latency, offline needs, or custom zone configuration

---

## Enable Browser Automation

To use browser control tools:

1. Visit [brightdata.com/cp/zones](https://brightdata.com/cp/zones)
2. Create a new 'Browser API' zone
3. Copy the zone name
4. Configure:
   - Remote: `&browser=your_zone_name`
   - Local: `BROWSER_ZONE=your_zone_name`

---

## Monitor Usage

- View API usage at [My Zones](https://brightdata.com/cp/zones)
- Use `session_stats` tool to check current session usage
- Free tier: 5,000 requests/month
