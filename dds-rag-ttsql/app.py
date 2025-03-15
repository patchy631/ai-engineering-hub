import streamlit as st
import asyncio
import os
import base64
from rag_tsql import get_agent_response, get_response, wf, load_documents, get_or_create_index, RouterOutputAgentWorkflow
from llama_index.core.tools import QueryEngineTool
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import fitz  # PyMuPDF for PDF extraction

# Initialize session state
if "response" not in st.session_state:
    st.session_state.response = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "workflow" not in st.session_state:
    st.session_state.workflow = wf  # Default to sql_tool only
if "embed_model" not in st.session_state:
    st.session_state.embed_model = None

# Function to display PDF
def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")
    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%">
                    </iframe>"""
    st.markdown(pdf_display, unsafe_allow_html=True)

# Sidebar for file upload
with st.sidebar:
    st.header("Add your PDF files!")
    uploaded_files = st.file_uploader("Choose your PDF files", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        with st.spinner("Indexing your PDFs..."):
            PDF_DIRECTORY = "./pdf"
            if not os.path.exists(PDF_DIRECTORY):
                os.makedirs(PDF_DIRECTORY)
            for uploaded_file in uploaded_files:
                file_path = os.path.join(PDF_DIRECTORY, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                display_pdf(uploaded_file)

            if st.session_state.embed_model is None:
                st.session_state.embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

            index = get_or_create_index(st.session_state.embed_model)
            local_query_engine = index.as_query_engine()

            local_pdf_tool = QueryEngineTool.from_defaults(
                query_engine=local_query_engine,
                description="Useful for answering semantic questions about content in the uploaded PDFs.",
                name="local_pdf_tool"
            )

            st.session_state.workflow = RouterOutputAgentWorkflow(
                tools=[st.session_state.workflow.tools[0], local_pdf_tool],
                verbose=True,
                timeout=120
            )
        st.success("PDFs indexed successfully!")

# Custom CSS for header with overlay caption
st.markdown("""
    <style>
        .header-container {
            position: relative;
            text-align: center;
            margin-bottom: 20px;
        }
        .header-container img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .header-caption {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: white;
            font-size: 24px;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
            font-family: 'Arial', sans-serif;
        }
        .stChatMessage {
            background-color: #f5f5f5;
            border-radius: 10px;
            padding: 10px;
        }
        .stButton>button {
            background-color: #0078D7;
            color: white;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
    </style>
""", unsafe_allow_html=True)

# Header with Image and Overlay Caption
st.markdown(
    """
    <div class="header-container">
        <img src="data:image/png;base64,{}" alt="CitySnooper Header">
        <div class="header-caption">CitySnooper – Your City Guide</div>
    </div>
    """.format(base64.b64encode(open("assets/image.png", "rb").read()).decode()),
    unsafe_allow_html=True
)

# Layout columns for clear button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("Clear ↺"):
        st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about US cities or uploaded PDFs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            full_response = get_response(prompt)
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})