# Combining RAG and Text-to-SQL in a Single Query Interface

This project demonstrates how to combine Retrieval-Augmented Generation (RAG) and Text-to-SQL capabilities in a single query interface. The interface allows users to ask questions about US cities, and the system responds with relevant information.

Here we use:

* [Streamlit](https://streamlit.io/) for the web interface
* [LlamaIndex](https://llamaindex.ai/) for RAG and Text-to-SQL
* [LlamaCloud](https://llamacloud.ai/) for semantic search
* sqlalchemy for in-memory SQL database

A demo is available [here](./record_chatbot.mp4).

## Installation and Setup

### 1. Create virtual environment and activate it.

```
conda create -n city-info python=3.10.14
conda activate city-info
```

### 2. Install dependencies: 

```
pip install -r requirements.txt
```

### 3. Set up environment variables in a `.env` file:

Get an API key from [OpenAI](https://platform.openai.com/api-keys) and get information from [LlamaCloud](https://cloud.llamaindex.ai/) and add them to the `.env` file:

```
OPENAI_API_KEY=<your_openai_api_key>
CLOUD_INDEX_NAME=<your_llama_index_name>
CLOUD_PROJECT_NAME=<your_llama_project_name>
CLOUD_ORG_ID=<your_organization_id>
CLOUD_API_KEY=<your_llama_cloud_api_key>

```

## Run the app

Run the app by running the following command in the terminal:

```
streamlit run streamlit_app.py
```

Have a look at the tutorial on X: [X tutorial](https://x.com/PhuoclocDinh_kt/status/1900076527544566034) for more details.