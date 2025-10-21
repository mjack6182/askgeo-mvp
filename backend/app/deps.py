"""Dependency injection for FastAPI routes."""
from functools import lru_cache
from pathlib import Path
import chromadb
from chromadb import PersistentClient

from app.settings import Settings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


@lru_cache
def get_chroma_client() -> PersistentClient:
    """Get cached ChromaDB persistent client."""
    settings = get_settings()
    chroma_path = Path(settings.CHROMA_PATH)
    chroma_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(chroma_path))
