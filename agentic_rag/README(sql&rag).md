SQL + RAG Query Engine

🔗 Twitter Post: View Here
🎥 Demo Video: Watch Here



Project Overview

This project is an AI-driven hybrid query engine that processes both structured SQL queries and unstructured document searches using LlamaIndex, Ollama (Mistral), and Qdrant.

Features
Structured Data: Uses SQL to query city statistics like population and state.
Unstructured Data: Retrieves answers from Wikipedia PDFs using embeddings.
Smart Query Routing: Uses LLMs to decide whether to use SQL or vector search.

Tech Stack
LlamaIndex – Vector-based document search (RAG).
Ollama (Mistral LLM) – Intelligent query understanding.
Qdrant – Efficient vector storage and retrieval.
SQLAlchemy – Managing structured SQL databases.
HuggingFace Embeddings – Encoding text into vector representations.

Installation Guide
Clone the repository:
git clone https://github.com/sakshiware25/ai-engineering-hub.git
cd ai-engineering-hub

Install dependencies:
pip install -r requirements.txt

Download model and PDFs:
Place the HuggingFace embeddings model at the specified path.
Add Wikipedia PDFs inside the /data/ folder.
Running the Code
Run the query engine with:
python llamacloud_sql_router.py

Example Queries:
Which city has the highest population?
Where is the Space Needle located?
How do people in Chicago get around?

The system intelligently decides whether to retrieve data from SQL or RAG.

Contact
For any questions, open an issue or reach out.