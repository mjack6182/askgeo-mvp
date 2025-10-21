"""Application settings loaded from environment variables."""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """Application configuration settings."""

    # OpenAI Configuration
    OPENAI_API_KEY: str
    OPENAI_EMBED_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # ChromaDB Configuration
    CHROMA_PATH: str = ".chroma"

    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:5173"

    # Ingestion Configuration
    INGEST_MAX_PAGES: int = 600

    # Server Configuration
    BACKEND_PORT: int = 8080

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
