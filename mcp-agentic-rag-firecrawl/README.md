# MCP-powered Agentic RAG using Firecrawl and Qdrant

This project implements Agentic RAG using Firecrawl and Qdrant.
- [Firecrawl](https://www.firecrawl.dev/i/api) is used to scrape data from the web
- Qdrant as the local vector database.
- Cursor IDE as the MCP client.


---
## Setup and installations

**Get Firecrawl API Key**:
- Go to [Firecrawl](https://www.firecrawl.dev/i/api) and sign up for an account.
- You will find your API key there.
- Store it in the .env file.

```
FIRECRAWL_API_KEY="..."
```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install firecrawl-py mcp qdrant-client
   ```

---

## Run the project

First, start a Qdrant docker container as follows (make sure you have downloaded Docker):

   ```bash
   docker run -p 6333:6333 -p 6334:6334 \
   -v $(pwd)/qdrant_storage:/qdrant/storage:z \
   qdrant/qdrant
   ```

Next, go to the notebook.ipynb file, run the code to create a collection in your vector database.

Finally, set up your local MCP server as follows:
- Go to Cursor settings
- Select MCP 
- Add new global MCP server.

In the JSON file, add this:
```json
{
  "mcpServers": {
      "mcp-rag-app": {
          "command": "python",
          "args": ["/absolute/path/to/server.py"],
          "host": "127.0.0.1",
          "port": 8080,
          "timeout": 30000
      }
  }
}
```

Done! You can now interact with your vector database and fallback to web search if needed.

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
