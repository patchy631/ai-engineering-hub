from typing import Union, Dict
from autogen import ConversableAgent, Agent
from zep_cloud.client import Zep
from zep_cloud import Message, Memory


class ZepConversableAgent(ConversableAgent):  # Agent with Zep memory
    """A custom ConversableAgent that integrates with Zep for long-term memory."""

    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: dict,
        function_map: dict,
        human_input_mode: str,
        zep_session_id: str,
        zep_client: Zep,
        min_fact_rating: float,
    ):
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode=human_input_mode,
            function_map=function_map,
        )
        self.zep_session_id = zep_session_id
        self.zep_client = zep_client
        self.min_fact_rating = min_fact_rating
        # Store the original system message as we will update it with relevant facts from Zep
        self.original_system_message = system_message
        self.register_hook(
            "process_message_before_send", self._zep_persist_assistant_messages
        )
        # Note: Persisting user messages needs to happen *before* the agent
        # processes them to fetch relevant facts. We'll handle this outside
        # the hook based on Streamlit input.

    def _zep_persist_assistant_messages(
        self,
        message: Union[Dict, str],
        sender: Agent,
        recipient: Agent,
        silent: bool,
    ):
        """Agent sends a message to the user. Add the message to Zep."""
        if sender == self:
            if isinstance(message, dict):
                content = message.get("content", "")
            else:
                content = str(message)

            if content:
                zep_message = Message(
                    role_type="assistant", role=self.name, content=content
                )
                self.zep_client.memory.add(
                    session_id=self.zep_session_id, messages=[zep_message]
                )
        return message

    def _zep_fetch_and_update_system_message(self):
        """Fetch facts and update system message."""
        memory: Memory = self.zep_client.memory.get(
            self.zep_session_id, min_rating=self.min_fact_rating
        )
        context = memory.context or "No specific facts recalled."

        # Update the system message for the next inference
        self.update_system_message(
            self.original_system_message
            + f"\n\nRelevant facts about the user and prior conversation:\n{context}"
        )

    def _zep_persist_user_message(self, user_content: str, user_name: str = "User"):
        """User sends a message to the agent. Add the message to Zep."""
        if user_content:
            zep_message = Message(
                role_type="user",
                role=user_name,
                content=user_content,
            )
            self.zep_client.memory.add(
                session_id=self.zep_session_id, messages=[zep_message]
            )
