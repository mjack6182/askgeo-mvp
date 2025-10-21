.PHONY: help install dev ingest test docker-build docker-up docker-down clean

# Load environment variables from .env file
ifneq (,$(wildcard .env))
    include .env
    export
endif

help: ## Show this help message
	@echo "UW-Parkside RAG Chatbot - Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (backend + frontend)
	@echo "Installing backend dependencies..."
	cd backend && pip install -e ".[dev]"
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✓ Dependencies installed"

dev: ## Run development servers (backend + frontend in parallel)
	@echo "Starting development servers..."
	@trap 'kill 0' EXIT; \
	(cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload) & \
	(cd frontend && npm run dev)

dev-backend: ## Run only backend development server
	cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

dev-frontend: ## Run only frontend development server
	cd frontend && npm run dev

ingest: ## Run ingestion pipeline (scrape + index)
	@echo "Starting data ingestion..."
	cd backend && python -m app.rag.scrape_uwp
	cd backend && python -m app.rag.build_index
	@echo "✓ Ingestion complete"

test: ## Run backend tests
	cd backend && pytest -v

docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start Docker containers
	docker compose up -d
	@echo "✓ Services started"
	@echo "  Backend: http://localhost:8080"
	@echo "  Frontend: http://localhost:5173"
	@echo "  API Docs: http://localhost:8080/docs"

docker-down: ## Stop Docker containers
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

clean: ## Clean build artifacts and caches
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/data backend/.chroma
	@echo "✓ Cleaned"

clean-data: ## Clean scraped data and index (but not node_modules)
	rm -rf backend/data backend/.chroma
	@echo "✓ Data cleaned"
