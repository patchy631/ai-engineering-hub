# City Information Assistant

This project builds a hybrid RAG and SQL query application for US cities information. We use:

- LlamaCloud for storing and querying unstructured data (Wikipedia content)
- SQLite database for storing structured data (population, state, area)
- LlamaIndex for orchestrating the RAG and SQL tools
- Streamlit to build the UI

A demo is shown below:

![demo_screenshot](https://github.com/user-attachments/assets/ae348c81-8c32-480c-87ef-79c6fcc2d75c)


## Installation and setup

### Setup LlamaCloud:

Get an API key from LlamaCloud and set it in the `.env` file as follows:
```
LLAMACLOUD_API_KEY=<YOUR_API_KEY>
```

### Setup OpenAI:

Get an API key from OpenAI and set it in the `.env` file:
```
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

### Setup SQLite Database:

The SQLite database will be automatically initialized with sample US cities data. No additional setup required.

### Install Dependencies:

Ensure you have Python 3.8 or later installed.

```bash
pip install streamlit llama-index llama-cloud sqlalchemy python-dotenv nest-asyncio
```

### Run the app:

Run the app by running the following command:

```bash
streamlit run city_info_assistant/app/main.py
``` 
