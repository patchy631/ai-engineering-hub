import os
import streamlit as st
import asyncio
from typing import List, Dict
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI
from router_output_agent_workflow import RouterOutputAgentWorkflow
import openai

# Set page title and layout
st.set_page_config(
    page_title="LlamaIndex Agent",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Define some example tools
def search_documents(query: str) -> str:
    """
    Search for information in a document database.
    
    Args:
        query: Search query to find relevant information
        
    Returns:
        Search results as a string
    """
    # This is a mock implementation
    return f"Found results for '{query}': Sample document containing information about {query}."

def calculate(expression: str) -> str:
    """
    Calculate the result of a mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate
        
    Returns:
        Result of the calculation
    """
    try:
        result = eval(expression)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"

def current_weather(location: str) -> str:
    """
    Get the current weather for a location.
    
    Args:
        location: City or location to check weather
        
    Returns:
        Current weather information
    """
    # This is a mock implementation
    return f"The current weather in {location} is 72°F and sunny."

# Create function tools
tools = [
    FunctionTool.from_defaults(fn=search_documents),
    FunctionTool.from_defaults(fn=calculate),
    FunctionTool.from_defaults(fn=current_weather),
]

# Define the async function to run the workflow
async def run_workflow(workflow, message):
    try:
        response = await workflow.run(message=message)
        return response
    except Exception as e:
        import traceback
        error_msg = f"Error: {str(e)}\n\nDetails: {traceback.format_exc()}"
        print(error_msg)
        return f"⚠️ I encountered a problem: {str(e)}. Please try again in a moment or ask a different question."

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "workflow" not in st.session_state:
    # Set API key directly
    api_key = "KEEP YOUR API KEY HERE"
    
    # Set the API key globally for OpenAI
    os.environ["OPENAI_API_KEY"] = api_key
    openai.api_key = api_key
    
    # Initialize the LLM with the API key explicitly provided
    llm = OpenAI(
        model="gpt-3.5-turbo-0125", 
        temperature=0,
        api_key=api_key
    )
    
    # Initialize the workflow
    st.session_state.workflow = RouterOutputAgentWorkflow(
        tools=tools,
        llm=llm,
        verbose=True,
        timeout=60.0,  # Increase timeout
    )

# App title
st.title("🦙 LlamaIndex Agent Chat")

# Sidebar with information and settings
with st.sidebar:
    st.header("About")
    st.markdown(
        """
        This application demonstrates a LlamaIndex agent workflow with tool use capabilities. 
        
        The agent can use the following tools:
        - **Search Documents**: Find information in a document database
        - **Calculate**: Evaluate mathematical expressions
        - **Current Weather**: Get weather information for a location
        
        Try asking questions that might use these tools!
        """
    )
    
    # API Key input
    api_key = st.text_input("OpenAI API Key", type="password")
    if api_key:
        # Update the API key when entered by the user
        os.environ["OPENAI_API_KEY"] = api_key
        openai.api_key = api_key
        
        # If workflow exists, update its LLM with the new API key
        if "workflow" in st.session_state:
            llm = OpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=api_key)
            st.session_state.workflow.llm = llm
            st.success("API key updated!")
    
    # Initialize the workflow if API key is provided but workflow doesn't exist
    if api_key and "workflow" not in st.session_state:
        llm = OpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=api_key)
        st.session_state.workflow = RouterOutputAgentWorkflow(
            tools=tools,
            llm=llm,
            verbose=True,
            timeout=60.0,
        )
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        if "workflow" in st.session_state:
            st.session_state.workflow.reset()
        st.rerun()

# Display chat messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input for new message
user_input = st.chat_input("Ask something...")

# Check if workflow exists before processing user input
if user_input:
    if "workflow" not in st.session_state:
        st.error("Please enter your OpenAI API key in the sidebar first!")
    else:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display assistant response with spinner
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run the workflow to get a response
                response = asyncio.run(run_workflow(st.session_state.workflow, user_input))
                st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
