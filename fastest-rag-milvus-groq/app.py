import os
import base64
import gc
import tempfile
import time
import uuid
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from rag import EmbedData, MilvusVDB_BQ, Retriever, RAG

load_dotenv()

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = str(uuid.uuid4())[:8]
    st.session_state.file_cache = {}
    st.session_state.is_indexed = False
    st.session_state.uploaded_file_name = None  
    st.session_state.processed_file = None  
    st.session_state.groq_api_key = os.getenv("GROQ_API_KEY", "")

session_id = st.session_state.id
collection_name = f"docs_{session_id}"  # Unique collection per session
batch_size = 512

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

def display_pdf(file):
    st.markdown("### PDF Preview")
    base64_pdf = base64.b64encode(file.read()).decode("utf-8")

    pdf_display = f"""<iframe src="data:application/pdf;base64,{base64_pdf}" width="400" height="100%" type="application/pdf"
                        style="height:100vh; width:100%">
                    </iframe>"""

    st.markdown(pdf_display, unsafe_allow_html=True)

with st.sidebar:
    st.header("📚 Add your documents!")

    groq_api_key = st.text_input(
        "🔑 Enter your Groq API Key:",
        type="password",
        value=st.session_state.groq_api_key,
        help="Get your API key from https://console.groq.com/",
        key="groq_api_key"
    )
    
    if groq_api_key != st.session_state.groq_api_key:
        st.session_state.groq_api_key = groq_api_key

    uploaded_file = st.file_uploader("Choose your `.pdf` file", type="pdf", key="pdf_uploader")
    if uploaded_file and uploaded_file.name != st.session_state.uploaded_file_name:
        st.session_state.uploaded_file_name = uploaded_file.name
        st.session_state.is_indexed = False

    if st.session_state.uploaded_file_name:
        if st.session_state.is_indexed:
            st.success("✅ Document processed and ready for chat!")

    if uploaded_file and groq_api_key:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                file_key = f"{session_id}-{uploaded_file.name}"
                st.write("Indexing your document...")

                if file_key not in st.session_state.get('file_cache', {}):
                    loader = SimpleDirectoryReader(
                        input_dir=temp_dir,
                        required_exts=[".pdf"],
                        recursive=True
                    )

                    docs = loader.load_data()
                    documents = [doc.text for doc in docs]

                    if not documents:
                        st.error("No text could be extracted from the PDF. Please try a different file.")
                        st.stop()

                    progress_bar = st.progress(0)
                    st.text("Generating embeddings...")

                    embeddata = EmbedData(
                        embed_model_name="BAAI/bge-large-en-v1.5",
                        batch_size=batch_size
                    )
                    embeddata.embed(documents)
                    progress_bar.progress(40)
                    st.text("Creating vector index...")

                    db_file = os.path.join(tempfile.gettempdir(), f"milvus_{session_id}.db")
                    if os.path.exists(db_file):
                        os.remove(db_file)

                    test_embedding = embeddata.embed_model.get_text_embedding("test")
                    actual_dim = len(test_embedding)

                    milvus_vdb = MilvusVDB_BQ(
                        collection_name=collection_name,
                        batch_size=batch_size,
                        vector_dim=actual_dim,
                        db_file=db_file
                    )
                    progress_bar.progress(60)
                    st.text("Storing in vector DB...")

                    milvus_vdb.define_client()
                    milvus_vdb.create_collection()
                    milvus_vdb.ingest_data(embeddata=embeddata)
                    
                    progress_bar.progress(80)
                    st.text("Creating query engine...")

                    retriever = Retriever(vector_db=milvus_vdb, embeddata=embeddata)
                    query_engine = RAG(
                        retriever=retriever,
                        llm_model="moonshotai/kimi-k2-instruct",
                        groq_api_key=groq_api_key
                    )

                    progress_bar.progress(100)
                    st.session_state.file_cache[file_key] = query_engine
                    st.session_state.is_indexed = True
                    st.session_state.processed_file = uploaded_file
                else:
                    query_engine = st.session_state.file_cache[file_key]
                
                st.success("✅ Ready to Chat!")
                st.info(f"📄 Document: {uploaded_file.name}")
                display_pdf(uploaded_file)

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            st.stop()

    elif uploaded_file and not groq_api_key:
        st.warning("⚠️ Please enter your Groq API key to process the document.")
    elif not uploaded_file and not st.session_state.uploaded_file_name:
        st.info("👆 Upload a PDF file to get started!")
    
    if st.session_state.processed_file and st.session_state.is_indexed:
        display_pdf(st.session_state.processed_file)

# Main chat interface
col1, col2 = st.columns([6, 1])

with col1:
    st.markdown('''
        <h1 style="text-align: center; font-weight: 500;">
            🚀 Fastest RAG Stack powered by 
            <a href="https://milvus.io/" target="_blank" style="display: inline-block; vertical-align: bottom;">
                <img src="https://milvus.io/images/layout/milvus-logo.svg" alt="Milvus Logo" style="height: 0.9em;">
            </a>
            and 
            <a href="https://groq.com/" target="_blank" style="display: inline-block; vertical-align: bottom;">
                <img src="https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/dark/groq-text.png" alt="Groq Logo" style="height: 0.8em;">
            </a>
        </h1>
    ''', unsafe_allow_html=True)

    st.markdown('''
        <div style="text-align: center; color: #808080; font-size: 1.2em;">
            This app is deployed on 
            <a href="https://www.beam.cloud/" target="_blank" style="display: inline-block; vertical-align: middle;">
                <img src="https://i.ibb.co/m5RtcvnY/beam-logo.png" alt="Beam Logo" style="height: 1.3em;">
            </a>
        </div>
    ''', unsafe_allow_html=True)      

with col2:
    st.button("Clear ↺", on_click=reset_chat, key="clear_button")

# Initialize chat history
if "messages" not in st.session_state:
    reset_chat()

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your document..."):
    if not st.session_state.is_indexed or not st.session_state.file_cache:
        st.error("Please upload and process a PDF document first!")
        st.stop()

    if st.session_state.uploaded_file_name:
        file_key = f"{session_id}-{st.session_state.uploaded_file_name}"
        if file_key in st.session_state.file_cache:
            query_engine = st.session_state.file_cache[file_key]
        else:
            st.error("Document not found in cache. Please re-upload the document.")
            st.stop()
    else:
        st.error("No document uploaded. Please upload a PDF document first.")
        st.stop()

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        try:
            # Measure retrieval time
            retrieval_start = time.perf_counter()
            context_text = query_engine.generate_context(query=prompt)
            retrieval_time = time.perf_counter() - retrieval_start

            prompt_text = query_engine.prompt_template.format(context=context_text, query=prompt)
            # Call the LLM for streaming
            streaming_response = query_engine.llm.stream_complete(prompt_text)

            for chunk in streaming_response:
                try:
                    if hasattr(chunk, 'delta') and chunk.delta:
                        new_text = chunk.delta
                    elif hasattr(chunk, 'text') and chunk.text is not None:
                        candidate = chunk.text
                        if candidate.startswith(full_response):
                            new_text = candidate[len(full_response):]
                        else:
                            new_text = candidate
                    else:
                        candidate = str(chunk)
                        new_text = candidate if not candidate.startswith(full_response) else ""

                    if new_text:
                        full_response += new_text
                        message_placeholder.markdown(full_response + "▌")
                except Exception:
                    continue

            message_placeholder.markdown(full_response)

            retrieval_ms = int(retrieval_time * 1000)
            st.caption(f"⏱️ Retrieval time: {retrieval_ms} ms")

        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            full_response = "I apologize, but I encountered an error while processing your question. Please try again."
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})