import streamlit as st
import asyncio
from hybrid_rag import setup_hybrid_rag, query_hybrid_rag
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for required API keys
required_env_vars = [
    "GROQ_API_KEY",
    "LLAMA_CLOUD_API_KEY",
    "LLAMA_CLOUD_INDEX_NAME",
    "LLAMA_CLOUD_PROJECT_NAME",
    "LLAMA_CLOUD_ORG_ID",
]
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
missing_vars = [var for var in required_env_vars if not os.getenv(var)]

# Set page config
st.set_page_config(page_title="Hybrid RAG System", page_icon="🔍", layout="wide")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown(
        "<h1 style='font-size: 32px;'>Hybrid RAG System powered by</h1>",
        unsafe_allow_html=True,
    )
with col2:
    st.image(
        "/Users/sanatwalia/Desktop/Technical_Writer/assignment1/ai-engineering-hub/SQL_ROUTER/assets/groq_logo.png",
        width=120,
    )
    st.image(
        "/Users/sanatwalia/Desktop/Technical_Writer/assignment1/ai-engineering-hub/SQL_ROUTER/assets/llamacloud_logo.png",
        width=120,
    )


# Header
st.title("Hybrid RAG System: SQL + Document Retrieval")
st.markdown(
    """
This application combines SQL-based structured data queries with document retrieval to answer 
questions about US cities. Ask questions about city populations, states, or other information 
about New York City, Los Angeles, Chicago, Houston, Miami, or Seattle.
"""
)

# Setup instructions if needed
if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.markdown(
        """
    ## Setup Instructions
    
    1. Create a `.env` file in the same directory as this app with the following variables:
    ```
    GROQ_API_KEY=your_groq_api_key
    LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
    LLAMA_CLOUD_INDEX_NAME=your_index_name
    LLAMA_CLOUD_PROJECT_NAME=your_project_name
    LLAMA_CLOUD_ORG_ID=your_organization_id
    ```
    
    2. Make sure you've uploaded the city Wikipedia PDFs to your LlamaCloud index.
    3. Restart the application.
    """
    )
    st.stop()

# Initialize session state for chat history and workflow
if "messages" not in st.session_state:
    st.session_state.messages = []


async def initialize_workflow():
    try:
        with st.spinner("Setting up the hybrid RAG system..."):
            return await setup_hybrid_rag()
    except Exception as e:
        st.error(f"Error initializing the system: {str(e)}")
        return None


if "workflow" not in st.session_state:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    st.session_state.workflow = loop.run_until_complete(initialize_workflow())

if not st.session_state.workflow:
    st.stop()


# Function to handle async queries properly in Streamlit
async def get_response(query):
    try:
        return await query_hybrid_rag(st.session_state.workflow, query)
    except Exception as e:
        st.error(f"Error during query: {str(e)}")
        return "An error occurred while processing your query."


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Query input
query = st.chat_input("Ask a question about the cities...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})

    # Display user message
    with st.chat_message("user"):
        st.markdown(query)

    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = asyncio.run(get_response(query))
            st.markdown(result)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": result})

# Sidebar with example queries
with st.sidebar:
    st.header("Example Queries")
    example_queries = [
        "Which city has the highest population?",
        "What state is Houston located in?",
        "Where is the Space Needle located?",
        "List all of the places to visit in Miami.",
        "How do people in Chicago get around?",
        "What is the historical name of Los Angeles?",
    ]

    for example in example_queries:
        if st.button(example):
            st.session_state.messages.append({"role": "user", "content": example})
            with st.chat_message("user"):
                st.markdown(example)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    result = asyncio.run(get_response(example))
                    st.markdown(result)

            st.session_state.messages.append({"role": "assistant", "content": result})
            st.rerun()

    st.divider()
    st.markdown(
        """
    ### Required Environment Variables
    - `GROQ_API_KEY`: API key for Groq  
    - `LLAMA_CLOUD_API_KEY`: API key for LlamaCloud  
    - `LLAMA_CLOUD_INDEX_NAME`: Name of your LlamaCloud index  
    - `LLAMA_CLOUD_PROJECT_NAME`: Name of your LlamaCloud project  
    - `LLAMA_CLOUD_ORG_ID`: Your LlamaCloud organization ID  
    """
    )

    st.divider()
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        if "workflow" in st.session_state and st.session_state.workflow:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            st.session_state.workflow = loop.run_until_complete(initialize_workflow())
        st.rerun()
