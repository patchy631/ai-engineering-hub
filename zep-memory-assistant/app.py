# Import necessary libraries
import re
import uuid
from autogen import UserProxyAgent
from zep_cloud.client import Zep
from zep_cloud import FactRatingExamples, FactRatingInstruction
from llm_config import config_list
from prompt import agent_system_message
from agent import ZepConversableAgent
from util import generate_user_id
import streamlit as st


# Define zep as a global variable to be initialized later
zep = None


def initialize_zep_client(api_key):
    """Initialize the Zep client with the provided API key."""
    global zep
    try:
        zep = Zep(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Failed to initialize Zep Client: {e}")
        return False


def initialize_session(first_name, last_name):
    """Initialize the session state and Zep connection."""
    # Check if we have a valid Zep client
    global zep
    if not zep:
        st.error("Zep client not initialized. Please enter a valid API key.")
        return

    if "zep_session_id" not in st.session_state:
        # Generate unique identifiers
        user_id = generate_user_id(first_name, last_name)

        # Streamlit session state
        st.session_state.zep_session_id = str(uuid.uuid4())
        st.session_state.zep_user_id = user_id
        st.session_state.chat_initialized = False
        st.session_state.messages = []  # Store chat history for display

        try:
            # Define fact rating instructions
            fact_rating_instruction = """Rate facts by relevance and utility. Highly relevant 
            facts directly impact the user's current needs or represent core preferences that 
            affect multiple interactions. Low relevance facts are incidental details that 
            rarely influence future conversations or decisions."""

            fact_rating_examples = FactRatingExamples(
                high="The user is developing a Python application using the Streamlit framework.",
                medium="The user prefers dark mode interfaces when available.",
                low="The user mentioned it was raining yesterday.",
            )

            # Attempt to add user
            user_exists = False
            try:
                # Try to get user
                zep.user.get(st.session_state.zep_user_id)
                user_exists = True
            except Exception:
                # User doesn't exist, create a new one
                zep.user.add(
                    first_name=first_name,
                    last_name=last_name,
                    user_id=st.session_state.zep_user_id,
                    fact_rating_instruction=FactRatingInstruction(
                        instruction=fact_rating_instruction,
                        examples=fact_rating_examples,
                    ),
                )

            # Add session for the user (whether new or existing)
            zep.memory.add_session(
                user_id=st.session_state.zep_user_id,
                session_id=st.session_state.zep_session_id,
            )

            # Show appropriate message
            if user_exists:
                st.sidebar.info(f"Using existing user: {st.session_state.zep_user_id}")
            else:
                st.sidebar.info(f"New user created for {first_name} {last_name}")

            st.session_state.chat_initialized = True
            st.sidebar.success("Zep user/session initialized successfully.")
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "Welcome! 😊 How can I assist you today?",
                }
            )

        # Handle any exceptions during initialization
        except Exception as e:
            st.error(f"Failed to initialize Zep user/session: {e}")
            st.stop()


def create_agents():
    """Create and configure the conversational agents."""
    if st.session_state.chat_initialized:
        # Create the autogen agent with Zep memory
        agent = ZepConversableAgent(
            name="ZEP AGENT",
            system_message=agent_system_message,
            llm_config={"config_list": config_list},
            zep_session_id=st.session_state.zep_session_id,
            zep_client=zep,
            min_fact_rating=0.7,
            function_map=None,
            human_input_mode="NEVER",
        )

        # Create UserProxy agent
        user = UserProxyAgent(
            name="UserProxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
            llm_config=False,
        )

        return agent, user
    return None, None


def handle_conversations(agent, user, prompt):
    """Process user input and generate assistant response."""
    # Add user message to display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Append /no_think token for the backend processing
    prompt_with_token = f"{prompt} /no_think"

    # Store user's full name instead of ID
    user_full_name = f"{st.session_state.get('first_name', '')} {st.session_state.get('last_name', '')}".strip()

    # Use proper name if available, otherwise fall back to user ID
    display_name = user_full_name if user_full_name else st.session_state.zep_user_id

    # Persist user message and update system message with facts
    agent._zep_persist_user_message(prompt, user_name=display_name.upper())
    agent._zep_fetch_and_update_system_message()

    # Generate and display response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            # Initiate chat with single turn
            user.initiate_chat(
                recipient=agent,
                message=prompt_with_token,
                max_turns=1,
                clear_history=False,
            )

            # Extract response from agent
            full_response = user.last_message(agent).get("content", "...")

            if not full_response or full_response == "...":
                full_response = "Sorry, I couldn't generate a response."

            # Remove <think> </think> tags from the response
            clean_response = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL).strip()

            # Display the response
            message_placeholder.markdown(clean_response)

            # Add assistant response to display history
            st.session_state.messages.append(
                {"role": "assistant", "content": clean_response}
            )

        # Handle any exceptions during chat
        except Exception as e:
            error_message = f"Error during chat: {e}"
            raise RuntimeError(error_message) from e


def main():
    """Main application entry point."""
    # Set page configuration
    st.set_page_config(
        page_title="Zep Memory Agent",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Create a layout with columns for title and clear button
    col1, col2 = st.columns([5, 1])
    with col1:
        st.title("🧠 Zep Memory Agent")
        powered_by_html = """
    <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
        <span style='font-size: 20px; color: #666;'>Powered by</span>
        <img src="https://files.buildwithfern.com/zep.docs.buildwithfern.com/2025-04-23T01:17:51.789Z/logo/zep-name-logo-pink.svg" width="100"> 
        <span style='font-size: 20px; color: #666;'>and</span>
        <img src="https://docs.ag2.ai/latest/assets/img/logo.svg" width="80">
    </div>
        """
        st.markdown(powered_by_html, unsafe_allow_html=True)

    # Clear chat history button
    with col2:
        if st.button("Clear ↺"):
            st.session_state.messages = []
            st.rerun()

    # Sidebar for API key, user information and controls
    with st.sidebar:
        # API Key input section
        zep_logo_html = """
        <div style='display: flex; align-items: center; gap: 10px; margin-top: 5px;'>
            <img src="https://files.buildwithfern.com/zep.docs.buildwithfern.com/2025-04-23T01:17:51.789Z/logo/zep-name-logo-pink.svg" width="100"> 
            <span style='font-size: 23px; color: #FFF; line-height: 1; display: flex; align-items: center; margin: 0;'>Configuration 🔑</span>
        </div>
        """
        st.markdown(zep_logo_html, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("[Get your API key](https://www.getzep.com/)", unsafe_allow_html=True)

        # Use session state to persist API key
        if "zep_api_key" not in st.session_state:
            st.session_state.zep_api_key = ""

        api_key = st.text_input(
            "Zep API Key",
            type="password",
            value=st.session_state.zep_api_key,
            help="Enter your Zep API key. This is required to use memory features.",
        )

        # Initialize Zep client when API key is provided
        if api_key:
            # Only initialize if the key has changed
            if api_key != st.session_state.zep_api_key or zep is None:
                if initialize_zep_client(api_key):
                    st.session_state.zep_api_key = api_key
                    st.success("✅ Zep client initialized successfully")
                else:
                    st.error("❌ Failed to initialize Zep client with provided key")
        else:
            st.warning("Please enter your Zep API key to continue!")

        # Only show user info section if Zep client is initialized
        if zep is not None:
            st.divider()
            st.header("👤 User Information")
            first_name = st.text_input("First Name", key="first_name")
            last_name = st.text_input("Last Name", key="last_name")

            if st.button("Initialize Session ✅"):
                if not first_name or not last_name:
                    st.warning("Please enter both first and last name")
                else:
                    initialize_session(first_name, last_name)

            # Show session info if initialized
            if "zep_session_id" in st.session_state:
                st.divider()
                st.subheader("Session Details 🔽")
                st.info(f"Session ID: {st.session_state.zep_session_id[:8]}...")
                st.info(f"User ID: {st.session_state.zep_user_id}")

    # Main chat interface
    if st.session_state.get("chat_initialized", False):
        # Create agents
        agent, user = create_agents()
        if not agent or not user:
            st.error(
                "Failed to create agents. Please check your autogen configuration."
            )
            return

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Handle user input
        if prompt := st.chat_input("How are you feeling today?"):
            if not st.session_state.chat_initialized:
                st.error("Chat not initialized yet. Try again.")
                return

            handle_conversations(agent, user, prompt)
    else:
        if zep is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            st.info(
                "Please enter your name and initialize a session to begin chatting 💬"
            )


# Run the Streamlit app
if __name__ == "__main__":
    main()
