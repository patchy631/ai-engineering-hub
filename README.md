# RAG + Text-to-SQL: Unified Query Interface

This project demonstrates the integration of **Retrieval-Augmented Generation (RAG)** and **Text-to-SQL** in a single query interface using Streamlit. It showcases how to route queries intelligently between a SQL database and a semantic search tool using LlamaIndex, Qdrant, and other key technologies.

## 🚀 Features

- **Natural Language to SQL**: Translate natural language queries into SQL queries.
- **RAG for Enhanced Retrieval**: Use LlamaCloud for semantic retrieval on unstructured data.
- **Custom Workflow**: Leverage a custom RouterOutputAgentWorkflow for intelligent tool selection.
- **Streamlit Interface**: Simple and interactive front-end for query interaction.
- **Observability**: Integrated with Arize Phoenix for tracing and logging.

## 📂 Project Structure

```
├── app.py                        # Streamlit application
├── llamacloud_sql_router.ipynb   # Core logic for RAG + Text-to-SQL integration
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview and setup guide
```

## Typefully Thread Link:
Check the detailed implementation thread here: https://typefully.com/t/s9P7VdA


## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<forked-repo-name>.git
cd <forked-repo-name>
```

### 2. Install Dependencies

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Install all required Python packages:

```bash
pip install -r requirements.txt
```
## 3.Configuration

Create a `secrets.toml` file in the root directory to securely store your API keys:

```toml
[default]
OPENAI_API_KEY = "your-openai-api-key"
PHOENIX_API_KEY = "your-phoenix-api-key"
LLAMA_API_KEY = "your-llama-api-key"
'''

### 4. Set Environment Variables

Replace placeholders with your actual API keys in the `.env` file or directly in the environment:

```bash
export OPENAI_API_KEY="<your-openai-api-key>"
export PHOENIX_API_KEY="<your-phoenix-api-key>"
```

### 5. Run the Application

```bash
streamlit run app.py
```

## ✅ Usage Guide

- Enter natural language queries in the Streamlit interface.
- The system will route the query appropriately—either to the SQL engine or the RAG model.
- Check the output directly on the interface.

## 🔍 Key Technologies Used

- **LlamaIndex**: For creating and managing indexes.
- **Qdrant**: Vector database for storing and retrieving embeddings.
- **Streamlit**: Front-end framework for interactive data apps.
- **Arize Phoenix**: Observability tool for tracing AI workflows.

## 📄 Sample Queries

- "Which city has the highest population?"
- "What state is Houston located in?"
- "Where is the Space Needle located?"
- "List all of the places to visit in Miami."

## 🤝 Contribution Guide

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request.

## 📜 License

This project is licensed under the [MIT License](LICENSE).

## 🙌 Acknowledgments

- Inspired by the [LlamaCloud Demo](https://github.com/run-llama/llamacloud-demo).
- Special thanks to the maintainers of LlamaIndex and Qdrant.




