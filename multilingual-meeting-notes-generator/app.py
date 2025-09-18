"""
Meeting Notes Generator

Automatically generates meeting notes from audio files with speaker identification,
summaries, and action items.
"""

import streamlit as st
import tempfile
import os
import gc
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from src.services.audio_processor import MeetingProcessor
from src.ui.ui_components import (
    display_meeting_header,
    display_meeting_summary,
    display_speaker_analysis,
    display_action_items,
    display_meeting_transcript
)


def main():
    """Main application function."""
    st.set_page_config(
        page_title="Multilingual Meeting Notes Generator", 
        layout="wide"
    )
    
    # Initialize session state variables
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    
    # Sidebar
    with st.sidebar:
        # Configuration
        st.header("🔧 Configuration")
        
        # API key input fields
        assemblyai_key = st.text_input(
            "AssemblyAI API Key", 
            type="password",
            help="Enter your AssemblyAI API key for audio transcription"
        )
        openai_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key for text analysis"
        )
        
        # Check if API keys are provided
        api_keys_configured = assemblyai_key and openai_key
        
        if api_keys_configured:
            st.success("✅ API Keys configured!")
        else:
            st.warning("⚠️ Please add your API keys to get started")
        
        st.markdown("---")
        
        # Audio input options
        st.header("🎤 Audio Input")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose your audio file", 
            type=['mp3', 'wav', 'm4a', 'mp4', 'webm', 'flac'],
            help="Upload an audio file to generate meeting notes"
        )
        
        # Process button with enhanced validation
        if uploaded_file and api_keys_configured:
            if st.button("🚀 Start Processing", type="primary", use_container_width=True):
                # Validate API keys format
                if not _validate_api_keys(assemblyai_key, openai_key):
                    st.error("⚠️ Invalid API key format. Please check your keys.")
                    return
                
                result = _process_uploaded_file(uploaded_file, {
                    "assemblyai_key": assemblyai_key,
                    "openai_key": openai_key
                })
                
                if result:
                    st.session_state.current_result = result
                    st.rerun()
        elif uploaded_file and not api_keys_configured:
            st.error("⚠️ Please add your API keys first")
        
        # Add reset button
        st.markdown("---")
        if st.button("🗑️ Reset", help="Clear results and reset session"):
            _cleanup_session()
            st.success("Session cleared!")
            st.rerun()
    
    # Main interface
    _display_main_interface()


def _process_uploaded_file(uploaded_file, config: dict):
    """Process the uploaded audio file with enhanced logging and error handling."""
    try:
        temp_path = _save_uploaded_file(uploaded_file)
        
        processor = MeetingProcessor(
            assemblyai_api_key=config["assemblyai_key"],
            openai_api_key=config["openai_key"]
        )
        
        # Show processing status
        status_container = st.empty()
        status_container.info("🔄 Processing audio...")
        
        result = processor.process_meeting_audio(
            audio_file_path=temp_path
        )
        
        _cleanup_temp_file(temp_path)
        
        status_container.success("✅ Processing complete!")
        
        return result
        
    except Exception as e:
        error_msg = f"❌ Processing failed: {str(e)}"
        st.error(error_msg)
        return None


def _save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temp location."""
    file_extension = uploaded_file.name.split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name


def _cleanup_temp_file(temp_path: str) -> None:
    """Delete temporary file safely and perform garbage collection."""
    try:
        os.unlink(temp_path)
        # Perform garbage collection
        gc.collect()
    except OSError as e:
        print(f"Warning: Could not delete temporary file {temp_path}: {e}")


def _validate_api_keys(assemblyai_key: str, openai_key: str) -> bool:
    """Validate API key formats."""
    # Basic validation - keys should be non-empty and have reasonable length
    if not assemblyai_key or len(assemblyai_key) < 20:
        return False
    if not openai_key or len(openai_key) < 20:
        return False
    return True


def _cleanup_session() -> None:
    """Clean up session state and perform garbage collection."""
    # Clear current result
    st.session_state.current_result = None
    
    # Perform garbage collection
    gc.collect()


def _display_main_interface():
    """Display the main interface."""
    # Header with branding - center aligned
    st.markdown('''
        <div style="text-align: center;">
            <h1 style='color: #1C59C3; margin-bottom: 10px;'>
                🎤 Multilingual Meeting Notes Generator
            </h1>
            <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 20px;">
                <span style='color: #A23B72; font-size: 16px;'>Powered by</span>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <a href="https://www.assemblyai.com/" style="display: inline-block; vertical-align: middle;">
                        <img src="https://cdn.prod.website-files.com/67a08d9d7d19f8fb63692894/67a1038c4a876d1cb37c09aa_AssemblyAI%20Logo.svg" 
                             alt="AssemblyAI" style="height: 32px;">
                    </a>
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    
    # System status - center aligned
    if st.session_state.current_result:
        st.success("🟢 Meeting processed successfully!")
        
    else:
        st.info("🔵 Upload an audio file to get started")
    
    # Display results if available
    if st.session_state.current_result:
        result = st.session_state.current_result
        
        # Display main results
        display_meeting_header(result)
        display_meeting_summary(result.summary)
        display_speaker_analysis(result.speakers, result.segments)
        display_action_items(result.action_items)
        
        # Always show transcript
        display_meeting_transcript(result.segments, result.language, result)
        
        # Export options
        _display_export_options(result)
    
    # Footer - center aligned
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center;'>"
        "<p style='color: #666; font-size: 12px;'>"
        "Multilingual Meeting Notes Generator • Powered by AssemblyAI"
        "</p>"
        "</div>",
        unsafe_allow_html=True
    )


def _display_export_options(result):
    """Show export options."""
    st.subheader("💾 Export Meeting Notes")
    
    markdown_content = _generate_markdown_export(result)
    
    st.download_button(
        label="📥 Download as Markdown",
        data=markdown_content,
        file_name=f"meeting_notes_{result.processed_at.strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )


def _generate_markdown_export(result) -> str:
    """Generate markdown content for export."""
    markdown_content = f"""# {result.title}

**Processed on:** {result.processed_at.strftime('%B %d, %Y at %I:%M %p')}
**Duration:** {result.duration // 60}m {result.duration % 60}s

## 📝 Meeting Summary

{result.summary}

## 👥 Speakers

"""
    
    for speaker in result.speakers:
        markdown_content += f"### {speaker.name}\n"
        markdown_content += f"- **Speaking Time:** {speaker.speaking_time // 60}m {speaker.speaking_time % 60}s\n"
        markdown_content += f"- **Words Spoken:** {speaker.word_count}\n\n"
    
    markdown_content += "## ✅ Action Items\n\n"
    
    for i, item in enumerate(result.action_items, 1):
        markdown_content += f"### Action {i}\n"
        markdown_content += f"**Description:** {item.description}\n"
        if item.assignee:
            markdown_content += f"**Assigned to:** {item.assignee}\n"
        if item.due_date:
            markdown_content += f"**Due Date:** {item.due_date}\n"
        if item.priority:
            markdown_content += f"**Priority:** {item.priority.title()}\n"
        markdown_content += "\n"
    
    markdown_content += "## 📄 Full Transcript\n\n"
    
    # Add transcript statistics
    total_words = result.total_words
    avg_confidence = result.avg_confidence
    unique_speakers = result.unique_speakers_count
    
    markdown_content += f"**Transcript Statistics:**\n"
    markdown_content += f"- Total Segments: {len(result.segments)}\n"
    markdown_content += f"- Total Words: {total_words}\n"
    markdown_content += f"- Average Confidence: {avg_confidence:.2f}\n"
    markdown_content += f"- Unique Speakers: {unique_speakers}\n\n"
    
    # Add full transcript with enhanced formatting
    markdown_content += "### Complete Transcript\n\n"
    
    for i, segment in enumerate(result.segments, 1):
        start_minutes = segment.start_time // 1000 // 60
        start_seconds = segment.start_time // 1000 % 60
        timestamp = f"{start_minutes:02d}:{start_seconds:02d}"
        
        markdown_content += f"#### Segment {i}: Speaker {segment.speaker_id} ({timestamp})\n"
        markdown_content += f"*Confidence: {segment.confidence:.2f}*\n\n"
        markdown_content += f"{segment.text}\n\n"
        markdown_content += "---\n\n"
    
    return markdown_content


if __name__ == "__main__":
    main()