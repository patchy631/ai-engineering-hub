"""Anam AI service for avatar management."""
import httpx
from typing import List, Dict, Any, Optional
from config.settings import settings


class AnamService:
    """Service for interacting with Anam AI API."""

    def __init__(self):
        """Initialize Anam AI service."""
        self.api_key = settings.anam_api_key
        self.base_url = settings.anam_api_base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.enabled = bool(self.api_key)

    async def create_session_token(
        self,
        persona_name: str = "Zep Assistant",
        system_prompt: Optional[str] = None,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        llm_id: Optional[str] = None,
        max_session_length_seconds: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a session token for initializing an Anam persona.

        Args:
            persona_name: Name of the persona
            system_prompt: Custom system prompt for the persona
            avatar_id: Avatar ID
            voice_id: Voice ID
            llm_id: LLM ID
            max_session_length_seconds: Maximum session duration in seconds

        Returns:
            Dict containing sessionToken and other session info, or None on error
        """
        if not self.enabled:
            return None

        try:
            url = f"{self.base_url}/v1/auth/session-token"

            # Use defaults from settings if not provided
            avatar_id = avatar_id or settings.anam_avatar_id
            voice_id = voice_id or settings.anam_voice_id

            if llm_id is None:
                llm_id = "CUSTOMER_CLIENT_V1"  # This tells Anam to use client-side/custom LLM

            # Default system prompt
            if not system_prompt:
                system_prompt = (
                    f"You are {persona_name}, a helpful AI assistant with access to "
                    "relevant information. You provide accurate, concise responses "
                    "based on the information available to you. Keep responses conversational."
                )

            payload = {
                "personaConfig": {
                    "name": persona_name,
                    "avatarId": avatar_id,
                    "voiceId": voice_id,
                    "llmId": llm_id,
                    "systemPrompt": system_prompt,
                }
            }

            if max_session_length_seconds:
                payload["personaConfig"]["maxSessionLengthSeconds"] = max_session_length_seconds

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=self.headers, json=payload, timeout=30.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"Error creating session token: {e}")
            return None


# Global service instance
anam_service = AnamService()
