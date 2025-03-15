# Adapted from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps#build-a-simple-chatbot-gui-with-streaming

import os
import gc
import uuid
import tempfile
import base64
from dotenv import load_dotenv
from rag_code import Transcribe, EmbedData, QdrantVDB_QB, Retriever, RAG
import streamlit as st

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

session_id = st.session_state.id
collection_name = "chat with audios"
batch_size = 32

load_dotenv()

def reset_chat():
    st.session_state.messages = []
    st.session_state.context = None
    gc.collect()

with st.sidebar:
    st.header("Add your audio file!")
    
    uploaded_file = st.file_uploader("Choose your audio file", type=["mp3", "wav", "m4a"])

    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                file_key = f"{session_id}-{uploaded_file.name}"
                st.write("Transcribing with AssemblyAI and storing in vector database...")

                if file_key not in st.session_state.get('file_cache', {}):
                    # Initialize transcriber
                    transcriber = Transcribe(api_key=os.getenv("ASSEMBLYAI_API_KEY"))
                    
                    # Get speaker-labeled transcripts
                    transcripts = transcriber.transcribe_audio(file_path)
                    st.session_state.transcripts = transcripts
                    
                    # Each speaker segment becomes a separate document for embedding
                    documents = [f"Speaker {t['speaker']}: {t['text']}" for t in transcripts]

                    # embed data    
                    embeddata = EmbedData(embed_model_name="BAAI/bge-large-en-v1.5", batch_size=batch_size)
                    embeddata.embed(documents)

                    # set up vector database
                    qdrant_vdb = QdrantVDB_QB(collection_name=collection_name,
                                          batch_size=batch_size,
                                          vector_dim=1024)
                    qdrant_vdb.define_client()
                    qdrant_vdb.create_collection()
                    qdrant_vdb.ingest_data(embeddata=embeddata)

                    # set up retriever
                    retriever = Retriever(vector_db=qdrant_vdb, embeddata=embeddata)

                    # set up rag
                    query_engine = RAG(retriever=retriever, llm_name="DeepSeek-R1-Distill-Llama-70B")
                    st.session_state.file_cache[file_key] = query_engine
                else:
                    query_engine = st.session_state.file_cache[file_key]

                # Inform the user that the file is processed
                st.success("Ready to Chat!")
                
                # Display audio player
                st.audio(uploaded_file)
                
                # Display speaker-labeled transcript
                st.subheader("Transcript")
                with st.expander("Show full transcript", expanded=True):
                    for t in st.session_state.transcripts:
                        st.text(f"**{t['speaker']}**: {t['text']}")
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.stop()     

col1, col2 = st.columns([6, 1])

with col1:
    st.markdown("""
    # RAG over Audio powered by <img src="data:image/png;base64,{}" width="200" style="vertical-align: -15px; padding-right: 10px;">  and <img src="data:image/png;base64,{}" width="200" style="vertical-align: -5px; padding-left: 10px;">
""".format(base64.b64encode(open("assets/Assemblyai.png", "rb").read()).decode(),
           base64.b64encode(open("assets/deep-seek.png", "rb").read()).decode()), unsafe_allow_html=True)

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
if prompt := st.chat_input("Ask about the audio conversation..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Get streaming response
        streaming_response = query_engine.query(prompt)
        
        for chunk in streaming_response:
            try:
                new_text = chunk.raw["choices"][0]["delta"]["content"]
                full_response += new_text
                message_placeholder.markdown(full_response + "▌")
            except:
                pass

        message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})