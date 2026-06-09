# ResearchMind AI

**AI-Powered Research Assistant for Understanding, Comparing, and Learning from Research Papers**

Production-grade full-stack RAG platform built for portfolio and interview demonstrations.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind, shadcn/ui, TanStack Query, Zustand, Framer Motion |
| Backend | FastAPI, Python 3.12, SQLAlchemy, PostgreSQL |
| AI | LangChain, LangGraph, Google Gemini, FAISS, RAGAS |
| Deploy | Docker Compose |

## Quick Start

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```
2. Set `GOOGLE_API_KEY` and `JWT_SECRET` in `.env`.
3. Start services:
   ```bash
   docker compose up --build
   ```
4. Open http://localhost:3000 — API at http://localhost:8000/docs

## Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**PostgreSQL:** Run via Docker: `docker compose up postgres -d`

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Database](docs/DATABASE.md)
- [Backend](backend/README.md)
- [Frontend](frontend/README.md)

## Features

- JWT auth (signup, login, refresh, logout)
- PDF upload & processing pipeline
- FAISS vector search with hybrid retrieval & reranking
- Citation-based Q&A with hallucination confidence
- Summaries, study notes, flashcards, literature reviews
- Multi-paper comparison & LangGraph research agent
- RAGAS evaluation dashboard

## License

MIT
