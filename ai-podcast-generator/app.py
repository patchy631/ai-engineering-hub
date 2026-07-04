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
        color: #ffffff;
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

st.markdown('<div class="sub-header">Transform any web article into an engaging podcast</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("API Keys")
    minimax_key = st.text_input("Minimax API Key", type="password", help="Get your key from platform.minimax.io")
    firecrawl_key = st.text_input("Firecrawl API Key", type="password", help="Get your key from firecrawl.dev")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", help="Get your key from openrouter.ai")
    
    st.divider()
    
    st.subheader("📝 Input")
    url = st.text_input("Article URL", placeholder="https://example.com/article")
    
    st.divider()
    
    generate_btn = st.button("🚀 Generate Podcast", type="primary", use_container_width=True)

# Main area
if generate_btn:
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
                        progress_text.text(f"Processing segment {i}/{total_segments} ...")
                        voice = converter.voices.get(speaker, converter.voices["male"])
                        audio_file = os.path.join(audio_dir, f"segment_{i:03d}.mp3")
                        
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
                    # Verify all files exist and filter out corrupted ones
                    st.info(f"Verifying {len(audio_files)} audio files...")
                    valid_files = []
                    corrupted_segments = []
                    
                    for i, (speaker, filepath) in enumerate(audio_files, 1):
                        if not os.path.exists(filepath):
                            corrupted_segments.append(i)
                            st.warning(f"⚠️ Segment {i} missing")
                            continue
                        
                        file_size = os.path.getsize(filepath)
                        if file_size < 1024:  # Less than 1KB is likely corrupted
                            corrupted_segments.append(i)
                            st.warning(f"⚠️ Segment {i} corrupted ({file_size} bytes)")
                            continue
                        
                        # Verify it's a valid MP3
                        try:
                            test_audio = AudioSegment.from_mp3(filepath)
                            if len(test_audio) < 100:  # Less than 100ms is suspicious
                                corrupted_segments.append(i)
                                st.warning(f"⚠️ Segment {i} too short")
                                continue
                        except Exception as e:
                            corrupted_segments.append(i)
                            st.warning(f"⚠️ Segment {i} invalid MP3: {str(e)}")
                            continue
                        
                        valid_files.append((speaker, filepath))
                        st.text(f"✓ Segment {i} verified ({file_size} bytes)")
                    
                    if corrupted_segments:
                        st.warning(f"⚠️ Skipping {len(corrupted_segments)} corrupted segments: {corrupted_segments}")
                    
                    if len(valid_files) == 0:
                        raise Exception("No valid audio segments to merge")
                    
                    st.info(f"Merging {len(valid_files)} valid audio segments...")
                    combined = AudioSegment.empty()
                    
                    for i, (speaker, filepath) in enumerate(valid_files, 1):
                        st.text(f"Adding segment {i}/{len(valid_files)}...")
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
                    if corrupted_segments:
                        st.info(f"ℹ️ Note: {len(corrupted_segments)} segments were skipped due to corruption")
                    status.update(label="✅ Podcast ready!", state="complete")
                    
                    # Update audio_files to only include valid ones
                    audio_files = valid_files
                    
                except Exception as e:
                    st.error(f"❌ Audio merging failed: {str(e)}")
                    st.write("Debug info:")
                    st.write(f"Audio directory: {audio_dir}")
                    st.write(f"Files in directory: {os.listdir(audio_dir) if os.path.exists(audio_dir) else 'Directory not found'}")
                    st.stop()
        
        st.divider()
        st.header("📊 Results")
        
        tab1, tab2 = st.tabs(["🎧 Podcast", "📝 Script"])
        
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
        
        st.balloons()

else:
    st.info("👈 Get started by entering your API keys in the sidebar and providing an article URL")
    
    with st.expander("ℹ️ How it works"):
        st.markdown("""
        1. **Scraping**: We use Firecrawl to extract clean content from any URL
        2. **Script Generation**: Minimax-M2.1 transforms the content into an engaging dialogue
        3. **Audio Synthesis**: Minimax Speech 2.6 creates natural-sounding voices for both hosts
        4. **Merging**: All segments are combined into one seamless podcast
        """)
    
    with st.expander("🔑 Where to get API keys"):
        st.markdown("""
        - **Minimax**: [platform.minimax.io](https://platform.minimax.io)
        - **Firecrawl**: [firecrawl.dev](https://firecrawl.dev)
        - **OpenRouter**: [openrouter.ai](https://openrouter.ai)
        """)