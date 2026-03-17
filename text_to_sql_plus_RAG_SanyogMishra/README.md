# RAG + SQL Router: Smart Query System

This project integrates RAG (Retrieval-Augmented Generation) with SQL querying using LlamaIndex and Ollama. Users can interact with structured SQL databases and document embeddings within a unified query interface.
We use:

- LlamaIndex for orchestration of query routing, SQL querying, and vector search
- SQLAlchemy for database handling (connection, schema inspection, etc.)
- Ollama for language and embedding models
- SQLite for in-memory database
- Streamlit to wrap the logic in an interactive UI

[Demo Video](demo_vid.mp4)

## Installation and Setup

### 1. Install Dependencies

Ensure you have Python 3.11 or later installed. Install the required dependencies using:

```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama

Ollama is used to run the LLM and embedding models locally. To install it, follow these steps:

#### Install Ollama (Linux/macOS)

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Install Ollama (Windows)

Download the installer from [Ollama’s official website](https://ollama.ai/) and follow the installation instructions.

### 3. Pull Models for Ollama

Before running the application, ensure you have the required models downloaded. Run the following command:

```bash
ollama pull <model_name>
```

We used `Qwen2.5-Coder 7B`:

```bash
ollama pull qwen2.5-coder:7b
```

For embeddings, you may also need:

```bash
ollama pull <embedding_model_name>
```

We used `all-minilm`:

```bash
ollama pull all-minilm
```

### 4. Run Ollama

Start the Ollama server locally:

```bash
ollama serve
```

### 5. Run the Application

Run the application with:

```bash
streamlit run ui.py
```

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.
