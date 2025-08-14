import os
import tempfile
import requests
from typing import Any, Dict

import streamlit as st
from groundx_utils import (
    create_client, 
    ensure_bucket, 
    check_file_exists, 
    get_xray_for_existing_document,
    process_document
)

# Application Configuration
st.set_page_config(page_title="Ground X - X-Ray", layout="wide")

# Custom CSS for enhanced chat interface layout
st.markdown("""
<style>
    /* Fixed chat input at bottom */
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 15% !important;
        width: 60% !important;
        max-width: 800px !important;
        background: var(--background-color) !important;
        z-index: 9999 !important;
        padding: 1rem !important;
        border-top: 1px solid var(--border-color) !important;
        margin: 0 !important;
    }
    
    /* Make chat area scrollable */
    .main .block-container {
        padding-bottom: 120px !important;
    }
    
    /* Limit chat message width to match main content */
    .stChatMessage {
        max-width: 60% !important;
        width: 60% !important;
    }
    
    /* Ensure chat message content doesn't overflow */
    .stChatMessageContent {
        max-width: 100% !important;
        word-wrap: break-word !important;
    }
</style>
""", unsafe_allow_html=True)

def reset_analysis():
    """Reset all analysis-related session state variables"""
    keys_to_delete = ["xray_data", "uploaded_file_path", "uploaded_file_name", "uploaded_file_type", 
                      "processing_complete", "used_existing_file", "auto_loaded_file", "chat_history"]
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

# Chat Interface Functions
def prepare_chat_context(xray_data, prompt):
    """Prepare context from X-Ray data for the LLM"""
    context_parts = []
    
    # Add summary first for quick overview
    if xray_data.get('fileSummary'):
        context_parts.append(f"Summary: {xray_data['fileSummary']}")
    
    # Add limited document content (first 2 pages, first 3 chunks each)
    if 'documentPages' in xray_data and xray_data['documentPages']:
        extracted_texts = []
        for page in xray_data['documentPages'][:2]:  # Only first 2 pages
            if 'chunks' in page:
                for chunk in page['chunks'][:3]:  # Only first 3 chunks per page
                    if 'text' in chunk and chunk['text']:
                        text = chunk['text']
                        if len(text) > 500:  # Shorter limit
                            text = text[:500] + "..."
                        extracted_texts.append(text)
        
        if extracted_texts:
            context_parts.append(f"Document Content: {' '.join(extracted_texts)}")
    
    # Add essential metadata
    if xray_data.get('fileType'):
        context_parts.append(f"File Type: {xray_data['fileType']}")
    if xray_data.get('language'):
        context_parts.append(f"Language: {xray_data['language']}")
    
    return "\n\n".join(context_parts)

def generate_chat_response(prompt, context):
    """Generate AI response using Ollama with structured prompt engineering"""
    # Construct comprehensive prompt for intelligent query handling
    full_prompt = f"""You are an AI assistant helping analyze a document. You have access to the following document information:

{context}

User Question: {prompt}

Instructions:
- Answer the question directly and concisely
- Use Document Content for specific details
- Use Summary for general overview
- Don't add unnecessary disclaimers or explanations
- If you don't have the information, simply say "I don't have enough information to answer that question"
- Keep responses focused and to the point

Response:"""

    # Initialize Ollama API request
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 300,
                    "top_k": 10,
                    "repeat_penalty": 1.1
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Sorry, I couldn't generate a response.")
        else:
            return f"I'm having trouble accessing the AI model right now. Status: {response.status_code}"
            
    except Exception as e:
        return f"I'm having trouble accessing the AI model right now. Error: {str(e)}"

# Initialize Streamlit session state
for key in ["xray_data", "uploaded_file_path", "uploaded_file_name", "uploaded_file_type", "processing_complete", "used_existing_file", "auto_loaded_file"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "xray_data" else False

# Application Header
st.markdown("""
# World-class Document Processing Pipeline
""")

# Load and display GroundX branding
import base64
try:
    with open("assets/groundx.png", "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <strong>powered by</strong>
        <img src="data:image/png;base64,{logo_base64}" width="200" style="display: inline-block;">
    </div>
    <br>
    """, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px;">
        <strong>powered by</strong>
        <strong>Ground X</strong>
    </div>
    <br>
    """, unsafe_allow_html=True)

# Document Upload Interface
with st.sidebar:
    st.header("📄 Upload Document")
    
    if st.session_state.uploaded_file_name:
        status_text = f"✅ **File loaded**: {st.session_state.uploaded_file_name}"
        if st.session_state.used_existing_file:
            status_text += " (Auto-loaded from bucket)" if st.session_state.auto_loaded_file else " (Used existing file in bucket)"
        st.success(status_text)
        if st.button("🔄 Re-process File"):
            st.session_state.processing_complete = False
            st.session_state.xray_data = None
            st.session_state.used_existing_file = False
            st.session_state.auto_loaded_file = False
            st.rerun()
    
    uploaded = st.file_uploader(
        "Choose a document", 
        type=["pdf", "png", "jpg", "jpeg", "docx"],
        help="Upload a document to analyze with Ground X X-Ray"
    )

    if uploaded is not None:
        st.info(f"**File**: {uploaded.name}\n**Size**: {uploaded.size / 1024:.1f} KB\n**Type**: {uploaded.type}")
        st.session_state.uploaded_file_name = uploaded.name
        st.session_state.uploaded_file_type = uploaded.type

    st.button("🔄 Clear Analysis", on_click=reset_analysis)

# Initialize Ground X API client and storage bucket
try:
    gx = create_client()
    bucket_id = ensure_bucket(gx)
except ValueError as e:
    st.error(f"❌ {e}")
    st.stop()

# Auto-load existing document from bucket if available
if not st.session_state.auto_loaded_file and not st.session_state.xray_data:
    # Configurable sample file - can be set via environment variable
    existing_file_name = os.getenv("SAMPLE_FILE_NAME", "tmpivkf8qf8_sample-file.pdf")
    existing_doc_id = check_file_exists(gx, bucket_id, existing_file_name)
    
    if existing_doc_id:
        xray = get_xray_for_existing_document(gx, existing_doc_id, bucket_id)
        st.session_state.xray_data = xray
        st.session_state.uploaded_file_name = existing_file_name
        st.session_state.uploaded_file_type = "application/pdf"
        st.session_state.processing_complete = True
        st.session_state.used_existing_file = True
        st.session_state.auto_loaded_file = True
        st.success(f"✅ **Auto-loaded**: {existing_file_name} from bucket")
        st.rerun()
    else:
        st.session_state.auto_loaded_file = True

# Document Processing Logic
should_process = False
file_to_process = None

if uploaded is not None:
    should_process = True
    file_to_process = uploaded
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{uploaded.name}")
    tmp_file.write(uploaded.getbuffer())
    tmp_file.close()
    st.session_state.uploaded_file_path = tmp_file.name
elif st.session_state.uploaded_file_path and not st.session_state.processing_complete:
    should_process = True
    class MockUploadedFile:
        def __init__(self, name, type, path):
            self.name = name
            self.type = type
            self.path = path
        def getbuffer(self):
            with open(self.path, 'rb') as f:
                return f.read()
    
    file_to_process = MockUploadedFile(
        st.session_state.uploaded_file_name,
        st.session_state.uploaded_file_type,
        st.session_state.uploaded_file_path
    )

if should_process and st.session_state.xray_data is None:
    with st.status("🔄 Processing document...", expanded=True) as status:
        # Determine file path for processing (temporary for new uploads, stored for existing)
        if hasattr(file_to_process, 'path'):
            file_path = file_to_process.path
        else:
            file_path = st.session_state.uploaded_file_path
        
        try:
            xray, used_existing = process_document(gx, bucket_id, file_to_process, file_path)
            st.session_state.xray_data = xray
            st.session_state.processing_complete = True
            st.session_state.used_existing_file = used_existing
            
            if used_existing:
                st.write("✅ **File already exists in bucket**")
                st.write("📥 **Fetched X-Ray data...**")
                st.success("✅ Document analysis completed! (Used existing file)")
            else:
                st.write("📤 **Uploaded to Ground X...**")
                st.write("⏳ **Processed document...**")
                st.write("📥 **Fetched X-Ray data...**")
                st.success("✅ Document parsed successfully! Explore the results below.")
            
            st.write("🎉 **Analysis complete!**")
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            st.session_state.processing_complete = False

# Analysis Results Display
if st.session_state.xray_data:
    xray = st.session_state.xray_data
    
    # Extract and display document metadata metrics
    file_type = xray.get('fileType', 'Unknown')
    language = xray.get('language', 'Unknown')
    pages = len(xray.get("documentPages", []))
    keywords = len(xray.get("fileKeywords", "").split(",")) if xray.get("fileKeywords") else 0
    
    st.markdown(f"**File Type:** {file_type} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Language:** {language} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Pages:** {pages} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Keywords:** {keywords}")
    
    # Primary interface tabs for analysis and interaction
    main_tabs = st.tabs([
        "📊 X-Ray Analysis",
        "💬 Chat"
    ])
    
    with main_tabs[0]:
        st.markdown("### 📊 X-Ray Analysis Results")
        tabs = st.tabs([
            "🔍 JSON Output",
            "📝 Narrative Summary", 
            "📋 File Summary",
            "💡 Suggested Text",
            "📄 Extracted Text",
            "🏷️ Keywords"
        ])

    with tabs[0]:
        st.subheader("🔍 Raw JSON Data")
        st.json(xray)

    with tabs[1]:
        st.subheader("📝 Narrative Summary")
        # Extract and display narrative content from document chunks
        narratives = []
        if "documentPages" in xray:
            for page in xray["documentPages"]:
                if "chunks" in page:
                    for chunk in page["chunks"]:
                        if "narrative" in chunk and chunk["narrative"]:
                            narratives.extend(chunk["narrative"])
        
        if narratives:
            for i, narrative in enumerate(narratives, 1):
                st.markdown(f"**Narrative {i}:**")
                st.markdown(narrative)
                st.divider()
        else:
            st.info("No narrative text found in the X-Ray data")

    with tabs[2]:
        st.subheader("📋 File Summary")
        file_summary = xray.get("fileSummary")
        if file_summary:
            st.markdown(file_summary)
        else:
            st.info("No file summary found in the X-Ray data")

    with tabs[3]:
        st.subheader("💡 Suggested Text")
        # Extract and display suggested text content from document chunks
        suggested_texts = []
        if "documentPages" in xray:
            for page in xray["documentPages"]:
                if "chunks" in page:
                    for chunk in page["chunks"]:
                        if "suggestedText" in chunk and chunk["suggestedText"]:
                            suggested_texts.append(chunk["suggestedText"])
        
        if suggested_texts:
            for i, suggested in enumerate(suggested_texts, 1):
                st.markdown(f"**Suggested Text {i}:**")
                st.markdown(suggested)
                st.divider()
        else:
            st.info("No suggested text found in the X-Ray data")

    with tabs[4]:
        st.subheader("📄 Extracted Text")
        # Extract and display raw text content from document chunks
        extracted_texts = []
        if "documentPages" in xray:
            for page in xray["documentPages"]:
                if "chunks" in page:
                    for chunk in page["chunks"]:
                        if "text" in chunk and chunk["text"]:
                            extracted_texts.append(chunk["text"])
        
        if extracted_texts:
            combined_text = "\n\n---\n\n".join(extracted_texts)
            st.text_area("Extracted Content", combined_text, height=400)
        else:
            st.info("No extracted text found in the X-Ray data")

    with tabs[5]:
        st.subheader("🏷️ Keywords")
        keywords = xray.get("fileKeywords")
        if keywords:
            st.write(keywords)
        else:
            st.info("No keywords found in the X-Ray data")
    
    # Interactive Chat Interface
    with main_tabs[1]:
        st.markdown("### 💬 Chat with Document")
        st.markdown("Ask questions about your document.")
        
        # Initialize and display chat conversation history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Render existing chat messages
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Process user input and generate responses
        if prompt := st.chat_input("Ask a question about your document..."):
            # Store user message in conversation history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message in chat interface
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display AI assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    context = prepare_chat_context(xray, prompt)
                    response = generate_chat_response(prompt, context)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.markdown(response)

elif uploaded is None and st.session_state.uploaded_file_name is None and not st.session_state.xray_data:
    st.info("👆 **Upload a document in the sidebar to begin analysis**")
elif uploaded is None and st.session_state.uploaded_file_name and st.session_state.xray_data:
    status = "Auto-loaded" if st.session_state.auto_loaded_file else "Analysis"
    st.success(f"✅ **{status} complete for**: {st.session_state.uploaded_file_name}")
    st.info("💡 **Tip**: You can re-process the file using the button in the sidebar, or upload a new document.")
