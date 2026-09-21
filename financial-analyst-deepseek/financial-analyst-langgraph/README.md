# MCP-powered Financial Analyst using Langgraph and Azure openai GPT4o

This project implements a financial analysis agentic workflow that analyzes stock market data and provides insights.

We use:
- Langgraph for multi-agent orchestration.
- Azure open ai model
- Cursor IDE as the MCP host.

---
## Setup and installations

**Clone the repository and navigate into the project directory:**

**Fill Your Environment Variables**

A `.env` file is already included in the project.  
Open the file and fill in your actual API keys:

```env
.env 

```
**Install Dependencies**

   Ensure you have Python 3.12 or later installed.
```
   pip install -r requirements.txt
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



