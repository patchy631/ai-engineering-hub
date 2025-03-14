import streamlit as st
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.ollama import Ollama
import qdrant_client

# ---------- Custom Title ----------
st.markdown(
    "<h1 style='color: blue;'>RAG + Text-to-SQL: Unified Query Interface 🚀</h1>", 
    unsafe_allow_html=True
)

st.write("This app processes queries using Retrieval-Augmented Generation (RAG) and Text-to-SQL.")


# ---------- API Keys / Configuration ----------
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")  # Ensure this is set in Streamlit secrets
QDRANT_URL = "http://localhost:6333"  # Update if using a different host

# ---------- Initialize Qdrant and Embedding ----------
qdrant_client = qdrant_client.QdrantClient(url=QDRANT_URL)
embedding_model = OpenAIEmbedding(api_key=OPENAI_API_KEY)
vector_store = QdrantVectorStore(client=qdrant_client, collection_name="rag_db")
index = VectorStoreIndex(vector_store=vector_store)

# ---------- Load Data (if needed) ----------
# reader = SimpleDirectoryReader('data').load_data()
# index.insert_documents(reader)

# ---------- Streamlit Input ----------
query = st.text_input("Enter your query:")

# ---------- Process Query ----------
if st.button("Submit"):
    if query:
        # Example processing logic (adjust based on your notebook's method)
        result = index.query(query, similarity_top_k=3)
        st.write("### Response:")
        st.write(result)
    else:
        st.write("Please enter a query first.")
