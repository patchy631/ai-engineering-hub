import streamlit as st
import asyncio
from main import main
from sqlalchemy import create_engine
import os
import shutil

# Custom CSS to style the file uploader in the middle
st.markdown(
    """
    <style>
    /* Center the file uploader */
    .stFileUploader {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    /* Add some padding and border for better visibility */
    .upload-container {
        padding: 20px;
        border: 2px dashed #808080.;
        border-radius: 10px;
        background-color: #0000ff;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create 'data' directory if it does not exist
if not os.path.exists('data'):
    os.makedirs('data')

# Ensure 'data' directory is deleted after execution
def cleanup_data_directory():
    if os.path.exists('data'):
        shutil.rmtree('data')

# Register the cleanup function to be called on exit
import atexit
atexit.register(cleanup_data_directory)

def delete_all_files_in_directory(directory: str):
    """Delete all files in the specified directory."""
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

# Set up the Streamlit app
st.title("RAG and Text-to-SQL Query In Single Interface")
st.subheader("Powered by OpenAI and Llama Cloud")

# Create a custom container for the file uploader in the middle
with st.container():
    st.markdown("### Upload CSV File")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="mid_uploader")

    if uploaded_file is not None:
        # Save the uploaded file to the 'data' directory
        delete_all_files_in_directory('data')
        with open(f"data/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' saved to 'data' directory.")
        if 'engine' in st.session_state:
            st.session_state['engine'].dispose()
        engine = create_engine("sqlite:///:memory:", future=True)
        st.session_state['engine'] = engine

# Accept user input
if prompt := st.chat_input("Ask Your Question Here"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process the input and display the result
    with st.spinner("Searching using Agent..."):
        sql_query = asyncio.run(main(prompt, st.session_state['engine']))
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.success("Here is the Output:")
        st.markdown(sql_query)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": sql_query})