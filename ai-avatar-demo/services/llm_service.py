"""LLM service for handling multiple providers (Minimax M2 via OpenRouter)."""
import json
from typing import AsyncGenerator, List, Dict, Any, Optional, cast
from config import settings


class LLMService:
    """Service for LLM interactions with Minimax M2 via OpenRouter."""

    def __init__(self):
        """Initialize LLM service with OpenRouter."""
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion from Minimax M2."""
        # Prepend system message
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(messages)

        try:
            # Stream response
            stream = await self.client.chat.completions.create(
                model="minimax/minimax-m2",
                messages=cast(Any, openai_messages),
                stream=True,
                temperature=0.8,
                max_tokens=2048,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # If streaming fails, try non-streaming
            print(f"\nStreaming failed, using non-streaming mode: {e}")
            response = await self.client.chat.completions.create(
                model="minimax/minimax-m2",
                messages=cast(Any, openai_messages),
                stream=False,
                temperature=0.8,
                max_tokens=2048,
            )
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content


# Global service instance
llm_service = LLMService()
