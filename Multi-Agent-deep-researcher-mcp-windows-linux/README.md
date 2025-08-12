# Agentic Deep Researcher

We're building an MCP-powered multi-agent deep researcher, it can perform deep web searches using [Linkup](https://www.linkup.so/) amd the agents are orchestrated using CrewAI.

We use:

- [LinkUp](https://www.linkup.so/) (Search Tool)
- CrewAI (Agentic design)
- Deepseek R1 (LLM)
- Streamlit to wrap the logic in an interactive UI

### SetUp

Run these commands in project root

```
uv sync
```


### Run the Application

Run the application with:

```bash
streamlit run app.py
```

### Use as MCP server

```json
{
  "mcpServers": {
    "crew_research": {
      "command": "uv",
      "args": [
        "--directory",
        "./Multi-Agent-deep-researcher-mcp-windows-linux",
        "run",
        "server.py"
      ],
      "env": {
        "LINKUP_API_KEY": "your_linkup_api_key_here"
      }
    }
  }
}
```
[Get your Linkup API keys here](https://www.linkup.so/)

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
