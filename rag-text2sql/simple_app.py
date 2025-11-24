import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="RAG + Text-to-SQL Demo",
    page_icon="🦙",
    layout="wide",
)

# App title and description
st.title("🦙 RAG + Text-to-SQL Unified Query Interface")
st.markdown("""
This application demonstrates how to combine Retrieval-Augmented Generation (RAG) and Text-to-SQL 
capabilities in a single query interface. Ask questions about US cities that can be answered either 
through SQL queries on structured data or through RAG on unstructured data.
""")

# Sidebar for API keys and configuration
with st.sidebar:
    st.header("Configuration")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    llama_cloud_api_key = st.text_input("LlamaCloud API Key", type="password")
    
    st.subheader("LlamaCloud Configuration")
    index_name = st.text_input("Index Name", "us-cities-index")
    project_name = st.text_input("Project Name", "demo-project")
    org_id = st.text_input("Organization ID", "your-org-id")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This demo shows how to:
    1. Route queries to the appropriate tool (SQL or RAG)
    2. Process structured data with Text-to-SQL
    3. Process unstructured data with RAG
    4. Combine results in a unified interface
    """)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["Chat Interface", "Data Explorer", "How It Works"])

# Tab 1: Chat Interface
with tab1:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about US cities..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            if not openai_api_key or not llama_cloud_api_key:
                st.markdown("⚠️ Please enter your API keys in the sidebar to continue.")
            else:
                with st.spinner("Thinking..."):
                    # Simulate response - in a real app, this would call the actual workflow
                    if "population" in prompt.lower() or "largest" in prompt.lower() or "smallest" in prompt.lower():
                        st.markdown("I'll use the SQL database to answer this question.")
                        st.markdown("New York City has the highest population among US cities in our database.")
                    elif "space needle" in prompt.lower():
                        st.markdown("I'll use the RAG system to answer this question.")
                        st.markdown("The Space Needle is located in Seattle, Washington.")
                    elif "visit" in prompt.lower() and any(city in prompt.lower() for city in ["miami", "new york", "los angeles", "chicago", "houston", "seattle"]):
                        st.markdown("I'll use the RAG system to answer this question about attractions.")
                        st.markdown("""Here are some places to visit in Miami:
- Beaches and parks
- Zoo Miami
- Jungle Island
- Miami Seaquarium
- Botanic Garden
- Key Biscayne
- South Beach
- Lincoln Road
- Bayside Marketplace""")
                    else:
                        st.markdown("I'll analyze your question and determine the best way to answer it.")
                        st.markdown("Based on my analysis, I would need to use both structured and unstructured data sources to fully answer this question. In a complete implementation, I would route this to the appropriate tool or combine results from multiple tools.")
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": "Response simulation for: " + prompt})

# Tab 2: Data Explorer
with tab2:
    st.header("Explore the Data")
    
    # Create sample data for display
    city_data = {
        "city_name": ["New York City", "Los Angeles", "Chicago", "Houston", "Miami", "Seattle"],
        "population": [8336000, 3822000, 2665000, 2303000, 449514, 749256],
        "state": ["New York", "California", "Illinois", "Texas", "Florida", "Washington"]
    }
    
    df = pd.DataFrame(city_data)
    
    st.subheader("Structured Data (SQL Database)")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Unstructured Data (RAG Index)")
    st.markdown("""
    The RAG system contains information from Wikipedia pages about:
    - New York City
    - Los Angeles
    - Chicago
    - Houston
    - Miami
    - Seattle
    
    This includes information about history, culture, attractions, transportation, and more that isn't captured in the structured database.
    """)

# Tab 3: How It Works
with tab3:
    st.header("How It Works")
    
    st.subheader("Architecture")
    st.markdown("""
    ```
    +------------------------------------------+
    |                                          |
    |           User Query Interface           |
    |                                          |
    +------------------+---------------------+
                       |
                       v
    +------------------------------------------+
    |                                          |
    |           Query Analysis (LLM)           |
    |                                          |
    +------------------+---------------------+
                       |
            +----------+-----------+
            |                      |
            v                      v
    +----------------+    +------------------+
    |                |    |                  |
    | SQL Query Tool |    |   RAG Query Tool |
    |                |    |                  |
    +-------+--------+    +--------+---------+
            |                      |
            v                      v
    +----------------+    +------------------+
    |                |    |                  |
    | SQL Database   |    |  Document Index  |
    | (Structured)   |    |  (Unstructured)  |
    |                |    |                  |
    +-------+--------+    +--------+---------+
            |                      |
            +----------+-----------+
                       |
                       v
    +------------------------------------------+
    |                                          |
    |          Response Generation (LLM)       |
    |                                          |
    +------------------------------------------+
                       |
                       v
    +------------------------------------------+
    |                                          |
    |              User Response               |
    |                                          |
    +------------------------------------------+
    ```
    """)
    
    st.subheader("Query Routing Process")
    st.markdown("""
    1. **User Query**: The user submits a natural language question.
    2. **Query Analysis**: The LLM analyzes the query to determine if it requires:
       - Structured data (SQL)
       - Unstructured data (RAG)
       - Both
    3. **Tool Selection**: The appropriate tool is selected based on the analysis.
    4. **Query Execution**: The query is executed using the selected tool(s).
    5. **Response Generation**: Results are formatted into a natural language response.
    """)
    
    st.subheader("Code Implementation")
    with st.expander("View Core Code"):
        st.code("""
# Create query engine tools
sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/state of"
        " each city located in the USA."
    ),
    name="sql_tool"
)

llama_cloud_tool = QueryEngineTool.from_defaults(
    query_engine=llama_cloud_query_engine,
    description=(
        "Useful for answering semantic questions about certain cities in the US."
    ),
    name="llama_cloud_tool"
)

# Create the workflow
wf = RouterOutputAgentWorkflow(
    tools=[sql_tool, llama_cloud_tool], 
    verbose=True
)

# Run the workflow
result = await wf.run(message="What is the population of Seattle?")
        """, language="python")

# Footer
st.markdown("---")
st.markdown("Created for DailyDoseofDS Technical Writer Task") 