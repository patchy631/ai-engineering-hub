# SQL-RAG LlamaIndex Agent

## Overview
This LlamaIndex-based application is an AI-powered query agent that retrieves data from both a database and a file-based system using LlamaIndex and OpenAI's GPT models. It utilizes an agent router to determine the appropriate source for answering user queries.

## Features
- **Hybrid Querying**: Supports querying structured SQL databases and unstructured text-based data.
- **Agent Router**: Determines whether to query the database or use a semantic search engine.
- **LlamaIndex Integration**: Uses LlamaCloudIndex for text-based queries.
- **OpenAI-powered LLM**: Uses GPT models for query interpretation and decision-making.
- **Arize Phoenix Logging**: Enables trace logging for query execution.
- **Streamlit UI**: Provides an interactive web interface for users to enter queries and view responses.

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Llama Cloud API Key
- Phoenix API Key

### Steps
```sh
# Clone the repository
git clone <repo-url>
cd sql-rag-streamlit

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
export OPENAI_API_KEY="your_openai_api_key"
export LLAMA_CLOUD_API_KEY="your_llama_cloud_api_key"
export PHOENIX_API_KEY="your_phoenix_api_key"
export ORGANIZATION_ID="your_organization_id"

# Run the application
streamlit run sql_rag.py
```

## Components

### 1. **Database Setup**
- Uses an in-memory SQLite database with a `city_stats` table containing city population and state information.
- Populates the table with sample data.
- Uses SQLAlchemy to manage the database connection.

### 2. **Query Engines**
- **SQL Query Engine**: Executes SQL queries against the `city_stats` table.
- **LlamaCloud Query Engine**: Handles semantic queries on text data.
- These tools are managed by `QueryEngineTool` instances.

### 3. **Agent Router Workflow**
- The `RouterOutputAgentWorkflow` (from `tool_workflow.py`) decides which query engine to use.
- It interacts with OpenAI's GPT model to analyze queries and select the appropriate tool.
- Implements multiple workflow steps such as preparing chat input, selecting tools, and dispatching calls.

### 4. **Streamlit UI**
- A simple interface where users enter queries.
- Displays the response after executing the query via the selected engine.

## Usage
1. Open the Streamlit UI.
2. Enter a query, e.g., "What is the population of New York City?"
3. The agent determines whether to query the SQL database or use the LlamaCloudIndex.
4. The response is displayed in the UI.

## Dependencies
The project relies on the following Python packages:
- `llama_index`
- `arize-phoenix`
- `nest-asyncio`
- `sqlalchemy`
- `streamlit`
- `llama-index-callbacks-arize-phoenix`

## Typefully

https://typefully.com/t/Vkxs861

## Contributing
Contributions are welcome! Feel free to fork the repo and submit a pull request.

## License
This project is licensed under the MIT License.

