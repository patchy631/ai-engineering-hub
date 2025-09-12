import os
import time
from typing import Optional, Any, Dict
from zep_cloud.client import Zep
from zep_crewai import ZepUserStorage
from crewai.memory.external.external_memory import ExternalMemory


class ZepMemoryLayer:
    def __init__(
        self,
        user_id: str,
        thread_id: str,
        mode: str = "summary",
        indexing_wait_time: int = 10,
        zep_api_key: Optional[str] = None,
    ):
        self.zep_client = Zep(api_key=zep_api_key or os.getenv("ZEP_API_KEY"))
        self.user_id = user_id
        self.thread_id = thread_id
        self.indexing_wait_time = indexing_wait_time

        try:
            self.zep_client.user.get(self.user_id)
        except:
            self.zep_client.user.add(user_id=self.user_id)
        
        # Create new session by first deleting the previous one
        self.zep_client.thread.delete(self.thread_id)
        self.zep_client.thread.create(thread_id=self.thread_id, user_id=self.user_id)

        self.user_storage = ZepUserStorage(
            client=self.zep_client,
            user_id=self.user_id,
            thread_id=self.thread_id,
            mode=mode,
        )
        self.external_memory = ExternalMemory(storage=self.user_storage)

    def as_external_memory(self) -> ExternalMemory:
        return self.external_memory

    def save_user_message(self, text: str, name: Optional[str] = None, **meta: Any) -> None:
        self.external_memory.save(
            text,
            metadata={"type": "message", "role": "user", "name": name or "User", **meta},
        )

    def save_assistant_message(self, text: str, name: Optional[str] = None, **meta: Any) -> None:
        self.external_memory.save(
            text,
            metadata={"type": "message", "role": "assistant", "name": name or "Assistant", **meta},
        )

    def save_preferences(self, prefs: Dict[str, Any]) -> None:
        self.external_memory.save(
            str({"preferences": prefs}),
            metadata={"type": "json", "category": "preferences"},
        )

    def wait_for_indexing(self) -> None:
        time.sleep(self.indexing_wait_time)

    def get_context_block(self) -> str:
        """
        Fetch the full user context block from Zep memory.
        Returns a string of concatenated memory facts (Zep's internal summary).
        """
        memory = self.zep_client.thread.get_user_context(thread_id=self.thread_id)
        return memory.context if memory and memory.context else ""
