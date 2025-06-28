import os
import streamlit as st
import asyncio
from dotenv import load_dotenv
from workflow import wf  # Import RAG workflow

# Load environment variables
load_dotenv()

def get_env_var(name, default=""):
    return os.getenv(name, default)

# Sidebar configuration with improved header and description
st.sidebar.header("🔧 Configuration")
st.sidebar.markdown("Enter your API keys and project settings below to enable the chatbot.")
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
st.sidebar.text("Afiz's Demo ⚡️")

# Improved title and description
st.title("🏙️ City Explorer Agent")
st.markdown(
    """
    Combining RAG and Text-to-SQL in a unified query interface powered by LlamaIndex Workflows.
    """
)

# Sample Questions section with clickable buttons
st.markdown("### Try a Sample Question")
col1, col2 = st.columns(2)
with col1:
    if st.button("Which city has the highest population?", key="sample1"):
        st.session_state.sample_question = "How do people in Chicago get around?"
with col2:
    if st.button("What state is Houston located in?", key="sample2"):
        st.session_state.sample_question = "What state is Houston located in?"
col3, col4 = st.columns(2)
with col3:
    if st.button("Where is the Space Needle located?", key="sample3"):
        st.session_state.sample_question = "Where is the Space Needle located?"
with col4:
    if st.button("List all of the places to visit in Miami.", key="sample4"):
        st.session_state.sample_question = "List all of the places to visit in Miami."

# Chat UI
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Determine prompt: prioritize chat input, then sample question if no input provided
user_input = st.chat_input("Ask a question...")
prompt = None
if user_input:
    prompt = user_input
elif st.session_state.get("sample_question"):
    prompt = st.session_state.sample_question
    st.session_state.sample_question = None

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
