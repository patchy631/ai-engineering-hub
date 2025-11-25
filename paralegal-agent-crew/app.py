import nest_asyncio
nest_asyncio.apply()

import os
import asyncio
import streamlit as st
import base64
import gc
import tempfile
import uuid
import time
import io
import re
from contextlib import redirect_stdout
from pathlib import Path

from src.embeddings.embed_data import EmbedData
from src.indexing.milvus_vdb import MilvusVDB
from src.retrieval.retriever_rerank import Retriever
from src.generation.rag import RAG
from src.workflows.agent_workflow import ParalegalAgentWorkflow
from pypdf import PdfReader
from dotenv import load_dotenv
from config.settings import settings

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Paralegal AI Assistant", layout="wide")

# Initialize session state variables
if "id" not in st.session_state:
    st.session_state.id = str(uuid.uuid4())[:8]
    st.session_state.file_cache = {}
    
if "workflow" not in st.session_state:
    st.session_state.workflow = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "workflow_logs" not in st.session_state:
    st.session_state.workflow_logs = []
    
if "vector_db" not in st.session_state:
    st.session_state.vector_db = None

session_id = st.session_state.id

def reset_chat():
    """Reset chat history and clear memory."""
    st.session_state.messages = []
    st.session_state.workflow_logs = []
    gc.collect()

def display_pdf(file):
    """Display PDF preview in sidebar."""
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""
    
    st.markdown(pdf_display, unsafe_allow_html=True)

def render_logs(log_text: str):
    """Render logs with ANSI colors and emojis nicely in Streamlit"""
    from ansi2html import Ansi2HTMLConverter
    conv = Ansi2HTMLConverter(inline=True)
    html_body = conv.convert(log_text, full=False)

    st.markdown(
        f"""
        <div style="font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; white-space: pre-wrap; line-height: 1.45; font-size: 13px;">
        {html_body}
        </div>
        """,
        unsafe_allow_html=True,
    )

def load_and_split_pdf(file_path: str, chunk_size: int = 512, chunk_overlap: int = 50):
    try:
        reader = PdfReader(file_path)
        full_text_parts = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text:
                full_text_parts.append(text)
        full_text = "\n".join(full_text_parts)

        words = full_text.split()
        chunks = []
        i = 0
        step = max(1, chunk_size - chunk_overlap)
        while i < len(words):
            segment = words[i : i + chunk_size]
            chunks.append(" ".join(segment))
            i += step
        return [c for c in chunks if c.strip()]
    except Exception as e:
        st.error(f"Error loading PDF: {e}")
        return []

def initialize_workflow(file_path: str):
    with st.spinner("🔄 Loading document and setting up the workflow..."):
        try:
            # Step 1: Load and split document
            st.info("📄 Loading and processing PDF...")
            text_chunks = load_and_split_pdf(file_path)
            
            if not text_chunks:
                st.error("No text chunks extracted from PDF")
                return None
            
            st.success(f"✅ Created {len(text_chunks)} text chunks")
            
            # Step 2: Create embeddings
            st.info("🧠 Generating embeddings...")
            embed_data = EmbedData(
                embed_model_name=settings.embedding_model,
                batch_size=settings.batch_size
            )
            embed_data.embed(text_chunks)
            st.success("✅ Embeddings generated with binary quantization")
            
            # Step 3: Setup vector database
            st.info("🗄️ Setting up Milvus vector database...")
            collection_name = f"{settings.collection_name}_{session_id}"
            
            vector_db = MilvusVDB(
                collection_name=collection_name,
                vector_dim=settings.vector_dim,
                batch_size=settings.batch_size,
                db_file=f"{settings.milvus_db_path}_{session_id}.db"
            )
            
            vector_db.initialize_client()
            vector_db.create_collection()
            vector_db.ingest_data(embed_data)
            
            # Store in session state for cleanup
            st.session_state.vector_db = vector_db
            st.success("✅ Vector database setup completed")
            
            # Step 4: Setup retrieval
            st.info("🔍 Setting up retrieval system...")
            retriever = Retriever(
                vector_db=vector_db,
                embed_data=embed_data,
                top_k=settings.top_k
            )
            st.success("✅ Retrieval system ready")
            
            # Step 5: Setup RAG system
            st.info("🤖 Setting up RAG system...")
            rag_system = RAG(
                retriever=retriever,
                llm_model=settings.llm_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens
            )
            st.success("✅ RAG system initialized")
            
            # Step 6: Setup workflow
            st.info("⚙️ Setting up agentic workflow...")
            workflow = ParalegalAgentWorkflow(
                retriever=retriever,
                rag_system=rag_system,
                firecrawl_api_key=settings.firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY"),
                openai_api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            )
            
            st.success("🎉 Workflow setup completed!")
            return workflow
            
        except Exception as e:
            st.error(f"Error initializing workflow: {e}")
            return None

async def run_workflow(query: str):
    f = io.StringIO()
    with redirect_stdout(f):
        result = await st.session_state.workflow.run_workflow(query)
    
    # Get aptured logs and store them
    logs = f.getvalue()
    if logs:
        st.session_state.workflow_logs.append(logs)
    
    return result

def cleanup_resources():
    """Cleanup vector database and other resources."""
    if st.session_state.vector_db:
        try:
            st.session_state.vector_db.close()
        except:
            pass
        st.session_state.vector_db = None

# Sidebar for configuration and document upload
with st.sidebar:
    st.header("🔧 Configuration")
    
    # st.subheader("API Keys")
    # openai_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    ollama_model = st.text_input("Ollama Model", value="gpt-oss:20b")
    firecrawl_key = st.text_input("Firecrawl API Key", type="password", value=os.getenv("FIRECRAWL_API_KEY", ""))
    
    # if openai_key:
        # os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        # st.success("✅ OpenAI API Key set!")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    if firecrawl_key:
        os.environ["FIRECRAWL_API_KEY"] = firecrawl_key
        st.success("✅ Firecrawl API Key set!")
    
    st.markdown("---")
    
    # Document upload section
    st.header("📄 Upload Document")
    st.markdown("Upload a PDF document to get started")
    
    uploaded_file = st.file_uploader("Choose your PDF file", type="pdf")
    
    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                file_key = f"{session_id}-{uploaded_file.name}"
                
                if file_key not in st.session_state.get('file_cache', {}):
                    # Initialize workflow with the uploaded document
                    workflow = initialize_workflow(file_path)
                    if workflow:
                        st.session_state.workflow = workflow
                        st.session_state.file_cache[file_key] = workflow
                        st.balloons()
                else:
                    st.session_state.workflow = st.session_state.file_cache[file_key]
                
                if st.session_state.workflow:
                    st.success("🎉 Ready to Chat!")
                    display_pdf(uploaded_file)
                    
        except Exception as e:
            st.error(f"An error occurred: {e}")
    
    # elif uploaded_file and not openai_key:
    #     st.warning("⚠️ Please enter your OpenAI API key first!")
    elif uploaded_file:
        st.info("📁 Please upload a PDF to continue")
    
    # Cleanup button
    st.markdown("---")
    if st.button("🗑️ Clean Up Resources"):
        cleanup_resources()
        st.success("Resources cleaned up!")

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown('''
        <h1 style='color: #2E86AB; margin-bottom: 10px;'>
            ⚖️ Paralegal AI assistant
        </h1>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
            <span style='color: #A23B72; font-size: 16px;'>Powered by</span>
            <div style="display: flex; align-items: center; gap: 20px;">
                <a href="#" style="display: inline-block; vertical-align: middle;">
                    <img src="https://images.seeklogo.com/logo-png/61/2/crew-ai-logo-png_seeklogo-619843.png" 
                         alt="CrewAI" style="height: 100px;">
                </a>
                <a href="#" style="display: inline-block; vertical-align: middle;">
                    <img src="https://milvus.io/images/layout/milvus-logo.svg" 
                         alt="Milvus" style="height: 32px;">
                </a>
                <a href="#" style="display: inline-block; vertical-align: middle;">
                    <img src="https://i.ibb.co/VcsfddTr/logo-dark.png" 
                         alt="Firecrawl" style="height: 45px;">
                </a>
                <a href="#" style="display: inline-block; vertical-align: middle;">
                    <img src="https://i.ibb.co/wt57zN1/ollama.png" 
                         alt="Ollama" style="height: 48px;">
                </a>
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    if st.button("Clear Chat ↺", on_click=reset_chat):
        st.rerun()

# System info
if st.session_state.workflow:
    st.success("🟢 System Ready - Workflow initialized successfully!")
else:
    st.info("🔵 Upload a PDF document to get started")

# Display chat messages from history
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
    # # Display workflow logs for user messages
    # if (message["role"] == "user" and 
    #     "log_index" in message and 
    #     message["log_index"] < len(st.session_state.workflow_logs)):
        
    #     with st.expander("🔍 View Workflow Execution Details", expanded=False):
    #         logs = st.session_state.workflow_logs[message["log_index"]]
    #         render_logs(logs)

# Accept user input
if prompt := st.chat_input("Ask a question about your document..."):
    if not st.session_state.workflow:
        st.error("⚠️ Please upload a document first to initialize the workflow.")
        st.stop()
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ Please set your OpenAI API key in the sidebar.")
        st.stop()
    
    # Add user message to chat history
    log_index = len(st.session_state.workflow_logs)
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt, 
        "log_index": log_index
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Run the workflow and get response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("🔄 Processing your query..."):
                # Measure end-to-end workflow time
                workflow_start = time.perf_counter()
                result = asyncio.run(run_workflow(prompt))
                workflow_end = time.perf_counter()
                workflow_time = workflow_end - workflow_start
            
            # # Display workflow logs
            # if log_index < len(st.session_state.workflow_logs):
            #     with st.expander("🔍 View Workflow Execution Details", expanded=False):
            #         render_logs(st.session_state.workflow_logs[log_index])
            
            # Get the final answer
            if isinstance(result, dict) and "answer" in result:
                full_response = result["answer"]
                
                # Show additional info about the workflow
                if result.get("web_search_used", False):
                    st.info("🌐 This response includes information from web search")
                    # if 'workflow_time' in locals():
                    #     st.caption(f"🕒 Completion time: {workflow_time:.2f} s")
                else:
                    st.info("📚 This response is based on your document")
                    try:
                        retriever = getattr(st.session_state.workflow, "retriever", None)
                        if retriever:
                            retrieve_start = time.perf_counter()
                            retriever.search(prompt)
                            retrieve_end = time.perf_counter()
                            retrieval_time = retrieve_end - retrieve_start

                            citations = retriever.get_citations(prompt, top_k=settings.top_k, snippet_chars=300)

                            if citations:
                                with st.expander("📎 Citations (top matches)"):
                                    for c in citations:
                                        score = c.get("score")
                                        try:
                                            score_str = f"{float(score):.3f}"
                                        except Exception:
                                            score_str = str(score)
                                        st.markdown(
                                            f"[{c['rank']}] score={score_str} id={c.get('node_id')}"
                                        )
                                        if c.get("snippet"):
                                            st.code(c["snippet"], language="text")
                    except Exception as e:
                        st.warning(f"Could not fetch citations: {e}")

                    # Show timing caption
                    times = []
                    if retrieval_time is not None:
                        times.append(f"🕒 Retrieval time: {retrieval_time:.2f} s")
                    # if 'workflow_time' in locals():
                    #     times.append(f"🕒 Completion time: {workflow_time:.2f} s")
                    if times:
                        st.caption(" • ".join(times))
                
            else:
                full_response = str(result)
            
            # Stream the response word by word
            streamed_response = ""
            words = full_response.split()
            
            for i, word in enumerate(words):
                streamed_response += word + " "
                message_placeholder.markdown(streamed_response + "▌")
                
                if i < len(words) - 1:
                    time.sleep(0.05)
            
            # Display final response
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            error_msg = f"❌ Error processing your question: {str(e)}"
            st.error(error_msg)
            full_response = "I apologize, but I encountered an error while processing your question. Please try again."
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response
    })

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px;'>"
    "Paralegal AI assistant • Built with Streamlit, CrewAI, Milvus, Firecrawl, and Ollama"
    "</p>",
    unsafe_allow_html=True
)
