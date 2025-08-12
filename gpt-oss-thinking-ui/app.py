import re
import base64
import streamlit as st
from ollama import chat

# Set Streamlit page configuration (optional)
st.set_page_config(page_title="Ollama Streaming Chat", layout="centered")

def process_thinking_stream(stream):
    """Process streaming response with native thinking support."""
    thinking_content = ""
    response_content = ""
    
    with st.status("Thinking...", expanded=True) as status:
        for chunk in stream:
            # Handle thinking content
            if chunk["message"].get("thinking"):
                thinking_content += chunk["message"]["thinking"]
            
            # Handle response content
            if chunk["message"].get("content"):
                response_content += chunk["message"]["content"]
        
        # Update status when done
        if thinking_content:
            status.update(label="Thinking complete!", state="complete", expanded=False)
    
    return thinking_content, response_content

def display_message(message):
    """Display a single message in the chat interface."""
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        if role == "assistant":
            thinking_content = message.get("thinking")
            display_assistant_message(message["content"], thinking_content)
        else:
            st.markdown(message["content"])

def display_assistant_message(content, thinking_content=None):
    """Display assistant message with thinking content if present."""
    # Display thinking content in expander if present
    if thinking_content and thinking_content.strip():
        with st.expander("🧠 Thinking process", expanded=False):
            st.markdown(thinking_content)
    
    # Display response content in the main chat area
    if content:
        st.markdown(content)

def display_chat_history():
    """Display all previous messages in the chat history."""
    for message in st.session_state["messages"]:
        if message["role"] != "system":  # Skip system messages
            display_message(message)

# Remove this function as it's replaced by process_thinking_stream

# Remove this function as it's replaced by process_thinking_stream

@st.cache_resource
def get_chat_model():
    """Get a cached instance of the chat model."""
    return lambda messages: chat(
        model="gpt-oss:20b",
        messages=messages,
        stream=True,
        think=True,
    )

def handle_user_input():
    """Handle new user input and generate assistant response."""
    if user_input := st.chat_input("Type your message here..."):
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            chat_model = get_chat_model()
            stream = chat_model(st.session_state["messages"])
            
            thinking_content, response_content = process_thinking_stream(stream)
            
            # Display response using the same function as historical messages
            display_assistant_message(response_content, thinking_content)
            
            # Save the complete response
            st.session_state["messages"].append(
                {"role": "assistant", "content": response_content, "thinking": thinking_content}
            )

def main():
    """Main function to handle the chat interface and streaming responses."""
    # Load and encode logos
    openai_logo = base64.b64encode(open("assets/openai.png", "rb").read()).decode()
    ollama_logo = base64.b64encode(open("assets/ollama.png", "rb").read()).decode()
    
    st.markdown(f"""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='margin-bottom: 1rem;'>
            <img src="data:image/png;base64,{openai_logo}" width="40" style="vertical-align: middle; margin-right: 10px;">
            GPT-OSS Chat
            <img src="data:image/png;base64,{ollama_logo}" width="40" style="vertical-align: middle; margin-left: 10px;">
        </h1>
        <h4 style='color: #666; margin-top: 0;'>With thinking UI! 💡</h4>
    </div>
    """, unsafe_allow_html=True)
    
    display_chat_history()
    handle_user_input()

if __name__ == "__main__":
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
    main()