"""Zep Cloud service for memory and graph operations."""
from typing import Optional, List, Dict, Any

from zep_cloud.client import AsyncZep
from zep_cloud.types import Message as ZepMessage
from config.settings import settings


class ZepService:
    """Service for interacting with Zep Cloud (async-safe)."""

    def __init__(self) -> None:
        self.client = AsyncZep(api_key=settings.zep_api_key)
        self.docs_user_id = settings.zep_docs_user_id

    # ======================
    # User Management
    # ======================

    async def create_user(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new user in Zep."""
        user = await self.client.user.add(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        return {
            "user_id": user.user_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "created_at": user.created_at,
        }

    # ======================
    # Thread Management
    # ======================

    async def create_thread(self, thread_id: str, user_id: str) -> Dict[str, Any]:
        """Create a new thread for a user."""
        thread = await self.client.thread.create(
            thread_id=thread_id,
            user_id=user_id,
        )
        return {
            "thread_id": thread.thread_id,
            "user_id": thread.user_id,
            "created_at": thread.created_at,
        }

    # ======================
    # Memory Operations
    # ======================

    async def add_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        name: Optional[str] = None,
    ) -> None:
        """
        Add a message to a thread.

        role should be "user" or "assistant".
        """
        message = ZepMessage(
            role=role,
            content=content,
            name=name,
        )
        await self.client.thread.add_messages(thread_id, messages=[message])

    async def get_user_context(self, thread_id: str) -> Optional[str]:
        """
        Get user context from a thread using thread.get_user_context.

        Returns the context block (string) or None.
        """
        try:
            memory = await self.client.thread.get_user_context(
                thread_id=thread_id,
                mode="basic",
            )
            if memory and memory.context:
                context = memory.context

                if "<EPISODES>" in context:
                    parts = context.split("<EPISODES>")
                    context = parts[0].strip()
                    if len(parts) > 1 and "</EPISODES>" in parts[1]:
                        remaining = parts[1].split("</EPISODES>", 1)
                        if len(remaining) > 1:
                            context += "\n\n" + remaining[1].strip()

                return context
        except Exception as e:
            print(f"[ZepService] Error getting user context: {e}")
        return None

    # ======================
    # Graph Operations
    # ======================

    async def search_graph(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 3,
        scope: str = "nodes",  # "edges" | "nodes" | "episodes"
    ) -> List[Dict[str, Any]]:
        """Search the knowledge graph for a docs user (or provided user_id)."""
        try:
            user_id = user_id or self.docs_user_id

            results = await self.client.graph.search(
                user_id=user_id,
                query=query,
                limit=limit,
                scope=scope,
            )

            nodes: List[Dict[str, Any]] = []
            if results.nodes:
                for node in results.nodes:
                    nodes.append(
                        {
                            "name": node.name,
                            "summary": node.summary or node.name,
                        }
                    )

            return nodes
        except Exception as e:
            print(f"[ZepService] Error searching graph: {e}")
            return []

    async def add_to_graph(
        self,
        data: str,
        data_type: str = "text",  # "text" | "json" | "message"
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """Add data to a user's graph (docs user by default)."""
        try:
            user_id = user_id or self.docs_user_id
            episode = await self.client.graph.add(
                user_id=user_id,
                type=data_type,
                data=data,
            )
            # episode uuid_ is the identifier
            return episode.uuid_
        except Exception as e:
            print(f"[ZepService] Error adding to graph: {e}")
            return None


# Global service instance
zep_service = ZepService()
