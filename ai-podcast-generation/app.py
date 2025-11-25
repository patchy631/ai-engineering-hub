import streamlit as st
import os
import tempfile
import time
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.podcast.script_generator import PodcastScriptGenerator
from src.podcast.text_to_speech import PodcastTTSGenerator
from src.web_scraping.web_scraper import WebScraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Podsite - AI Podcast Generator",
    page_icon="🎙️",
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

    .script-segment {
        background: #1a202c;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }

    .speaker-1 {
        border-left: 3px solid #ec4899;
    }

    .speaker-2 {
        border-left: 3px solid #10b981;
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

def init_session_state():
    if 'sources' not in st.session_state:
        st.session_state.sources = []
    if 'script_generator' not in st.session_state:
        st.session_state.script_generator = None
    if 'tts_generator' not in st.session_state:
        st.session_state.tts_generator = None
    if 'web_scraper' not in st.session_state:
        st.session_state.web_scraper = None
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    if 'firecrawl_key' not in st.session_state:
        # st.session_state.firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "")
        st.session_state.firecrawl_key = None

def initialize_generators():
    if st.session_state.initialized:
        return True

    openai_key = os.getenv("OPENAI_API_KEY")

    if not openai_key:
        st.error("❌ OPENAI_API_KEY not found. Please set it in your .env file.")
        return False

    try:
        st.session_state.script_generator = PodcastScriptGenerator(openai_key)

        # Initialize TTS in background - don't block UI
        if st.session_state.tts_generator is None:
            try:
                st.session_state.tts_generator = PodcastTTSGenerator()
                logger.info("TTS Generator initialized successfully")
            except ImportError:
                logger.warning("Kokoro TTS not available. Podcast audio generation will be disabled.")
                st.session_state.tts_generator = None
            except Exception as e:
                logger.error(f"Error initializing TTS: {e}")
                st.session_state.tts_generator = None

        st.session_state.initialized = True
        return True

    except Exception as e:
        st.error(f"❌ Failed to initialize: {str(e)}")
        logger.error(f"Initialization error: {e}")
        return False

def initialize_web_scraper(api_key: str):
    """Initialize or reinitialize web scraper with provided API key"""
    if api_key:
        try:
            st.session_state.web_scraper = WebScraper(api_key)
            st.session_state.firecrawl_key = api_key
            logger.info("Web scraper initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize web scraper: {e}")
            st.error(f"❌ Failed to initialize web scraper: {str(e)}")
            return False
    return False

def add_url_source(url: str):
    if not st.session_state.web_scraper:
        st.error("Web scraper not available. Please add FIRECRAWL_API_KEY to your .env file.")
        return

    with st.spinner(f"Scraping {url}..."):
        try:
            result = st.session_state.web_scraper.scrape_url(url)

            if result['success'] and result['content']:
                source_info = {
                    'name': result['title'],
                    'url': url,
                    'type': 'Website',
                    'content': result['content'],
                    'word_count': result['word_count'],
                    'added_at': time.strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.sources.append(source_info)
                st.success(f"✅ Added: {result['title']} ({result['word_count']} words)")
            else:
                st.error(f"❌ Failed to scrape URL: {result.get('error', 'No content found')}")

        except Exception as e:
            st.error(f"❌ Error scraping URL: {str(e)}")
            logger.error(f"URL scraping error: {e}")

def add_text_source(text_content: str, source_name: str):
    if not text_content.strip():
        st.warning("Please enter some text content")
        return

    source_info = {
        'name': source_name,
        'url': None,
        'type': 'Text',
        'content': text_content,
        'word_count': len(text_content.split()),
        'added_at': time.strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.sources.append(source_info)
    st.success(f"✅ Added: {source_name} ({len(text_content.split())} words)")

def remove_source(index: int):
    if 0 <= index < len(st.session_state.sources):
        removed = st.session_state.sources.pop(index)
        st.success(f"✅ Removed: {removed['name']}")
        st.rerun()

def render_sources_sidebar():
    with st.sidebar:
        st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)

        # Firecrawl API Key input
        st.markdown("#### 🔑 Firecrawl API Key")
        firecrawl_input = st.text_input(
            "Enter Firecrawl API Key",
            value=st.session_state.firecrawl_key,
            type="password",
            help="Required for web scraping. Get your key from https://firecrawl.dev",
            key="firecrawl_input"
        )

        if firecrawl_input != st.session_state.firecrawl_key:
            if st.button("Save API Key", use_container_width=True):
                if initialize_web_scraper(firecrawl_input):
                    st.success("✅ API key saved!")
                    st.rerun()

        st.markdown("---")

        # Add URL section
        st.markdown("#### 🌐 Add Website")
        url_input = st.text_input(
            "Website URL",
            placeholder="https://example.com/article",
            help="Paste a URL to scrape content",
            key="sidebar_url"
        )

        if st.button("Add Website", key="sidebar_add_url", use_container_width=True):
            if url_input.strip():
                add_url_source(url_input.strip())
                st.rerun()
            else:
                st.warning("Please enter a URL")

        st.markdown("---")

        # Sources list
        st.markdown('<div class="main-header">📚 Sources</div>', unsafe_allow_html=True)

        if st.session_state.sources:
            st.markdown(f'<div class="source-count">{len(st.session_state.sources)} sources</div>', unsafe_allow_html=True)

            for i, source in enumerate(st.session_state.sources):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f'''
                        <div class="source-item">
                            <div class="source-title">{source['name']}</div>
                            <div class="source-meta">{source['type']} • {source['word_count']} words</div>
                            <div class="source-meta">{source['added_at']}</div>
                        </div>
                        ''', unsafe_allow_html=True)
                    with col2:
                        if st.button("🗑️", key=f"del_{i}", help="Remove source"):
                            remove_source(i)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 20px; color: #a0aec0;">
                <p>No sources added yet</p>
                <p style="font-size: 14px;">Add websites or text to generate podcasts</p>
            </div>
            """, unsafe_allow_html=True)

def generate_podcast(selected_source_name: str, podcast_style: str, podcast_length: str):
    if not st.session_state.script_generator:
        st.error("Script generator not available")
        return

    source_info = None
    for source in st.session_state.sources:
        if source['name'] == selected_source_name:
            source_info = source
            break

    if not source_info:
        st.error("Source not found")
        return

    try:
        with st.spinner("✍️ Generating podcast script..."):
            podcast_script = st.session_state.script_generator.generate_script_from_text(
                text_content=source_info['content'],
                source_name=source_info['name'],
                podcast_style=podcast_style.lower(),
                target_duration=podcast_length
            )

            st.success(f"✅ Generated podcast script with {podcast_script.total_lines} dialogue segments!")

        if st.session_state.tts_generator:
            with st.spinner("🎵 Generating podcast audio... This may take several minutes..."):
                try:
                    temp_dir = tempfile.mkdtemp(prefix="podcast_")

                    audio_files = st.session_state.tts_generator.generate_podcast_audio(
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
        else:
            st.warning("⚠️ Audio generation not available - TTS not initialized.")

        st.markdown("### 📝 Generated Podcast Script")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Total Lines", podcast_script.total_lines)
        with col2:
            st.metric("⏱️ Est. Duration", podcast_script.estimated_duration)
        with col3:
            st.metric("📚 Source Type", source_info['type'])

        with st.expander("👀 View Complete Script", expanded=True):
            for i, line_dict in enumerate(podcast_script.script, 1):
                speaker, dialogue = next(iter(line_dict.items()))

                if speaker == "Speaker 1":
                    st.markdown(f'<div class="script-segment speaker-1"><strong>👩 {speaker}:</strong> {dialogue}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="script-segment speaker-2"><strong>👨 {speaker}:</strong> {dialogue}</div>', unsafe_allow_html=True)

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

def render_add_sources_tab():
    st.markdown("### 📁 Add Text Source")
    st.markdown("""
    Paste text content to create podcasts. Use the sidebar to add website URLs.
    """)

    source_name = st.text_input(
        "Source Name",
        placeholder="e.g., Article Title, Research Notes",
        help="Give your text content a name"
    )

    text_content = st.text_area(
        "Text Content",
        placeholder="Paste your text here...",
        height=400,
        help="Enter the text content you want to convert into a podcast"
    )

    if st.button("Add Text Source", use_container_width=True) and text_content.strip():
        name = source_name.strip() if source_name.strip() else f"Text ({time.strftime('%H:%M')})"
        add_text_source(text_content, name)
        st.rerun()

def render_studio_tab():
    st.markdown('<div class="main-header">🎙️ Studio</div>', unsafe_allow_html=True)

    if not st.session_state.sources:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #a0aec0;">
            <p>No sources available</p>
            <p>Add sources in the "Add Sources" tab to generate podcasts!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("#### 🎙️ Generate Podcast")
        st.markdown("Create an AI-generated podcast discussion from your content")

        source_names = [source['name'] for source in st.session_state.sources]
        selected_source = st.selectbox(
            "Select Source",
            source_names,
            help="Choose content to create a podcast from"
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
                ["5 minutes", "10 minutes", "15 minutes", "20 minutes"],
                index=1
            )

        if st.button("🎙️ Generate Podcast", use_container_width=True):
            if selected_source:
                generate_podcast(selected_source, podcast_style, podcast_length)
            else:
                st.warning("Please select a source")

def main():
    init_session_state()

    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #ffffff; margin: 0;">🎙️ Podsite</h1>
        <p style="color: #a0aec0; font-size: 18px;">Transform Web Content into Engaging Podcasts</p>
    </div>
    """, unsafe_allow_html=True)

    initialize_generators()

    render_sources_sidebar()

    tab1, tab2 = st.tabs(["📋 Add Text", "🎙️ Studio"])

    with tab1:
        render_add_sources_tab()

    with tab2:
        render_studio_tab()

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #a0aec0; font-size: 12px;">
        Podsite - AI-Powered Podcast Generation | Built with Streamlit & OpenAI
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
