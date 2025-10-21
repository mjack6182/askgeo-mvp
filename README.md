# UW-Parkside RAG Chatbot

A production-ready RAG (Retrieval-Augmented Generation) chatbot that answers questions using UW-Parkside website content.

## Features

- **Smart Retrieval**: Uses ChromaDB vector search with OpenAI embeddings
- **Accurate Answers**: GPT-4o-mini generates answers with citation support
- **Web Scraping**: Automated crawling of uwp.edu with robots.txt compliance
- **Modern Stack**: FastAPI backend + React/Vite frontend with Tailwind CSS
- **Real-time Status**: Monitor indexing progress from the UI
- **Cost Efficient**: Uses `text-embedding-3-small` and `gpt-4o-mini` for optimal pricing

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI & Uvicorn
- ChromaDB (persistent vector storage)
- OpenAI SDK (embeddings + chat)
- Trafilatura (web scraping)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS
- Marked (markdown rendering)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ask-geo-mvp

# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

### 2. Install Dependencies

```bash
# Install everything
make install

# Or manually:
cd backend && pip install -e ".[dev]"
cd frontend && npm install
```

### 3. Ingest Data

Scrape UW-Parkside website and build the search index:

```bash
make ingest
```

This will:
1. Scrape up to 600 pages from uwp.edu (configurable)
2. Extract clean text and save to `backend/data/uwp_docs.jsonl`
3. Chunk text into ~350 token segments
4. Generate embeddings and store in ChromaDB

**Note:** This takes 5-15 minutes depending on the number of pages.

### 4. Run Development Servers

```bash
# Run both backend and frontend
make dev

# Or run separately:
make dev-backend  # Backend only (http://localhost:8080)
make dev-frontend # Frontend only (http://localhost:5173)
```

Visit [http://localhost:5173](http://localhost:5173) to use the chatbot!

## Docker Deployment

### Local Docker

```bash
# Build images
make docker-build

# Start services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Production Deployment

#### Railway / Render / Fly.io

1. Set environment variables:
   ```
   OPENAI_API_KEY=your-key-here
   OPENAI_EMBED_MODEL=text-embedding-3-small
   OPENAI_CHAT_MODEL=gpt-4o-mini
   ```

2. Deploy using Docker Compose or separate containers

3. Run ingestion:
   ```bash
   # SSH into backend container or use platform CLI
   python -m app.rag.scrape_uwp --max-pages 800
   python -m app.rag.build_index
   ```

#### Generic VM (Ubuntu/Debian)

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone repo and configure
git clone <repo-url> && cd ask-geo-mvp
cp .env.example .env
nano .env  # Add OPENAI_API_KEY

# Run with Docker Compose
docker compose up -d

# Ingest data
docker compose exec backend python -m app.rag.scrape_uwp
docker compose exec backend python -m app.rag.build_index
```

## Project Structure

```
ask-geo-mvp/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── settings.py          # Configuration
│   │   ├── deps.py              # Dependency injection
│   │   ├── models.py            # Pydantic models
│   │   ├── middleware.py        # CORS & logging
│   │   ├── rag/
│   │   │   ├── scrape_uwp.py    # Web scraper
│   │   │   ├── build_index.py   # Indexing pipeline
│   │   │   ├── retriever.py     # Vector search
│   │   │   └── prompts.py       # System prompts
│   │   └── routers/
│   │       ├── health.py        # Health check
│   │       ├── ingest.py        # Ingestion endpoints
│   │       └── ask.py           # Q&A endpoint
│   ├── tests/                   # Pytest tests
│   ├── pyproject.toml           # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── lib/api.ts           # API client
│   │   ├── App.tsx              # Root component
│   │   └── main.tsx             # Entry point
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
└── README.md
```

## API Documentation

Once running, visit [http://localhost:8080/docs](http://localhost:8080/docs) for interactive API documentation.

### Key Endpoints

- `GET /health` - Health check with system status
- `POST /ask` - Ask a question
  ```json
  {
    "question": "What programs does UW-Parkside offer?",
    "k": 5  // Number of chunks to retrieve
  }
  ```
- `POST /ingest/start` - Start background ingestion
- `GET /ingest/status` - Get ingestion status

## Configuration

All configuration is via environment variables (`.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *required* | OpenAI API key |
| `OPENAI_EMBED_MODEL` | `text-embedding-3-small` | Embedding model |
| `OPENAI_CHAT_MODEL` | `gpt-4o-mini` | Chat completion model |
| `CHROMA_PATH` | `.chroma` | ChromaDB storage path |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS allowed origins |
| `INGEST_MAX_PAGES` | `600` | Max pages to scrape |

## Testing

```bash
# Run all tests
make test

# Or manually:
cd backend && pytest -v

# Run specific test file
cd backend && pytest tests/test_ask.py -v
```

## Development

### Backend

```bash
cd backend

# Install in dev mode
pip install -e ".[dev]"

# Run with auto-reload
uvicorn app.main:app --reload

# Format code
black app/

# Type checking
mypy app/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Troubleshooting

### "No module named 'app'"

Make sure you've installed the backend package:
```bash
cd backend && pip install -e .
```

### "Collection 'uwp' not found"

You need to run the ingestion pipeline:
```bash
make ingest
```

### CORS errors

Check that `ALLOWED_ORIGINS` in `.env` matches your frontend URL.

### OpenAI API errors

- Verify your `OPENAI_API_KEY` is correct
- Check you have sufficient API credits
- Ensure you're using supported model names

### Slow scraping

- Reduce `--max-pages` parameter
- Check your internet connection
- Some pages may timeout (this is normal)

## Cost Estimation

Approximate OpenAI API costs for 600 pages:

- **Indexing** (one-time):
  - ~500K tokens → $0.01 for embeddings
  - Total: **~$0.01**

- **Queries** (per question):
  - Embedding: ~20 tokens → $0.000004
  - Chat completion: ~1500 tokens → $0.0009
  - Total: **~$0.001 per question**

**Monthly estimate** (100 questions/day): ~$3

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Vector search by [ChromaDB](https://www.trychroma.com/)
- AI by [OpenAI](https://openai.com/)
- Web scraping with [Trafilatura](https://trafilatura.readthedocs.io/)

---

**Questions?** Open an issue or contact the maintainers.
