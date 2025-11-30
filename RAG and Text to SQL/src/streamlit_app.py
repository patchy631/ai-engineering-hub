import streamlit as st
from sqlalchemy import create_engine, inspect
from llama_index.core.indices.struct_store.sql import SQLDatabase
from llama_index.core.indices.struct_store.sql_query import SQLTableRetrieverQueryEngine
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.objects import SQLTableNodeMapping, SQLTableSchema, ObjectIndex
import os
from dotenv import load_dotenv
import time


# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Configure LLM and Embedding model
Settings.llm = Groq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-large-en-v1.5")

# Streamlit UI Configuration
st.set_page_config(page_title="Chat with Your Database", page_icon="📊", layout="wide")
st.title("📊 Chat with your Database!")

with st.expander("ℹ️ Instructions"):
    st.write("""
    1. Choose a database connection using the sidebar.
    2. Use the demo database or enter your credentials.
    3. Ask a sales-related question in plain English.
    4. Click 'Send' to get an AI-generated response.
    """)

# Sidebar for Database Selection
st.sidebar.header("🛠 Database Connection")
use_demo_db = st.sidebar.toggle("Use Demo DB", value=False)
db_url = "sqlite:///sales.db" if use_demo_db else None

if not use_demo_db:
    db_type = st.sidebar.selectbox("Database Type", ["postgresql", "mysql", "sqlite"], key="db_type")
    db_user = st.sidebar.text_input("Username", key="db_user")
    db_password = st.sidebar.text_input("Password", type="password", key="db_password")
    db_host = st.sidebar.text_input("Host (e.g., localhost)", key="db_host")
    db_port = st.sidebar.text_input("Port (e.g., 5432)", key="db_port")
    db_name = st.sidebar.text_input("Database Name", key="db_name")

    if st.sidebar.button("🔗 Connect to Database"):
        if db_type == "sqlite":
            db_url = "sqlite:///:memory:"
        else:
            db_url = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        st.sidebar.success("✅ Database connected!")
else:
    st.sidebar.expander("About the demo database.", expanded=False).write(""""
    sales.db is a SQLite database with the following tables:
    1. city_stats"
    2. customers""
    3. products""
    4. orders
    5. order_items
    """)

if db_url:
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        if not table_names:
            st.error("❌ Database connected, but no tables found!")
        else:
            st.sidebar.success(f"✅ Connected! Found {len(table_names)} tables.")

    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {str(e)}")
        db_url = None 

    sql_db = SQLDatabase(engine)
    
    # Setup Qdrant
    qdrant_client = QdrantClient(host="localhost", port=6333)
    qdrant_store = QdrantVectorStore(client=qdrant_client, collection_name="my_collection")
    
    # Define table schemas
    table_node_mapping = SQLTableNodeMapping(sql_db)
    table_names = inspect(engine).get_table_names()
    table_schema_objs = [SQLTableSchema(table_name=table) for table in table_names]

    
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        vector_store=qdrant_store,
    )
    
    query_engine = SQLTableRetrieverQueryEngine(
        sql_db, obj_index.as_retriever(similarity_top_k=1, embed_model=Settings.embed_model, llm=Settings.llm)
    )


def stream_response(text):
        for word in text.split():
            yield word + " "
            time.sleep(0.05)

if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


if db_url:
    if question := st.chat_input("💬 Ask a question about your data"):
        st.session_state.messages.append({"role": "user", "content": question})
    
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            response = query_engine.query(question)
            response_text = st.write_stream(stream_response(response.response))  
     
        st.session_state.messages.append({"role": "assistant", "content": response_text})

else:
    st.warning("⚠️ Please connect to a database to start querying.")
