# Crash Course: Building AI Agents with Open-Source Tools

This project is a hands-on crash course on building AI agents using a 100% open-source tech stack! You'll learn:

- What is an AI agent
- Connecting agents to tools
- Overview of MCP (Multi-Component Protocol)
- Replacing tools with MCP servers
- Setting up observability and tracing

All concepts are demonstrated with real, runnable code.

### Watch this tutorial on YouTube
<a href="https://youtu.be/R6sMAZaTCR4">
  <img src="assets/thumbnail.jpeg" alt="Watch this tutorial on YouTube" width="550"/>
</a>

## What is an AI Agent?

An AI agent uses an LLM as its brain, has memory to retain context, and can take real-world actions through tools (like browsing the web, running code, etc.).

In short: it thinks, remembers, and acts.

## Tech Stack

- [CrewAI](https://github.com/crewAIInc) — Build MCP-ready agents
- [Zep Graphiti](https://github.com/getzep/graphiti) — Add human-like memory
- [CometML Opik](https://github.com/comet-ml/opik) — Observability and tracing
- 100% open-source!

## System Overview

Here's how the system works:

1. User sends a query
2. Assistant runs a web search via MCP
3. Query + results go to the Memory Manager
4. Memory Manager stores context in Graphiti
5. Response agent crafts the final answer

---

### SetUp

- **Setup ollama:**

1. Install Ollama by following the official instructions for your OS:

   **For macOS:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

   **For Linux:**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

   **For Windows:**
   Download and install from [Ollama's official website](https://ollama.com/download)

2. Pull the required model:
   ```bash
   ollama pull llama3.2
   ```

You should see a response from the model. If you get any errors, check that Ollama is running with:


- **Add all necessary keys:**
  
  Create a new `.env` file in the project root, using `.env.example` as a template. Copy the example file and fill in your own API keys and secrets as needed.
  
  ```bash
  cp .env.example .env
  # Then edit .env to add your keys
  ```

- **Install dependencies:**
  
  Run the following command in the project root to install all required dependencies:
  
  ```bash
  uv sync
  ```

#### Start MCP servers:

- **Start Linkup server:**

  [Get your Linkup API keys here](https://www.linkup.so/)
  
  Run the following command in the project root:
  
  ```bash
  python server.py
  ```

- **Start the Graphiti MCP server:**
  
  This is only for advanced usage, you cna still learn all the fundamentals with just Linkup MCP server also.

  Follow the instructions in the [Graphiti MCP README](https://github.com/patchy631/ai-engineering-hub/blob/main/graphiti-mcp/README.md)


## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
