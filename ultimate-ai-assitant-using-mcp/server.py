import asyncio
import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
import mcp_use
import warnings

warnings.filterwarnings("ignore")
mcp_use.set_debug(0)

async def main():
    # Load environment variables
    load_dotenv()

    # Create configuration dictionary
    config = {
      "mcpServers": {
          "stagehand": {
            "command": "node",
            "args": ["/path/to/mcp-server-browserbase/stagehand/dist/index.js"],
            "env": {
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "LOCAL_CDP_URL": "http://localhost:9222",
                "DOWNLOADS_DIR": "/path/to/downloads/stagehand"
            }
        },
        "mcp-server-firecrawl": {
            "command": "npx",
            "args": ["-y", "firecrawl-mcp"],
            "env": {
              "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY")
            }
          },
          "graphiti": {
            "transport": "stdio",
            "command": "/Users/your-username/.local/bin/uv",
            "args": [
              "run",
              "--isolated",
              "--directory",
              "/path/to/graphiti/mcp_server",
              "--project",
              ".",
              "graphiti_mcp_server.py",
              "--transport",
              "stdio"
            ],
            "env": {
              "NEO4J_URI": "bolt://localhost:7687",
              "NEO4J_USER": "neo4j",
              "NEO4J_PASSWORD": "demodemo",
              "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
              "MODEL_NAME": "gpt-4o-mini"
            }
          },

          "ragie": {
            "command": "npx",
            "args": [
              "-y",
              "@ragieai/mcp-server",
              "--partition",
              "default"
            ],
            "env": {
              "RAGIE_API_KEY": os.getenv("RAGIE_API_KEY")
            }
        },
        "mcp-git-ingest": {
            "command": "/path/to/.local/bin/uvx",
            "args": ["--from", "git+https://github.com/adhikasp/mcp-git-ingest", "mcp-git-ingest"]
          },
        "desktop-commander": {
          "command": "npx",
          "args": [
            "-y",
            "@wonderwhy-er/desktop-commander"
          ]
        }
      }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM
    # llm = ChatOllama(model="qwen3:1.7b")
    llm = ChatOpenAI(model="gpt-4o")
    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=100)

    
    prompt = "What tools do you have from MCP?"

    # Run the query
    result = await agent.run(prompt)

    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())