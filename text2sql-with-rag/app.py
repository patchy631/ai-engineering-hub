import os
import asyncio
import re
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from utils.sql_engine import SQLQueryEngine
from utils.rag_engine import retrieve_rag_tool
from utils.agent import RouterOutputAgentWorkflow


class CityExplorerChatbot:
    """
    Streamlit-based chatbot that retrieves structured data and knowledge-based insights 
    about major U.S. cities using a combination of RAG and SQL query engines.
    """

    def __init__(self):
        """Initialize chatbot, load environment variables, and setup tools."""
        load_dotenv()

        # Configure Ollama LLM
        Settings.llm = Ollama("mistral")
        Settings.embed_model = OllamaEmbedding(model_name="mistral")

        # Initialize AI tools
        self.sql_tool, self.rag_tool = self.initialize_tools()

        # Initialize workflow agent
        self.workflow = RouterOutputAgentWorkflow(
            tools=[self.sql_tool, self.rag_tool], verbose=True, timeout=120
        )

        # Initialize chat session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def initialize_tools(self):
        """Initializes SQL and RAG tools for processing queries."""
        sql_tool = SQLQueryEngine().get_sql_tool()
        rag_tool = retrieve_rag_tool()
        return sql_tool, rag_tool

    def format_response(self, response):
        """
        Detects lists and formats them into proper markdown bullet points while
        preserving introductory text before the list.

        Args:
            response (str): Raw AI response.

        Returns:
            str: Formatted response.
        """
        match = re.match(r"^(.*?:)(.*)$", response, re.DOTALL)
        if match:
            intro, list_part = match.groups()
            list_items = [item.strip() for item in list_part.split(", ") if item.strip()]
            if len(list_items) > 1:
                formatted_list = "\n".join(f"- {item}" for item in list_items)
                return f"{intro}\n\n{formatted_list}"
        return response

    async def get_response(self, user_input):
        """Runs the chatbot workflow asynchronously."""
        return await self.workflow.run(message=user_input)

    def run_chat(self):
        """Runs the Streamlit chat interface."""
        st.set_page_config(page_title="City Explorer Chatbot", page_icon="🌆")
        st.title("City Explorer Chatbot")

        # Sidebar description
        st.sidebar.title("About This Chatbot")
        st.sidebar.image(os.path.dirname(os.path.abspath(__file__)) + "/assets/us_cities.jpeg")
        st.sidebar.info(
            "Welcome to the City Explorer Chatbot! This tool helps you find key attractions, "
            "places to visit, and other essential details about major U.S. cities.\n\n"
            "**Supported cities:** New York City, Los Angeles, Chicago, Houston, Miami, Seattle.\n\n"
            "Simply ask a question, and our AI will retrieve useful information from structured databases and knowledge sources."
        )

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user input
        if user_input := st.chat_input("Ask about New York City, Los Angeles, Chicago, Houston, Miami, or Seattle..."):
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            # Get response
            response = asyncio.run(self.get_response(user_input))
            formatted_response = self.format_response(response)

            with st.chat_message("assistant"):
                st.markdown(formatted_response, unsafe_allow_html=True)

            # Append response to chat history
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})


# Run the chatbot
if __name__ == "__main__":
    chatbot = CityExplorerChatbot()
    chatbot.run_chat()