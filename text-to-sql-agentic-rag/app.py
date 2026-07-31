import streamlit as st
import asyncio
import nest_asyncio
from db_setup import setup_db
from agent_tool_setup import setup_agent_tools
from agent_setup import (
    RouterOutputAgentWorkflow
)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Initialize the database only once
@st.cache_resource
def create_workflow():
    print("Creating workflow")
    engine = setup_db()
    tools = setup_agent_tools(engine)

    # Create the router agent workflow
    workflow = RouterOutputAgentWorkflow(
        tools=tools,
        verbose=True,
        timeout=120
    )

    return workflow

st.session_state['workflow'] = create_workflow() 

# Initialize session state for storing chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Initialize a flag to track processing state
if 'processing' not in st.session_state:
    st.session_state['processing'] = False

st.title("CityAssist – Ask, Explore, Discover")

# Display chat history with chat_message containers
for message in st.session_state['messages']:
    role = message["role"]
    content = message["content"]
    
    with st.chat_message(role):
        st.markdown(content)

# Create a form for input
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Enter your message:", key="user_input", height=150)
    submit_button = st.form_submit_button(label="Send")

    if submit_button and user_input:
        # Add user message to chat history
        st.session_state['messages'].append({"role": "user", "content": user_input})
        
        # Set processing flag
        st.session_state['processing'] = True
        
        # Force a rerun to update the UI with the new message
        st.rerun()

# Process response if needed (after form handling to avoid state conflicts)
if st.session_state.get('processing'):
    with st.spinner("Generating response..."):
        # Get response from workflow using the improved helper function
        workflow = st.session_state['workflow']
        async def get_workflow_response():
            return await workflow.run(message=st.session_state['messages'][-1]['content'])
        response = asyncio.run(get_workflow_response())

            # Add AI response to messages
        if hasattr(response, 'result'):
            st.session_state['messages'].append({"role": "assistant", "content": response.result})
        else:
            st.session_state['messages'].append({"role": "assistant", "content": str(response)})
        
        # Clear processing flag
        st.session_state['processing'] = False
        
        # Force a rerun to update the UI with the assistant's response
        st.rerun()