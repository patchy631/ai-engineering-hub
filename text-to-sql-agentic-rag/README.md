# Agent Workflow with LlamaIndex for both RAG and Text-to-SQL

This project uses LlamaIndex to create a custom workflow that can perform RAG using LlamaCloud index or query an SQL engine in a single query interface. The workflow will answer questions about US cities using data from Wikipedia and an SQL database.

LlamaCloudIndex is used for cloud-based indexing and retrieval. In this project, we will use it to index the Wikipedia pages of various cities. To begin, we will first download the Wikipedia pages in PDF format and then upload them to the index.

To create a LlamaCloudIndex click here: https://cloud.llamaindex.ai/

To access the LlamaCloudIndex data from the application an API key is required, so make sure to create a LlamaCloud API key too.

**Get API Keys**:

- [LlamaCloud](https://cloud.llamaindex.ai/)

### Watch Demo on YouTube

[Application Demo](https://youtu.be/SiBvkEZ2y4Y)

## Installation and setup

**Get API Keys**:

- [LlamaCloud](https://cloud.llamaindex.ai/)

**Install Dependencies**:
Ensure you have Python 3.11 or later installed.

```bash
pip install streamlit nest-asyncio SQLAlchemy llama-index
```

**Running the app**:

Use command
`python -m streamlit run app.py`
