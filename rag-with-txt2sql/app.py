import os
import streamlit as st
import asyncio
from dotenv import load_dotenv
from rag import wf  # Import RAG workflow

# Load environment variables
load_dotenv()


def get_env_var(name, default=""):
    return os.getenv(name, default)


# Sidebar for environment variables
st.sidebar.header("🔧 Configuration")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key", get_env_var("OPENAI_API_KEY"), type="password"
)
llama_index_api_key = st.sidebar.text_input(
    "LlamaIndex API Key", get_env_var("LLAMA_INDEX_API_KEY"), type="password"
)
llama_index_name = st.sidebar.text_input(
    "LlamaIndex Name", get_env_var("LLAMA_INDEX_NAME")
)
llama_index_project_name = st.sidebar.text_input(
    "LlamaIndex Project Name", get_env_var("LLAMA_INDEX_PROJECT_NAME")
)
llama_index_organization_id = st.sidebar.text_input(
    "LlamaIndex Organization ID", get_env_var("LLAMA_INDEX_ORGANIZATION_ID")
)


def save_env():
    os.environ["OPENAI_API_KEY"] = openai_api_key
    os.environ["LLAMA_INDEX_API_KEY"] = llama_index_api_key
    os.environ["LLAMA_INDEX_NAME"] = llama_index_name
    os.environ["LLAMA_INDEX_PROJECT_NAME"] = llama_index_project_name
    os.environ["LLAMA_INDEX_ORGANIZATION_ID"] = llama_index_organization_id


st.sidebar.button("Save Config", on_click=save_env)

# Title
st.title("🧠  City Knowledge Chatbot")
st.markdown(
    "Interact with your Retrieval-Augmented Generation (RAG) pipeline using LlamaIndex and OpenAI. To ask questions about - New York City, Los Angeles, Chicago, Miami, or Seattle."
)

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a question...")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call RAG workflow asynchronously
    async def get_response():
        return await wf.run(message=prompt)

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    response = loop.run_until_complete(get_response())

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
