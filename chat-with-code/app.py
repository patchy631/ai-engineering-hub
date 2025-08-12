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
    unique_collection_id = uuid.uuid4().hex
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
    codex_logo_html = """
        <div style='display: flex; align-items: center; gap: 0px; margin-top: 2px;'>
            <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAjgAAACACAMAAAAxreP1AAAC91BMVEVHcEz///8AAJP///7+/v9/f//////9/fzIyO/+/v/8/Pz+/v/7+/3////////n5/D////29vvp6e3////7+/v////7+/3////////+/v/6+vz////////+/v/5+fz////9/f7////////////29vr////39//39/v39/f////39/3////8/P3////4+Pv39/r+/v/////8/P75+fn////8/P35+fv////9/f7////6+v36+v3////////6+vv6+v36+vv9/f78/P38/P39/f79/f78/P78/P79/f/9/f/7+/z7+/v8/P77+/z////8/P/7+/v8/P37+/z+/v7+/v/8/P39/f79/f38/P79/f78/P/8/Pz8/P38/P3+/v79/f78/P3+/v/8/P38/P39/f78/P38/P38/P38/P78/P38/P38/P38/P39/f78/Pz9/f77+/39/f7+/v/9/f77+/3+/v78/P78/P3+/v/+/v7////7+/37+/v8/P38/P39/f79/f79/f78/P39/f39/f79/f78/P39/f77+/38/P77+/3+/v79/f39/f79/f38/P36+vz8/P79/f79/f39/f/9/f38/P39/f78/P39/f79/f39/f38/P38/P3////9/f79/f39/f39/f39/f79/f39/f78/P39/f79/f39/f38/P39/f7////9/f79/f38/P38/P3////8/P39/f79/f79/f78/P3////9/f78/P39/f79/f78/Pz////9/f79/f39/f78/P3+/v/7+/z////////+/v/8/P3////9/f/9/f78/P3////8/P38/Pz9/f/9/f79/f3////9/f78/P3////9/f/9/f78/P3////////9/f78/P37+/z////////9/f7////////9/f/8/P3////////9/f/9/f79/f38/P3////////9/f/9/f79/f38/P38/P38/Pz////////+/v/+/v79/f/9/f79/f38/P/8/P38/P159MFNAAAA/HRSTlMAAQEDAgIEBQQGBwgJCgsLDA0MDg8QERITFRQWFxkYGxocHh8eICEgISMiJCUnJygqLSwuMTAzNTQ3Njc5Ozo9PD8+QUJERklKTE1MTk9QUFBTUlRWV1hZ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" width="140"> 
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

    openrouter_logo_html = """
        <div style='display: flex; align-items: center; gap: 0px; margin-top: 0px;'>
            <img src="https://files.buildwithfern.com/openrouter.docs.buildwithfern.com/docs/2025-07-24T05:04:17.529Z/content/assets/logo-white.svg" width="180"> 
        </div>
    """
    st.markdown(openrouter_logo_html, unsafe_allow_html=True)
    st.markdown(
        "[Get your API key](https://openrouter.ai/keys)",
        unsafe_allow_html=True,
    )
    openrouter_api_key = st.text_input(
        "OpenRouter API Key", type="password", help="Get your API key from OpenRouter"
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
