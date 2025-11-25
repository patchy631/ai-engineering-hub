import streamlit as st

CONTENT_MAX = 980

def inject_css():
    st.markdown(
        f"""
        <style>
          .main .block-container {{
            max-width: {CONTENT_MAX}px;
            margin-left: 0;
            margin-right: auto;
            padding-top: 1.2rem;
          }}
          .stChatInput, .stChatFloatingInputContainer {{
            max-width: {CONTENT_MAX}px !important;
            margin-left: 0 !important;
            margin-right: auto !important;
          }}

          .hero {{ display: inline-block; }}
          .hero h1 {{
            margin: 0 0 6px 0;
            font-weight: 600;
            text-align: left;
          }}
          .logo-row {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 14px;
            margin-bottom: 20px;
          }}
          .logo-row img {{
            max-height: 48px;
            width: auto;
            display: block;
          }}

          .stChatMessage {{
            opacity: 1 !important;
            filter: none !important;
            transition: none !important;
          }}
          .stChatMessage pre {{
            background: #1e1e1e !important;
          }}

          .bubble-opaque {{
            background: var(--color-background, #0e1117);
            border-radius: 12px;
            padding: 6px 10px;
            min-height: 20px;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )
