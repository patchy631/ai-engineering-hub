# RAG and Text-to-SQL

This project enables AI-driven querying over city data, intelligently selecting between SQL-based retrieval and RAG-based retrieval using LlamaIndex and LlamaCloud.

---

## 🚀 Tech Stack

- **SQLite + SQLAlchemy** for structured data storage and retrieval  
- **LlamaIndex + LlamaCloud** for RAG-based retrieval of unstructured city information  
- **OpenAI** for LLM-powered query understanding  
- **Streamlit** for an interactive user interface  

---

## Watch the Demo

https://drive.google.com/file/d/1V1QyaNn7OP2Nt63BUGVtFXfDixyckTDJ/view?usp=sharing 

---

## X Thread Draft Link

https://typefully.com/t/K2oyWAT 

---

## Installation & Setup

### 1️- Install Dependencies  
Ensure you have Python 3.11+ installed, then run:  

```bash
pip install streamlit sqlalchemy llama-index llama-index-core openai
```
---
### 2- Set Up the Database  
Run the following script to create and populate the SQLite database:
```bash
python database.py
```

### 3- Upload City Data to LlamaCloud (Optional for RAG Retrieval)
To use LlamaCloud RAG, manually upload Wikipedia PDF files about cities into LlamaCloud Index.
Ensure the index is set up correctly for retrieval.

### 4- Define your API keys in the backend.py
```bash
os.environ["OPENAI_API_KEY"] = "sk-proj-xxxxxxx"
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-xxxxxx"
```

### 5- Run the App
```bash
streamlit run streamlit.py
```



