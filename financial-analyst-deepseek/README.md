# MCP-powered Financial Analyst using CrewAI and Deepseek-R1

This project implements a financial analysis agentic workflow that analyzes stock market data and provides insights.

We use:
- CrewAI for multi-agent orchestration.
- Ollama for serving Deepseek-R1 locally.
- Cursor IDE as the MCP host.

---
## Setup and installations

**Install Ollama**

```bash
# Setting up Ollama on linux
curl -fsSL https://ollama.com/install.sh | sh

# Pull the Deepseek-R1 model
ollama pull deepseek-r1
```

**Install Dependencies**

   Ensure you have Python 3.12 or later installed.

   You can use uv to directly install the required dependencies (recommended).
   ```bash
    uv sync
   ```

   Or you can also use pip to install the following dependencies to your local environment.
   ```bash
   pip install crewai crewai-tools ollama mcp pydantic yfinance pandas matplotlib
   ```

---

## Run the project

First, set up your MCP server as follows:
- Go to Cursor settings
- Select MCP 
- Add new global MCP server.

In the JSON file, add this:
```json
{
    "mcpServers": {
        "financial-analyst": {
         "command": "uv",
            "args": [
                "--directory",
                "absolute/path/to/project_root",
                "run",
                "server.py"
            ]
        }
    }
}
```

You should now be able to see the MCP server listed in the MCP settings.

In Cursor MCP settings make sure to toggle the button to connect the server to the host. Done! Your server is now up and running. 

You can now chat with Cursor and analyze stock market data. Simply provide the stock symbol and timeframe you want to analyze, and watch the magic unfold.

**Example queries**:
- "Show me Tesla's stock performance over the last 3 months"
- "Compare Apple and Microsoft stocks for the past year"
- "Analyze the trading volume of Amazon stock for the last month"

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
