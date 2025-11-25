from contextlib import redirect_stdout
import io
from workflow import CorrectiveRAGWorkflow
from llama_index.core import Settings
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
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

    llm = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
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
    try:
        with st.spinner("Loading documents and initializing the workflow..."):
            documents = SimpleDirectoryReader(file_path).load_data()
            print(f"DEBUG: Loaded {len(documents)} documents")
            for i, doc in enumerate(documents):
                print(f"DEBUG: Document {i} preview: {doc.text[:100]}...")

            vector_store = MilvusVectorStore(
                uri="./milvus_demo.db", dim= 1024, overwrite=True
            )
            print("DEBUG: Milvus vector store created")
            
            embed_model = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5", cache_dir="./hf_cache")
            Settings.embed_model = embed_model
            print("DEBUG: Embedding model set")
            
            llm = load_llm()
            print("DEBUG: LLM loaded")

            Settings.llm = llm
            storage_context = StorageContext.from_defaults(
                vector_store=vector_store)
            print("DEBUG: Storage context created")
            
            index = VectorStoreIndex.from_documents(
                documents,
                storage_context=storage_context,
            )
            print("DEBUG: Index created")

            # Check if FIRECRAWL_API_KEY is available
            if "FIRECRAWL_API_KEY" not in os.environ:
                raise ValueError("FireCrawl API key not found. Please enter it in the sidebar.")

            workflow = CorrectiveRAGWorkflow(
                index=index,
                firecrawl_api_key=os.environ["FIRECRAWL_API_KEY"],
                verbose=True,
                timeout=249,  # Increased timeout to match workflow execution
                llm=llm
            )
            print("DEBUG: Workflow created")

            st.session_state.workflow = workflow
            return workflow
    except Exception as e:
        st.error(f"Failed to initialize workflow: {e}")
        raise e

# Function to run the async workflow


async def run_workflow(query):
    try:
        # Capture stdout to get the workflow logs
        f = io.StringIO()
        with redirect_stdout(f):
            # Add timeout to prevent hanging
            result = await asyncio.wait_for(
                st.session_state.workflow.run(query_str=query),
                timeout=120  # 2 minutes timeout
            )

        # Get the captured logs and store them
        logs = f.getvalue()
        if logs:
            st.session_state.workflow_logs.append(logs)

        return result
    except asyncio.TimeoutError:
        st.error("Workflow execution timed out after 2 minutes")
        raise Exception("Workflow execution timed out")
    except Exception as e:
        # Log the error and re-raise it
        st.error(f"Workflow execution failed: {e}")
        raise e

# Sidebar for document upload
with st.sidebar:

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
    # Centered main heading
    st.markdown('''
        <h1 style="text-align: center; font-weight: 500; color: #8de2ff;">
            Corrective RAG Agentic Workflow
        </h1>
    ''', unsafe_allow_html=True)
    
    # Logos section below the heading
    st.markdown('''
        <div style="text-align: center; margin: 20px 0;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div style="text-align: center;">
                    <img src="https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png" alt="Firecrawl" style="height: 60px; margin-bottom: 5px;">
                </div>
                <div style="text-align: center;">
                    <img src="https://i.ibb.co/m5RtcvnY/beam-logo.png" alt="Beam Cloud" style="height: 60px; margin-bottom: 5px;">
                </div>
                <div style="text-align: center;">
                    <img src="https://milvus.io/images/layout/milvus-logo.svg" alt="Milvus" style="height: 60px; margin-bottom: 5px;">
                </div>
                <div style="text-align: center;">
                    <img src="https://www.comet.com/site/wp-content/uploads/2024/09/comet-logo-1.png" alt="CometML" style="height: 60px; margin-bottom: 5px;">
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    # Animation GIF section
    if "show_animation" not in st.session_state:
        st.session_state.show_animation = True
    
    if st.session_state.show_animation:
        st.image("https://d3e0luujhwn38u.cloudfront.net/original/img/original/186727/fbd774b8-29da-479a-a60c-880f84d66424.gif", use_container_width=True)

with col2:
    if st.button("Clear ↺", on_click=reset_chat):
        st.session_state.show_animation = False

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
        try:
            # Run the async workflow with proper error handling
            result = asyncio.run(run_workflow(prompt))

            # Display the workflow logs in an expandable section OUTSIDE and BEFORE the assistant chat bubble
            if log_index < len(st.session_state.workflow_logs):
                with st.expander("View Workflow Execution Logs", expanded=False):
                    st.code(
                        st.session_state.workflow_logs[log_index], language="text")

            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                if hasattr(result, 'response'):
                    result_text = result.response
                else:
                    result_text = str(result)

                # Stream the response word by word
                words = result_text.split()
                for i, word in enumerate(words):
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")
                    # Add a delay between words
                    if i < len(words) - 1:  # Don't delay after the last word
                        time.sleep(0.1)

                # Display final response without cursor
                message_placeholder.markdown(full_response)

        except Exception as e:
            st.error(f"Error running workflow: {e}")
            full_response = f"An error occurred while processing your request: {e}"
            st.markdown(full_response)

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
        # else:
        #     full_response = "Please upload a document first to initialize the workflow."
        #     st.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})
