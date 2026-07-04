import streamlit as st
import base64
import uuid
import sys
from io import StringIO

from config import vector_collection
from ingest_data import ingest_data
from planning import generate_response, tool_selector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Database Memory Agent", layout="wide")

# Initialize session state variables
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
    
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "vector_index_ready" not in st.session_state:
    st.session_state.vector_index_ready = False
    
if "data_ingested" not in st.session_state:
    st.session_state.data_ingested = False

session_id = st.session_state.session_id

def reset_chat():
    """Reset chat history."""
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())[:8]

def display_pdf(file):
    """Display PDF preview in sidebar."""
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%"
                    >
                    </iframe>"""
    
    st.markdown(pdf_display, unsafe_allow_html=True)

def check_vector_index():
    """Check if vector index exists and is ready."""
    if st.session_state.vector_index_ready:
        return True
    
    try:
        existing_indexes = list(vector_collection.list_search_indexes("vector_index"))
        if existing_indexes and existing_indexes[0].get("queryable"):
            st.session_state.vector_index_ready = True
            return True
    except Exception as e:
        st.error(f"Error checking vector index: {e}")
        return False
    
    return False

def process_pdf_upload(uploaded_file):
    """Process uploaded PDF and ingest into MongoDB."""
    with st.spinner("🔄 Processing..."):
        try:
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                ingest_data()
            finally:
                sys.stdout = old_stdout
            
            if check_vector_index():
                st.session_state.data_ingested = True
                st.success("✅ Document processed and ready for queries!")
                return True
            return False
        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
            return False

def ingest_sample_data():
    """Ingest sample MongoDB earnings report."""
    try:
        with st.spinner("🔄 Processing..."):
            # Suppress print output from ingest_data()
            old_stdout = sys.stdout
            sys.stdout = StringIO()
            
            try:
                ingest_data()
            finally:
                sys.stdout = old_stdout
        
        # ingest_data() already creates the index, just check if it's ready
        if check_vector_index():
            st.session_state.data_ingested = True
            st.success("✅ Sample data ingested and ready for queries!")
            return True
        return False
    except Exception as e:
        st.error(f"Error ingesting sample data: {str(e)}")
        return False

# Sidebar for configuration and document upload
with st.sidebar:
    st.header("🔧 Configuration")
    
    st.markdown("**Session ID:**")
    st.code(session_id)
    
    if st.button("🔄 New Session"):
        reset_chat()
        st.rerun()
    
    st.markdown("---")
    
    # Document upload section
    st.header("📄 Upload Document")
    st.markdown("Upload a PDF document or use sample data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Use Sample Data", use_container_width=True):
            ingest_sample_data()
    
    with col2:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.data_ingested = False
            st.session_state.vector_index_ready = False
            st.info("Data cleared. Upload a new document to continue.")
    
    uploaded_file = st.file_uploader("Or upload your PDF file", type="pdf")
    
    if uploaded_file:
        if process_pdf_upload(uploaded_file):
            display_pdf(uploaded_file)
    
    st.markdown("---")
    
    # System status
    st.header("📊 System Status")
    if st.session_state.data_ingested:
        st.success("🟢 Data Ready")
    else:
        st.info("🔵 No Data Loaded")
    
    if st.session_state.vector_index_ready:
        st.success("🟢 Vector Index Ready")
    else:
        st.warning("🟡 Vector Index Not Ready")

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown('''
        <h1 style='color: #2E86AB; margin-bottom: 10px; font-size: 2.5em;'>
            Database Memory Agent
        </h1>
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
            <span style='color: #A23B72; font-size: 16px;'>Powered by</span>
            <div style="display: flex; align-items: center; gap: 20px;">
                <a href="https://www.mongodb.com/" style="display: inline-block; vertical-align: middle;">
                    <img src="https://webimages.mongodb.com/_com_assets/cms/mongodb_logo1-76twgcu2dm.png" 
                         alt="MongoDB" style="height: 40px;">
                </a>
                <a href="https://www.voyageai.com/" style="display: inline-block; vertical-align: middle;">
                    <img src="https://www.voyageai.com/favicon.ico" 
                         alt="Voyage AI" style="height: 32px;">
                </a>
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col2:
    if st.button("Clear Chat ↺", on_click=reset_chat):
        st.rerun()

# System info
if st.session_state.data_ingested and st.session_state.vector_index_ready:
    st.success("🟢 System Ready - You can ask questions about your document!")
elif st.session_state.data_ingested:
    st.warning("🟡 Data loaded but vector index is not ready. Please wait...")
else:
    st.info("🔵 Upload a PDF document or use sample data to get started")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        

# Accept user input
if prompt := st.chat_input("Ask a question about your document..."):
    if not st.session_state.data_ingested or not st.session_state.vector_index_ready:
        st.error("⚠️ Please upload a document or use sample data first.")
        st.stop()
    
    # Add user message to chat history
    st.session_state.messages.append({
        "role": "user", 
        "content": prompt
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("🔄 Processing..."):
                # Get tool info for display (simple check)
                session_history = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages[-5:]]
                tool, _ = tool_selector(prompt, session_history if session_history else None)
                
                # Generate response
                response = generate_response(session_id, prompt)
            
            message_placeholder.markdown(response)
            
            # Show simple tool indicator
            if tool == "vector_search_tool":
                st.info("📚 Using document search")
            elif tool == "calculator_tool":
                st.info("🔢 Using calculator")
            
            metadata = {"tool": tool}
            
        except Exception as e:
            st.error(f"❌ Error processing your question: {str(e)}")
            response = "I apologize, but I encountered an error while processing your question. Please try again."
            message_placeholder.markdown(response)
            metadata = {}
    
    # Add assistant response to chat history
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response,
        "metadata": metadata
    })

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #666; font-size: 12px;'>"
    "Database Memory Agent • Built with Streamlit, MongoDB Atlas Vector Search, and Voyage AI"
    "</p>",
    unsafe_allow_html=True
)

