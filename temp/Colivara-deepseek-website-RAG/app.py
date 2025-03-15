# Adapted from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming
import os

import base64
import gc
import random
import tempfile
import time
import uuid

from IPython.display import Markdown, display

import streamlit as st

import torch
import time
import numpy as np
from tqdm import tqdm
from pdf2image import convert_from_path

from rag_code import Retriever, RAG
from firecrawl import FirecrawlApp
from PIL import Image
from fpdf import FPDF
import io
import requests
import math
from colivara_py import ColiVara
from dotenv import load_dotenv

from streamlit_pdf_viewer import pdf_viewer


load_dotenv()

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.collection_name = "webpage_collection" + str(st.session_state.id)
    st.session_state.file_cache = {}
    st.session_state.url_input = ""  # Initialize URL input
    st.session_state.pdf_displayed = False  # Track if PDF is displayed

session_id = st.session_state.id

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    # Don't reset URL and PDF state when clearing chat
    gc.collect()


def display_pdf(file):
    # Opening file from file path
    if isinstance(file, str):
        # If file is a path
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    else:
        # If file is already a file object/buffer
        base64_pdf = base64.b64encode(file.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = f"""<embed
        class="pdfobject"
        type="application/pdf"
        title="Embedded PDF"
        src="data:application/pdf;base64,{base64_pdf}"
        style="overflow: auto; width: 100%; height: 800px;">"""

    # Displaying File
    st.markdown(pdf_display, unsafe_allow_html=True)


def create_pdf_from_screenshot(screenshot_url):
    response = requests.get(screenshot_url)
    response.raise_for_status()

    # Save screenshot
    with open('image.png', 'wb') as f:
        f.write(response.content)
    
    image = Image.open('image.png')
    width, height = image.size
    slice_height = math.ceil(height / 10)

    # Create PDF with custom page size matching the image aspect ratio
    pdf = FPDF(unit='pt', format=[width, slice_height])
    pdf.set_auto_page_break(auto=False)  # Disable auto page break

    for i in range(10):
        top = i * slice_height
        bottom = min((i + 1) * slice_height, height)
        slice_img = image.crop((0, top, width, bottom))
        
        temp_filename = f'temp_slice_{i}.png'
        slice_img.save(temp_filename)
        
        pdf.add_page()
        # Add image with explicit dimensions matching the PDF page
        pdf.image(temp_filename, x=0, y=0, w=width, h=bottom-top)
        os.remove(temp_filename)
    
    pdf_path = "screenshot_slices.pdf"
    pdf.output(pdf_path)
    return pdf_path


with st.sidebar:
    st.header(f"Add your content!")
    
    # Use session state to persist URL input
    url_input = st.text_input("Enter webpage URL", value=st.session_state.url_input, key="url_field")
    st.session_state.url_input = url_input  # Store URL in session state
    start_rag = st.button("Start RAG")

    if start_rag and url_input:
        try:
            # Step 2: Get screenshot using FireCrawl
            status_container = st.empty()
            with status_container.status("Processing webpage...", expanded=True) as status:
                status.write("🔍 Scraping webpage with Firecrawl...")
                app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
                scrape_result = app.scrape_url(url_input,
                                               params={'formats': ['screenshot@fullPage'],
                                                       'waitFor': 10000})
                
                status.update(label="Creating PDF", state="running")
                status.write("📄 Creating PDF from screenshot...")
                # Step 3: Create PDF from screenshot
                st.session_state.pdf_path = create_pdf_from_screenshot(scrape_result['screenshot'])
                st.session_state.pdf_displayed = True  # Mark PDF as ready to display

                # Rest of the code for RAG setup
                file_key = f"{session_id}-webpage.pdf"
                
                if file_key not in st.session_state.get('file_cache', {}):
                    status.update(label="Indexing content", state="running")
                    status.write("🔎 Indexing content with ColiVara...")
                    # Initialize ColiVara client and process document
                    rag_client = ColiVara(api_key=os.getenv("COLIVARA_API_KEY"))
                    
                    new_collection = rag_client.create_collection(
                        name=st.session_state.collection_name, 
                        metadata={"description": "Webpage screenshots"}
                    )
                    
                    document = rag_client.upsert_document(
                        collection_name=st.session_state.collection_name,
                        name="webpage_document",
                        document_path=st.session_state.pdf_path
                    )
                    
                    # Initialize retriever and RAG
                    retriever = Retriever(rag_client=rag_client, collection_name=st.session_state.collection_name)
                    st.session_state.query_engine = RAG(retriever=retriever)
                    
                    st.session_state.file_cache[file_key] = st.session_state.query_engine
                else:
                    st.session_state.query_engine = st.session_state.file_cache[file_key]
                
                status.update(label="Processing complete!", state="complete")
            st.success("Ready to Chat!")
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()

    # Always show PDF if it exists
    if st.session_state.get('pdf_displayed', False) and hasattr(st.session_state, 'pdf_path'):
        pdf_viewer(st.session_state.pdf_path)

col1, col2 = st.columns([6, 1])

# st.header("""# Multimodal RAG powered by <img src="data:image/png;base64,{}" width="170" style="vertical-align: -3px;"> Janus""".format(base64.b64encode(open("assets/deep-seek.png", "rb").read()).decode()))

with col1:
# #     st.header("""
# #     # Agentic RAG powered by <img src="data:image/png;base64,{}" width="170" style="vertical-align: -3px;">
# # """.format(base64.b64encode(open("assets/deep-seek.png", "rb").read()).decode()))
    st.markdown("""
    ## Multimodal RAG powered by ColiVara SOTA Retrieval and <img src="data:image/png;base64,{}" width="170" style="vertical-align: -3px;"> Janus""".format(base64.b64encode(open("assets/deep-seek.png", "rb").read()).decode()), unsafe_allow_html=True)


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

        streaming_response = st.session_state.query_engine.query(prompt)
                
        for chunk in streaming_response:
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")

            time.sleep(0.01)
        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})