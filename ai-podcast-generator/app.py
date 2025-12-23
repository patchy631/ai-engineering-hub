import os
import tempfile
import streamlit as st
from pathlib import Path
from pydub import AudioSegment

from scraper import WebScraper
from script_generator import ScriptGenerator
from tts_converter import TTSConverter

# Page config
st.set_page_config(
    page_title="AI Podcast Generator",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .status-success {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-info {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    .status-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎙️ AI Podcast Generator</div>', unsafe_allow_html=True)

# Powered by widget
st.markdown('''
    <div style="text-align: center; margin-bottom: 30px;">
        <div style="display: flex; justify-content: center; align-items: center; gap: 8px; margin-bottom: 20px;">
            <span style='color: #64748b; font-size: 16px; font-weight: 500;'>Powered by</span>
            <div style="display: flex; align-items: center; gap: 25px; margin-left: 15px;">
                <a href="https://platform.minimax.io/" target="_blank" style="display: inline-block; vertical-align: middle; text-decoration: none;">
                    <img src="http://largelanguagemodel.com.tr/api/uploads/2863cd18-0ce7-4b89-bf7d-702e01575400/MiniMaxLogo-Dark.png" 
                         alt="Minimax" style="height: 40px;">
                </a>
                <a href="https://www.firecrawl.dev/" target="_blank" style="display: inline-block; vertical-align: middle; text-decoration: none;">
                    <img src="https://i.ibb.co/67jyMHfy/firecrawl-light-wordmark.png" 
                         alt="Firecrawl" style="height: 28px;">
                </a>
            </div>
        </div>
    </div>
''', unsafe_allow_html=True)

st.markdown('<div class="sub-header">Transform any article into an engaging podcast conversation</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    firecrawl_key = st.text_input("Firecrawl API Key", type="password", help="Get your key from firecrawl.dev")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", help="Get your key from openrouter.ai")
    minimax_key = st.text_input("Minimax API Key", type="password", help="Get your key from platform.minimax.io")
    
    st.divider()
    
    st.subheader("📝 Input")
    url = st.text_input("Article URL", placeholder="https://example.com/article")
    
    st.divider()
    
    generate_btn = st.button("🚀 Generate Podcast", type="primary", use_container_width=True)
    
    st.divider()
    st.caption("💡 Tip: Make sure all API keys are valid before generating")

# Main area
if generate_btn:
    if not all([firecrawl_key, openrouter_key, minimax_key, url]):
        st.error("❌ Please fill in all API keys and provide a URL")
    else:
        os.environ['FIRECRAWL_API_KEY'] = firecrawl_key
        os.environ['OPENROUTER_API_KEY'] = openrouter_key
        os.environ['MINIMAX_API_KEY'] = minimax_key
        
        progress_container = st.container()
        
        with progress_container:
            # Step 1: Scraping
            with st.status("🌐 Scraping content from URL...", expanded=True) as status:
                try:
                    scraper = WebScraper()
                    content = scraper.scrape(url)
                    st.success(f"✅ Successfully scraped {len(content)} characters")
                    status.update(label="✅ Content scraped successfully!", state="complete")
                except Exception as e:
                    st.error(f"❌ Scraping failed: {str(e)}")
                    st.stop()
            
            # Step 2: Script Generation
            with st.status("✍️ Generating podcast script...", expanded=True) as status:
                try:
                    generator = ScriptGenerator()
                    script = generator.generate(content)
                    st.success("✅ Podcast script generated successfully")
                    status.update(label="✅ Script generated successfully!", state="complete")
                except Exception as e:
                    st.error(f"❌ Script generation failed: {str(e)}")
                    st.stop()
            
            # Step 3: Audio Generation
            with st.status("🎙️ Converting script to audio...", expanded=True) as status:
                try:
                    converter = TTSConverter()
                    
                    # Parse script to get segment count
                    segments = converter._parse_script(script)
                    total_segments = len(segments)
                    
                    st.info(f"Generating {total_segments} audio segments...")
                    
                    progress_bar = st.progress(0)
                    progress_text = st.empty()
                    
                    # Create persistent audio directory
                    audio_dir = tempfile.mkdtemp()
                    audio_files = []
                    
                    for i, (speaker, text) in enumerate(segments, 1):
                        progress_text.text(f"Processing segment {i}/{total_segments} ({speaker})...")
                        voice = converter.voices.get(speaker, converter.voices["male"])
                        audio_file = os.path.join(audio_dir, f"segment_{i:03d}_{speaker}.mp3")
                        
                        converter._generate_and_save_speech(text, voice, audio_file)
                        
                        # Verify file exists before adding to list
                        if os.path.exists(audio_file) and os.path.getsize(audio_file) > 0:
                            audio_files.append((speaker, audio_file))
                        else:
                            raise Exception(f"Failed to generate audio for segment {i}")
                        
                        progress_bar.progress(i / total_segments)
                    
                    progress_text.text("✅ All segments generated!")
                    status.update(label="✅ Audio generated successfully!", state="complete")
                    
                except Exception as e:
                    st.error(f"❌ Audio generation failed: {str(e)}")
                    st.stop()
            
            # Step 4: Merge Audio
            with st.status("🔗 Merging audio segments...", expanded=True) as status:
                try:
                    # Verify all files exist before merging
                    st.info(f"Verifying {len(audio_files)} audio files...")
                    for i, (speaker, filepath) in enumerate(audio_files, 1):
                        if not os.path.exists(filepath):
                            raise Exception(f"Audio file missing: {filepath}")
                        if os.path.getsize(filepath) == 0:
                            raise Exception(f"Audio file is empty: {filepath}")
                        st.text(f"✓ Segment {i} verified ({os.path.getsize(filepath)} bytes)")
                    
                    st.info("Merging audio segments...")
                    combined = AudioSegment.empty()
                    
                    for i, (speaker, filepath) in enumerate(audio_files, 1):
                        st.text(f"Adding segment {i}/{len(audio_files)}...")
                        audio = AudioSegment.from_mp3(filepath)
                        combined += audio
                    
                    # Export merged audio
                    output_path = os.path.join(audio_dir, "full_podcast.mp3")
                    st.info("Exporting final podcast...")
                    combined.export(output_path, format="mp3")
                    
                    # Verify output file
                    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                        raise Exception("Failed to create merged podcast file")
                    
                    st.success(f"✅ Podcast merged successfully ({os.path.getsize(output_path)} bytes)")
                    status.update(label="✅ Podcast ready!", state="complete")
                    
                except Exception as e:
                    st.error(f"❌ Audio merging failed: {str(e)}")
                    st.write("Debug info:")
                    st.write(f"Audio directory: {audio_dir}")
                    st.write(f"Files in directory: {os.listdir(audio_dir) if os.path.exists(audio_dir) else 'Directory not found'}")
                    st.stop()
        
        st.divider()
        st.header("📊 Results")
        
        tab1, tab2, tab3 = st.tabs(["🎧 Podcast", "📝 Script", "🎵 Individual Segments"])
        
        with tab1:
            st.subheader("Full Podcast")
            with open(output_path, "rb") as f:
                st.audio(f.read(), format="audio/mp3")
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Full Podcast",
                    data=f.read(),
                    file_name="podcast.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
        
        with tab2:
            st.subheader("Podcast Script")
            st.text_area("", script, height=400)
            
            st.download_button(
                label="📥 Download Script",
                data=script,
                file_name="podcast_script.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with tab3:
            st.subheader("Individual Audio Segments")
            for i, (speaker, filepath) in enumerate(audio_files, 1):
                with st.expander(f"Segment {i} - {speaker.title()}"):
                    with open(filepath, "rb") as f:
                        audio_data = f.read()
                        st.audio(audio_data, format="audio/mp3")
                        st.download_button(
                            label=f"Download Segment {i}",
                            data=audio_data,
                            file_name=f"segment_{i}_{speaker}.mp3",
                            mime="audio/mp3",
                            key=f"download_{i}"
                        )
        
        st.balloons()

else:
    st.info("👈 Get started by entering your API keys in the sidebar and providing an article URL")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Scraping**: We use Firecrawl to extract clean content from any URL
        2. **Script Generation**: Minimax-M2 transforms the content into an engaging dialogue
        3. **Audio Synthesis**: Minimax TTS creates natural-sounding voices for both hosts
        4. **Merging**: All segments are combined into one seamless podcast
        """)
    
    with st.expander("🔑 Where to get API keys"):
        st.markdown("""
        - **Firecrawl**: [firecrawl.dev](https://firecrawl.dev)
        - **OpenRouter**: [openrouter.ai](https://openrouter.ai)
        - **Minimax**: [platform.minimax.io](https://platform.minimax.io)
        """)