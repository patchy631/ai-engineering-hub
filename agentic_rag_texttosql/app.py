import streamlit as st
import uuid
import asyncio
import gc
from rag import process_query  # Import your query handling function

st.title("🧠 RAG + Text-to-SQL Interface")

# Session state initialization
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.messages = []  # List to hold chat history

# Reset chat function
def reset_chat():
    st.session_state.messages = []
    gc.collect()

# Sidebar for resetting the chat
with st.sidebar:
    st.header("Chat with the Assistant!")
    reset_button = st.button("Reset Chat", on_click=reset_chat)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asynchronously call backend to get assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Define an async function to process the query
        async def handle_query():
            try:
                # Fetch the response asynchronously
                response = await process_query(prompt)
                # Update the message placeholder with the response
                message_placeholder.markdown(response)
                # Return the response to be appended to the session history
                return response
            except Exception as e:
                message_placeholder.markdown(f"Error: {e}")
                return f"Error: {e}"

        # Run the async query processing task
        full_response = asyncio.run(handle_query())

        # Add the assistant's response to chat history after it's received
        st.session_state.messages.append({"role": "assistant", "content": full_response})
