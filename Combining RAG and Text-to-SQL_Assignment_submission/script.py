import streamlit as st
import asyncio
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, insert
from my_agent import RouterOutputAgentWorkflow, NLSQLTableQueryEngine, SQLDatabase, sql_tool, llama_cloud_tool
from llama_index.core.tools import QueryEngineTool
from llama_index.core.workflow import Workflow, StartEvent
from typing import List, Any, Optional

# Use a persistent database file instead of in-memory
DATABASE_PATH = "sqlite:///city_stats.db"

def ensure_database():
    """Ensures the database and table exist."""
    engine = create_engine(DATABASE_PATH, future=True)
    metadata_obj = MetaData()

    # Define the table
    table_name = "city_stats"
    city_stats_table = Table(
        table_name,
        metadata_obj,
        Column("city_name", String(50), primary_key=True),
        Column("population", Integer),
        Column("state", String(50), nullable=False),
    )

    # Create table if it doesn't exist
    metadata_obj.create_all(engine)

    # Insert sample data only if table is empty
    with engine.begin() as connection:
        result = connection.execute(city_stats_table.select())
        if not result.fetchall():  # Table is empty
            rows = [
                {"city_name": "New York City", "population": 8336000, "state": "New York"},
                {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
                {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
                {"city_name": "Houston", "population": 2303000, "state": "Texas"},
                {"city_name": "Miami", "population": 449514, "state": "Florida"},
                {"city_name": "Seattle", "population": 749256, "state": "Washington"},
            ]
            for row in rows:
                connection.execute(insert(city_stats_table).values(**row))

    return engine

# Ensure DB exists before Streamlit reruns
engine = ensure_database()

# Ensure event loop compatibility in Streamlit
if "loop" not in st.session_state:
    st.session_state.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(st.session_state.loop)

# Reinitialize SQL Database & Query Engine on every rerun
sql_database = SQLDatabase(engine, include_tables=["city_stats"])
sql_query_engine = NLSQLTableQueryEngine(sql_database=sql_database, tables=["city_stats"])

# Replace the SQL tool with the new engine reference
sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description="Tool for querying city population and states from SQL database.",
    name="sql_tool"
)

# Enhanced Workflow with Step and Tool Logging
class EnhancedRouterOutputAgentWorkflow(RouterOutputAgentWorkflow):
    def __init__(self, tools: List[Any], update_callback=None, *args, **kwargs):
        super().__init__(tools=tools, *args, **kwargs)
        self.update_callback = update_callback  # Callback to send step updates
        self.current_step = 0  # Track step number
        self.called_tools = set()  # Track tools called

    async def log_step(self, message: str, tools: Optional[List[str]] = None):
        """Log a step to the UI via callback with step numbering and tools."""
        self.current_step += 1
        if tools:
            self.called_tools.update(tools)
            tool_msg = f" (Tools called: {', '.join(tools)})"
        else:
            tool_msg = ""
        if self.update_callback:
            await self.update_callback(f"Step {self.current_step}: {message}{tool_msg}")

    async def run(self, *args, **kwargs):
        """Override run to add logging at key points and infer tool usage."""
        self.current_step = 0  # Reset step counter
        self.called_tools.clear()  # Reset tool set
        message = kwargs.get("message")
        await self.log_step(f"Starting query: '{message}'")

        # Log entry into prepare_chat
        await self.log_step("Preparing chat history...")
        
        # Simulate "chat" step and infer tool usage based on query
        await self.log_step("Analyzing query with LLM...")
        inferred_tools = self.infer_tools(message)
        await self.log_step("Processing tools...", tools=inferred_tools)
        
        # Call the base class run method
        result = await super().run(*args, **kwargs)
        
        # Log final result preparation
        await self.log_step("Gathering results and finalizing response...")
        
        # Log completion and all called tools
        if self.called_tools:
            await self.log_step(f"Query processing completed. Total tools used: {', '.join(self.called_tools)}")
        else:
            await self.log_step("Query processing completed.")
        
        return result

    def infer_tools(self, query: str) -> List[str]:
        """Infer which tools might be used based on the query (simple heuristic)."""
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ["population", "state", "city"]):
            return ["sql_tool"]  # Likely uses SQL for population/state data
        elif any(keyword in query_lower for keyword in ["history", "landmark", "significance"]):
            return ["llama_cloud_tool"]  # Likely uses LlamaCloud for historical data
        elif "population" in query_lower and "history" in query_lower:
            return ["sql_tool", "llama_cloud_tool"]  # Combined query
        return []  # No tools inferred

# Create the workflow instance with callback
wf = EnhancedRouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool])

# Streamlit UI
st.title("Combining RAG and Text-to-SQL in a Single Query Interface")

# User Input
user_query = st.text_input("Enter your question:")

# Container for step-by-step updates
if "steps" not in st.session_state:
    st.session_state.steps = []
steps_container = st.empty()

# Callback to update steps in UI
async def update_steps(message: str):
    st.session_state.steps.append(message)
    with steps_container.container():
        st.markdown("### Processing Steps:")
        for step in st.session_state.steps:
            st.markdown(f"- {step}")

# Update workflow with callback
wf.update_callback = update_steps

# Async function to call the workflow
async def process_query(query):
    st.session_state.steps = []  # Reset steps for new query
    return await wf.run(message=query)

# Handle Streamlit button click
if st.button("Submit Query"):
    if user_query:
        with st.spinner("Fetching answer..."):
            task = st.session_state.loop.create_task(process_query(user_query))
            result = st.session_state.loop.run_until_complete(task)
        st.success("Query completed!")
        st.markdown("### Final Result:")
        st.markdown(result)
    else:
        st.warning("Please enter a question before submitting.")