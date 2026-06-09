# ResearchMind AI — System Architecture

## Overview

ResearchMind AI is a full-stack RAG platform for research papers. Users authenticate, upload PDFs, and interact via semantic search, Q&A with citations, summaries, study tools, literature reviews, and multi-paper analysis.

**Tagline:** AI-Powered Research Assistant for Understanding, Comparing, and Learning from Research Papers

## High-Level Architecture

```
┌─────────────┐     HTTPS/JWT      ┌──────────────┐     SQL      ┌────────────┐
│  Next.js 15 │ ◄────────────────► │   FastAPI    │ ◄──────────► │ PostgreSQL │
│  Frontend   │                    │   Backend    │              └────────────┘
└─────────────┘                    └──────┬───────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    ▼                     ▼                     ▼
              ┌──────────┐         ┌──────────┐         ┌──────────────┐
              │  FAISS   │         │  Gemini  │         │ File Storage │
              │  Vectors │         │  LLM/Emb │         │   (uploads)  │
              └──────────┘         └──────────┘         └──────────────┘
```

## Request Flow (Authenticated Q&A)

1. Client sends `POST /api/v1/chat/sessions/{id}/messages` with question + optional paper IDs.
2. **Middleware:** Request ID, rate limit, JWT validation, prompt-injection sanitizer on user text.
3. **ChatService:** Persist user message; resolve paper scope (single or multi).
4. **RAGService:**
   - Embed question (Google Gemini embeddings).
   - **Hybrid retrieval:** FAISS similarity + metadata filter (paper_id, user_id).
   - **Rerank** top-k with cross-encoder style scoring (Gemini relevance prompt).
   - Build context window with chunk metadata (page, section, title).
5. **RAGChain:** LangChain prompt → Gemini → structured answer with citations.
6. **HallucinationService:** Verify claims against retrieved chunks; compute confidence.
7. Persist assistant message, citations, confidence; return to client.

## RAG Pipeline (Ingestion)

```
PDF Upload → PyMuPDF/pdfplumber extract → Clean (headers/footers/noise)
→ Section-aware chunking (1000 chars, 200 overlap)
→ Metadata (paper_id, title, page, section)
→ Gemini embeddings → FAISS index (per-user namespace) + PostgreSQL chunk rows
→ KnowledgeExtractor (authors, models, datasets, metrics) → paper metadata JSON
```

## AI Pipeline

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| Embeddings | LangChain + Google Generative AI | Query & document vectors |
| Vector store | FAISS (disk per user) | Similarity + metadata filter |
| Generation | Gemini 1.5 Flash/Pro | Answers, summaries, study content |
| Agent | LangGraph | Multi-step research: search, compare, report |
| Evaluation | RAGAS | Faithfulness, relevance, precision, recall |

## Database Schema (ER Summary)

- **users** — auth, profile
- **papers** — ownership, file path, status, extracted metadata
- **chunks** — text, page, section, paper FK
- **embeddings** — chunk FK, vector reference (FAISS id)
- **chat_sessions** — user, title, paper scope
- **messages** — role, content, citations JSON, confidence
- **summaries**, **study_notes**, **flashcards**, **literature_reviews** — generated artifacts
- **evaluations** — RAGAS metrics per Q&A turn
- **refresh_tokens** — hashed refresh tokens

Relationships: User 1─* Papers, Papers 1─* Chunks, User 1─* ChatSessions 1─* Messages.

## Backend Folder Structure

See `backend/README.md` for per-module responsibilities.

## Frontend Folder Structure

See `frontend/README.md` for pages, components, hooks, and state.

## Deployment

- **Docker Compose:** `postgres`, `backend`, `frontend`
- **Volumes:** `postgres_data`, `faiss_indices`, `uploads`
- **Health:** `/health`, `/ready` on backend
- **Secrets:** `.env` (never committed); `GOOGLE_API_KEY`, `JWT_SECRET`, `DATABASE_URL`

## Security

JWT access (15m) + refresh (7d), bcrypt passwords, upload MIME/size validation, CORS allowlist, SQLAlchemy parameterized queries, XSS via React escaping + CSP headers, rate limiting (slowapi), prompt injection patterns stripped server-side.
