# 🚀 Agentic RAG + Text-to-SQL System  

An **LLM-powered Agentic RAG** system that dynamically selects tools, retrieves structured/unstructured data, and generates responses by leveraging **SQL databases & LlamaIndex**.

## 🛠 Features
- **Hybrid Query Processing**: Retrieves knowledge from both **vector databases** (RAG) and **SQL databases**.
- **Autonomous Tool Selection**: LLM decides the best tool for each query.
- **Conversational Memory**: Maintains chat history for better context.
- **Streamlit to build the UI**: Fastest Way to Build UI.

## 📌 How It Works
1. **User Input** → Query is stored in chat history.
2. **Tool Routing** → LLM decides between:
   - **SQL Querying**: Converts NL queries into SQL.
   - **Vector Search**: Finds semantic context from documents.
3. **Execution & Response** → Results are aggregated & returned.


## 🔑 Set Up API Keys

This project requires API keys for **OpenAI** and **LlamaIndex Cloud**.

### 1️⃣ Get OpenAI API Key  
1. Sign up at [OpenAI](https://platform.openai.com/signup).  
2. Navigate to [API Keys](https://platform.openai.com/account/api-keys).  
3. Click **Create API Key** and copy it.

### 2️⃣ Get LlamaIndex Cloud API Key  
1. Register at [LlamaIndex Cloud](https://cloud.llamaindex.ai/).  
2. Go to **API Settings** in your dashboard.  
3. Generate and copy your API key.

---

## 🔧 Configure API Keys  

Get API keys and add in the following fields:  
```
OPENAI_API_KEY=your_openai_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
```

Get API keys and add in the following fields:  
```
OPENAI_API_KEY=your_openai_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
```

## 🔧 Install Dependencies:
Ensure you have Python 3.11 or later installed.

```
pip install streamlit llama-index sqlalchemy llama-index-llms-openai llama-index-indices-managed llama-index-utils-workflow llama-index-core llama_index.indices.managed.llama_cloud
```

## Run the app:
Run the app by using the following command:
```
streamlit run app.py
```