import streamlit as st
from agents import run_research
import os

# Set up page configuration
st.set_page_config(page_title="🔍 Agentic Deep Researcher", layout="wide")

# Initialize session state variables
if "linkup_api_key" not in st.session_state:
    st.session_state.linkup_api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

def reset_chat():
    st.session_state.messages = []

# Sidebar: Linkup Configuration with updated logo link
with st.sidebar:
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("")
        st.image(
            "https://avatars.githubusercontent.com/u/175112039?s=200&v=4", width=65)
    with col2:
        st.header("Linkup Configuration")
        st.write("Deep Web Search")

    st.markdown("[Get your API key](https://app.linkup.so/sign-up)",
                unsafe_allow_html=True)

    linkup_api_key = st.text_input(
        "Enter your Linkup API Key", type="password")
    if linkup_api_key:
        st.session_state.linkup_api_key = linkup_api_key
        # Update the environment variable
        os.environ["LINKUP_API_KEY"] = linkup_api_key
        st.success("API Key stored successfully!")

# Main Chat Interface Header with powered by logos from original code links
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown("<h2 style='color: #0066cc;'>🔍 Agentic Deep Researcher</h2>",
                unsafe_allow_html=True)
    powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://cdn.prod.website-files.com/66cf2bfc3ed15b02da0ca770/66d07240057721394308addd_Logo%20(1).svg" width="80"> 
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://framerusercontent.com/images/wLLGrlJoyqYr9WvgZwzlw91A8U.png?scale-down-to=512" width="100">
    </div>
    """
    st.markdown(powered_by_html, unsafe_allow_html=True)
with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Add spacing between header and chat history
st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input and process the research query
if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.linkup_api_key:
        response = "Please enter your Linkup API Key in the sidebar."
    else:
        with st.spinner("Researching... This may take a moment..."):
            try:
                result = run_research(prompt)
                response = result
            except Exception as e:
                response = f"An error occurred: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
