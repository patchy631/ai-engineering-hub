import streamlit as st
import os
import pandas as pd
import re
import requests
import sys
import io
from contextlib import contextmanager
import json
from datetime import datetime, timedelta
from markdownify import markdownify
from requests.exceptions import RequestException
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    HfApiModel,
    ManagedAgent,
    DuckDuckGoSearchTool,
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
    
    Args:
        query: Search query string
        time_period: Time period for results ('d' for day, 'w' for week, 'm' for month)
    
    Returns:
        dict: Search results with timestamps, URLs, and relevance scores
    """
    try:
        # Use DuckDuckGo HTML API for better results
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Add explicit time-based keywords to the query
        current_year = datetime.now().year
        time_keywords = f"{current_year} {query}"
        
        # First request to get token
        response = requests.get('https://html.duckduckgo.com/html/', headers=headers)
        
        # Extract search parameters
        search_params = {
            'q': time_keywords,
            's': '0',
            'dc': '20',
            'v': 'l',
            'o': 'json',
            'api': '/d.js',
        }
        
        # Make the actual search request
        search_response = requests.post(
            'https://html.duckduckgo.com/html/',
            headers=headers,
            data=search_params
        )
        
        if search_response.status_code == 200:
            # Parse the HTML response to extract results
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
                    
                    # Extract and verify dates in the content
                    date_matches = re.findall(r'\b20\d{2}\b', result_data['snippet'])
                    result_data['verified_year'] = max(map(int, date_matches)) if date_matches else None
                    
                    # Score results based on recency
                    result_data['recency_score'] = calculate_recency_score(result_data['verified_year'])
                    
                    results.append(result_data)
            
            return {
                'Results': results[:10],  # Limit to top 10 results
                'meta': {
                    'query': query,
                    'time_period': time_period,
                    'total_results': len(results)
                }
            }
        
        return {"error": "Search failed", "status": search_response.status_code}
    
    except Exception as e:
        return {"error": str(e)}



# Add this to your requirements for the enhanced search functionality
# pip install beautifulsoup4

def calculate_recency_score(year: int | None) -> float:
    """Calculate a score based on how recent the content is."""
    if not year:
        return 0.0
    
    current_year = datetime.now().year
    years_old = current_year - year
    
    # Exponential decay based on age
    return max(0.0, 1.0 * (0.8 ** years_old))

@tool
def visit_webpage(url: str) -> str:
    """Visits a webpage and converts its content to markdown format.

    Args:
        url: The complete URL of the webpage to visit (e.g., 'https://example.com').
            Must be a valid HTTP or HTTPS URL.

    Returns:
        str: The webpage content converted to Markdown format with the reference webpages links.
            Returns an error message if the request fails.
    """
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
    """Format the agent's response into a readable string with URLs."""
    if isinstance(response, dict):
        formatted_parts = []
        
        if 'Results' in response:
            formatted_parts.append("## Search Results")
            for idx, result in enumerate(response['Results'], 1):
                formatted_parts.append(f"### {idx}. {result.get('title', 'No Title')}")
                formatted_parts.append(f"**Source:** {result.get('url', 'No URL')}")
                formatted_parts.append(result.get('snippet', 'No description available'))
                formatted_parts.append("---")
        
        # Add log display section
        st.markdown("---")
        log_expander = st.expander("📋 Terminal Logs", expanded=False)
        with log_expander:
            # Add controls for the log display
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### Terminal Output")
            with col2:
                if st.button("Clear Logs"):
                    st.session_state.log_container = []
            
            # Create a container for the logs
            log_placeholder = st.empty()
            
            # Display logs with timestamps in a formatted way
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

# Initialize the model and agents
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

# Cache webpage content
@st.cache_data
def fetch_webpage_content(url):
    return visit_webpage(url)

# Sidebar
# [Previous imports and initial code remain the same until the sidebar section]

# Sidebar
with st.sidebar:
    st.title("🔍 Search Settings")
    st.markdown("---")
    
    max_results = st.slider("Max Results", 1, 10, 5)
    search_depth = st.select_slider(
        "Search Depth",
        options=["Basic", "Moderate", "Deep"],
        value="Moderate"
    )
    
    # Fixed time period selector
    time_options = ["Last 24 Hours", "Last Week", "Last Month"]
    time_period_display = st.select_slider(
        "Time Period",
        options=time_options,
        value="Last Week"
    )
    
    # Convert display value to API parameter
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

# [Rest of the code remains the same]

# Main content
st.title("🔍 Web Research Assistant")
st.markdown("### Intelligent Web Search and Analysis")

# Initialize agents
manager_agent = initialize_agents()

# Search input
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("Enter your research query", placeholder="What would you like to know?")
with col2:
    search_button = st.button("🔎 Search", type="primary", disabled=not query)

if search_button and query:
    # Add to search history
    if query not in st.session_state.search_history:
        st.session_state.search_history.append(query)
    
    with st.spinner("🕵️‍♂️ Researching..."):
        try:
            # Capture all output during the search process
            with capture_output() as output:
                # Create tabs for different views
                result_tab, sources_tab, analysis_tab, logs_tab = st.tabs(
                    ["📝 Results", "🔗 Sources", "📊 Analysis", "📋 Logs"]
                )
                
                # Perform the search with time period
                raw_result = manager_agent.run(
                    f"""
                    Search for recent information about: {query}
                    Time period: {time_period}
                    Required year: {datetime.now().year}
                    Depth: {search_depth}
                    Max results: {max_results}
                    """
                )
                
                # Get the captured output
                captured_logs = list(zip(output.timestamps, output.logs))
                st.session_state.log_container.extend(captured_logs)
                
                # Display logs in the logs tab
                with logs_tab:
                    st.markdown("### 📋 Search Logs")
                    for timestamp, log in captured_logs:
                        st.markdown(f"`[{timestamp}]` {log}")
                

            # Format the result
            formatted_result = format_agent_response(raw_result)
            
            # Extract sources (URLs) from the formatted result
            sources = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', formatted_result)
            
            with result_tab:
                st.markdown("### 📊 Research Results")
                st.markdown(formatted_result)
                
                # Add export buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download Results",
                        formatted_result,
                        file_name="research_results.md",
                        mime="text/markdown"
                    )
                with col2:
                    if isinstance(raw_result, dict):
                        st.download_button(
                            "📥 Download Raw JSON",
                            json.dumps(raw_result, indent=2),
                            file_name="research_results.json",
                            mime="application/json"
                        )
            
            with sources_tab:
                st.markdown("### 📚 Sources Referenced")
                if sources:
                    for idx, source in enumerate(sources, 1):
                        with st.expander(f"Source {idx}: {source}"):
                            # Add a loading spinner while fetching content
                            with st.spinner(f"Loading content from source {idx}..."):
                                # Fetch and display webpage content
                                content = fetch_webpage_content(source)
                                
                                # Create columns for metadata and controls
                                meta_col1, meta_col2 = st.columns([3, 1])
                                with meta_col1:
                                    st.markdown(f"**URL:** [{source}]({source})")
                                with meta_col2:
                                    st.download_button(
                                        "📥 Download Source",
                                        content,
                                        file_name=f"source_{idx}.md",
                                        mime="text/markdown"
                                    )
                                
                                st.markdown("---")
                                st.markdown("### Content Preview")
                                # Display a preview of the content with a character limit
                                preview_length = 1000
                                if len(content) > preview_length:
                                    st.markdown(content[:preview_length] + "...")
                                    st.markdown("*Content truncated. Download the full source using the button above.*")
                                else:
                                    st.markdown(content)
                else:
                    st.info("No external sources were referenced in this search.")
            
            with analysis_tab:
                st.markdown("### 📈 Content Analysis")
                
                # Create some metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sources Found", len(sources))
                with col2:
                    st.metric("Content Length", len(formatted_result))
                with col3:
                    st.metric("Sections", len(formatted_result.split("##")) - 1)
                
                # Add recency analysis
                st.markdown("### 📅 Recency Analysis")
                if isinstance(raw_result, dict) and 'Results' in raw_result:
                    recency_data = pd.DataFrame([
                        {
                            'Source': f"Source {idx + 1}",
                            'Year': result.get('verified_year', 'Unknown'),
                            'Recency Score': result.get('recency_score', 0)
                        }
                        for idx, result in enumerate(raw_result['Results'])
                    ])
                    
                    st.dataframe(recency_data)
                
        except Exception as e:
            st.error(f"🚨 An error occurred: {str(e)}")
            st.markdown("""
            Please try:
            - Rephrasing your query
            - Checking your internet connection
            - Trying again in a few moments
            """)

# Footer with quick tips and stats
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 🚀 Quick Tips")
    st.markdown("""
    - Be specific in your queries
    - Use relevant keywords
    - Check multiple sources
    """)
with col2:
    st.markdown("### 🎯 Features")
    st.markdown("""
    - Intelligent search
    - Source verification
    - Export capabilities
    """)
with col3:
    st.markdown("### 📊 Stats")
    st.markdown(f"""
    - Searches today: {len(st.session_state.search_history)}
    - Sources analyzed: {len(sources) if 'sources' in locals() else 0}
    """)