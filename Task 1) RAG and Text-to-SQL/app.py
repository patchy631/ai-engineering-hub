import streamlit as st
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from query_router import setup_database, create_query_engines, create_workflow, process_query
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

nest_asyncio.apply()
# Title of the Streamlit app
st.title("Advanced RAG: Combining RAG and Text-to-SQL")

# Instructions
st.markdown("The chatbot uses a custom agent workflow that can perform both SQL and semantic queries according to the needs of the user from a single interface.")

# Set up the in-memory SQL database
engine = setup_database()

# Retrieve API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
llama_cloud_api_key = os.getenv("LLAMA_CLOUD_API_KEY")

# Check if API keys are provided
if not openai_api_key or not llama_cloud_api_key:
    st.error("Please set OPENAI_API_KEY and LLAMA_CLOUD_API_KEY in your .env file.")
    st.stop()

# Configuration for LlamaCloud (from .env file)
LLAMA_CLOUD_INDEX_NAME = os.getenv("LLAMA_CLOUD_INDEX_NAME")
LLAMA_CLOUD_PROJECT_NAME = os.getenv("LLAMA_CLOUD_PROJECT_NAME")
LLAMA_CLOUD_ORG_ID = os.getenv("LLAMA_CLOUD_ORG_ID")

# Create query engines
sql_tool, llama_cloud_tool = create_query_engines(
    engine=engine,
    llama_cloud_api_key=llama_cloud_api_key,
    llama_cloud_index_name=LLAMA_CLOUD_INDEX_NAME,
    llama_cloud_project_name=LLAMA_CLOUD_PROJECT_NAME,
    llama_cloud_org_id=LLAMA_CLOUD_ORG_ID
)

# Initialize the LLM
llm = OpenAI(temperature=0, model="gpt-3.5-turbo", api_key=openai_api_key)

# Initialize the workflow in session state to persist across reruns
if "workflow" not in st.session_state:
    st.session_state.workflow = create_workflow(
        tools=[sql_tool, llama_cloud_tool],
        llm=llm,
        verbose=False  # Set to True for debugging
    )

workflow = st.session_state.workflow

# Initialize display messages in session state
if "display_messages" not in st.session_state:
    st.session_state.display_messages = []

# Display chat history
st.subheader("Conversation History")
for msg in st.session_state.display_messages:
    role = msg["role"].capitalize()
    content = msg["content"]
    st.markdown(f"**{role}:** {content}")

# User input section
st.subheader("Ask a Question")
query = st.text_input("Enter your question:", key="query_input")

# Submit button
if st.button("Submit"):
    if query:
        # Add user's message to display
        st.session_state.display_messages.append({"role": "user", "content": query})
        
        # Process the query 
        with st.spinner("Processing your query..."):
            result = asyncio.run(process_query(workflow, query))
        
        # Add assistant's response to display
        st.session_state.display_messages.append({"role": "assistant", "content": result})
        
        # Rerun to update the display
        st.rerun()
    else:
        st.warning("Please enter a question.")

# Reset button
if st.button("Reset Conversation"):
    st.session_state.display_messages = []
    workflow.reset()
    st.success("Conversation has been reset.")
    st.rerun()

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and LlamaIndex. Data includes an in-memory SQL database and LlamaCloud index.")