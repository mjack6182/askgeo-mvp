"""Pydantic models for API request/response validation."""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for /ask endpoint."""
    question: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    """Source document metadata."""
    url: str
    title: Optional[str] = None


class AskResponse(BaseModel):
    """Response model for /ask endpoint."""
    answer: str
    sources: List[Source]


class IngestStartRequest(BaseModel):
    """Request model for /ingest/start endpoint."""
    max_pages: Optional[int] = Field(default=None, ge=10, le=2000)


class IngestStatus(BaseModel):
    """Ingest status information."""
    status: Literal["idle", "running", "done", "error"]
    pages_scraped: int = 0
    chunks_indexed: int = 0
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
