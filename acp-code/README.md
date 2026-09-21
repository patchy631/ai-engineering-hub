# Summary Generator multi-agent workflow with ACP

A simple demonstration of the Agent Communication Protocol (ACP), showcasing how two agents built using different frameworks (CrewAI and Smolagents) can collaborate seamlessly to generate and verify a research summary.

---

## Setup and Installation

1. **Install Ollama:**
   ```bash
   # Setting up Ollama on linux
   curl -fsSL https://ollama.com/install.sh | sh

   # Pull the Qwen2.5 model
   ollama pull qwen2.5:14b
   ```

2. **Install project dependencies:**

    Ensure you have Python 3.10 or later installed on your system.

    First, install `uv` and set up the environment:
    ```bash
    # MacOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

    Install dependencies:
    ```bash
    # Create a new directory for our project
    uv init acp-project
    cd acp-project

    # Create virtual environment and activate it
    uv venv
    source .venv/bin/activate  # MacOS/Linux

    .venv\Scripts\activate     # Windows

    # Install dependencies
    uv add acp-sdk crewai smolagents duckduckgo-search ollama
    ```

You can also use any other LLM providers such as OpenAI or Anthropic. Create a `.env` file and add your API keys
```
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

## Usage
Start the two ACP servers in separate terminals:

```bash
# Terminal 1
uv run crew_acp_server.py

# Terminal 2
uv run smolagents_acp_server.py
```

Run the ACP client to trigger the agent workflow:

```bash
uv run acp_client.py
```

Output:

A general summary from the first agent

A fact-checked and updated version from the second agent


## ACP-Code Repository Explanation

This repository demonstrates the Agent Communication Protocol (ACP) - a standardized way for AI agents built with different frameworks to communicate and collaborate. Here's a breakdown:
Overview
The project shows how two agents using different frameworks (CrewAI and Smolagents) work together to:
Generate a research summary on a topic
Fact-check and enhance it using web search

## Core Components
1. CrewAI ACP Server (crew_acp_server.py)

@server.agent()
async def research_drafter(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
Purpose: Creates initial research summaries Key elements:
Uses Ollama's Qwen2.5:14b model (line 8-12)
Defines a CrewAI Agent with role "Research summarizer" (lines 18-23)
Creates a Task to write a brief summary (lines 25-29)
Executes the crew and returns the result as an ACP Message (lines 31-33)
Runs on port 8000 (line 36)
How it works: Takes a topic as input, uses CrewAI's agent to generate a summary, and yields it back through ACP protocol.
2. Smolagents ACP Server (smolagents_acp_server.py)

@server.agent()
async def research_verifier(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
Purpose: Fact-checks and enhances summaries using web search Key elements:
Uses the same Ollama model via LiteLLM (lines 11-16)
Creates a CodeAgent with DuckDuckGo search tool (line 22)
Takes the draft summary and searches for updated information (lines 24-25)
Returns enhanced version (line 27)
Runs on port 8001 (line 30)
How it works: Receives a draft summary, uses DuckDuckGo to find current information, and returns a fact-checked, enhanced version.
3. ACP Client (acp_client.py)

async def run_workflow() -> None:
Purpose: Orchestrates the multi-agent workflow Workflow:
Connects to both servers (lines 5-6)
drafter client → CrewAI server (port 8000)
verifier client → Smolagents server (port 8001)
Step 1 - Generate draft (lines 9-14):
Sends topic to research_drafter agent
Receives and prints draft summary
Step 2 - Enhance draft (lines 16-21):
Sends draft to research_verifier agent
Agent searches web for latest info
Receives and prints final enhanced summary

## Architecture Diagram

┌─────────────┐
│   Client    │
│ (acp_client)│
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
┌──────────────┐  ┌──────────────┐
│ CrewAI Agent │  │Smolagent Agent│
│   (Port 8000)│  │   (Port 8001) │
│              │  │               │
│ Research     │  │ Research      │
│ Drafter      │  │ Verifier      │
│              │  │ + DuckDuckGo  │
└──────┬───────┘  └──────┬────────┘
       │                 │
       └────────┬────────┘
                ▼
       Ollama (Qwen2.5:14b)

## Key Concepts

ACP SDK: Provides standardized communication (Messages, MessageParts) between agents regardless of framework
Framework Agnostic: CrewAI and Smolagents can collaborate seamlessly
Async Architecture: Uses Python async/await for efficient I/O operations
Tool Integration: Smolagents agent has access to DuckDuckGo for real-time information


## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements. 
