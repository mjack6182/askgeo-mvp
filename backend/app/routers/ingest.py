"""Ingestion endpoints for scraping and indexing."""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.models import IngestStartRequest, IngestStatus
from app.deps import get_settings
from app.settings import Settings
from app.rag.scrape_uwp import UWPScraper
from app.rag.build_index import IndexBuilder

router = APIRouter()

STATUS_FILE = Path("data/ingest_status.json")


def load_status() -> IngestStatus:
    """Load ingest status from file."""
    if not STATUS_FILE.exists():
        return IngestStatus(status="idle")

    try:
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
            return IngestStatus(**data)
    except:
        return IngestStatus(status="idle")


def save_status(status: IngestStatus) -> None:
    """Save ingest status to file."""
    STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump(status.model_dump(), f, indent=2)


def run_ingest_task(max_pages: int, settings: Settings) -> None:
    """Background task to scrape and index content.

    Args:
        max_pages: Maximum number of pages to scrape
        settings: Application settings
    """
    # Update status to running
    status = IngestStatus(
        status="running",
        started_at=datetime.now().isoformat()
    )
    save_status(status)

    try:
        # Step 1: Scrape
        print(f"Starting scrape with max_pages={max_pages}")
        scraper = UWPScraper(max_pages=max_pages)
        data_path = Path("data/uwp_docs.jsonl")

        try:
            docs = scraper.scrape()
            scraper.save_to_jsonl(docs, data_path)
            pages_scraped = len(docs)
        finally:
            scraper.close()

        # Step 2: Index
        print("Starting indexing...")
        builder = IndexBuilder(
            chroma_path=settings.CHROMA_PATH,
            embed_model=settings.OPENAI_EMBED_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )

        stats = builder.build_index(data_path, reset=True)
        stats_path = Path("data/stats.json")
        builder.save_stats(stats, stats_path)

        chunks_indexed = stats["total_chunks"]

        # Update status to done
        status = IngestStatus(
            status="done",
            pages_scraped=pages_scraped,
            chunks_indexed=chunks_indexed,
            started_at=status.started_at,
            completed_at=datetime.now().isoformat()
        )
        save_status(status)

        print(f"Ingest complete: {pages_scraped} pages, {chunks_indexed} chunks")

    except Exception as e:
        # Update status to error
        error_msg = str(e)
        print(f"Ingest error: {error_msg}")

        status = IngestStatus(
            status="error",
            started_at=status.started_at,
            completed_at=datetime.now().isoformat(),
            error_message=error_msg
        )
        save_status(status)


@router.post("/ingest/start")
async def start_ingest(
    request: IngestStartRequest,
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings)
):
    """Start background ingestion task.

    Args:
        request: Ingestion parameters
        background_tasks: FastAPI background tasks

    Returns:
        Acknowledgment message
    """
    # Check if already running
    current_status = load_status()
    if current_status.status == "running":
        raise HTTPException(status_code=409, detail="Ingestion already in progress")

    # Determine max_pages
    max_pages = request.max_pages or settings.INGEST_MAX_PAGES

    # Start background task
    background_tasks.add_task(run_ingest_task, max_pages, settings)

    return {
        "message": "Ingestion started",
        "max_pages": max_pages
    }


@router.get("/ingest/status", response_model=IngestStatus)
async def get_ingest_status():
    """Get current ingestion status.

    Returns:
        Current ingest status
    """
    return load_status()
