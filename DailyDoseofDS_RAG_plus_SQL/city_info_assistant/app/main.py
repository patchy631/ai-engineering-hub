import streamlit as st
import asyncio
import nest_asyncio
from core.workflow import create_workflow, run_workflow
from app.ui.components import (
    init_session_state, 
    display_chat_history, 
    display_debug_info, 
    display_available_cities,
    display_previous_chat
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

def main():
    st.set_page_config(
        page_title="City Information Assistant",
        page_icon="🏙️",
        layout="wide"
    )
    
    init_session_state()
    
    # Initialize event loop if not exists
    if "loop" not in st.session_state:
        st.session_state.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(st.session_state.loop)
    
    # Sidebar
    display_available_cities()
    display_debug_info()
    
    # Main content
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.markdown("<h1 style='font-size: 2.5em; margin: 0; padding: 0;'>🏙️</h1>", unsafe_allow_html=True)
    with col2:
        st.title("City Information Assistant")
    
    st.markdown("""
    This application can answer questions about various US cities using both structured data (population, state) 
    and unstructured data (general information from Wikipedia).
    """)
    
    # Initialize workflow if not exists
    if not st.session_state.workflow:
        st.session_state.workflow = create_workflow()
    
    # User input
    user_question = st.text_input(
        "Ask a question about the cities:",
        placeholder="e.g., What is the historical name of Los Angeles?"
    )
    
    if user_question:
        try:
            # Process question using the existing event loop
            with st.spinner("Processing your question..."):
                result = st.session_state.loop.run_until_complete(
                    run_workflow(st.session_state.workflow, user_question)
                )
                
                # Update chat history
                st.session_state.chat_history.append(f"Q: {user_question}")
                st.session_state.chat_history.append(f"A: {result}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    
    # Display current chat
    display_chat_history()
    
    # Display previous chat history
    display_previous_chat()

if __name__ == "__main__":
    main() 