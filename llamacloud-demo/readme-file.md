# Hybrid RAG + Text-to-SQL Query Interface

A powerful natural language interface that intelligently routes user questions to either search documents or query databases. This unified query system removes the need for users to know whether their question requires structured or unstructured data access.

## Overview

This project demonstrates how to build an intelligent query routing system that can:

1. Determine whether a natural language query requires structured data (SQL) or unstructured data (RAG)
2. Route the query to the appropriate processing pipeline
3. Return formatted results from either path in a consistent manner

The system uses LlamaIndex for orchestration, vector stores for RAG functionality, and LLMs for both routing decisions and answer generation.

## Features

- **Intelligent Query Routing**: Automatically determines if a question requires SQL or document search
- **Text-to-SQL Processing**: Translates natural language to SQL for database queries
- **RAG Pipeline**: Retrieves relevant context from documents to answer knowledge-based questions
- **Unified Interface**: Users can ask any question through a single conversational interface
- **Workflow-based Architecture**: Uses LlamaIndex's workflow system for flexible, maintainable design

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/hybrid-query-interface.git
cd hybrid-query-interface

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Environment Setup

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
```

### Running the Application

```bash
# Run the Streamlit application
streamlit run app.py
```

## How It Works

The system uses a workflow-based approach with these key components:

1. **Query Router**: Analyzes user questions to determine the appropriate processing path
2. **Text-to-SQL Pipeline**: For structured data queries requiring database access
3. **RAG Pipeline**: For knowledge-based queries requiring document retrieval
4. **Response Generator**: Formats answers consistently regardless of the source

## Example Queries

**SQL Path Examples:**
- "How many sales were made in Q1?"
- "What's the average transaction value for premium customers?"
- "List the top 5 products by revenue last month"

**RAG Path Examples:**
- "What's our refund policy?"
- "How do I reset my account password?"
- "Explain the company's work-from-home guidelines"

## Development

This project is based on the [LlamaCloud SQL Router example](https://github.com/run-llama/llamacloud-demo/blob/main/examples/advanced_rag/llamacloud_sql_router.ipynb).

To extend or modify:
1. Fork the repository
2. Make your changes
3. Submit a pull request

## Requirements

- Python 3.9+
- LlamaIndex
- OpenAI API key
- Streamlit

## License

MIT

## Acknowledgements

- [LlamaIndex](https://www.llamaindex.ai/) for the core toolkit
- [OpenAI](https://openai.com/) for LLM capabilities
