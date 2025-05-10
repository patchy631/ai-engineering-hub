from contextlib import redirect_stdout
import io
from workflow import CorrectiveRAGWorkflow
from llama_index.core import Settings
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.llms.lmstudio import LMStudio
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from IPython.display import Markdown, display
import time
import uuid
import tempfile
import gc
import base64
import qdrant_client
import streamlit as st
import asyncio
import os
import sys
import logging
from dotenv import load_dotenv
import nest_asyncio
nest_asyncio.apply()

load_dotenv()


# Set up page configuration
st.set_page_config(page_title="Corrective RAG Demo", layout="wide")

# Initialize session state variables
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "workflow_logs" not in st.session_state:
    st.session_state.workflow_logs = []

session_id = st.session_state.id


@st.cache_resource
def load_llm():
    llm = LMStudio(
        model_name="deepseek-r1-distill-qwen-7b",
        base_url="http://localhost:1234/v1",
        temperature=0.1,
    )
    return llm


def reset_chat():
    st.session_state.messages = []
    gc.collect()


def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

# Function to initialize the workflow with uploaded documents


def initialize_workflow(file_path):
    with st.spinner("Loading documents and initializing the workflow..."):
        documents = SimpleDirectoryReader(file_path).load_data()

        client = qdrant_client.QdrantClient(
            host="localhost",
            port=6333
        )

        vector_store = QdrantVectorStore(client=client, collection_name="test")
        embed_model = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")
        Settings.embed_model = embed_model
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
        )

        workflow = CorrectiveRAGWorkflow(
            index=index,
            firecrawl_api_key=os.environ["FIRECRAWL_API_KEY"],
            verbose=True,
            timeout=60,
            llm=load_llm()
        )

        st.session_state.workflow = workflow
        return workflow

# Function to run the async workflow


async def run_workflow(query):
    # Capture stdout to get the workflow logs
    f = io.StringIO()
    with redirect_stdout(f):
        result = await st.session_state.workflow.run(query_str=query)

    # Get the captured logs and store them
    logs = f.getvalue()
    if logs:
        st.session_state.workflow_logs.append(logs)

    return result

# Sidebar for document upload
with st.sidebar:
    # Add FireCrawl logo and Configuration header in the same line
    col1, col2 = st.columns([1, 3])
    with col1:
        # Add vertical space to align with header
        st.write("")
        st.image("./assets/firecrawl_logo.png", width=65)
    with col2:
        st.header("Firecrawl Configuration")
        st.write("Deep Web Search")

    # Add hyperlink to get API key
    st.markdown("[Get your API key](https://www.firecrawl.dev/signin/signup)",
                unsafe_allow_html=True)

    firecrawl_api_key = st.text_input(
        "Enter your Firecrawl API Key", type="password")

    # Store API key as environment variable
    if firecrawl_api_key:
        os.environ["FIRECRAWL_API_KEY"] = firecrawl_api_key
        st.success("API Key stored successfully!")

    st.header("Add your documents!")

    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf")

    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                file_key = f"{session_id}-{uploaded_file.name}"
                st.write("Indexing your document...")

                if file_key not in st.session_state.get('file_cache', {}):
                    # Initialize workflow with the uploaded document
                    workflow = initialize_workflow(temp_dir)
                    st.session_state.file_cache[file_key] = workflow
                else:
                    st.session_state.workflow = st.session_state.file_cache[file_key]

                # Inform the user that the file is processed and Display the PDF uploaded
                st.success("Ready to Chat!")
                display_pdf(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    # Removed the original header
    st.markdown("<h2 style='color: #0066cc;'>⚙️ Corrective RAG agentic workflow</h2>",
                unsafe_allow_html=True)
    # Replace text with image and subtitle styling
    st.markdown("<div style='display: flex; align-items: center; gap: 10px;'><span style='font-size: 28px; color: #666;'>Powered by LlamaIndex</span><img src='data:image/png;base64,{}' width='50'></div>".format(
        base64.b64encode(open("./assets/images.jpeg", "rb").read()).decode()
    ), unsafe_allow_html=True)

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Display chat messages from history on app rerun
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # If this is a user message and there are logs associated with it
    # Display logs AFTER the user message but BEFORE the next assistant message
    if message["role"] == "user" and "log_index" in message and i < len(st.session_state.messages) - 1:
        log_index = message["log_index"]
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("View Workflow Execution Logs", expanded=False):
                st.code(
                    st.session_state.workflow_logs[log_index], language="text")

# Accept user input
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message to chat history with placeholder for log index
    log_index = len(st.session_state.workflow_logs)
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "log_index": log_index})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    if st.session_state.workflow:
        # Run the async workflow
        result = asyncio.run(run_workflow(prompt))

        # Display the workflow logs in an expandable section OUTSIDE and BEFORE the assistant chat bubble
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("View Workflow Execution Logs", expanded=False):
                st.code(
                    st.session_state.workflow_logs[log_index], language="text")

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        if st.session_state.workflow:
            message_placeholder = st.empty()
            full_response = ""

            result = result.response

            # Stream the response word by word
            words = result.split()
            for i, word in enumerate(words):
                full_response += word + " "
                message_placeholder.markdown(full_response + "▌")
                # Add a delay between words
                if i < len(words) - 1:  # Don't delay after the last word
                    time.sleep(0.1)

            # Display final response without cursor
            message_placeholder.markdown(full_response)
        else:
            full_response = "Please upload a document first to initialize the workflow."
            st.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
