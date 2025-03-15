# RAG and Text-to-SQL

Welcome to the CitySnooper – Your City Guide Chat App, an interactive Streamlit-based application that lets you ask questions about U.S. cities! This app leverages a custom agent workflow built with llama-index, combining a SQL database of city statistics (e.g., population, state) with semantic search over local PDF documents. Powered by OpenAI's GPT-3.5-turbo and a local embedding model, it provides insightful answers about cities like New York, Los Angeles, and more.

## Features
- Natural Language Queries: Ask questions like "What’s the population of Chicago?" or "Tell me about Seattle from the PDFs."
- Dual Query Engines: Combines structured SQL data (city_stats table) and unstructured PDF content.
- Custom Workflow: Uses a RouterOutputAgentWorkflow to intelligently route queries to the appropriate tool (SQL or PDF).
- Local Persistence: Indexes PDFs and saves them for faster reuse.
- Audio Upload (WIP): Placeholder for future audio file processing in the sidebar.

A demo is shown below:

Ask away! Example queries:

- Which city in California has the highest population?
- What does the PDF say about Miami?

[Video demo](demo.mov)


## Installation and setup

**Setup AssemblyAI**:

Get an API key from [OPENAI](https://shorturl.at/F6PJF) and set it in the `.env` file as follows:

```bash
OPENAI_API_KEY=<YOUR_API_KEY> 
```


**Install Dependencies**:
   Python: Version 3.8 or higher
   ```bash
  pip install -r requirements.txt
  ```

**Run the app**:

   Run the app by running the following command:

   ```bash
   streamlit run app.py
   ```

---
