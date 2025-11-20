import fitz  # PyMuPDF for PDF extraction
import docx  # python-docx for Word extraction
import os
import uuid
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import base64
import gc
import asyncio
import time
from llama_index.readers.file.docs.base import DocxReader, HWPReader, PDFReader
from rag_code import StructuredDataSQLHandler, OllamaLLM,EmbedData, QdrantVectoreDBHandler, Tool
from llama_index.llms.sambanovasystems import SambaNovaCloud
from IPython.display import Markdown, display
from workflow import RouterOutputAgentWorkflow, StartEvent, StopEvent, Workflow
import io
import streamlit as st
from contextlib import redirect_stdout
from llama_index.core import Settings
from llama_index.core.schema import Document  

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Advance Agentic RAG + Text-to-SQL Demo", layout="wide")

# Initialize session state variables efficiently
st.session_state.setdefault("id", uuid.uuid4())
st.session_state.setdefault("file_cache", {})
st.session_state.setdefault("messages", [])  # Store chat history
st.session_state.setdefault("workflow", None)
st.session_state.setdefault("workflow_logs", [])


session_id = st.session_state.id

def reset_chat():
    st.session_state.messages = []
    gc.collect()

def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    # Embedding PDF in HTML
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

def initialize_workflow(documents, dataframe, llm_name, collection_name):
    with st.spinner("Loading documents and initializing the workflow..."):
        documents = [Document(text=documents)]  # Explicitly set 'text' parameter

        qdrant_vdb = QdrantVectoreDBHandler(collection_name="testing_mayank")
        qdrant_vdb.define_client()
        qdrant_vdb.ingest_data(documents=documents)

        vectorIndexTool = Tool(
            name="vectorIndexTool",
            description="A tool to do semantic search on AI Market News Information. The document uploaded contains more market news regarding AI Market Growth Surpasses Expectations, NVIDIA's AI Dominance Continues, Investment in AI Startups Hits New High, AI in Healthcare Revolutionizing Medical Diagnosis. Call it to get more context of user question. argument required = query ",
            tool_id="vector_index_001",
            execute_fn= qdrant_vdb.query_data #lambda query: asyncio.run(qdrant_vdb.query_data.acall(query=query))  # Ensures proper execution
        )
        data = dataframe
        # Convert to DataFrame
        df = pd.DataFrame(data)
        # Initialize DB and insert data
        db = StructuredDataSQLHandler()
        db.create_table(df)
        db.insert_data(df)
        text_to_sql_tool = Tool(
            name="text_to_sql_tool",
            description="A tool to query the structured document provided by the user. Call it to get understanding of comparative analysis of various Large Language Models (LLMs) based on key performance metrics like BLEU, ROUGE, Perplexity, Accuracy, Latencys. Argument required = user_question ",
            tool_id="text_to_sql_001",
            execute_fn= db.sql_tool 
        )       
        # **Initialize the chatbot tool**
        chatbot_instance = OllamaLLM()  # Assuming CustomChatbot has `chatbot_tool` method
        chatbotTool = Tool(
            name="chatbotTool",
            description="A conversational AI assistant to answer general user questions.",
            tool_id="chatbot_tool_001",
            execute_fn=chatbot_instance.chatbot_tool  # Pass the function reference
        )

        # Initialize RouterOutputAgentWorkflow with both tools
        workflow = RouterOutputAgentWorkflow(
            tools=[text_to_sql_tool, vectorIndexTool],  # Include both tools
            llm=OllamaLLM(),  # Pass an LLM instance
            timeout=60,
            verbose=True
        )

        # Store workflow in session state (only if using Streamlit)
        st.session_state.workflow = workflow
        return workflow

# Function to run the async workflow
async def run_workflow(query):
    # Ensure the workflow is initialized
    if "workflow" not in st.session_state or st.session_state.workflow is None:
        st.error("Error: Workflow is not initialized! Please upload the documents and try again.")
        return None
    # Ensure workflow_logs exists
    if "workflow_logs" not in st.session_state:
        st.session_state.workflow_logs = []

    # Capture stdout to get workflow logs
    f = io.StringIO()
    with redirect_stdout(f):
        try:
            result = await st.session_state.workflow.run(message=query)
        except Exception as e:
            st.error(f"Workflow execution failed: {e}")
            return None
    
    # Get the captured logs and store them
    logs = f.getvalue()
    if logs:
        st.session_state.workflow_logs.append(logs)
    
    return result

with st.sidebar:
    st.header("Upload Your Investment Documents")
    
    # Allow multiple file uploads
    uploaded_files = st.file_uploader(
        "Upload PDF, Word, Text, Excel, or CSV files", 
        type=["pdf", "docx", "txt", "xlsx", "csv"], 
        accept_multiple_files=True
    )
    
    # Process multiple uploaded files
    if uploaded_files:
      try:
          session_id = str(uuid.uuid4())  # Ensure session ID exists
          collection_name = f"Mayank_project_file_data_collection_{session_id}"
          llm_name = "Meta-Llama-3.1-405B-Instruct"
          uploaded_dataframe = None
          uploaded_documents = None
          st.write(f"Indexing your document...")

          for uploaded_file in uploaded_files:
              file_name = uploaded_file.name
              file_type = file_name.split(".")[-1]
              
              if file_type in ["pdf", "docx", "txt"]:

                  # Read file into memory
                  # Convert buffer to BytesIO
                  file_bytes = io.BytesIO(uploaded_file.getvalue())
                  text = ""
                  pdf_document = fitz.open(stream=file_bytes, filetype="pdf")
                  for page in pdf_document:
                      text += page.get_text()
                  uploaded_documents = text
                  if not uploaded_documents:
                      raise ValueError("No text extracted from the file!")

              elif file_type in ["xlsx", "csv"]:
                
                  df = pd.read_csv(uploaded_file) if file_type == "csv" else pd.read_excel(uploaded_file)
                  st.dataframe(df.head())
                  uploaded_dataframe = df

              # Generate a unique file key
              file_key = f"{session_id}-{file_name}"

              # Initialize workflow if the file is not cached
              if file_key not in st.session_state.get('file_cache', {}):
                  workflow = initialize_workflow(documents=uploaded_documents, dataframe=uploaded_dataframe, llm_name=llm_name, collection_name=collection_name)
                  st.session_state.file_cache[file_key] = workflow
              else:
                  st.session_state.workflow = st.session_state.file_cache[file_key]

              # Display the PDF file if applicable
              if file_type in ["pdf", "docx", "txt"]:
                  st.success(" Ready to Chat!")
                  display_pdf(uploaded_file)

      except Exception as e:
          st.error(f"An error occurred: {e}")
          st.stop()      
           

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    
    # Chatbot Interface - Stock Market Analysis
    st.markdown(
        "<h1 style='text-align: center;'>🚀 Agentic Multi-Modal RAG with Dynamic Tool Selection</h1>", 
        unsafe_allow_html=True
    )

    st.markdown(
        "<h3 style='text-align: center;'>🤖 An Intelligent System Talking To Structured & Unstructured Data</h3>", 
        unsafe_allow_html=True
    )


with col2:
    st.button("Clear ↺", on_click=reset_chat)

# Display chat messages from history on app rerun
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Display logs AFTER the user message but BEFORE the next assistant message
    if message["role"] == "user" and "log_index" in message and i < len(st.session_state.messages) - 1:
        log_index = message["log_index"]
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("📜 View Workflow Execution Logs", expanded=False):
                st.code(st.session_state.workflow_logs[log_index], language="text")

# Accept user input
if prompt := st.chat_input("💬 Ask a question about your documents..."):
    log_index = len(st.session_state.workflow_logs)
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": prompt, "log_index": log_index})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    if not st.session_state.workflow:
        st.warning("⚠️ Please upload a document first to initialize the workflow.")
    else:
        # Run workflow
        result = asyncio.run(run_workflow(prompt))
        print("Result:", result)

        # Display workflow logs (before assistant's response)
        if log_index < len(st.session_state.workflow_logs):
            with st.expander("📜 View Workflow Execution Logs", expanded=False):
                st.code(st.session_state.workflow_logs[log_index], language="text")

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # Stream response word by word
                for word in result.split():
                    full_response += word + " "
                    message_placeholder.markdown(full_response + "▌")
                    time.sleep(0.1)  # Simulating typing effect
            except Exception as e:
              full_response = "Sorry! I don't know the answer."
            # Display final response
            message_placeholder.markdown(full_response)

        # Store assistant response
        st.session_state.messages.append({"role": "assistant", "content": full_response})
