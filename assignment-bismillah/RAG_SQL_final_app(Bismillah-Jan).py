
# Adapted from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming
#All in one document
import os
import gc
import tempfile
import streamlit as st
import httpx
import hashlib
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
st.set_page_config(page_title="Combining RAG and Text-to-SQL in a Single Query Interface", layout="wide")

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_INDEX_API_KEY = os.getenv("LLAMA_INDEX_API_KEY")
Settings.llm = OpenAI("gpt-3.5-turbo")

# Connect to the existing LlamaCloud index
if "llama_cloud_index" not in st.session_state:
    st.session_state["llama_cloud_index"] = LlamaCloudIndex(
        name="dailydoseofds-2025-03-12",  # Use the exact index name from LlamaCloud UI
        project_name="Default",
        organization_id="32a9b69b-a901-41a8-8ff1-6807d15dcfed",
        api_key=LLAMA_INDEX_API_KEY,
        request_timeout=180  # Increase timeout to 180 seconds
    )

llama_cloud_index = st.session_state["llama_cloud_index"]
llama_cloud_query_engine = llama_cloud_index.as_query_engine()

# Custom implementation to track indexed files locally
def get_existing_documents():
    """Track indexed files using a local dictionary."""
    try:
        if "indexed_files_dict" not in st.session_state:
            st.session_state["indexed_files_dict"] = {}
        return st.session_state["indexed_files_dict"]
    except Exception as e:
        st.sidebar.error(f"Error retrieving indexed files: {e}")
        return {}

# Calculate file hash to identify if content has changed
def calculate_file_hash(file_content):
    """Generate a hash for the file content to identify unique files."""
    return hashlib.md5(file_content).hexdigest()

# Store indexed documents in session state
if "indexed_documents" not in st.session_state:
    st.session_state["indexed_documents"] = get_existing_documents()

# Store file hashes to check for content changes
if "file_hashes" not in st.session_state:
    st.session_state["file_hashes"] = {}

# Streamlit UI
st.sidebar.header("Web UI")
st.title("Combining RAG and Text-to-SQL in a Single Query Interface")

# File Upload UI
st.sidebar.subheader("Add your documents!")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type=["pdf"])

def reset_chat():
    st.session_state.messages = []
    gc.collect()

if "messages" not in st.session_state:
    reset_chat()

# Document processing with correct upload parameters
if uploaded_file:
    file_name = uploaded_file.name
    file_content = uploaded_file.getvalue()
    file_hash = calculate_file_hash(file_content)
    
    # Check if file exists by name in our indexed documents
    if file_name in st.session_state["indexed_documents"] and file_name in st.session_state["file_hashes"]:
        # Get stored hash
        stored_hash = st.session_state["file_hashes"].get(file_name)
        
        if stored_hash == file_hash:
            # Same file, no need to upload
            st.sidebar.info(f"✅ {file_name} is already indexed. No re-upload needed.")
        else:
            # Different content with same name
            st.sidebar.info(f"🔄 {file_name} exists but content differs. Uploading new version...")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content)
                temp_filepath = temp_file.name
            
            try:
                # Upload as a new document since we can't specifically update
                response = llama_cloud_index.upload_file(temp_filepath)
                
                # Update our tracking
                st.session_state["file_hashes"][file_name] = file_hash
                
                st.sidebar.success(f"{file_name} successfully updated!")
            except Exception as e:
                st.sidebar.error(f"Update failed: {e}")
    else:
        # New file, upload it
        st.sidebar.info(f"🆕 New document detected! Uploading {file_name} to LlamaCloud...")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_content)
            temp_filepath = temp_file.name

        try:
            # Upload file without any special parameters
            llama_cloud_index.upload_file(temp_filepath)
            
            # Store the file info in our tracking system
            st.session_state["indexed_documents"][file_name] = True
            st.session_state["file_hashes"][file_name] = file_hash
                
            st.sidebar.success(f"{file_name} successfully uploaded and indexed!")
        except Exception as e:
            st.sidebar.error(f" Upload failed: {e}")

col1, col2 = st.columns([6, 1])
with col1:
    st.header(" ")
with col2:
    st.button("Clear ↺", on_click=reset_chat)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input with timeout handling
if prompt := st.chat_input("Ask something about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = llama_cloud_query_engine.query(prompt)
            full_response = response.response  # Extract only clean response text
        except httpx.ReadTimeout:
            full_response = "**Query timed out. Please try again later.**"
        except Exception as e:
            full_response = f" **Error:** {str(e)}"

        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})