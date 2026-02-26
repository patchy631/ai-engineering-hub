# Text2SQL with RAG Chatbot

This repository contains a **Streamlit-based chatbot** that leverages **SQL databases** and **Retrieval-Augmented Generation (RAG)** to provide answers about major U.S. cities. The chatbot integrates **LLM-powered query engines** to fetch structured data from SQL and unstructured data from Llama Cloud.

---

## **Features**
- **SQL Query Engine**: Queries structured city data using `SQLAlchemy`.
- **RAG Query Engine**: Retrieves semantic knowledge from Llama Cloud.
- **Hybrid Agent**: Uses `RouterOutputAgentWorkflow` to route queries.
- **Interactive Chat UI**: Built with `Streamlit`.
- **Formatted Responses**: Detects lists and formats output using Markdown.

---

## **Installation**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/text2sql-with-rag.git
   cd text2sql-with-rag
   ```

2. **Create a Virtual Environment (Optional)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate  # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   - Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```
   - Open `.env` and add your Llama Cloud credentials:
     ```ini
     LLAMA_CLOUD_ORG_ID="your-org-id"
     LLAMA_CLOUD_API_KEY="your-llama-cloud-api-key"
     ```

---

## **Usage**
Run the chatbot with:
```bash
streamlit run app.py
```
This will launch a **web-based UI** where you can enter queries about **New York City, Los Angeles, Chicago, Houston, Miami, and Seattle**.

---

## **Project Structure**
```
text2sql-with-rag/
│── assets/                  # Images & static assets
│── utils/                   # Utility modules
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Query routing logic
│   ├── rag_engine.py        # RAG retrieval tool setup
│   ├── sql_engine.py        # SQL database setup & query tool
│── .env.example             # Environment variable template
│── .gitignore               # Git ignore file
│── requirements.txt         # Python dependencies
│── app.py                   # Main Streamlit app
│── README.md                # Documentation
```

---

## **How It Works**
1. **SQL Query Engine (`sql_engine.py`)**:
   - Creates an **in-memory SQLite database**.
   - Stores structured **city statistics**.
   - Uses `NLSQLTableQueryEngine` to answer structured queries.

2. **RAG Query Engine (`rag_engine.py`)**:
   - Connects to **Llama Cloud** for unstructured queries.
   - Uses `LlamaCloudIndex` to retrieve semantic data.

3. **Agent (`agent.py`)**:
   - Routes queries between **SQL** and **RAG tools**.
   - Uses `RouterOutputAgentWorkflow`.

4. **Streamlit UI (`app.py`)**:
   - Loads chatbot tools.
   - Formats and displays responses interactively.

---

## **Example Queries**
| Query                        | Response Source  |
|------------------------------|-----------------|
| "What's the population of Miami?" | **SQL Database** |
| "What are some popular attractions in New York City?" | **RAG (Llama Cloud)** |
| "Which U.S. city has the largest population?" | **SQL Database** |
| "Tell me something unique about Seattle." | **RAG (Llama Cloud)** |

---

## **Troubleshooting**
### 1️⃣ API Key Issues
If you see **authentication errors**, ensure:
- Your `.env` file has **valid API keys**.
- You have **sufficient API quota**.

### 2️⃣ Streamlit Not Running
Ensure dependencies are installed:
```bash
pip install -r requirements.txt
```

### 3️⃣ SQLite Connection Errors
- Try restarting the app:  
  ```bash
  streamlit run app.py
  ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.