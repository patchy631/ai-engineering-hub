import streamlit as st
import nest_asyncio
import asyncio
from opik import track
from app import RouterOutputAgentWorkflow
from db_init import create_sql_tool, create_llama_cloud_tool

sql_tool = create_sql_tool()
llama_cloud_tool = create_llama_cloud_tool()

st.title("RAG and Text-to-SQL")

user_query = st.text_input("Enter your question")

wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=300)

@track
async def async_query_execution(query):
    """Runs the async function properly within Streamlit."""
    response = await wf.run(message=query)
    return str(response)

if st.button("Get the answer"):
    with st.spinner("Processing your query..."):
        result = asyncio.run(async_query_execution(user_query))
        
        st.markdown(f" Answer: {result}")