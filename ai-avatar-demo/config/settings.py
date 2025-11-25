"""Configuration settings for the Zep Demo application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    anam_api_key: str
    zep_api_key: str
    openrouter_api_key: str

    # Anam AI Configuration (for avatar/voice only - we use custom LLM)
    anam_api_base_url: str = "https://api.anam.ai"
    anam_avatar_id: str = "30fa96d0-26c4-4e55-94a0-517025942e18"  # Default
    anam_voice_id: str = "6bfbe25a-979d-40f3-a92b-5394170af54b"   # Default

    # Zep Config
    zep_docs_user_id: str

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
