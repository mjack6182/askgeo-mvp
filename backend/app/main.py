"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.deps import get_settings
from app.middleware import RequestLoggingMiddleware
from app.routers import health, ingest, ask

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="UW-Parkside RAG Chatbot API",
    description="RAG-powered chatbot for UW-Parkside website content",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(ingest.router, tags=["ingest"])
app.include_router(ask.router, tags=["ask"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "UW-Parkside RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }
