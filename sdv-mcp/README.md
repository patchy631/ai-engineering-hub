# SDV MCP Server

We are going to implement an MCP server to orchestrate the Synthetic Data Vault (SDV) for completely local synthetic data generation. Agents will be able to connect to discover tools and then create, statistically evaluate, and visualize synthetic datasets based on our real-world tabular data.

We use:

- [SDV](https://docs.sdv.dev/sdv) for synthetic data generation of tabular data
- Cursor (MCP Host)

## Set Up

Run these commands in project root

### Install Dependencies

```bash
uv sync
```

### Use MCP Server

Run the MCP server with the created configuration file as `mcp.json` either globally or in the current project directory. Here's the code of configuring MCP globally to run the server:

```json
{
  "mcpServers": {
    "sdv_mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/akshay/Eigen/ai-engineering-hub/sdv-mcp",
        "run",
        "--with",
        "mcp",
        "server.py"
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
