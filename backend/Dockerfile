FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY pyproject.toml ./
COPY app ./app

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /app/data /app/.chroma

# Expose port
EXPOSE 8080

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
