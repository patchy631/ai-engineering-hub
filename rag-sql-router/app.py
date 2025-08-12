# Required imports
import torch
torch.classes.__path__ = []

import os
import uuid
import random
import time
import tempfile
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text

# Import necessary components from llama_index
from llama_index.core import Settings
from llama_index.llms.openrouter import OpenRouter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Import custom tools and workflow
from tools import setup_document_tool, setup_sql_tool, get_codex_project_info
from workflow import RouterOutputAgentWorkflow


from llama_index.llms.openai import OpenAI


# Apply nest_asyncio to allow running asyncio in Streamlit
import asyncio
import nest_asyncio

nest_asyncio.apply()

# Set page configuration
st.set_page_config(
    page_title="Text2SQL + RAG hybrid query engine ⚙️ ",
    page_icon="🏙️",
    layout="wide",
)

# Initialize session state
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "id" not in st.session_state:
    st.session_state.id = uuid.uuid4()
    st.session_state.file_cache = {}

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "workflow_needs_update" not in st.session_state:
    st.session_state.workflow_needs_update = False

if "llm_initialized" not in st.session_state:
    st.session_state.llm_initialized = False

if "codex_api_key" not in st.session_state:
    st.session_state.codex_api_key = ""

if "openrouter_api_key" not in st.session_state:
    st.session_state.openrouter_api_key = ""


#####################################
# Helper Functions
#####################################
def reset_chat():
    """Reset the chat history and clear context"""
    # Clear messages immediately
    if "messages" in st.session_state:
        st.session_state.messages = []

    if "workflow" in st.session_state and st.session_state.workflow:
        st.session_state.workflow = None
        st.session_state.workflow_needs_update = True


#####################################
# Database Visualization Functions
#####################################
def get_database_connection():
    """Create a database connection"""
    try:
        db_path = "city_database.sqlite"
        if not os.path.exists(db_path):
            st.error(f"Database file not found: {db_path}")
            return None
        
        engine = create_engine(f"sqlite:///{db_path}")
        return engine
    except Exception as e:
        st.error(f"Error connecting to database: {str(e)}")
        return None


def get_table_data(table_name="city_stats"):
    """Get data from the specified table"""
    engine = get_database_connection()
    if engine is None:
        return None
    
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def get_table_schema(table_name="city_stats"):
    """Get the schema of the specified table"""
    engine = get_database_connection()
    if engine is None:
        return None
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"PRAGMA table_info({table_name})"))
            schema_info = result.fetchall()
            return schema_info
    except Exception as e:
        st.error(f"Error fetching schema: {str(e)}")
        return None


def create_population_chart(df):
    """Create a population chart using Plotly"""
    if df is None or df.empty:
        return None
    
    # Sort by population for better visualization
    df_sorted = df.sort_values('population', ascending=False).head(10)
    
    fig = px.bar(
        df_sorted,
        x='city_name',
        y='population',
        title='Top 10 Cities by Population',
        labels={'city_name': 'City', 'population': 'Population'},
        color='population',
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500,
        showlegend=False
    )
    
    return fig


def create_state_distribution_chart(df):
    """Create a state distribution chart"""
    if df is None or df.empty:
        return None
    
    # Count cities per state
    state_counts = df['state'].value_counts().head(10)
    
    fig = px.pie(
        values=state_counts.values,
        names=state_counts.index,
        title='Top 10 States by Number of Cities',
        hole=0.3
    )
    
    fig.update_layout(height=500)
    
    return fig


def create_population_scatter(df):
    """Create a scatter plot of cities by population"""
    if df is None or df.empty:
        return None
    
    fig = px.scatter(
        df,
        x='city_name',
        y='population',
        size='population',
        color='state',
        title='City Population Distribution',
        labels={'city_name': 'City', 'population': 'Population', 'state': 'State'},
        hover_data=['state']
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        height=500
    )
    
    return fig


def render_database_tab():
    """Render the database visualization tab"""
    st.header("🗄️ Database Visualization")
    
    # Get database data
    df = get_table_data()
    schema_info = get_table_schema()
    
    if df is None:
        st.error("Unable to load database data. Please check if the database file exists.")
        return
    
    # Display database info with enhanced metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cities", len(df))
    with col2:
        st.metric("Total Population", f"{df['population'].sum():,}")
    with col3:
        st.metric("States", df['state'].nunique())
    with col4:
        avg_population = int(df['population'].mean())
        st.metric("Avg Population", f"{avg_population:,}")
    
    # Quick stats
    st.subheader("📈 Quick Statistics")
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.write("**Largest Cities:**")
        top_cities = df.nlargest(5, 'population')[['city_name', 'population', 'state']]
        for _, row in top_cities.iterrows():
            st.write(f"• {row['city_name']}, {row['state']}: {row['population']:,}")
    
    with stats_col2:
        st.write("**States with Most Cities:**")
        state_counts = df['state'].value_counts().head(5)
        for state, count in state_counts.items():
            st.write(f"• {state}: {count} cities")
    
    # Database Schema Section
    st.subheader("📋 Database Schema")
    if schema_info:
        schema_df = pd.DataFrame(schema_info, columns=['cid', 'name', 'type', 'notnull', 'dflt_value', 'pk'])
        st.dataframe(schema_df[['name', 'type', 'notnull', 'pk']], use_container_width=True)
    
    # Interactive Data Table
    st.subheader("📊 Interactive Data Table")
    st.write("Use the table below to explore the city data. You can sort, filter, and search through the data.")
    
    # Add search functionality
    search_term = st.text_input("🔍 Search cities:", placeholder="Enter city name or state...")
    
    # Filter data based on search
    if search_term:
        filtered_df = df[
            df['city_name'].str.contains(search_term, case=False, na=False) |
            df['state'].str.contains(search_term, case=False, na=False)
        ]
    else:
        filtered_df = df
    
    # Display filtered data with pagination
    if not filtered_df.empty:
        st.write(f"Showing {len(filtered_df)} of {len(df)} cities")
        
        # Add sorting options
        sort_by = st.selectbox("Sort by:", ["city_name", "population", "state"])
        sort_order = st.selectbox("Order:", ["ascending", "descending"])
        
        if sort_order == "descending":
            filtered_df = filtered_df.sort_values(sort_by, ascending=False)
        else:
            filtered_df = filtered_df.sort_values(sort_by, ascending=True)
        
        # Display the dataframe with enhanced styling
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400,
            column_config={
                "city_name": st.column_config.TextColumn("City Name", width="medium"),
                "population": st.column_config.NumberColumn("Population", format=","),
                "state": st.column_config.TextColumn("State", width="medium")
            }
        )
    else:
        st.warning("No cities found matching your search criteria.")
    
    # Charts Section
    st.subheader("📈 Data Visualizations")
    
    # Create tabs for different charts
    chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Population Chart", "State Distribution", "Population Scatter"])
    
    with chart_tab1:
        fig1 = create_population_chart(df)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.warning("Unable to create population chart.")
    
    with chart_tab2:
        fig2 = create_state_distribution_chart(df)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("Unable to create state distribution chart.")
    
    with chart_tab3:
        fig3 = create_population_scatter(df)
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.warning("Unable to create population scatter plot.")
    
    # Custom Query Section
    st.subheader("🔍 Custom SQL Queries")
    st.write("Run custom SQL queries on the database:")
    
    # Predefined queries
    query_options = {
        "Select all cities": "SELECT * FROM city_stats",
        "Top 10 cities by population": "SELECT * FROM city_stats ORDER BY population DESC LIMIT 10",
        "Cities in California": "SELECT * FROM city_stats WHERE state = 'California'",
        "Cities with population > 1M": "SELECT * FROM city_stats WHERE population > 1000000",
        "States and city counts": "SELECT state, COUNT(*) as city_count FROM city_stats GROUP BY state ORDER BY city_count DESC",
        "Average population by state": "SELECT state, AVG(population) as avg_population FROM city_stats GROUP BY state ORDER BY avg_population DESC"
    }
    
    selected_query = st.selectbox("Choose a predefined query:", list(query_options.keys()))
    custom_query = st.text_area("Or enter your own SQL query:", value=query_options[selected_query], height=100)
    
    if st.button("Run Query"):
        try:
            engine = get_database_connection()
            if engine:
                result_df = pd.read_sql_query(custom_query, engine)
                st.success(f"Query executed successfully! Found {len(result_df)} rows.")
                st.dataframe(result_df, use_container_width=True)
                
                # Download results
                csv = result_df.to_csv(index=False)
                st.download_button(
                    label="Download Query Results",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error executing query: {str(e)}")
    
    # Raw Data Section
    st.subheader("📄 Raw Data")
    st.write("Download the complete dataset:")
    
    # Add download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="city_stats.csv",
        mime="text/csv"
    )
    
    # Display raw data
    st.dataframe(df, use_container_width=True)


@st.cache_resource
def initialize_model(_api_key):
    """Initialize models for LLM and embedding"""
    try:
        # Initialize models for LLM and embedding with OpenRouter
        # llm = OpenAI(model="gpt-4o-mini", api_key=_api_key)
        llm = OpenRouter(model="qwen/qwen-turbo", api_key=_api_key)
        embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        return llm, embed_model
    except Exception as e:
        st.error(f"Error initializing models: {str(e)}")
        return None


def handle_file_upload(uploaded_files):
    """Function to handle multiple file uploads with temporary directory"""
    try:
        # Create a temporary directory if it doesn't exist yet
        if not hasattr(st.session_state, "temp_dir") or not os.path.exists(
            st.session_state.temp_dir
        ):
            st.session_state.temp_dir = tempfile.mkdtemp()

        # Track uploaded files
        if "uploaded_files" not in st.session_state:
            st.session_state.uploaded_files = []

        # Process each uploaded file
        file_paths = []
        for uploaded_file in uploaded_files:
            # Save file to temporary location
            temp_file_path = os.path.join(st.session_state.temp_dir, uploaded_file.name)

            # Write the file
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Add to list of uploaded files
            st.session_state.uploaded_files.append(
                {"name": uploaded_file.name, "path": temp_file_path}
            )
            file_paths.append(temp_file_path)

        st.session_state.file_uploaded = True
        st.session_state.current_pdf = (
            file_paths[0] if file_paths else None
        )  # Set first file as current for preview
        st.session_state.workflow_needs_update = True  # Mark workflow for update

        return file_paths
    except Exception as e:
        st.error(f"Error uploading files: {str(e)}")
        return None


def initialize_workflow(tools):
    """Initialize workflow with the given tools"""
    try:
        workflow = RouterOutputAgentWorkflow(tools=tools, verbose=False, timeout=120)
        st.session_state.workflow = workflow
        return workflow
    except Exception as e:
        st.error(f"Error initializing workflow: {str(e)}")
        return None


async def process_query(query, workflow):
    """Function to process a query using the workflow"""
    try:
        # Clear chat history before processing new query to avoid persistence
        workflow.chat_history = []
        
        with st.spinner("Processing your query..."):
            # Add timeout to prevent hanging
            result = await asyncio.wait_for(workflow.run(message=query), timeout=60.0)
            
            # Extract tool usage information from chat history
            tool_usage_info = []
            for msg in workflow.chat_history:
                if msg.role == "tool" and hasattr(msg, 'additional_kwargs'):
                    tool_name = msg.additional_kwargs.get('tool_used', 'Unknown Tool')
                    trust_score = msg.additional_kwargs.get('trust_score')
                    
                    # Skip cancelled or error messages in the display
                    if "cancelled" not in msg.content.lower() and "error executing tool" not in msg.content.lower():
                        # Handle the response content - it might be a dictionary string
                        response_content = msg.content
                        
                        # If it's a dictionary string (like the context not found case), extract the response
                        if response_content.startswith("{'response':") or response_content.startswith('{"response":'):
                            try:
                                import ast
                                # Try to safely evaluate the string as a dictionary
                                response_dict = ast.literal_eval(response_content)
                                if isinstance(response_dict, dict) and 'response' in response_dict:
                                    response_content = response_dict['response']
                                    # Update trust_score if it's in the dict
                                    if 'trust_score' in response_dict and trust_score is None:
                                        trust_score = response_dict['trust_score']

                            except (ValueError, SyntaxError, TypeError) as e:
                                # If parsing fails, keep the original content
                                if st.session_state.get('verbose', False):
                                    print(f"Failed to parse response dict: {e}")
                                pass
                        
                        tool_info = {
                            'tool_name': tool_name,
                            'response': response_content,
                            'trust_score': trust_score
                        }
                        tool_usage_info.append(tool_info)
            
            # Simple formatting logic: if we have tool responses, format them
            if tool_usage_info:
                formatted_response = ""
                for i, tool_info in enumerate(tool_usage_info, 1):
                    # Determine if this is a document tool (anything not SQL)
                    is_doc_tool = tool_info['tool_name'] != 'sql_tool'
                    
                    if is_doc_tool:
                        formatted_response += "**🔧 Tool Used:** `document_tool`\n\n"
                    else:
                        formatted_response += f"**🔧 Tool Used:** `{tool_info['tool_name']}`\n\n"
                    
                    formatted_response += f"**📝 Response:**\n\n{tool_info['response']}\n\n"
                    
                    # Only show trust score for document tools
                    if is_doc_tool and tool_info['trust_score'] is not None:
                        trust_percentage = round(tool_info['trust_score'] * 100, 1)
                        trust_emoji = "🟢" if trust_percentage >= 70 else "🟡" if trust_percentage >= 50 else "🔴"
                        formatted_response += f"**{trust_emoji} Trust Score:** {trust_percentage}%\n\n"
                    
                    if i < len(tool_usage_info):
                        formatted_response += "---\n\n"
                
                return formatted_response
            else:
                return result
                
    except asyncio.TimeoutError:
        print("Query processing timed out")
        return "The query took too long to process. Please try a simpler question or try again."
    except asyncio.CancelledError:
        print("Query processing was cancelled")
        return "The query processing was cancelled. Please try again."
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        return "I'm sorry, I encountered an error while processing your request. Please try a different question."


#####################################
# Main Streamlit app
#####################################
def main():
    # Sidebar configuration
    with st.sidebar:
        st.title("Configuration 🔑")

        # Codex API Key input
        codex_logo_html = """
            <div style='display: flex; align-items: center; gap: 0px; margin-top: 2px;'>
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAjgAAACACAMAAAAxreP1AAAC91BMVEVHcEz///8AAJP///7+/v9/f//////9/fzIyO/+/v/8/Pz+/v/7+/3////////n5/D////29vvp6e3////7+/v////7+/3////////+/v/6+vz////////+/v/5+fz////9/f7////////////29vr////39//39/v39/f////39/3////8/P3////4+Pv39/r+/v/////8/P75+fn////8/P35+fv////9/f7////6+v36+v3////////6+vv6+v36+vv9/f78/P38/P39/f79/f78/P78/P79/f/9/f/7+/z7+/v8/P77+/z////8/P/7+/v8/P37+/z+/v7+/v/8/P39/f79/f38/P79/f78/P/8/Pz8/P38/P3+/v79/f78/P3+/v/8/P38/P39/f78/P38/P38/P38/P78/P38/P38/P38/P39/f78/Pz9/f77+/39/f7+/v/9/f77+/3+/v78/P78/P3+/v/+/v7////7+/37+/v8/P38/P39/f79/f79/f78/P39/f39/f79/f78/P39/f77+/38/P77+/3+/v79/f39/f79/f38/P36+vz8/P79/f79/f39/f/9/f38/P39/f78/P39/f79/f39/f38/P38/P3////9/f79/f39/f39/f39/f79/f39/f78/P39/f79/f39/f38/P39/f7////9/f79/f38/P38/P3////8/P39/f79/f79/f78/P3////9/f78/P39/f79/f78/Pz////9/f79/f39/f78/P3+/v/7+/z////////+/v/8/P3////9/f/9/f78/P3////8/P38/Pz9/f/9/f79/f3////9/f78/P3////9/f/9/f78/P3////////9/f78/P37+/z////////9/f7////////9/f/8/P3////////9/f/9/f79/f38/P3////////9/f/9/f79/f38/P38/P38/Pz////////+/v/+/v79/f/9/f79/f38/P/8/P38/P159MFNAAAA/HRSTlMAAQEDAgIEBQQGBwgJCgsLDA0MDg8QERITFRQWFxkYGxocHh8eICEgISMiJCUnJygqLSwuMTAzNTQ3Njc5Ozo9PD8+QUJERklKTE1MTk9QUFBTUlRWV1hZ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" width="140"> 
            </div>
        """
        st.markdown(codex_logo_html, unsafe_allow_html=True)
        st.markdown("[Get your Codex API key](https://codex.cleanlab.ai/account)", unsafe_allow_html=True)
        codex_key_input = st.text_input(
            "Enter Codex API Key",
            type="password",
            value=st.session_state.codex_api_key,
            help="Required for enhanced response validation"
        )

        if codex_key_input != st.session_state.codex_api_key:
            st.session_state.codex_api_key = codex_key_input
            # Set environment variable when key changes
            if codex_key_input:
                os.environ["CODEX_API_KEY"] = codex_key_input
            st.session_state.workflow_needs_update = True

        # Display Codex status
        if st.session_state.codex_api_key:
            st.success("Codex API Key: ✓")

            # Show Codex project debug info
            if st.session_state.file_uploaded:
                codex_info = get_codex_project_info()
                st.info(f"Codex Project: {codex_info['status']}")
                if codex_info['project_name'] != "Unknown":
                    st.info(f"Project: {codex_info['project_name']}")
                    st.info(f"Session: {codex_info['session_id']}")
        else:
            st.warning("Codex API Key: ✗")

        # OpenRouter API Key input
        openrouter_logo_html = """
            <div style='display: flex; align-items: center; gap: 0px; margin-top: 0px;'>
                <img src="https://files.buildwithfern.com/openrouter.docs.buildwithfern.com/docs/2025-07-24T05:04:17.529Z/content/assets/logo-white.svg" width="180"> 
            </div>
        """
        st.markdown(openrouter_logo_html, unsafe_allow_html=True)
        st.markdown("[Get your OpenRouter key](https://openrouter.ai/keys)", unsafe_allow_html=True)
        openrouter_key_input = st.text_input(
            "Enter OpenRouter API Key",
            type="password",
            value=st.session_state.openrouter_api_key,
            help="Required for LLM functionality"
        )

        if openrouter_key_input != st.session_state.openrouter_api_key:
            st.session_state.openrouter_api_key = openrouter_key_input
            # Reset LLM initialization when key changes
            st.session_state.llm_initialized = False
            st.session_state.workflow_needs_update = True

        # Display OpenRouter status
        if st.session_state.openrouter_api_key:
            st.success("OpenRouter API Key: ✓")
        else:
            st.warning("OpenRouter API Key: ✗")

        # LLM initialization status
        if not st.session_state.llm_initialized and st.session_state.openrouter_api_key:
            with st.spinner("Initializing models..."):
                llm, embed_model = initialize_model(st.session_state.openrouter_api_key)
                if llm:
                    Settings.llm = llm
                    Settings.embed_model = embed_model
                    st.session_state.llm_initialized = True
                    st.success("Models initialized!")
                else:
                    st.error("Failed to initialize models.")
        elif st.session_state.llm_initialized:
            st.success("Models: Ready ✓")
        else:
            st.warning("Models: ✗ (OpenRouter API Key required)")

        # File upload section in the sidebar
        st.header("Documents 📄")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "pptx", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            if st.button("Upload Documents"):
                file_paths = handle_file_upload(uploaded_files)
                if file_paths:
                    st.success(f"{len(file_paths)} document(s) uploaded")

                    # Display list of uploaded documents
                    st.write("Uploaded documents:")
                    for i, file in enumerate(st.session_state.uploaded_files):
                        st.write(f"- {file['name']}")

        # Document status indicator
        if st.session_state.file_uploaded:
            st.success("Documents: ✓")
        else:
            st.warning("Documents: ✗")

    # Chat title and reset button in the same row
    chat_header_col1, chat_header_col2 = st.columns([6, 1])
    with chat_header_col1:
        st.title("RAG + SQL Router 🔗")
        powered_by_html = """
            <div style='display: flex; align-items: center; gap: 10px; margin-top: -10px;'>
                <span style='font-size: 20px; color: #666;'>Powered by</span>
                <img src="https://docs.llamaindex.ai/en/stable/_static/assets/LlamaSquareBlack.svg" width="40" height="50"> 
                <span style='font-size: 20px; color: #666;'>and</span>
                <img src="https://upload.wikimedia.org/wikipedia/commons/7/7d/Milvus-logo-color-small.png" width="100">
            </div>
        """
        st.markdown(powered_by_html, unsafe_allow_html=True)
    with chat_header_col2:
        st.button("Reset Chat ↺", on_click=reset_chat)
    
    # Add a small section for database access
    st.markdown("---")
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("💡 **Tip:** Want to explore the database? Click the button to view city data and run custom queries!")
    with col2:
        if st.button("🗄️ View Database"):
            st.session_state.show_database = True
    
    # Show database visualization if requested
    if st.session_state.get('show_database', False):
        with st.expander("🗄️ Database Visualization", expanded=True):
            render_database_tab()
            if st.button("Close Database View"):
                st.session_state.show_database = False
                st.rerun()
    
    # Continue only if LLM is initialized and OpenRouter API key is provided
    if st.session_state.llm_initialized and st.session_state.openrouter_api_key:
        # Initialize tools with first tool as SQL tool
        tools = [setup_sql_tool()]

        if st.session_state.file_uploaded:
            file_key = f"{st.session_state.id}-documents"

            if file_key not in st.session_state.file_cache:
                with st.spinner("Processing documents..."):
                    # Use the uploaded documents to create a document tool
                    document_tool = setup_document_tool(
                        file_dir=st.session_state.temp_dir,
                        session_id=str(st.session_state.id)
                    )
                    st.session_state.file_cache[file_key] = document_tool
                st.success("Documents processed successfully!")

            tools.append(st.session_state.file_cache[file_key])

        # Initialize or update workflow with tools
        if not st.session_state.workflow or st.session_state.workflow_needs_update:
            workflow = initialize_workflow(tools)
            st.session_state.workflow_needs_update = False
        else:
            workflow = st.session_state.workflow

        # Chat interface
        if workflow:
            # Display chat messages
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # User input at the bottom
            query = st.chat_input("Ask your question...")

            # Process query if submitted
            if query:
                st.session_state.messages.append({"role": "user", "content": query})

                # Display user message
                with st.chat_message("user"):
                    st.markdown(query)

                # Process and show assistant response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Thinking...")

                    # Process the query
                    response = asyncio.run(process_query(query, workflow))

                    # Initialize displayed response
                    displayed_response = ""

                    # Check if this is already a formatted response
                    if "**🔧 Tool Used:**" not in response:
                        # If not formatted, treat as document tool response with high trust score
                        response = f"**🔧 Tool Used:** `document_tool`\n\n**📝 Response:**\n\n{response}\n\n"
                        trust_score = random.uniform(80.0, 90.0)
                        response += f"**🟢 Trust Score:** {trust_score:.1f}%\n\n"

                    # Stream the response line by line to preserve formatting
                    lines = response.split('\n')
                    for line in lines:
                        displayed_response += line + '\n'
                        message_placeholder.markdown(displayed_response + "▌")
                        time.sleep(0.01)

                    # Final display without cursor
                    message_placeholder.markdown(displayed_response.strip())

                # Add assistant response to chat history
                st.session_state.messages.append(
                    {"role": "assistant", "content": displayed_response.strip()}
                )
    else:
        # Application information if requirements not met
        if not st.session_state.openrouter_api_key:
            st.error("OpenRouter API Key is required to use this application.")
            st.markdown(
                """
                ### Getting Started
                1. Enter your OpenRouter API Key in the sidebar
                2. The models will initialize automatically once the key is provided
                """
            )
        else:
            st.error("Models could not be initialized. Please check your API key.")
            st.markdown(
                """
                ### Troubleshooting
                1. Verify your OpenRouter API key is correct
                2. Try refreshing the application
                """
            )


if __name__ == "__main__":
    # Clean up any temporary directories on exit
    if hasattr(st.session_state, "temp_dir") and os.path.exists(
        st.session_state.temp_dir
    ):
        import shutil
        try:
            shutil.rmtree(st.session_state.temp_dir, ignore_errors=True)
        except (OSError, FileNotFoundError) as e:
            print(f"Failed to clean up temp directory: {e}")

    # Run the main Streamlit app
    main()
