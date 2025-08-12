# Documentation Writer Flow using CrewAI and Deepseek-R1

This project implements a documentation writing agentic workflow that can generate documentation for your code.

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
   ```bash
   pip install crewai crewai-tools ollama mcp
   ```

   Alternatively, you can also use uv to directly install the required dependencies.
   ```bash
    uv sync
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
        "doc-writer": {
            "url": "http://127.0.0.1:8000/sse"
        }
    }
}
```

You should now be able to see the MCP server listed in the MCP settings.

Next, start the server using
```bash
python server.py
```

In Cursor MCP settings make sure to toggle the button to connect the server to the host.

Done! Your server is now up and running. 

You can now chat with Cursor and generate the documentation for your code. Simply provide the GitHub URL to your project and watch the magic unfold.

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
