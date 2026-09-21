import os
import tempfile
import base64
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

st.markdown("""
<style>
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
    
    .main .block-container {
        padding-bottom: 120px !important;
    }
    
    .stChatMessage {
        max-width: 60% !important;
        width: 60% !important;
    }
    
    .stChatMessageContent {
        max-width: 100% !important;
        word-wrap: break-word !important;
    }
    
    .stButton > button {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
        font-weight: 400 !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
    }
    
    .stButton > button:hover {
        background-color: #404040 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        box-shadow: none !important;
    }
    
    .stButton > button:focus {
        border: 1px solid #555555 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #404040 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #262730 !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        opacity: 0.8 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #404040 !important;
        opacity: 1 !important;
        border: 1px solid #555555 !important;
    }
    
    /* Aggressive spacing removal for tab buttons */
    .stColumns > div {
        padding: 0 !important;
        margin: 0 !important;
        gap: 0 !important;
    }
    
    .stColumns {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Target specific column containers */
    div[data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
        gap: 0 !important;
    }
    
    /* Remove all button margins and padding */
    .stButton {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stButton > button {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Force zero spacing between columns */
    .stColumns > div:first-child {
        margin-right: 0 !important;
        padding-right: 0 !important;
        border-right: none !important;
    }
    
    .stColumns > div:last-child {
        margin-left: 0 !important;
        padding-left: 0 !important;
        border-left: none !important;
    }
    
    /* Target the specific button columns */
    .stColumns > div[data-testid="column"] {
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }
    
    /* Override Streamlit's default column spacing */
    .stColumns {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Make buttons fill their containers completely */
    .stButton {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Remove any internal spacing */
    .stButton > button {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Make buttons full-width and adjacent */
    .stColumns > div {
        margin: 0 !important;
        padding: 0 !important;
        width: 50% !important;
    }
    
    /* Remove gap between columns */
    .stColumns {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Force zero spacing between button columns */
    .stColumns > div:first-child {
        margin-right: 0 !important;
        padding-right: 0 !important;
        border-right: none !important;
    }
    
    .stColumns > div:last-child {
        margin-left: 0 !important;
        padding-left: 0 !important;
        border-left: none !important;
    }
    
    /* Override any Streamlit default spacing */
    div[data-testid="column"] {
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }
    
    /* Use negative margins to pull buttons together */
    .stColumns > div:first-child {
        margin-right: -2px !important;
    }
    
    .stColumns > div:last-child {
        margin-left: -2px !important;
    }
    
    /* Force buttons to overlap slightly */
    .stButton {
        position: relative !important;
        z-index: 1 !important;
    }
    
    .stButton:last-child {
        z-index: 2 !important;
    }
    
    /* Target the specific button columns more aggressively */
    .stColumns > div[data-testid="column"] {
        margin: 0 !important;
        padding: 0 !important;
        width: 50% !important;
    }
    
    /* Override Streamlit's default column spacing completely */
    .stColumns {
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
    }
    
    /* Make buttons fill their containers */
    .stButton {
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stButton > button {
        width: 100% !important;
        margin: 0 !important;
        padding: 0.5rem 1rem !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
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

def display_pdf(file):
    """Display PDF preview using embedded iframe"""
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
<<<<<<< Updated upstream
    
    # Embedding PDF in HTML
=======
>>>>>>> Stashed changes
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"
                        style="border: 1px solid #ddd; border-radius: 8px;"
                    >
                    </iframe>"""
<<<<<<< Updated upstream
    
    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)

# Chat Interface Functions
=======
    st.markdown(pdf_display, unsafe_allow_html=True)

>>>>>>> Stashed changes
def prepare_chat_context(xray_data, prompt):
    """Prepare context from X-Ray data for the LLM"""
    context_parts = []
    
    if xray_data.get('fileSummary'):
        context_parts.append(f"Summary: {xray_data['fileSummary']}")
    
    if 'documentPages' in xray_data and xray_data['documentPages']:
        extracted_texts = []
        for page in xray_data['documentPages'][:2]:
            if 'chunks' in page:
                for chunk in page['chunks'][:3]:
                    if 'text' in chunk and chunk['text']:
                        text = chunk['text']
                        if len(text) > 500:
                            text = text[:500] + "..."
                        extracted_texts.append(text)
        
        if extracted_texts:
            context_parts.append(f"Document Content: {' '.join(extracted_texts)}")
    
    if xray_data.get('fileType'):
        context_parts.append(f"File Type: {xray_data['fileType']}")
    if xray_data.get('language'):
        context_parts.append(f"Language: {xray_data['language']}")
    
    return "\n\n".join(context_parts)

def generate_chat_response(prompt, context):
    """Generate AI response using Ollama"""
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

for key in ["xray_data", "uploaded_file_path", "uploaded_file_name", "uploaded_file_type", "processing_complete", "used_existing_file", "auto_loaded_file", "active_tab"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "xray_data" else False

st.markdown("# World-class Document Processing Pipeline")

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
        
<<<<<<< Updated upstream
        # Document Preview Section
        st.markdown("---")
        st.markdown("### 📄 Document Preview")
        
        # Show preview based on file type
        if uploaded.type == "application/pdf":
            # For PDF files, show the actual PDF preview using iframe
            display_pdf(uploaded)
            
        elif uploaded.type.startswith("image/"):
            # For image files, show the actual image
            st.image(uploaded, caption=f"Preview: {uploaded.name}", use_column_width=True)
            
        elif uploaded.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # For DOCX files
            st.info("📝 **Word Document** - Preview will be available after processing")
            st.markdown(f"**Content**: Text extraction in progress...")
            
        else:
            # For other file types
            st.info(f"📄 **{uploaded.type}** - Preview will be available after processing")
        
        # Show file metadata
        st.markdown("**File Details:**")
        st.markdown(f"- **Name**: {uploaded.name}")
        st.markdown(f"- **Size**: {uploaded.size / 1024:.1f} KB")
        st.markdown(f"- **Type**: {uploaded.type}")
        st.markdown(f"- **Status**: Ready for processing")
=======
        st.markdown("---")
        st.markdown("### 📄 Document Preview")
        
        if uploaded.type == "application/pdf":
            display_pdf(uploaded)
        elif uploaded.type.startswith("image/"):
            st.image(uploaded, caption=f"Preview: {uploaded.name}", use_column_width=True)
        elif uploaded.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.info("📝 **Word Document** - Preview will be available after processing")
            st.markdown(f"**Content**: Text extraction in progress...")
        else:
            st.info(f"📄 **{uploaded.type}** - Preview will be available after processing")
        
>>>>>>> Stashed changes

    st.button("🔄 Clear Analysis", on_click=reset_analysis)

try:
    gx = create_client()
    bucket_id = ensure_bucket(gx)
except ValueError as e:
    st.error(f"❌ {e}")
    st.stop()

if not st.session_state.auto_loaded_file and not st.session_state.xray_data:
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
    # Create half-width container for status
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if hasattr(file_to_process, 'path'):
            file_path = file_to_process.path
        else:
            file_path = st.session_state.uploaded_file_path
        
        try:
            # Step 1: Upload
            st.write("📤 **Uploading to Ground X...**")
            
            xray, used_existing = process_document(gx, bucket_id, file_to_process, file_path)
            
            if used_existing:
                st.write("✅ **File already exists in bucket**")
                st.write("📥 **Fetching existing X-Ray data...**")
            else:
                st.write("⏳ **Processing document...**")
                st.write("📥 **Fetching X-Ray data...**")
            
            st.session_state.xray_data = xray
            st.session_state.processing_complete = True
            st.session_state.used_existing_file = used_existing
            st.session_state.active_tab = "analysis"  # Auto-switch to analysis tab
            
            if used_existing:
                st.success("✅ Document analysis completed! (Used existing file)")
            else:
                st.success("✅ Document parsed successfully! Explore the results below.")
            
            st.write("🎉 **Analysis complete!**")
                
        except Exception as e:
            st.error(f"❌ Error processing document: {str(e)}")
            st.session_state.processing_complete = False

if st.session_state.xray_data:
    xray = st.session_state.xray_data
    
    file_type = xray.get('fileType', 'Unknown')
    language = xray.get('language', 'Unknown')
    pages = len(xray.get("documentPages", []))
    keywords = len(xray.get("fileKeywords", "").split(",")) if xray.get("fileKeywords") else 0
    
    st.markdown(f"**File Type:** {file_type} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Language:** {language} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Pages:** {pages} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Keywords:** {keywords}")
    
<<<<<<< Updated upstream
    # Document Preview Section (after processing)
    with st.expander("📄 Document Preview", expanded=False):
        st.markdown("### 📋 Document Summary")
        file_summary = xray.get("fileSummary")
        if file_summary:
            st.markdown(file_summary)
        else:
            st.info("No summary available")
        
        st.markdown("### 📝 Sample Content")
        # Show first few chunks of extracted text
        if "documentPages" in xray and xray["documentPages"]:
            sample_texts = []
            for page in xray["documentPages"][:2]:  # First 2 pages
                if "chunks" in page:
                    for chunk in page["chunks"][:2]:  # First 2 chunks per page
                        if "text" in chunk and chunk["text"]:
                            text = chunk["text"]
                            if len(text) > 200:
                                text = text[:200] + "..."
                            sample_texts.append(text)
            
            if sample_texts:
                for i, text in enumerate(sample_texts, 1):
                    st.markdown(f"**Sample {i}:**")
                    st.markdown(text)
                    st.markdown("---")
            else:
                st.info("No text content available for preview")
        
        st.markdown("### 🏷️ Key Topics")
        if xray.get("fileKeywords"):
            keywords_list = xray["fileKeywords"].split(",")
            # Show first 10 keywords
            display_keywords = keywords_list[:10]
            keyword_tags = " ".join([f"`{kw.strip()}`" for kw in display_keywords])
            st.markdown(keyword_tags)
        else:
            st.info("No keywords available")
    
    # Primary interface tabs for analysis and interaction
    main_tabs = st.tabs([
        "📊 X-Ray Analysis",
        "💬 Chat"
    ])
=======
    # Create a left-aligned container for the tab buttons
    col1, col2 = st.columns([1, 4])
>>>>>>> Stashed changes
    
    with col1:
        # Create a single container with custom button styling
        st.markdown("""
        <style>
        /* Make Streamlit buttons look like segmented control */
        .stButton > button {
            border-radius: 0 !important;
            margin: 0 !important;
            border: 1px solid #404040 !important;
            background-color: #262730 !important;
            color: #ffffff !important;
            font-weight: 400 !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        
        .stButton > button:hover {
            background-color: #404040 !important;
            color: #ffffff !important;
            border: 1px solid #555555 !important;
            box-shadow: none !important;
        }
        
        .stButton > button:focus {
            border: 1px solid #555555 !important;
            outline: none !important;
            box-shadow: none !important;
        }
        
        .stButton > button[kind="primary"] {
            background-color: #404040 !important;
            color: #ffffff !important;
            border: 1px solid #555555 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.2) !important;
        }
        
        .stButton > button[kind="secondary"] {
            background-color: #262730 !important;
            color: #ffffff !important;
            border: 1px solid #404040 !important;
            opacity: 0.8 !important;
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: #404040 !important;
            opacity: 1 !important;
            border: 1px solid #555555 !important;
        }
        
        /* Make first button rounded on left, second on right */
        .stColumns > div:first-child .stButton > button {
            border-top-left-radius: 0.5rem !important;
            border-bottom-left-radius: 0.5rem !important;
            border-top-right-radius: 0 !important;
            border-bottom-right-radius: 0 !important;
            border-right: none !important;
        }
        
        .stColumns > div:last-child .stButton > button {
            border-top-left-radius: 0 !important;
            border-bottom-left-radius: 0 !important;
            border-top-right-radius: 0.5rem !important;
            border-bottom-right-radius: 0.5rem !important;
            border-left: none !important;
        }
        
        /* Remove gap between columns completely */
        .stColumns {
            gap: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .stColumns > div {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Force buttons to be adjacent with negative margins */
        .stColumns > div:first-child {
            margin-right: -5px !important;
            padding-right: 0 !important;
        }
        
        .stColumns > div:last-child {
            margin-left: -15px !important;
            padding-left: 0 !important;
        }
        
        /* Make buttons overlap to eliminate gap */
        .stButton {
            position: relative !important;
            z-index: 1 !important;
        }
        
        .stButton:last-child {
            z-index: 2 !important;
        }
        
        /* Use transform to move chat button left */
        .stColumns > div:last-child .stButton {
            transform: translateX(-15px) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Use uneven column widths to move chat button left
        col1, col2 = st.columns([0.7, 1.3])
        
        with col1:
            if st.button("📊 X-Ray Analysis", key="analysis_tab_btn", type="primary" if st.session_state.active_tab == "analysis" else "secondary"):
                st.session_state.active_tab = "analysis"
                st.rerun()
        
        with col2:
            if st.button("💬 Chat", key="chat_tab_btn", type="primary" if st.session_state.active_tab == "chat" else "secondary"):
                st.session_state.active_tab = "chat"
                st.rerun()
    
    if st.session_state.active_tab is None:
        st.session_state.active_tab = "analysis"
    
    if st.session_state.active_tab == "analysis":
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
<<<<<<< Updated upstream
            # Extract and display narrative content from document chunks
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            # Extract and display suggested text content from document chunks
=======
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            # Extract and display raw text content from document chunks
=======
>>>>>>> Stashed changes
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
    
    elif st.session_state.active_tab == "chat":
        st.markdown("### 💬 Chat with Document")
        st.markdown("Ask questions about your document.")
        
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if prompt := st.chat_input("Ask a question about your document..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.active_tab = "chat"
            
<<<<<<< Updated upstream
            # Ensure we stay in chat mode
            st.session_state.in_chat_mode = True
            
            # Display user message in chat interface
=======
>>>>>>> Stashed changes
            with st.chat_message("user"):
                st.markdown(prompt)
            
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