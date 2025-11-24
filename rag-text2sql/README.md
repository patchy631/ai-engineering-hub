# RAG + Text-to-SQL Unified Query Interface

This application demonstrates how to combine Retrieval-Augmented Generation (RAG) and Text-to-SQL capabilities in a single query interface. Users can ask questions about US cities that can be answered either through SQL queries on structured data or through RAG on unstructured data.

## Features

- **Unified Query Interface**: Ask questions in natural language and get answers from the most appropriate data source
- **Intelligent Query Routing**: Automatically determines whether to use SQL, RAG, or both
- **Structured Data Access**: Queries a SQL database containing city population and state information
- **Unstructured Data Access**: Retrieves information from Wikipedia pages about US cities
- **Interactive UI**: User-friendly Streamlit interface with chat history and data exploration

## Architecture

The application uses a custom workflow that:

1. Analyzes the user's query
2. Determines which tool(s) to use (SQL, RAG, or both)
3. Executes the query using the selected tool(s)
4. Formats the results into a natural language response

## Setup and Installation

### Prerequisites

- Python 3.9+
- OpenAI API key with added credit balance
- LlamaCloud API key and account with Index

### Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit application:

```bash
streamlit run app.py
```

4. Enter your API keys in the sidebar

## Example Queries

- "Which city has the highest population?"
- "Where is the Space Needle located?"
- "List all of the places to visit in Miami."
- "How do people in Chicago get around?"
- "What is the historical name of Los Angeles?"

## Implementation Details

The application uses:

- **LlamaIndex**: For both RAG and Text-to-SQL capabilities
- **OpenAI**: As the LLM for query understanding and response generation
- **SQLite**: For storing structured city data
- **Streamlit**: For the web interface

## Limitations

- The demo uses a small dataset of only six US cities
- In a production environment, you would need to implement proper security measures for SQL queries
- The application requires API keys for OpenAI and LlamaCloud
- There is simple_app.py which mocks RAG & SQL capabilities

## Credits

This application is based on the LlamaIndex example notebook: [Combining RAG and Text-to-SQL in a Single Query Interface](https://github.com/run-llama/llamacloud-demo/blob/main/examples/advanced_rag/llamacloud_sql_router.ipynb)
