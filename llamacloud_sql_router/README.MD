# Advanced RAG: Combining RAG and Text-to-SQL

This project builds an advanced RAG application which combines RAG and Text-to-SQL. 

+ LlamaCloud index for RAG-based retrieval
+ SQL query engine as a Tool
+ Streamlit to build the UI.

Quick Demo: [Video](demo.mp4)

## Installation and setup 
**installation**: 
```
pip install -r requirements.txt
```

**Set the API keys**
Get the API Keys from OpenAI and LlamaCloud and keep them in the `.env` file
```
OPENAI_API_KEY= "YOUR OPENAI API KEY"

LLAMA_INDEX_API_KEY= "<YOUR_LLAMA_INDEX_KEY>"
LLAMA_INDEX_ORGANIZATION_ID="YOUR_ORGANIZATION_ID"
LLAMA_INDEX_PROJECT_NAME="YOUR_PROJECT_NAME"
LLAMA_INDEX_NAME="YOUR_INDEX_NAME"
```
Steps to get `LLAMA_INDEX` details: 
If you haven't done, create your LlamaCloud account here: https://cloud.llamaindex.ai/ and Create the index and load the below PDF files. 
- [New York City](https://en.wikipedia.org/wiki/New_York_City)
- [Los Angeles](https://en.wikipedia.org/wiki/Los_Angeles)
- [Chicago](https://en.wikipedia.org/wiki/Chicago)
- [Houston](https://en.wikipedia.org/wiki/Houston)
- [Miami](https://en.wikipedia.org/wiki/Miami)
- [Seattle](https://en.wikipedia.org/wiki/Seattle)

Keep the project name and index name handy, which will be used in the app.

## Run the App
```
streamlit run app.py
```
