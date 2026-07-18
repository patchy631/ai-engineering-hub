# Combining RAG and Text-to-SQL in a Single Query Interface

## Introduction
This project integrates Retrieval-Augmented Generation (RAG) with Text-to-SQL capabilities into a single query interface using Streamlit, LlamaIndex, SQL database, and LLM(ChatGPT). It enables users to upload documents, index them, and perform queries to retrieve structured and unstructured information.

## Requirements
Ensure you have the following installed before running the code:
- Python 3.8+
- pip

### Required Python Packages
You can install the dependencies by running:
```sh
pip install -r requirements.txt
```

The `requirements.txt` should include:
```txt
streamlit
python-dotenv
llama-index
llama-index-core
llama-index-llms-openai
sqlalchemy
httpx
pandas
```

## Setting Up Environment Variables
Create a `.env` file in the project root and add the following API keys:
```env
OPENAI_API_KEY=your_openai_api_key
LLAMA_INDEX_API_KEY=your_llama_index_api_key
```

## Running the App
To run the app, use the following command:

```sh
streamlit run app.py
```

## Usage Instructions
1. **Upload Documents:** Navigate to the upload section and add your PDF files.
2. **File Tracking:** The system detects and prevents duplicate file uploads.
3. **Query Execution:** Use the text box to input natural language questions.
4. **Results Display:** Queries will be processed and displayed using SQL database and LlamaCloud.

## Error Handling
- If a file fails to upload, check API keys and try again.
- If a query times out, increase the timeout setting in `request_timeout`.


