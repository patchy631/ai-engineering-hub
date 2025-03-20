import os

import gc
import re
import glob
import uuid
import textwrap
import subprocess
import nest_asyncio
from dotenv import load_dotenv

import streamlit as st

from llama_index.core import Settings
from llama_index.core import PromptTemplate
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.node_parser import CodeSplitter, MarkdownNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
import qdrant_client

from dotenv import load_dotenv

load_dotenv()

# setting up the llm
@st.cache_resource
def load_llm(model_name, provider="openai"):
    if provider == "anthropic":
        return Anthropic(model=model_name)
    elif provider == "openai":
        return OpenAI(model=model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


# utility functions
def parse_github_url(url):
    pattern = r"https://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    return match.groups() if match else (None, None)

def clone_repo(repo_url):
    return subprocess.run(["git", "clone", repo_url], check=True, text=True, capture_output=True)


def validate_owner_repo(owner, repo):
    return bool(owner) and bool(repo)

def parse_docs_by_file_types(ext, language, input_dir_path):
    """Parse documents based on file extension"""
    files = glob.glob(f"{input_dir_path}/**/*{ext}", recursive=True)
    
    if len(files) > 0:
        print(f"Found {len(files)} files with extension {ext}")
        loader = SimpleDirectoryReader(
            input_dir=input_dir_path, required_exts=[ext], recursive=True
        )
        docs = loader.load_data()
        parser = (
            MarkdownNodeParser()
            if ext == ".md"
            else CodeSplitter.from_defaults(language=language)
        )
        nodes = parser.get_nodes_from_documents(docs)
        print(f"Processed {len(nodes)} nodes from {ext} files")
        return nodes
    return []


# create an qdrant collection and return an index
def create_index(nodes, client):
    unique_collection_id = uuid.uuid4()
    collection_name = f"chat_with_docs_{unique_collection_id}"
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
    )
    return index

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None


def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()


with st.sidebar:
    
    # Model selection
    model_options = {
        "OpenAI o3-mini": {"provider": "openai", "model": "o3-mini"},
        "Claude 3.7 Sonnet": {"provider": "anthropic", "model": "claude-3-7-sonnet-20250219"}
    }
    selected_model = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        index=0
    )
    
    # Input for GitHub URL
    github_url = st.text_input("GitHub Repository URL")

    # Button to load and process the GitHub repository
    process_button = st.button("Load")

    message_container = st.empty()  # Placeholder for dynamic messages

    if process_button and github_url:
        owner, repo = parse_github_url(github_url)
        if validate_owner_repo(owner, repo):
            with st.spinner(f"Loading {repo} repository by {owner}..."):
                try:
                    input_dir_path = f"./{repo}"
                    
                    if not os.path.exists(input_dir_path):
                        subprocess.run(["git", "clone", github_url], check=True, text=True, capture_output=True)

                    if os.path.exists(input_dir_path):
                        file_types = {
                            ".md": "markdown",
                            ".py": "python",
                            ".ipynb": "python",
                            ".js": "javascript",
                            ".ts": "typescript"
                        }

                        nodes = []
                        for ext, language in file_types.items():
                            nodes += parse_docs_by_file_types(ext, language, input_dir_path)
                    else:    
                        st.error('Error occurred while cloning the repository, carefully check the url')
                        st.stop()
                    
                    # setting up the embedding model
                    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")                 
                    try:
                        index = create_index(nodes)
                    except:
                        index = VectorStoreIndex(nodes=nodes)

                    # ====== Setup a query engine ======
                    model_info = model_options[selected_model]
                    Settings.llm = load_llm(model_name=model_info["model"], provider=model_info["provider"])
                    query_engine = index.as_query_engine(streaming=True, similarity_top_k=4)
                    
                    # ====== Customise prompt template ======
                    qa_prompt_tmpl_str = (
                    "Context information is below.\n"
                    "---------------------\n"
                    "{context_str}\n"
                    "---------------------\n"
                    "Given the context information and your knowledge, I want you to think step by step to answer the query in a crisp manner, incase case you don't know the answer say 'I don't know!'.\n"
                    "Query: {query_str}\n"
                    "Answer: "
                    )
                    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

                    query_engine.update_prompts(
                        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                    )

                    if nodes:
                        message_container.success("Data loaded successfully!!")
                    else:
                        message_container.write(
                            "No data found, check if the repository is not empty!"
                        )
                    st.session_state.query_engine = query_engine

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.stop()

                st.success("Ready to Chat!")
        else:
            st.error('Invalid owner or repository')
            st.stop()

col1, col2 = st.columns([6, 1])

with col1:
    st.header(f"Claude 3.7 Sonnet vs OpenAI o3! </>")

with col2:
    st.button("Clear ↺", on_click=reset_chat)


# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # context = st.session_state.context
        query_engine = st.session_state.query_engine

        # Simulate stream of response with milliseconds delay
        streaming_response = query_engine.query(prompt)
        
        for chunk in streaming_response.response_gen:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

        # full_response = query_engine.query(prompt)

        message_placeholder.markdown(full_response)
        # st.session_state.context = ctx

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})