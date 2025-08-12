import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import base64
import gc
import random
import tempfile
import time
import uuid

from IPython.display import Markdown, display

from llama_index.core import Settings
from llama_index.llms.ollama import Ollama

from llama_index.core import PromptTemplate
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import VectorStoreIndex, ServiceContext, SimpleDirectoryReader

import streamlit as st

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

@st.cache_resource
def load_llm(model_option):
    if model_option == "Qwen3":
        return Ollama(model="qwen3")
    elif model_option == "DeepSeek-R1":
        return Ollama(model="deepseek-r1")

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""
    st.markdown(pdf_display, unsafe_allow_html=True)

with st.sidebar:
    
    # Add dropdown for model selection
    model_option = st.selectbox("Select Model", ["Qwen3", "DeepSeek-R1"])
    
    
    st.header(f"Add your documents!")
    
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
                    if os.path.exists(temp_dir):
                        loader = SimpleDirectoryReader(
                            input_dir=temp_dir,
                            required_exts=[".pdf"],
                            recursive=True
                        )
                    else:    
                        st.error('Could not find the file you uploaded, please check again...')
                        st.stop()
                    
                    docs = loader.load_data()
                    llm = load_llm(model_option)
                    embed_model = FastEmbedEmbedding(model_name="BAAI/bge-large-en-v1.5")
                    Settings.embed_model = embed_model
                    index = VectorStoreIndex.from_documents(docs, show_progress=True)
                    Settings.llm = llm
                    query_engine = index.as_query_engine(streaming=True)

                    qa_prompt_tmpl_str = (
                    "Context information is below.\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Given the context information above I want you to think step by step to answer the query in a crisp manner, in case you don't know the answer say 'I don't know!'.\n"
                    "Query: {query_str}\n"
                    "Answer: "
                    )
                    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

                    query_engine.update_prompts(
                        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                    )
                    
                    st.session_state.file_cache[file_key] = query_engine
                else:
                    query_engine = st.session_state.file_cache[file_key]

                st.success("Ready to Chat!")
                display_pdf(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    # Removed the original header
    st.markdown("<h2 style='color: #0066cc;'> Qwen3 vs DeepSeek-R1 RAG Battle </h2>", unsafe_allow_html=True)
    # Replace text with image and subtitle styling
    st.markdown("<div style='display: flex; align-items: center; gap: 10px;'><span style='font-size: 28px; color: #666;'>Powered by LlamaIndex</span><img src='data:image/png;base64,{}' width='50'></div>".format(
        base64.b64encode(open("./assets/llamaindex.png", "rb").read()).decode()
    ), unsafe_allow_html=True)


with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Logic to handle model selection and API Key
# Use API Key from session state if available, otherwise from environment variable


st.write(f"Using {model_option}...")
Settings.llm = load_llm(model_option) # Reload LLM with potentially new key if model is selected *after* key entry

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        streaming_response = query_engine.query(prompt)
        
        for chunk in streaming_response.response_gen:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
