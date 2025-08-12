import assemblyai as aai
import streamlit as st
import uuid
import gc
import base64
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set API key from environment variable
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# Configure page
st.set_page_config(
    page_title="AssemblyAI Audio Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

# Application styling with dark theme
st.markdown("""
<style>
/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #23272f !important;
    padding-top: 2rem !important;
    position: static !important;
}

/* Sidebar section headers */
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] label {
    color: #fff !important;
    font-weight: 700 !important;
    margin-bottom: 1rem !important;
    margin-top: 1.5rem !important;
    letter-spacing: 0.01em;
}

/* File uploader dropzone and file list */
section[data-testid="stSidebar"] .stFileUploader > div,
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] {
    background-color: #111215 !important;
    color: #fff !important;
    border-radius: 12px !important;
    border: none !important;
    margin-bottom: 1rem !important;
    padding: 1.25rem 1rem !important;
    box-shadow: none !important;
}

/* Uploaded file display */
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderFileContainer"] {
    background-color: #181a1f !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: 1px solid #23272f !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
    padding: 0.5rem 0.75rem !important;
}

/* File uploader label and help text */
section[data-testid="stSidebar"] .stFileUploader label,
section[data-testid="stSidebar"] .stFileUploader p {
    color: #fff !important;
    font-size: 1rem !important;
    margin-bottom: 0.5rem !important;
}
/* Force the file uploader limit/help line to be fully white and visible */
section[data-testid="stSidebar"] .stFileUploader span,
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] span,
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] p,
section[data-testid="stSidebar"] .stFileUploader [data-testid="stFileUploaderDropzone"] * {
    color: #fff !important;
    opacity: 1 !important;
    filter: none !important;
    text-shadow: none !important;
}

/* File uploader button */
section[data-testid="stSidebar"] .stFileUploader button {
    background-color: #181a1f !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
    padding: 0.6rem 0 !important;
    box-shadow: none !important;
    transition: background 0.2s;
}
section[data-testid="stSidebar"] .stFileUploader button:hover {
    background-color: #23272f !important;
}

/* Remove dotted borders from file uploader */
.stFileUploader, .stFileUploader * {
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Uploaded file X/delete button */
section[data-testid="stSidebar"] .stFileUploader svg {
    color: #b0b0b0 !important;
}

/* Status bar (e.g., Ready to Chat!) */
section[data-testid="stSidebar"] .stAlert, 
section[data-testid="stSidebar"] .stSuccess, 
section[data-testid="stSidebar"] .stInfo {
    background-color: #181a1f !important;
    color: #fff !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 500 !important;
    margin-bottom: 1rem !important;
}

/* Sidebar card/preview (if you add one) */
.sidebar-preview-card {
    background-color: #181a1f !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    color: #fff !important;
    border: 1px solid #23272f !important;
    box-shadow: none !important;
}

/* Spacing between sidebar elements */
section[data-testid="stSidebar"] > div {
    margin-bottom: 1.5rem !important;
}

/* Center align the main heading */
.main-header {
    text-align: center !important;
}

/* Remove white patch at the top of the main area */
div.stApp, .block-container, .main, .main > div:first-child, .st-emotion-cache-uf99v8, .st-emotion-cache-1wrcr25, .st-emotion-cache-18ni7ap {
    background-color: #111215 !important;
    background: #111215 !important;
}
/* Remove unwanted top margin/padding */
.block-container, .main, .main > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Aggressive reset for top white patch */
html, body, #root, .stApp {
    background-color: #111215 !important;
    background: #111215 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    min-height: 100vh !important;
    height: 100% !important;
}

header[data-testid="stHeader"] {
    background: #111215 !important;
    background-color: #111215 !important;
    box-shadow: none !important;
    border: none !important;
    min-height: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 0 !important;
    display: none !important;
}

/* Center main content vertically with flexbox */
div.stApp {
    display: flex !important;
    flex-direction: column !important;
    min-height: 100vh !important;
}
.block-container {
    max-width: 1100px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-top: 4rem !important;
    min-height: 80vh !important;
}

/* Restore card/box look for feature cards only */
.metric-card {
    background-color: #23272f !important;
    border-radius: 12px !important;
    color: #fff !important;
    border: none !important;
    padding: 1.5rem !important;
    margin-bottom: 2.5rem !important;
    box-shadow: 0 2px 16px 0 rgba(0,0,0,0.12) !important;
}

/* Remove box styling from .section-card and .welcome-card */
.section-card, .welcome-card {
    background: none !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Main header styling */
.main-header {
    font-size: 2.8rem !important;
    letter-spacing: 0.02em !important;
    margin-bottom: 2.5rem !important;
}

/* Feature cards: equal dimensions and flex layout */
.cards-row {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin-top: 2.5rem;
}
.metric-card {
    min-width: 300px !important;
    max-width: 340px !important;
    min-height: 140px !important;
    flex: 1 1 0 !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: flex-start !important;
    box-sizing: border-box !important;
}

/* Increase spacing between bullet points and cards */
.bullet-section {
    margin-bottom: 2.5rem !important;
}

/* Increase font size of bullet points for visibility */
.bullet-section ul,
.bullet-section li {
    font-size: 1.15rem !important;
    line-height: 1.7 !important;
}

/* Responsive adjustments */
@media (max-width: 900px) {
    .block-container {
        max-width: 98vw !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    .metric-card {
        min-width: unset !important;
        width: 100% !important;
        margin-bottom: 1rem !important;
    }
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background-color: #23272f !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #b0b0b0 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #23272f !important;
    color: #fff !important;
}

/* General text color */
body, .stApp, .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
    color: #fff !important;
}

/* AGGRESSIVE CHAT INPUT STYLING - FORCE CENTER AND WHITE TEXT */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 0 !important;
    left: 280px !important;
    right: 0 !important;
    width: calc(100vw - 280px) !important;
    max-width: none !important;
    background-color: #111215 !important;
    z-index: 1000 !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 1rem !important;
    box-shadow: 0 2px 16px 0 rgba(0,0,0,0.12) !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

[data-testid="stChatInput"] > div {
    width: 100% !important;
    max-width: 900px !important;
    margin: 0 auto !important;
    display: flex !important;
    justify-content: center !important;
}

[data-testid="stChatInput"] input,
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    background: rgba(17, 18, 21, 0.8) !important;
    border: 1px solid #444 !important;
    border-radius: 8px !important;
    text-align: center !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 1rem !important;
    width: 100% !important;
    max-width: 800px !important;
}

[data-testid="stChatInput"] input::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: rgba(255, 255, 255, 0.7) !important;
    text-align: center !important;
}

/* Force chat input text to be white */
[data-testid="stChatInput"] *,
[data-testid="stChatInput"] input,
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] span {
    color: #ffffff !important;
}

/* --- PATCH FOR STREAMLIT FILE UPLOADER (2024) --- */
.st-emotion-cache-taue2i {
    background-color: #111215 !important;
    color: #fff !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: none !important;
}
.st-emotion-cache-13ejsyy {
    background-color: #181a1f !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
    padding: 0.6rem 0 !important;
    box-shadow: none !important;
    transition: background 0.2s;
}
.st-emotion-cache-13ejsyy:hover {
    background-color: #23272f !important;
}

/* Improve main header visibility */
.main-header, h1.main-header, .stMarkdown h1 {
    color: #fff !important;
    font-weight: 800 !important;
    text-shadow: 0 2px 8px rgba(0,0,0,0.2);
    letter-spacing: 0.02em;
}

/* File uploader help/limit text */
.st-emotion-cache-1aehpvj, .st-emotion-cache-9ycgxx, .st-emotion-cache-u8hs99, .st-emotion-cache-1fttcpj, .st-emotion-cache-nwtri {
    color: #fff !important;
    opacity: 1 !important;
    filter: none !important;
    text-shadow: none !important;
}

/* Welcome heading in main area */
.welcome-card h3, .welcome-card p, .welcome-card ul, .welcome-card li {
    color: #fff !important;
}

/* Card names/titles */
.metric-card h4, .metric-card p {
    color: #fff !important;
}

/* Feature section titles under tabs bar */
.section-card .stSubheader, .section-card h2, .section-card h3, .section-card h4 {
    color: #fff !important;
}

/* Remove Streamlit anchor link icon from headers */
.st-emotion-cache-1wivap2, .stMarkdown a[href^='#'] {
    display: none !important;
}

/* Force all headings under tabs bar to be white */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp .stSubheader, .stApp .stMarkdown h2, .stApp .stMarkdown h3, .stApp .stMarkdown h4 {
    color: #fff !important;
}

/* Fix for Streamlit metric value and label visibility in dark themes */
/* This ensures the text for stats (like in Speaker and Sentiment tabs) is white. */
[data-testid="stMetric"] * {
    color: #fff !important;
}

/* Styling for our custom-built metric/stat display */
.custom-metric {
    text-align: left;
    margin-bottom: 1rem;
}
.metric-label {
    color: #b0b0b0; /* Lighter grey for the label */
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}
.metric-value {
    color: #fff;
    font-size: 2rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

def get_logo_base64():
    """Convert logo file to base64 string for embedding"""
    logo_path = Path("audio-analysis-toolkit/assets/logo.png")
    
    if logo_path.exists():
        try:
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception:
            return ""
    
    return ""

def reset_chat():
    """Reset chat session"""
    st.session_state.messages = []
    gc.collect()

def timestamp_string(milliseconds):
    """Convert milliseconds to HH:MM:SS format"""
    seconds = milliseconds // 1000
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def display_transcription(transcript):
    """Display transcription with timestamps"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📝 Full Transcription")
    
    sentences = transcript.get_sentences()
    for sentence in sentences:
        col1, col2 = st.columns([0.8, 7])
        with col1:
            # Compact timestamp styling
            st.markdown(f"""
            <div class="timestamp-compact">
                {timestamp_string(sentence.start)}
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="margin-left: -1rem;">{sentence.text}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_summary(transcript):
    """Display summary"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📋 Summary")
    st.write(transcript.summary)
    st.markdown('</div>', unsafe_allow_html=True)

def display_speakers(transcript):
    """Display speaker analysis"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("\U0001F465 Speaker Analysis")
    
    # Count speakers
    speakers = set()
    for utterance in transcript.utterances:
        speakers.add(str(utterance.speaker))
    total_speakers = len(speakers)
    total_utterances = len(transcript.utterances)
    
    # Simple metrics row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">Total Speakers</div>
            <div class="metric-value">{total_speakers}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">Total Utterances</div>
            <div class="metric-value">{total_utterances}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Speaker Dialogue")
    for utterance in transcript.utterances:
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown(f'<span style="color: var(--accent-primary); font-weight: 600;">Speaker {utterance.speaker}</span>', unsafe_allow_html=True)
        with col2:
            st.write(utterance.text)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_sentiment(transcript):
    """Display sentiment analysis"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("\U0001F60A Sentiment Analysis")
    
    # Count sentiments
    sentiment_counts = {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0}
    for sent in transcript.sentiment_analysis:
        sentiment = str(sent.sentiment).upper()
        if "POSITIVE" in sentiment:
            sentiment_counts["POSITIVE"] += 1
        elif "NEGATIVE" in sentiment:
            sentiment_counts["NEGATIVE"] += 1
        elif "NEUTRAL" in sentiment:
            sentiment_counts["NEUTRAL"] += 1
    
    # Simple metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">😊 Positive</div>
            <div class="metric-value">{sentiment_counts['POSITIVE']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">😐 Neutral</div>
            <div class="metric-value">{sentiment_counts['NEUTRAL']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="custom-metric">
            <div class="metric-label">😞 Negative</div>
            <div class="metric-value">{sentiment_counts['NEGATIVE']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.subheader("Detailed Sentiment")
    for sent in transcript.sentiment_analysis:
        timestamp = timestamp_string(sent.start)
        text = f"**{timestamp}** - Speaker {sent.speaker}: {sent.text}"
        
        if "NEUTRAL" in str(sent.sentiment).upper():
            st.info(text)
        elif "POSITIVE" in str(sent.sentiment).upper():
            st.success(text)
        else:
            st.error(text)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_topics(transcript):
    """Display topic analysis"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("🏷️ Topic Analysis")
    
    sorted_topics = sorted(transcript.iab_categories.summary.items(), key=lambda x: x[1], reverse=True)
    
    if sorted_topics:
        for topic, relevance in sorted_topics[:10]:
            percentage = relevance * 100
            
            # Create a clean layout with topic name and percentage
            st.markdown(f"""
            <div style="margin-bottom: 1rem; padding: 0.75rem; background: #23272f; border-radius: 0.5rem; border: 1px solid #181a1f;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-weight: 600; color: #fff;">{topic}</span>
                    <span style="font-weight: 700; color: #4f8cff; font-size: 1.1rem;">{percentage:.1f}%</span>
                </div>
                <div style="background: #181a1f; border-radius: 0.25rem; height: 8px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #4f8cff, #00e6e6); height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Topics analysis not available for this audio.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_chat(transcript):
    """Display chat interface"""
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("💬 Ask Questions About Your Audio")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display welcome message if no messages
    if not st.session_state.messages:
        # Add spacing above welcome message to center it better
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 2rem 1.5rem; color: var(--text-secondary); margin: 1rem 0 3rem 0;">
            <h4 style="color: var(--text-primary); margin-bottom: 1rem; text-align: center;">Start a conversation about your audio</h4>
            <p style="color: var(--text-secondary); line-height: 1.6; text-align: center;">Ask questions about the content, speakers, sentiment, or get insights from your audio analysis.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # # Add spacing to position chat input (moved up by input's height)
    # st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Chat input - appears naturally at bottom, always visible
    if prompt := st.chat_input("What would you like to know about this audio?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                full_prompt = f"Based on the transcript, answer the following question: {prompt}"
                result = st.session_state.transcript.lemur.task(full_prompt, final_model=aai.LemurModel.claude3_5_sonnet)
                response = result.response.strip()
            st.markdown(response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        # Company branding with logo
        logo_path = Path("assets/logo.png")
        
        if logo_path.exists():
            # Convert logo to base64 for better control over positioning
            with open(logo_path, "rb") as img_file:
                logo_data = base64.b64encode(img_file.read()).decode()
            
            # Show logo with full CSS control for perfect centering
            st.markdown(f"""
            <div class="logo-center-container">
                <img src="data:image/png;base64,{logo_data}" class="logo-centered" alt="Logo">
            </div>
            """, unsafe_allow_html=True)
            
            # Add separator
            st.markdown('<div style="border-bottom: 1px solid var(--border-color); margin: 1rem 0;"></div>', unsafe_allow_html=True)
            logo_found = True
        else:
            logo_found = False
        
        if not logo_found:
            # Fallback to base64 method with debug info
            logo_base64 = get_logo_base64()
            if logo_base64:
                # Show actual logo only, no text, bigger size
                st.markdown("""
                <div class="logo-container">
                    <img src="data:image/png;base64,{}" class="logo-image-large" alt="Logo">
                </div>
                """.format(logo_base64), unsafe_allow_html=True)
            else:
                # Show placeholder if logo not found - bigger size, no text
                st.markdown("""
                <div class="logo-container">
                    <div class="logo-placeholder-large">A</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Add separator after logo/fallback
            st.markdown('<div style="border-bottom: 1px solid var(--border-color); margin: 1rem 0;"></div>', unsafe_allow_html=True)
        
        st.markdown('<h2 class="sidebar-header">Upload Your Audio File</h2>', unsafe_allow_html=True)
        
        audio_file = st.file_uploader(
            "Choose an audio file",
            type=['wav', 'mp3', 'mp4', 'm4a', 'flac'],
            help="Upload audio files in WAV, MP3, MP4, M4A, or FLAC format"
        )
        
        if audio_file is not None:
            st.success("File uploaded successfully!")
            st.audio(audio_file)
            
            # Add spacing between upload and file details
            st.markdown("<br>", unsafe_allow_html=True)
            
            # File details
            st.markdown("### File Details")
            st.write(f"**Filename:** {audio_file.name}")
            st.write(f"**Size:** {audio_file.size:,} bytes")
    
    # Main content area - simple title
    st.markdown('<h1 class="main-header">🎵 Audio Analysis Toolkit</h1>', unsafe_allow_html=True)
    
    if audio_file is None:
        # Welcome screen - matching original layout
        st.markdown('<div class="bullet-section">', unsafe_allow_html=True)
        st.markdown("""
        <div class="welcome-card">
            <h3>🎵 Welcome to Audio Analysis Toolkit</h3>
            <p>Upload an audio file to get started with powerful AI-driven analysis:</p>
            <ul>
                <li>🎯 <strong>Transcription</strong> - Convert speech to text with precise timestamps</li>
                <li>👥 <strong>Speaker Detection</strong> - Automatically identify different speakers</li>
                <li>😊 <strong>Sentiment Analysis</strong> - Analyze emotional tone and context</li>
                <li>📋 <strong>Summarization</strong> - Extract key points and insights</li>
                <li>🏷️ <strong>Topic Detection</strong> - Identify main topics and themes</li>
                <li>💬 <strong>Q&A Chat</strong> - Ask intelligent questions about your audio</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add feature cards at the bottom
        st.markdown("""
        <div class="cards-row" style="margin-top: 3rem;">
            <div class="metric-card">
                <h4>🎯 Accurate Transcription</h4>
                <p>High-quality speech-to-text with precise timestamps and speaker detection</p>
            </div>
            <div class="metric-card">
                <h4>😊 Sentiment Analysis</h4>
                <p>Understand emotional tone and context of conversations</p>
            </div>
            <div class="metric-card">
                <h4>🏷️ Topic Detection</h4>
                <p>Identify key themes and topics discussed in your audio</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Process audio and show results
        with st.spinner('🔄 Processing your audio with AssemblyAI...'):
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                iab_categories=True,
                speakers_expected=2,
                sentiment_analysis=True,
                summarization=True,
                language_detection=True
            )
            
            st.session_state.transcriber = aai.Transcriber()
            st.session_state.transcript = st.session_state.transcriber.transcribe(audio_file, config=config)
        
        st.success('✅ Audio processed successfully!')
        
        # Create tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📝 Transcription", 
            "📋 Summary", 
            "👥 Speakers", 
            "😊 Sentiment", 
            "🏷️ Topics", 
            "💬 Chat"
        ])
        
        with tab1:
            display_transcription(st.session_state.transcript)
        
        with tab2:
            display_summary(st.session_state.transcript)
        
        with tab3:
            display_speakers(st.session_state.transcript)
        
        with tab4:
            display_sentiment(st.session_state.transcript)
        
        with tab5:
            display_topics(st.session_state.transcript)
        
        with tab6:
            display_chat(st.session_state.transcript)

if __name__ == "__main__":
    main() 
