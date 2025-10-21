"""Health check endpoint."""
from fastapi import APIRouter, Depends
from chromadb import PersistentClient

from app.deps import get_chroma_client, get_settings
from app.settings import Settings

router = APIRouter()


@router.get("/health")
async def health_check(
    settings: Settings = Depends(get_settings),
    chroma_client: PersistentClient = Depends(get_chroma_client)
):
    """Health check endpoint.

    Returns:
        Basic health status and configuration info
    """
    # Check if collection exists
    collection_exists = False
    chunk_count = 0

    try:
        collection = chroma_client.get_collection(name="uwp")
        collection_exists = True
        chunk_count = collection.count()
    except:
        pass

    return {
        "status": "healthy",
        "embed_model": settings.OPENAI_EMBED_MODEL,
        "chat_model": settings.OPENAI_CHAT_MODEL,
        "collection_exists": collection_exists,
        "chunk_count": chunk_count
    }
