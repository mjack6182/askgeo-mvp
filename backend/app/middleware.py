"""Custom middleware for FastAPI app."""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request
        print(
            f"{request.method} {request.url.path} "
            f"- {response.status_code} "
            f"({duration:.3f}s)"
        )

        return response
