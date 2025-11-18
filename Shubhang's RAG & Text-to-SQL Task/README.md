# RAG Text-to-SQL with LlamaIndex and Streamlit

This project builds a powerful RAG (Retrieval-Augmented Generation) application that combines SQL database querying with semantic search capabilities. The app allows users to ask questions about cities in natural language, and the system automatically routes the query to either a SQL database or a semantic search engine based on the question type.

We use:

- **LlamaIndex** for orchestrating the RAG system and query routing
- **SQLite** for storing structured city data
- **LlamaCloud** for semantic search capabilities
- **Streamlit** to build the interactive UI

A demo of the application is shown below: 

https://app.visla.us/clip/1347259516399513601

## Features

- **Natural Language to SQL Translation**: Ask questions about city statistics in plain English
- **Semantic Search**: Get answers about general knowledge questions related to US cities
- **Automatic Query Routing**: The system intelligently selects the appropriate tool based on your question
- **Interactive Chat Interface**: Engage with the system through a chat-like interface
- **Conversation History**: Review previous interactions with newest conversations at the top


## Installation and Setup

### Prerequisites

- Python 3.9 or later
- Virtual environment (recommended)


### API Keys Setup

1. Create a `config.py` file in the project root with the following API keys:
```python
# API Keys and Configuration
OPENAI_API_KEY = "your-openai-api-key"
PHOENIX_API_KEY = "your-phoenix-api-key"
LLAMA_CLOUD_API_KEY = "your-llama-cloud-api-key"
LLAMA_ORGANIZATION_ID = "your-llama-organization-id"
LLAMA_NAME = "your-llama-index-name"
```

You'll need to obtain:

- An OpenAI API key from [OpenAI](https://platform.openai.com/)
- A Phoenix API key for logging/observability (optional)
- A LlamaCloud API key and organization ID from [LlamaIndex](https://cloud.llamaindex.ai/)


### Install Dependencies

Create and activate a virtual environment, then install the required packages:

```bash
# Create and activate virtual environment
python -m venv myenv
source myenv/bin/activate  # On Windows: myenv\Scripts\activate

# Install dependencies
pip install streamlit llama-index-core llama-index-llms-openai llama-index-indices-managed-llama-cloud sqlalchemy nest-asyncio openai pandas
```

Alternatively, you can use the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```


## Running the App

Run the Streamlit app with:

```bash
python -m streamlit run streamlit_chatbot.py
```

The app will be available at `http://localhost:8501` in your web browser.

## How It Works

The application uses a hybrid approach to answer questions:

1. **SQL Database**: Contains structured data about city populations and states
2. **Semantic Search**: Provides general knowledge about US cities

When a user asks a question:

1. The query is analyzed to determine if it's about city statistics or general knowledge
2. For statistics questions, the app translates the natural language to SQL and queries the database
3. For general knowledge questions, the app uses LlamaCloud's semantic search capabilities
4. The appropriate response is displayed to the user in the chat interface

## Code Structure

- `streamlit_app.py`: Main Streamlit application
- `config.py`: Configuration file with API keys
- `city_stats.db`: SQLite database with city information (created on first run)


## Example Questions

Try asking questions like:

- Which city has the highest population?
- What state is Houston located in?
- Where is the Space Needle located?
- List places to visit in Miami.
- How do people in Chicago get around?
- What is the historical name of Los Angeles?


## Customization

You can extend the application by:

- Adding more cities to the database
- Expanding the database schema with additional information
- Implementing more sophisticated query routing logic
- Adding visualization capabilities for city data


## Troubleshooting

If you encounter issues:

1. Ensure all API keys are correctly set in `config.py`
2. Verify that your virtual environment is activated
3. Check that all dependencies are installed
4. Make sure you're running the app with `python -m streamlit run app.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) for the RAG framework
- [Streamlit](https://streamlit.io/) for the web interface
- [OpenAI](https://openai.com/) for the language model

