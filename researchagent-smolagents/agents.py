import streamlit as st
import os
import re
import requests
import sys
import io
from contextlib import contextmanager
from datetime import datetime
from markdownify import markdownify
from requests.exceptions import RequestException
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    HfApiModel,
    ManagedAgent,
    tool,
)
from dotenv import load_dotenv
from huggingface_hub import login

load_dotenv()

class StreamCapture(io.StringIO):
    def __init__(self):
        super().__init__()
        self.timestamps = []
        self.logs = []

    def write(self, text):
        if text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.timestamps.append(timestamp)
            self.logs.append(text.strip())
        return super().write(text)

@contextmanager
def capture_output():
    stream_capture = StreamCapture()
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stream_capture, stream_capture
    try:
        yield stream_capture
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

if 'log_container' not in st.session_state:
    st.session_state.log_container = []

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    st.error("HuggingFace token not found in .env file. Please add HF_TOKEN=your_token_here to your .env file.")
    st.stop()

login(HF_TOKEN)

@tool
def enhanced_search(query: str, time_period: str = "m") -> dict:
    """
    Enhanced search tool that explicitly requests recent results and returns URLs.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }
        current_year = datetime.now().year
        time_keywords = f"{current_year} {query}"

        response = requests.get('https://html.duckduckgo.com/html/', headers=headers)

        search_params = {
            'q': time_keywords,
            's': '0',
            'dc': '20',
            'v': 'l',
            'o': 'json',
            'api': '/d.js',
        }

        search_response = requests.post(
            'https://html.duckduckgo.com/html/',
            headers=headers,
            data=search_params
        )

        if search_response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(search_response.text, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result__body'):
                title = result.find('a', class_='result__a')
                snippet = result.find('a', class_='result__snippet')
                url = title.get('href') if title else None

                if title and url:
                    result_data = {
                        'title': title.text.strip(),
                        'url': url,
                        'snippet': snippet.text.strip() if snippet else '',
                    }
                    date_matches = re.findall(r'\b20\d{2}\b', result_data['snippet'])
                    result_data['verified_year'] = max(map(int, date_matches)) if date_matches else None
                    result_data['recency_score'] = calculate_recency_score(result_data['verified_year'])
                    results.append(result_data)

            return {
                'Results': results[:10],
                'meta': {
                    'query': query,
                    'time_period': time_period,
                    'total_results': len(results)
                }
            }

        return {"error": "Search failed", "status": search_response.status_code}

    except Exception as e:
        return {"error": str(e)}

def calculate_recency_score(year: int | None) -> float:
    if not year:
        return 0.0
    current_year = datetime.now().year
    years_old = current_year - year
    return max(0.0, 1.0 * (0.8 ** years_old))

@tool
def visit_webpage(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        markdown_content = markdownify(response.text).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
        return markdown_content
    except RequestException as e:
        return f"Error fetching the webpage: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def format_agent_response(response):
    if isinstance(response, dict):
        formatted_parts = []

        if 'Results' in response:
            formatted_parts.append("## Search Results")
            for idx, result in enumerate(response['Results'], 1):
                formatted_parts.append(f"### {idx}. {result.get('title', 'No Title')}")
                formatted_parts.append(f"**Source:** {result.get('url', 'No URL')}")
                formatted_parts.append(result.get('snippet', 'No description available'))
                formatted_parts.append("---")

        st.markdown("---")
        log_expander = st.expander("📋 Terminal Logs", expanded=False)
        with log_expander:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### Terminal Output")
            with col2:
                if st.button("Clear Logs"):
                    st.session_state.log_container = []

            log_placeholder = st.empty()
            if st.session_state.log_container:
                log_text = ""
                for timestamp, log in st.session_state.log_container:
                    log_text += f"`[{timestamp}]` {log}\n"
                log_placeholder.markdown(log_text)
            else:
                log_placeholder.info("No logs to display yet.")

        if 'thoughts' in response:
            formatted_parts.append("## Analysis")
            formatted_parts.append(response['thoughts'])

        if 'answer' in response:
            formatted_parts.append("## Summary")
            formatted_parts.append(response['answer'])

        return "\n\n".join(formatted_parts)
    else:
        return str(response)

@st.cache_resource
def initialize_agents():
    model = HfApiModel(
        model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
        token=HF_TOKEN
    )

    web_agent = ToolCallingAgent(
        tools=[enhanced_search, visit_webpage],
        model=model,
        max_steps=10,
    )

    managed_web_agent = ManagedAgent(
        agent=web_agent,
        name="search",
        description="Performs enhanced web searches with recency prioritization.",
    )

    manager_agent = CodeAgent(
        tools=[],
        model=model,
        managed_agents=[managed_web_agent],
        additional_authorized_imports=["time", "numpy", "pandas", "datetime"],
    )

    return manager_agent

@st.cache_data
def fetch_webpage_content(url):
    return visit_webpage(url)

with st.sidebar:
    st.title("🔍 Search Settings")
    st.markdown("---")

    max_results = st.slider("Max Results", 1, 10, 5)
    search_depth = st.select_slider(
        "Search Depth",
        options=["Basic", "Moderate", "Deep"],
        value="Moderate"
    )

    time_options = ["Last 24 Hours", "Last Week", "Last Month"]
    time_period_display = st.select_slider(
        "Time Period",
        options=time_options,
        value="Last Week"
    )

    time_period_map = {
        "Last 24 Hours": "d",
        "Last Week": "w",
        "Last Month": "m"
    }
    time_period = time_period_map[time_period_display]

    st.markdown("---")
    st.markdown("### 📜 Search History")
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []

    for hist in st.session_state.search_history[-5:]:
        st.markdown(f"• {hist}")

st.title("🔍 Web Research Assistant")
st.markdown("### Intelligent Web Search and Analysis")

manager_agent = initialize_agents()

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Enter your research query", placeholder="What would you like to know?")
with col2:
    search_button = st.button("🔎 Search", type="primary", disabled=not query)

if search_button and query:
    if query not in st.session_state.search_history:
        st.session_state.search_history.append(query)

    with st.spinner("🕵️‍♂️ Researching..."):
        try:
            with capture_output() as output:
                result_tab, sources_tab, analysis_tab, logs_tab = st.tabs(
                    ["📝 Results", "🔗 Sources", "📊 Analysis", "📋 Logs"]
                )
