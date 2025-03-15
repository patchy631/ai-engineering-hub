import os

import gc
import tempfile
import uuid
import pandas as pd

from gitingest import ingest

from llama_index.core import Settings
from llama_index.core import PromptTemplate
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import MarkdownNodeParser

import streamlit as st

from dotenv import load_dotenv

load_dotenv()

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
client = None

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def process_with_gitingets(github_url):
    # or from URL
    summary, tree, content = ingest(github_url)
    return summary, tree, content


with st.sidebar:
    st.header(f"Add your GitHub repository!")
    
    github_url = st.text_input("Enter GitHub repository URL", placeholder="GitHub URL")
    load_repo = st.button("Load Repository")

    if github_url and load_repo:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                st.write("Processing your repository...")
                repo_name = github_url.split('/')[-1]
                file_key = f"{session_id}-{repo_name}"
                
                if file_key not in st.session_state.get('file_cache', {}):

                    if os.path.exists(temp_dir):
                        summary, tree, content = process_with_gitingets(github_url)

                        # Write summary to a markdown file in temp directory
                        content_path = os.path.join(temp_dir, f"{repo_name}_content.md")
                        with open(content_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        loader = SimpleDirectoryReader(
                            input_dir=temp_dir,
                        )
                    else:    
                        st.error('Could not find the file you uploaded, please check again...')
                        st.stop()
                    
                    docs = loader.load_data()
                    node_parser = MarkdownNodeParser()
                    index = VectorStoreIndex.from_documents(documents=docs, transformations=[node_parser], show_progress=True)

                    # Create the query engine, where we use a cohere reranker on the fetched node
                    query_engine = index.as_query_engine(streaming=True)

                    # ====== Customise prompt template ======
                    qa_prompt_tmpl_str = """
                    You are an AI assistant specialized in analyzing GitHub repositories.

                    Repository structure:
                    {tree}
                    ---------------------

                    Context information from the repository:
                    {context_str}
                    ---------------------

                    Given the repository structure and context above, provide a clear and precise answer to the query. 
                    Focus on the repository's content, code structure, and implementation details. 
                    If the information is not available in the context, respond with 'I don't have enough information about that aspect of the repository.'

                    Query: {query_str}
                    Answer: """
                    qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

                    query_engine.update_prompts(
                        {"response_synthesizer:text_qa_template": qa_prompt_tmpl}
                    )
                    
                    st.session_state.file_cache[file_key] = query_engine
                else:
                    query_engine = st.session_state.file_cache[file_key]

                # Inform the user that the file is processed and Display the PDF uploaded
                st.success("Ready to Chat!")
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    st.header(f"Chat with GitHub using RAG </>")

with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What's up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Get the repo name from the GitHub URL
            repo_name = github_url.split('/')[-1]
            file_key = f"{session_id}-{repo_name}"
            
            # Get query engine from session state
            query_engine = st.session_state.file_cache.get(file_key)
            
            if query_engine is None:
                st.error("Please load a repository first!")
                st.stop()
                
            # Use the query engine
            response = query_engine.query(prompt)
            
            # Handle streaming response
            if hasattr(response, 'response_gen'):
                for chunk in response.response_gen:
                    if isinstance(chunk, str):  # Only process string chunks
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
            else:
                # Handle non-streaming response
                full_response = str(response)
                message_placeholder.markdown(full_response)

            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"An error occurred while processing your query: {str(e)}")
            full_response = "Sorry, I encountered an error while processing your request."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})