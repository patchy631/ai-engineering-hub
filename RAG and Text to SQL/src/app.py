import streamlit as st
from texttosqlrag import TextToSQLRAG
import time

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

if db_url:
    try:
        text_to_sql_rag = TextToSQLRAG(db_url)
        st.sidebar.success("✅ Database connection successful!")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {str(e)}")
        db_url = None

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
            response = text_to_sql_rag.query(question)
            response_text = st.write_stream(stream_response(response))

        st.session_state.messages.append({"role": "assistant", "content": response_text})

else:
    st.warning("⚠️ Please connect to a database to start querying.")
