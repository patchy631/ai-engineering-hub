"""
Chat UI Component for RAG-SQL Assistant

This module provides the Streamlit UI components for the chat interface,
including message history management, user input handling, and response rendering.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable
import uuid

def initialize_chat_state():
    """Initialize the chat state in the Streamlit session if it doesn't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_id" not in st.session_state:
        st.session_state.chat_id = str(uuid.uuid4())

def reset_chat():
    """Reset the chat by clearing message history."""
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())

def display_chat_history():
    """Display all messages in the chat history."""
    for message in st.session_state.messages:
        display_message(message)

def display_message(message: Dict[str, Any]):
    """
    Display a single chat message with appropriate styling.
    
    Args:
        message: Message dictionary containing role and content
    """
    role = message["role"]
    content = message["content"]
    
    # Use Streamlit's native chat_message component
    with st.chat_message(role):
        st.markdown(content)

def add_user_message(message: str):
    """
    Add a user message to the chat history.
    
    Args:
        message: The user's message content
    """
    st.session_state.messages.append({"role": "user", "content": message})

def add_assistant_message(message: str):
    """
    Add an assistant message to the chat history.
    
    Args:
        message: The assistant's message content
    """
    assistant_message = {"role": "assistant", "content": message}
    st.session_state.messages.append(assistant_message)

def chat_input_area(on_submit: Callable[[str], None]):
    """
    Render the chat input area and handle user input.
    
    Args:
        on_submit: Callback function to execute when user submits a query
    """
    # Use Streamlit's chat input
    if prompt := st.chat_input("Ask a question about the data..."):
        add_user_message(prompt)
        on_submit(prompt)
