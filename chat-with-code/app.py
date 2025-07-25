import os
import time
import uuid
import re
import gc
import glob
import subprocess
import nest_asyncio
from dotenv import load_dotenv

from llama_index.core import Settings
from llama_index.llms.openrouter import OpenRouter
from llama_index.core import PromptTemplate
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core.node_parser import CodeSplitter, MarkdownNodeParser

from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore

from cleanlab_codex.project import Project
from cleanlab_codex.client import Client
import streamlit as st
from validation import codex_validated_query


# Setting up the llm
@st.cache_resource
def load_llm(model_name, api_key):
    llm = OpenRouter(api_key=api_key, model=model_name, max_tokens=1024)
    return llm


# Initialize Codex project
@st.cache_resource
def initialize_codex_project(codex_api_key):
    os.environ["CODEX_API_KEY"] = codex_api_key
    codex_client = Client()
    project = codex_client.create_project(
        name="Chat-with-Code",
        description="Code RAG project with added validation of Codex",
    )
    access_key = project.create_access_key("test-access-key")
    project = Project.from_access_key(access_key)
    return project


#####################
# Utility functions
#####################
def parse_github_url(url):
    """Parse the GitHub URL to extract owner and repository name."""
    pattern = r"https://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    return match.groups() if match else (None, None)


def clone_repo(repo_url):
    """Clone the GitHub repository."""
    return subprocess.run(
        ["git", "clone", repo_url], check=True, text=True, capture_output=True
    )


def validate_owner_repo(owner, repo):
    """Validate the owner and repository name."""
    return bool(owner) and bool(repo)


def parse_docs_by_file_types(ext, language, input_dir_path):
    """Parse documents by file types in the specified directory."""
    files = glob.glob(f"{input_dir_path}/**/*{ext}", recursive=True)

    if len(files) > 0:
        loader = SimpleDirectoryReader(
            input_dir=input_dir_path, required_exts=[ext], recursive=True
        )
        docs = loader.load_data()
        parser = (
            MarkdownNodeParser()
            if ext == ".md"
            else CodeSplitter.from_defaults(language=language)
        )
        return parser.get_nodes_from_documents(docs)
    else:
        return []


def create_index(nodes):
    """Create a Milvus collection and return a vectorstore index."""
    unique_collection_id = uuid.uuid4()
    collection_name = f"chat_with_docs_{unique_collection_id}"
    vector_store = MilvusVectorStore(
        uri="http://localhost:19530",
        dim=768,
        overwrite=True,
        collection_name=collection_name,
    )
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
    """Reset the chat state."""
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()


with st.sidebar:
    st.header("API Configuration 🔑")

    # API Key inputs for OpenRouter and Codex
    openrouter_logo_html = """
        <div style='display: flex; align-items: center; gap: 0px; margin-top: 0px;'>
            <img src="https://files.buildwithfern.com/openrouter.docs.buildwithfern.com/docs/2025-07-24T05:04:17.529Z/content/assets/logo-white.svg" width="180"> 
        </div>
    """
    st.markdown(openrouter_logo_html, unsafe_allow_html=True)
    st.markdown(
        "[Get your API key](https://openrouter.ai/settings/keys)",
        unsafe_allow_html=True,
    )
    openrouter_api_key = st.text_input(
        "OpenRouter API Key", type="password", help="Get your API key from OpenRouter"
    )

    codex_logo_html = """
        <div style='display: flex; align-items: center; gap: 0px; margin-top: 0px;'>
            <img src="https://help.cleanlab.ai/assets/images/cleanlab-codex-black-text-6d57153664e54d704a33ee946792628d.png" width="180"> 
        </div>
    """
    st.markdown(codex_logo_html, unsafe_allow_html=True)
    st.markdown(
        "[Get your API key](https://codex.cleanlab.ai/account)", unsafe_allow_html=True
    )
    codex_api_key = st.text_input(
        "Codex API Key",
        type="password",
        help="Get your API key from Cleanlab Codex",
    )

    st.divider()

    # Input for GitHub URL
    github_url = st.text_input("GitHub Repository URL")

    # Button to load and process the GitHub repository
    process_button = st.button("Load")

    message_container = st.empty()  # Placeholder for dynamic messages

    if process_button and github_url:
        if not openrouter_api_key:
            st.error("Please provide OpenRouter API Key")
            st.stop()

        if not codex_api_key:
            st.error("Please provide Codex API Key")
            st.stop()

        owner, repo = parse_github_url(github_url)
        if validate_owner_repo(owner, repo):
            with st.spinner(f"Loading {repo} repository by {owner}..."):
                try:
                    # Initialize Codex project
                    project = initialize_codex_project(codex_api_key)

                    # input_dir_path = f"/teamspace/studios/this_studio/{repo}"
                    input_dir_path = os.path.join(os.getcwd(), repo)

                    if not os.path.exists(input_dir_path):
                        subprocess.run(
                            ["git", "clone", github_url],
                            check=True,
                            text=True,
                            capture_output=True,
                        )

                    if os.path.exists(input_dir_path):
                        file_types = {
                            ".md": "markdown",
                            ".py": "python",
                            ".ipynb": "python",
                            ".js": "javascript",
                            ".ts": "typescript",
                        }

                        nodes = []
                        for ext, language in file_types.items():
                            nodes += parse_docs_by_file_types(
                                ext, language, input_dir_path
                            )
                    else:
                        st.error(
                            "Error occurred while cloning the repository, carefully check the url"
                        )
                        st.stop()

                    # Setting up the embedding model
                    Settings.embed_model = HuggingFaceEmbedding(
                        model_name="BAAI/bge-base-en-v1.5"
                    )
                    try:
                        index = create_index(nodes)
                    except:
                        index = VectorStoreIndex(nodes=nodes)

                    # ====== Setup a query engine ======
                    Settings.llm = load_llm(
                        model_name="qwen/qwen3-coder:free", api_key=openrouter_api_key
                    )
                    query_engine = index.as_query_engine(
                        streaming=True, similarity_top_k=4
                    )

                    # ====== Customise prompt template ======
                    qa_prompt_tmpl_str = (
                        "Context information is below.\n"
                        "---------------------\n"
                        "{context_str}\n"
                        "---------------------\n"
                        "Given the context information above, I want you to think step by step to answer the query in a crisp manner. "
                        "First, carefully check if the answer can be found in the provided context. "
                        "If the answer is available in the context, use that information to respond. "
                        "If the answer is not available in the context or the context is insufficient, "
                        "you may use your own knowledge to provide a helpful response. "
                        "Only say 'I don't know!' if you cannot answer the question using either the context or your general knowledge.\n"
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
                    st.session_state.project = project

                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.stop()

                st.success("Ready to Chat!")
        else:
            st.error("Invalid owner or repository")
            st.stop()

col1, col2 = st.columns([6, 1])

with col1:
    st.header(f"Chat with Code using Qwen3-Coder!")
    powered_by_html = """
        <div style='display: flex; align-items: center; gap: 10px; margin-top: -10px;'>
            <span style='font-size: 20px; color: #666;'>Powered by</span>
            <img src="https://docs.llamaindex.ai/en/stable/_static/assets/LlamaSquareBlack.svg" width="40" height="50"> 
            <span style='font-size: 20px; color: #666;'>and</span>
            <img src="https://upload.wikimedia.org/wikipedia/commons/7/7d/Milvus-logo-color-small.png" width="100">
        </div>
    """
    st.markdown(powered_by_html, unsafe_allow_html=True)

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
    # Check if query engine and project are available
    if "query_engine" not in st.session_state or "project" not in st.session_state:
        st.error("Please load a repository first!")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # context = st.session_state.context
        query_engine = st.session_state.query_engine
        project = st.session_state.project

        # Simulate stream of response with milliseconds delay
        emoji, trust_score, streaming_response = codex_validated_query(
            query_engine=query_engine, project=project, user_query=prompt
        )

        # Streaming
        full_response = ""
        for char in streaming_response:
            full_response += char
            message_placeholder.markdown(full_response + "▌")
            time.sleep(0.01)  # Adjust speed as needed

        message_placeholder.markdown(full_response)
        st.markdown(f"{emoji} **Trust Score**: `{trust_score}`")
        # st.session_state.context = ctx

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
