import os
import html
import base64
import tempfile
from pathlib import Path

import streamlit as st

from rag_code import build_rag_pipeline, format_speaker

st.set_page_config(page_title="RAG over Audio", layout="wide")

ASSETS_DIR = Path(__file__).parent / "assets"
MAX_AUDIO_MB = 200
MONO_FONT = 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace'

if "messages" not in st.session_state:
    st.session_state.messages = []


def reset_chat():
    st.session_state.messages = []
    st.session_state.transcripts = None
    st.session_state.query_engine = None
    st.session_state.processed_file_key = None


def _render_transcript(transcripts) -> None:
    lines_html = []
    for turn in transcripts:
        speaker = html.escape(format_speaker(turn["speaker"]))
        text = html.escape(" ".join(turn["text"].split()))
        lines_html.append(
            f'<p class="transcript-line">'
            f'<span class="speaker-label">{speaker}</span>'
            f'<span class="speaker-colon">:</span> '
            f'<span class="transcript-text">{text}</span>'
            f"</p>"
        )

    st.markdown(
        f"""
        <div class="transcript-section">
            <div class="transcript-heading">Transcript</div>
            <details class="transcript-card" open>
                <summary class="transcript-summary">Show full transcript</summary>
                <div class="transcript-body">{"".join(lines_html)}</div>
            </details>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _logo_data_uri(filename: str) -> str:
    path = ASSETS_DIR / filename
    encoded = base64.b64encode(path.read_bytes()).decode()
    return f"data:image/png;base64,{encoded}"


def _inject_styles() -> None:
    st.markdown(
        f"""
        <style>
        .main .block-container {{
            padding: 1.5rem;
            max-width: 100%;
        }}
        .rag-header {{
            text-align: left;
            width: 100%;
        }}
        .rag-header h1 {{
            font-size: 3rem;
            font-weight: 700;
            margin: 0;
            line-height: 1.15;
            white-space: nowrap;
        }}
        .rag-header .logo-row {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            margin-top: 0.5rem;
        }}
        .rag-header .and {{
            font-size: 3rem;
            font-weight: 700;
            line-height: 1;
        }}
        .rag-header .logo-speechmatics {{ height: 1.65rem; }}
        .rag-header .logo-voyage {{ height: 2rem; }}
        .rag-header img {{
            width: auto;
            object-fit: contain;
            display: block;
        }}
        .main [data-testid="stHorizontalBlock"] [data-testid="stButton"] button,
        .main [data-testid="stHorizontalBlock"] [data-testid="stButton"] button p {{
            white-space: nowrap;
        }}
        section[data-testid="stSidebar"] h2 {{
            font-size: 1.25rem;
            font-weight: 700;
            margin: 0 0 0.35rem 0;
        }}
        section[data-testid="stSidebar"] .sidebar-choose-label {{
            font-size: 0.95rem;
            margin: 0 0 0.5rem 0;
            display: block;
        }}
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] button[aria-label="Add files"],
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] button[aria-label="Add file"] {{
            display: none !important;
        }}
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
            justify-content: flex-start;
        }}
        section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
            flex: 0 0 auto;
        }}
        section[data-testid="stSidebar"] [data-testid="stMarkdown"]:has(.transcript-section) {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        section[data-testid="stSidebar"] [data-testid="stMarkdown"]:has(.transcript-section) > div {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
            height: 100%;
        }}
        section[data-testid="stSidebar"] .transcript-section {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
            margin-top: 0.75rem;
            margin-bottom: 0.75rem;
        }}
        section[data-testid="stSidebar"] .transcript-heading {{
            font-size: 1rem;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.95);
            margin: 0 0 0.45rem 0;
            font-family: inherit;
            flex-shrink: 0;
        }}
        section[data-testid="stSidebar"] .transcript-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            overflow: hidden;
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        section[data-testid="stSidebar"] .transcript-summary {{
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.55rem 0.8rem;
            font-size: 0.84rem;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.82);
            cursor: pointer;
            user-select: none;
            flex-shrink: 0;
        }}
        section[data-testid="stSidebar"] .transcript-summary::-webkit-details-marker {{
            display: none;
        }}
        section[data-testid="stSidebar"] .transcript-summary::after {{
            content: "⌃";
            font-size: 0.9rem;
            line-height: 1;
            opacity: 0.65;
        }}
        section[data-testid="stSidebar"] .transcript-card:not([open]) .transcript-summary::after {{
            content: "⌄";
        }}
        section[data-testid="stSidebar"] .transcript-body {{
            flex: 1 1 auto;
            overflow-y: auto;
            padding: 0.2rem 0.8rem 0.65rem;
            min-height: 0;
        }}
        section[data-testid="stSidebar"] .transcript-line {{
            font-family: {MONO_FONT};
            font-size: 0.86rem;
            line-height: 1.75;
            margin: 0 0 0.5rem 0;
            padding: 0.28rem 0.35rem;
            color: rgba(255, 255, 255, 0.92);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: clip;
            border-radius: 5px;
            transition: background 0.15s ease;
        }}
        section[data-testid="stSidebar"] .transcript-line:hover {{
            background: rgba(255, 255, 255, 0.04);
        }}
        section[data-testid="stSidebar"] .transcript-line:last-child {{
            margin-bottom: 0;
        }}
        section[data-testid="stSidebar"] .speaker-label {{
            font-weight: 700;
            letter-spacing: 0.01em;
            color: rgba(255, 255, 255, 0.98);
        }}
        section[data-testid="stSidebar"] .speaker-colon {{
            font-weight: 700;
            color: rgba(255, 255, 255, 0.55);
        }}
        section[data-testid="stSidebar"] .transcript-text {{
            color: rgba(255, 255, 255, 0.9);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    speechmatics_logo = _logo_data_uri("speechmatics_logo.png")
    voyage_mongo_logo = _logo_data_uri("voyageai-mongodb-logo.png")

    title_col, clear_col = st.columns([9, 1.5], vertical_alignment="top", gap="small")

    with title_col:
        st.markdown(
            '<div class="rag-header"><h1>RAG over Audio powered by</h1></div>',
            unsafe_allow_html=True,
        )

    with clear_col:
        st.button("Clear", icon=":material/autorenew:", on_click=reset_chat, key="clear_chat")

    st.markdown(
        f"""
        <div class="rag-header">
            <div class="logo-row">
                <img class="logo-speechmatics" src="{speechmatics_logo}" alt="Speechmatics" />
                <span class="and">and</span>
                <img class="logo-voyage" src="{voyage_mongo_logo}" alt="Voyage AI and MongoDB" />
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


_inject_styles()

with st.sidebar:
    st.header("Add your audio file!")
    st.markdown(
        '<span class="sidebar-choose-label">Choose your audio file</span>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose your audio file",
        type=["mp3", "wav", "m4a"],
        accept_multiple_files=False,
        label_visibility="collapsed",
        key="audio_uploader",
    )

    if uploaded_file and uploaded_file.size > MAX_AUDIO_MB * 1024 * 1024:
        st.error(f"File is too large. Limit is {MAX_AUDIO_MB}MB per file.")
        uploaded_file = None

    if uploaded_file:
        file_key = f"{uploaded_file.name}-{uploaded_file.size}"

        if st.session_state.get("processed_file_key") != file_key:
            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    with st.spinner("Transcribing with Speechmatics and storing in MongoDB Atlas..."):
                        query_engine, transcripts = build_rag_pipeline(file_path)

                    st.session_state.query_engine = query_engine
                    st.session_state.transcripts = transcripts
                    st.session_state.processed_file_key = file_key

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.stop()

        if st.session_state.get("query_engine"):
            st.success("Ready to Chat!")
            st.audio(uploaded_file)
            _render_transcript(st.session_state.transcripts)

render_header()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about the audio conversation..."):
    if not st.session_state.get("query_engine"):
        st.warning("Upload and process an audio file first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in st.session_state.query_engine.query(prompt):
            full_response += chunk.delta or ""
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
