import streamlit as st
import asyncio
from query_agent import RouterOutputAgentWorkflow
from tool_setup import QueryEngineTools

class RAGSQLAgentApp:
    """Streamlit UI for querying SQL databases using an agent workflow with continuous chat history."""

    def __init__(self):
        """Initialize the application and workflow."""
        self.tools = QueryEngineTools()
        self.workflow = RouterOutputAgentWorkflow(
            tools=[self.tools.get_sql_tool(), self.tools.get_llama_cloud_tool()], 
            verbose=True, 
            timeout=120
        )
        self._setup_ui()

    async def run_query(self, query):
        """Runs the query asynchronously using the workflow."""
        return await self.workflow.run(message=query)

    def _setup_ui(self):
        """Setup Streamlit UI components."""
        with st.sidebar:
            st.image("./assets/my_image.png", width=300)
            st.markdown("## How to Use")
            st.write(
                "1. Enter your query about the US cities in the chat box given and press Enter.\n"
                "2. The assistant will process your query and respond.\n"
                
            )
            st.markdown("## Powered By")
            
            col1, col2, col3 = st.columns(3)

            # Display images in each column
            with col1:
                st.image("./assets/image1.png", width=80)

            with col2:
                st.image("./assets/image2.png", width=80)

            with col3:
                st.image("./assets/image3.png", width=80)

        # Main UI Title
        st.image("./assets/cover.png", width=800)
         

        # Initialize session state for chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Display chat history
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["query"])
            with st.chat_message("assistant"):
                st.write(chat["response"])

        # User input box for new queries
        query = st.chat_input("Enter your query:")

        if query:
            with st.chat_message("user"):
                st.write(query)

            with st.spinner("Processing..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.run_query(query))

            with st.chat_message("assistant"):
                st.write(result)

            # Store chat in session history
            st.session_state.chat_history.append({"query": query, "response": result})

# Run the app
if __name__ == "__main__":
    RAGSQLAgentApp()
