import streamlit as st
import os
import tempfile
import time
import logging
from typing import List, Dict, Any
import uuid
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_interactive_citations(response_text: str, sources_used: List[Dict[str, Any]]) -> str:
    import re
    
    logger.info(f"Processing interactive citations for {len(sources_used)} sources")

    citation_map = {}
    for source in sources_used:
        ref = source.get('reference', '')
        if ref:
            match = re.search(r'\[(\d+)\]', ref)
            if match:
                num = match.group(1)
                citation_map[num] = source
    
    def replace_citation(match):
        """Replace citation number with interactive element"""
        full_match = match.group(0)  # e.g., '[1]'
        num = match.group(1)  # e.g., '1'
        
        if num in citation_map:
            source = citation_map[num]
            chunk_content = "Content not available"
            source_info = f"Source: {source.get('source_file', 'Unknown')}"
            
            if source.get('page_number'):
                source_info += f", Page: {source['page_number']}"
            
            try:
                if st.session_state.pipeline and st.session_state.pipeline['vector_db']:
                    chunk_id = source.get('chunk_id')
                    logger.info(f"Processing citation {num} with chunk_id: {chunk_id}")
                    
                    if chunk_id:
                        chunk_data = st.session_state.pipeline['vector_db'].get_chunk_by_id(chunk_id)
                        logger.info(f"Retrieved chunk data: {chunk_data is not None}")
                        
                        if chunk_data and chunk_data.get('content'):
                            chunk_content = chunk_data['content']
                            logger.info(f"Got chunk content: {len(chunk_content)} characters")
                            if len(chunk_content) > 300:
                                chunk_content = chunk_content[:300] + "..."
                        else:
                            chunk_content = "Chunk content not available"
                            logger.warning(f"Chunk data missing or no content: {chunk_data}")
                    else:
                        chunk_content = "No chunk ID provided"
                        logger.warning(f"No chunk_id in source: {source}")
                else:
                    chunk_content = "Vector database not available"
                    logger.warning("Pipeline or vector_db not available")
            except Exception as e:
                logger.error(f"Error retrieving chunk content for citation {num}: {e}")
                chunk_content = f"Error retrieving chunk content: {str(e)}"
            
            chunk_content_escaped = (chunk_content
                                    .replace('<', '&lt;')
                                    .replace('>', '&gt;')
                                    .replace('\n', '<br>')
                                    .replace('"', '&quot;'))
            source_info_escaped = (source_info
                                 .replace('<', '&lt;')
                                 .replace('>', '&gt;')
                                 .replace('"', '&quot;'))
            
            return f'''<span class="citation-number">
                {num}
                <div class="citation-tooltip">
                    <div class="tooltip-source">{source_info_escaped}</div>
                    <div class="tooltip-content">{chunk_content_escaped}</div>
                </div>
            </span>'''
        else:
            return full_match
    
    # Replace all citation patterns [1], [2], etc.
    interactive_text = re.sub(r'\[(\d+)\]', replace_citation, response_text)
    
    return interactive_text

from src.document_processing.doc_processor import DocumentProcessor
from src.embeddings.embedding_generator import EmbeddingGenerator
from src.vector_database.milvus_vector_db import MilvusVectorDB
from src.generation.rag import RAGGenerator
from src.memory.memory_layer import NotebookMemoryLayer
from src.audio_processing.audio_transcriber import AudioTranscriber
from src.audio_processing.youtube_transcriber import YouTubeTranscriber
from src.web_scraping.web_scraper import WebScraper
from src.podcast.script_generator import PodcastScriptGenerator
from src.podcast.text_to_speech import PodcastTTSGenerator

st.set_page_config(
    page_title="NotebookLM",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 24px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 20px;
    }
    
    .source-item {
        background: #2d3748;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        border-left: 3px solid #4299e1;
    }
    
    .source-title {
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 4px;
    }
    
    .source-meta {
        font-size: 12px;
        color: #a0aec0;
    }
    
    .chat-message {
        background: #2d3748;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
    }
    
    .user-message {
        background: #4299e1;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #2d3748;
        margin-right: 20%;
        border-left: 3px solid #48bb78;
    }
    
    .citation {
        background: #1a202c;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 11px;
        color: #90cdf4;
        margin: 2px;
        display: inline-block;
    }
    
    /* Interactive citation styling */
    .citation-number {
        background: #4299e1;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        cursor: pointer;
        display: inline-block;
        margin: 0 2px;
        position: relative;
        transition: all 0.2s ease;
    }
    
    .citation-number:hover {
        background: #3182ce;
        transform: scale(1.1);
    }
    
    /* Tooltip styling */
    .citation-tooltip {
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        background: #2d3748;
        color: #e2e8f0;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        border: 1px solid #4a5568;
        max-width: 400px;
        width: max-content;
        z-index: 1000;
        font-size: 12px;
        line-height: 1.4;
        margin-bottom: 8px;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease;
        pointer-events: none;
    }
    
    .citation-number:hover .citation-tooltip {
        opacity: 1;
        visibility: visible;
    }
    
    /* Tooltip arrow */
    .citation-tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 6px solid transparent;
        border-top-color: #2d3748;
    }
    
    .tooltip-source {
        font-weight: bold;
        color: #4299e1;
        margin-bottom: 6px;
        font-size: 11px;
    }
    
    .tooltip-content {
        max-height: 200px;
        overflow-y: auto;
        text-align: left;
    }
    
    .upload-area {
        border: 2px dashed #4a5568;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        background: #1a202c;
        margin: 20px 0;
    }
    
    .upload-text {
        color: #a0aec0;
        font-size: 16px;
        margin-bottom: 20px;
    }
    
    .stButton > button {
        background: #4299e1;
        color: white;
        border-radius: 6px;
        border: none;
        padding: 8px 24px;
        font-weight: 500;
    }
    
    .source-count {
        background: #4a5568;
        color: #ffffff;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = None
    if 'sources' not in st.session_state:
        st.session_state.sources = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'show_source_dialog' not in st.session_state:
        st.session_state.show_source_dialog = False
    if 'pipeline_initialized' not in st.session_state:
        st.session_state.pipeline_initialized = False

def reset_chat():
    try:
        # Clear existing session from Zep if memory is available
        # if st.session_state.pipeline and st.session_state.pipeline['memory']:
        memory = st.session_state.pipeline['memory']
        try:
            memory.clear_session()
            st.success("✅ Zep session cleared and recreated")
        except Exception as e:
            st.warning(f"Could not clear Zep session: {str(e)}")
        
        st.session_state.chat_history = []
        st.session_state.session_id = str(uuid.uuid4())
        
        # Reinitialize memory with new session if available
        if st.session_state.pipeline and st.session_state.pipeline['memory']:
            new_memory = NotebookMemoryLayer(
                user_id="streamlit_user",
                session_id=st.session_state.session_id,
                create_new_session=True
            )
            st.session_state.pipeline['memory'] = new_memory
            st.success("✅ New Zep session initialized")
        
        st.success("✅ Chat reset successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error resetting chat: {str(e)}")

def initialize_pipeline():
    if st.session_state.pipeline_initialized:
        return True
    
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        assemblyai_key = os.getenv("ASSEMBLYAI_API_KEY")
        firecrawl_key = os.getenv("FIRECRAWL_API_KEY")
        zep_key = os.getenv("ZEP_API_KEY")
        
        with st.spinner("Initializing NotebookLM pipeline..."):
            doc_processor = DocumentProcessor()
            embedding_generator = EmbeddingGenerator()
            vector_db = MilvusVectorDB(
                db_path=f"./milvus_lite_{st.session_state.session_id[:8]}.db", 
                collection_name=f"collection_{st.session_state.session_id[:8]}"
            )
            
            rag_generator = RAGGenerator(
                embedding_generator=embedding_generator,
                vector_db=vector_db,
                openai_api_key=openai_key
            )
            
            audio_transcriber = AudioTranscriber(assemblyai_key) if assemblyai_key else None
            youtube_transcriber = YouTubeTranscriber(assemblyai_key) if assemblyai_key else None
            web_scraper = WebScraper(firecrawl_key) if firecrawl_key else None
            podcast_script_generator = PodcastScriptGenerator(openai_key) if openai_key else None
            
            try:
                podcast_tts_generator = PodcastTTSGenerator() if openai_key else None
                if podcast_tts_generator:
                    logger.info("PodcastTTSGenerator initialized successfully")
            except ImportError:
                logger.warning("Kokoro TTS not available. Podcast audio generation will be disabled.")
                podcast_tts_generator = None
            except Exception as e:
                logger.error(f"Error initializing TTS: {e}")
                podcast_tts_generator = None
            
            memory = None
            if zep_key:
                memory = NotebookMemoryLayer(
                    user_id="streamlit_user",
                    session_id=st.session_state.session_id,
                    create_new_session=True
                )
            
            st.session_state.pipeline = {
                'doc_processor': doc_processor,
                'embedding_generator': embedding_generator,
                'vector_db': vector_db,
                'rag_generator': rag_generator,
                'audio_transcriber': audio_transcriber,
                'youtube_transcriber': youtube_transcriber,
                'web_scraper': web_scraper,
                'podcast_script_generator': podcast_script_generator,
                'podcast_tts_generator': podcast_tts_generator,
                'memory': memory
            }
            
            st.session_state.pipeline_initialized = True
            st.success("✅ Pipeline initialized successfully!")
            return True
            
    except Exception as e:
        st.error(f"❌ Failed to initialize pipeline: {str(e)}")
        return False

def process_uploaded_files(uploaded_files):
    if not st.session_state.pipeline:
        return
    
    pipeline = st.session_state.pipeline

    with st.spinner(f"Processing {len(uploaded_files)} file(s)..."):
        for uploaded_file in uploaded_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_path = tmp_file.name
                
                if uploaded_file.type.startswith('audio/'):
                    if pipeline['audio_transcriber']:
                        chunks = pipeline['audio_transcriber'].transcribe_audio(temp_path)
                        source_type = "Audio"
                        
                        for chunk in chunks:
                            chunk.source_file = uploaded_file.name
                    else:
                        st.warning(f"Audio processing not available for {uploaded_file.name}")
                        os.unlink(temp_path)
                        continue
                else:
                    chunks = pipeline['doc_processor'].process_document(temp_path)
                    source_type = "Document"
                    
                    for chunk in chunks:
                        chunk.source_file = uploaded_file.name
                
                if chunks:
                    embedded_chunks = pipeline['embedding_generator'].generate_embeddings(chunks)
                    
                    if len(st.session_state.sources) == 0:
                        pipeline['vector_db'].create_index(use_binary_quantization=False)
                    
                    pipeline['vector_db'].insert_embeddings(embedded_chunks)
                    
                    source_info = {
                        'name': uploaded_file.name,
                        'type': source_type,
                        'size': f"{len(uploaded_file.getbuffer()) / 1024:.1f} KB",
                        'chunks': len(chunks),
                        'uploaded_at': time.strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.sources.append(source_info)
                    st.success(f"✅ Processed {uploaded_file.name}: {len(chunks)} chunks")
                
                os.unlink(temp_path)
                
            except Exception as e:
                st.error(f"❌ Failed to process {uploaded_file.name}: {str(e)}")
                if 'temp_path' in locals():
                    os.unlink(temp_path)

def process_urls(urls_text):
    if not st.session_state.pipeline or not st.session_state.pipeline['web_scraper']:
        st.warning("Web scraping not available (missing FIRECRAWL_API_KEY)")
        return
    
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    if not urls:
        return
    
    pipeline = st.session_state.pipeline
    
    with st.spinner(f"Scraping {len(urls)} URL(s)..."):
        for url in urls:
            try:
                chunks = pipeline['web_scraper'].scrape_url(url)
                
                if chunks:
                    for chunk in chunks:
                        chunk.source_file = url
                    
                    embedded_chunks = pipeline['embedding_generator'].generate_embeddings(chunks)
                    # Create index if first document
                    if len(st.session_state.sources) == 0:
                        pipeline['vector_db'].create_index(use_binary_quantization=False)
                    
                    pipeline['vector_db'].insert_embeddings(embedded_chunks)
                    source_info = {
                        'name': url,
                        'type': "Website",
                        'size': f"{len(chunks)} chunks",
                        'chunks': len(chunks),
                        'uploaded_at': time.strftime("%Y-%m-%d %H:%M")
                    }
                    st.session_state.sources.append(source_info)
                    st.success(f"✅ Scraped {url}: {len(chunks)} chunks")
                else:
                    st.warning(f"No content extracted from {url}")
                    
            except Exception as e:
                st.error(f"❌ Failed to scrape {url}: {str(e)}")

def process_youtube_video(youtube_url):
    if not st.session_state.pipeline or not st.session_state.pipeline['youtube_transcriber']:
        st.warning("YouTube processing not available (missing ASSEMBLYAI_API_KEY)")
        return
    
    pipeline = st.session_state.pipeline
    transcriber = pipeline['youtube_transcriber']
    
    with st.spinner("Processing YouTube video..."):
        try:
            chunks = transcriber.transcribe_youtube_video(youtube_url, cleanup_audio=True)
            
            if chunks:
                video_id = transcriber.extract_video_id(youtube_url)
                video_name = f"YouTube Video {video_id}"
                for chunk in chunks:
                    chunk.source_file = video_name
                
                embedded_chunks = pipeline['embedding_generator'].generate_embeddings(chunks)
                
                if len(st.session_state.sources) == 0:
                    pipeline['vector_db'].create_index(use_binary_quantization=False)
                
                pipeline['vector_db'].insert_embeddings(embedded_chunks)
                
                source_info = {
                    'name': video_name,
                    'type': "YouTube Video",
                    'size': f"{len(chunks)} utterances",
                    'chunks': len(chunks),
                    'uploaded_at': time.strftime("%Y-%m-%d %H:%M"),
                    'url': youtube_url,
                    'video_id': video_id
                }
                st.session_state.sources.append(source_info)
                st.success(f"✅ Processed YouTube video: {len(chunks)} utterances")
            else:
                st.warning("No transcript content extracted from the video")
                
        except Exception as e:
            st.error(f"❌ Failed to process YouTube video: {str(e)}")
            logger.error(f"YouTube processing error: {str(e)}")

def process_text(text_content):
    if not st.session_state.pipeline or not text_content.strip():
        return
    
    pipeline = st.session_state.pipeline
    
    with st.spinner("Processing text..."):
        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(text_content)
                temp_path = tmp_file.name
            
            chunks = pipeline['doc_processor'].process_document(temp_path)
            
            original_name = f"Pasted Text ({time.strftime('%H:%M')})"
            for chunk in chunks:
                chunk.source_file = original_name
            
            if chunks:
                embedded_chunks = pipeline['embedding_generator'].generate_embeddings(chunks)
                
                if len(st.session_state.sources) == 0:
                    pipeline['vector_db'].create_index(use_binary_quantization=False)
                
                pipeline['vector_db'].insert_embeddings(embedded_chunks)
                
                source_info = {
                    'name': original_name,
                    'type': "Text",
                    'size': f"{len(text_content)} chars",
                    'chunks': len(chunks),
                    'uploaded_at': time.strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.sources.append(source_info)
                st.success(f"✅ Processed text: {len(chunks)} chunks")
            
            os.unlink(temp_path)
            
        except Exception as e:
            st.error(f"❌ Failed to process text: {str(e)}")

def render_sources_sidebar():
    with st.sidebar:
        st.markdown('<div class="main-header">📚 Sources</div>', unsafe_allow_html=True)
        
        # if st.button("➕ Add", use_container_width=True):
        #     st.session_state.show_source_dialog = True
        
        # Display sources
        if st.session_state.sources:
            st.markdown(f'<div class="source-count">{len(st.session_state.sources)} sources</div>', unsafe_allow_html=True)
            
            for i, source in enumerate(st.session_state.sources):
                with st.container():
                    st.markdown(f'''
                    <div class="source-item">
                        <div class="source-title">{source['name']}</div>
                        <div class="source-meta">{source['type']} • {source['size']} • {source['chunks']} chunks</div>
                        <div class="source-meta">{source['uploaded_at']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 20px; color: #a0aec0;">
                <p>Saved sources will appear here</p>
                <p style="font-size: 14px;">Click Add source above to add PDFs, websites, text, videos, or audio files.</p>
            </div>
            """, unsafe_allow_html=True)

def render_source_upload_dialog():
    st.markdown("### 📁 Add sources")
    st.markdown("""
    Sources let NotebookLM base its responses on the information that matters most to you.  
    (Examples: marketing plans, course reading, research notes, meeting transcripts, sales documents, etc.)
    """)
    
    # File upload section
    st.markdown("#### Upload sources")
    uploaded_files = st.file_uploader(
        "Drag & drop or choose file to upload",
        accept_multiple_files=True,
        type=['pdf', 'txt', 'md', 'mp3', 'wav', 'm4a', 'ogg'],
        help="Supported file types: PDF, .txt, Markdown, Audio (e.g. mp3)"
    )
    
    if uploaded_files:
        if st.button("Process Files"):
            process_uploaded_files(uploaded_files)
            st.rerun()
    
    # Tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["🌐 Website", "🎥 YouTube", "📋 Paste text"])
    
    with tab1:
        st.markdown("#### Website URLs")
        urls_text = st.text_area(
            "Paste in Web URLs below to upload as sources",
            placeholder="https://example.com\nhttps://another-site.com",
            help="To add multiple URLs, separate with a space or new line.\nOnly the visible text on the website will be imported.\nPaid articles are not supported."
        )
        if st.button("Process URLs", key="url_btn") and urls_text.strip():
            process_urls(urls_text)
            st.rerun()
    
    with tab2:
        st.markdown("#### YouTube Videos")
        youtube_url = st.text_input(
            "Paste YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste a YouTube video URL to extract and transcribe its audio content"
        )
        
        if st.button("Process YouTube Video", key="youtube_btn") and youtube_url.strip():
            process_youtube_video(youtube_url.strip())
            st.rerun()
    
    with tab3:
        st.markdown("#### Paste copied text")
        text_content = st.text_area(
            "Paste your copied text below to upload as a source",
            placeholder="Paste text here...",
            height=200
        )
        if st.button("Process Text", key="text_btn") and text_content.strip():
            process_text(text_content)
            st.rerun()

def render_chat_interface():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="main-header">💬 Chat</div>', unsafe_allow_html=True)
    with col2:
        if st.session_state.chat_history:
            if st.button("🗑️ Reset", help="Clear chat history and start new session"):
                reset_chat()
    
    if not st.session_state.sources:
        st.markdown("""
        <div class="upload-area">
            <div class="upload-text">Add a source in the "Add Sources" tab to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'''
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                ''', unsafe_allow_html=True)
            else:
                content_to_display = message.get('interactive_content', message['content'])
                
                st.markdown(f'''
                <div class="chat-message assistant-message">
                    <strong>Assistant:</strong> {content_to_display}
                </div>
                ''', unsafe_allow_html=True)
                
                if 'citations' in message and not message.get('interactive_content'):
                    citation_html = "".join([f'<span class="citation">{cite}</span>' for cite in message['citations']])
                    st.markdown(f'<div style="margin-top: 8px;">{citation_html}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([10, 1])
        with col1:
            query = st.text_input(
                "Upload a source to get started",
                placeholder="Ask me anything about your sources...",
                key="chat_input"
            )
        with col2:
            send_button = st.button("➤", key="send_btn")
        
        if send_button and query.strip() and st.session_state.pipeline:
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.pipeline['rag_generator'].generate_response(query)
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': query
                    })
                    
                    interactive_response = None
                    if result.sources_used:
                        try:
                            interactive_response = create_interactive_citations(result.response, result.sources_used)
                            logger.info(f"Created interactive citations for {len(result.sources_used)} sources")
                        except Exception as e:
                            logger.error(f"Failed to create interactive citations: {e}")
                    else:
                        logger.info("No sources available for interactive citations")
                    
                    citations = []
                    for source in result.sources_used:
                        cite_text = f"Source: {source.get('source_file', 'Unknown')}"
                        if source.get('page_number'):
                            cite_text += f", Page: {source['page_number']}"
                        citations.append(cite_text)
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': result.response,
                        'interactive_content': interactive_response,
                        'citations': citations,
                        'sources_used': result.sources_used
                    })
                    
                    if st.session_state.pipeline['memory']:
                        st.session_state.pipeline['memory'].save_conversation_turn(result)
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

def generate_podcast(selected_source: str, podcast_style: str, podcast_length: str):
    if not st.session_state.pipeline or not st.session_state.pipeline['podcast_script_generator']:
        st.error("Podcast generation not available. Please check your OpenAI API key.")
        return
    
    pipeline = st.session_state.pipeline
    
    try:
        source_info = None
        for source in st.session_state.sources:
            if source['name'] == selected_source:
                source_info = source
                break
        
        if not source_info:
            st.error(f"Could not find source: {selected_source}")
            return
        
        # Gather content from the selected source
        with st.spinner(f"📚 Gathering content from {selected_source}..."):
            try:
                query_embedding = pipeline['embedding_generator'].generate_query_embedding(f"content from {selected_source}")
                search_results = pipeline['vector_db'].search(
                    query_embedding, 
                    limit=50,
                    filter_expr=f'source_file == "{selected_source}"'
                )
                
                if not search_results:
                    st.error(f"Could not find content for {selected_source}. Please try again.")
                    return
                
                search_results.sort(key=lambda x: x.get('chunk_index', 0))
                
            except Exception as e:
                st.error(f"Error retrieving content from {selected_source}: {e}")
                return
        
        with st.spinner("✍️ Generating podcast script..."):
            script_generator = pipeline['podcast_script_generator']
            
            if source_info['type'] == 'Website':
                # For websites, use the specialized website method
                from dataclasses import dataclass
                
                @dataclass
                class ChunkLike:
                    content: str
                
                chunks = [ChunkLike(content=result['content']) for result in search_results]
                
                podcast_script = script_generator.generate_script_from_website(
                    website_chunks=chunks,
                    source_url=selected_source,
                    podcast_style=podcast_style.lower(),
                    target_duration=podcast_length
                )
            else:
                # For documents, audio, text, etc., use the text method
                combined_content = "\n\n".join([result['content'] for result in search_results])
                
                podcast_script = script_generator.generate_script_from_text(
                    text_content=combined_content,
                    source_name=selected_source,
                    podcast_style=podcast_style.lower(),
                    target_duration=podcast_length
                )
            
            st.success(f"✅ Generated podcast script with {podcast_script.total_lines} dialogue segments!")
            
            # Store script in session state for audio generation
            st.session_state.current_podcast_script = podcast_script
        
        # Automatically generate audio if TTS is available
        tts_generator = pipeline.get('podcast_tts_generator')
        if tts_generator:
            with st.spinner("🎵 Generating podcast... This may take several minutes..."):
                try:
                    import tempfile
                    temp_dir = tempfile.mkdtemp(prefix="podcast_")
                    
                    # Generate audio
                    audio_files = tts_generator.generate_podcast_audio(
                        podcast_script=podcast_script,
                        output_dir=temp_dir,
                        combine_audio=True
                    )
                    
                    st.success(f"✅ Generated {len(audio_files)} audio files!")
                    
                    st.markdown("### 🎙️ Generated Podcast")
                    for audio_file in audio_files:
                        file_name = Path(audio_file).name
                        
                        if "complete_podcast" in file_name:
                            st.audio(audio_file, format="audio/wav")
                            
                            with open(audio_file, "rb") as f:
                                st.download_button(
                                    label="📥 Download Complete Podcast",
                                    data=f.read(),
                                    file_name=f"complete_podcast_{int(time.time())}.wav",
                                    mime="audio/wav"
                                )
                
                except Exception as e:
                    st.error(f"❌ Audio generation failed: {str(e)}")
                    logger.error(f"Audio generation error: {e}")
                    
                    if "No module named" in str(e):
                        st.error("🔧 Missing dependency. Please check the installation.")
                    elif "File" in str(e) and "not found" in str(e):
                        st.error("📁 File system error. Check permissions and disk space.")
        else:
            st.warning("⚠️ Audio generation not available - TTS not initialized.")
        
        # Display the generated script
        st.markdown("### 📝 Generated Podcast Script")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Lines", podcast_script.total_lines)
        with col2:
            st.metric("⏱️ Est. Duration", podcast_script.estimated_duration)
        with col3:
            st.metric("📚 Source Type", source_info['type'])
        
        # Display script content
        with st.expander("👀 View Complete Script", expanded=True):
            for i, line_dict in enumerate(podcast_script.script, 1):
                speaker, dialogue = next(iter(line_dict.items()))
                
                # Color code speakers
                if speaker == "Speaker 1":
                    st.markdown(f'<div style="background: #1e3a8a; padding: 10px; border-radius: 5px; margin: 5px 0;"><strong>👩 {speaker}:</strong> {dialogue}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="background: #166534; padding: 10px; border-radius: 5px; margin: 5px 0;"><strong>👨 {speaker}:</strong> {dialogue}</div>', unsafe_allow_html=True)
        
        script_json = podcast_script.to_json()
        st.download_button(
            label="📥 Download Script (JSON)",
            data=script_json,
            file_name=f"podcast_script_{int(time.time())}.json",
            mime="application/json"
        )
    
    except Exception as e:
        st.error(f"❌ Podcast generation failed: {str(e)}")
        logger.error(f"Podcast generation error: {e}")

def render_studio_tab():
    st.markdown('<div class="main-header">🎙️ Studio</div>', unsafe_allow_html=True)
    
    if not st.session_state.sources:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #a0aec0;">
            <p>Studio output will be saved here.</p>
            <p>After adding sources, click to add Podcast Generation and more!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("#### 🎙️ Generate Podcast")
        st.markdown("Create an AI-generated podcast discussion from your documents")
        
        source_names = [source['name'] for source in st.session_state.sources]
        selected_source = st.selectbox(
            "Select source for podcast",
            source_names,
            index=0 if source_names else None,
            help="Choose a document to create a podcast discussion about"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            podcast_style = st.selectbox(
                "Podcast Style",
                ["Conversational", "Interview", "Debate", "Educational"]
            )
        with col2:
            podcast_length = st.selectbox(
                "Duration",
                ["5 minutes", "10 minutes", "15 minutes", "20 minutes"]
            )
        
        if st.button("🎙️ Generate Podcast", use_container_width=True):
            if selected_source:
                generate_podcast(selected_source, podcast_style, podcast_length)
            else:
                st.warning("Please select a source for the podcast")

def main():
    init_session_state()
    
    st.markdown("""
    <div style="display: flex; align-items: center; margin-bottom: 30px;">
        <h1 style="color: #ffffff; margin: 0;">🧠 NotebookLM: Understand Anything</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if not initialize_pipeline():
        st.stop()
    
    render_sources_sidebar()
    
    tab1, tab2, tab3 = st.tabs(["📁 Add Sources", "💬 Chat", "🎙️ Studio"])
    with tab1:
        render_source_upload_dialog()
    with tab2:
        render_chat_interface()
    with tab3:
        render_studio_tab()
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #a0aec0; font-size: 12px;">
        NotebookLM can be inaccurate; please double check its responses.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
