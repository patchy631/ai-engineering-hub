import streamlit as st
import asyncio
import nest_asyncio
from agent import RouterOutputAgentWorkflow, llama_cloud_tool, create_sql_database

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Initialize session state variables
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Recreate SQL tool and workflow on each session initialization
    sql_tool = create_sql_database()
    if "workflow" not in st.session_state:
        st.session_state.workflow = RouterOutputAgentWorkflow(
            tools=[sql_tool, llama_cloud_tool],
            verbose=True,
            timeout=120
        )

# Helper function to run async code
async def process_message(message: str) -> str:
    # Recreate SQL tool and workflow for each message
    sql_tool = create_sql_database()
    workflow = RouterOutputAgentWorkflow(
        tools=[sql_tool, llama_cloud_tool],
        verbose=True,
        timeout=120
    )
    # Copy over existing chat history
    workflow.chat_history = st.session_state.workflow.chat_history
    return await workflow.run(message=message)

def main():
    st.title("City Information Chatbot")
    
    # Initialize session state
    init_session_state()

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask me about US cities..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run async code in the current event loop
                result = asyncio.run(process_message(prompt))
                st.markdown(result)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": result})

    # Add a reset button
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.workflow.reset()
        st.rerun()

if __name__ == "__main__":
    main()