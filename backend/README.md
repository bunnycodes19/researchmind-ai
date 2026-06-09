# ResearchMind AI — Backend

## Structure

```
app/
  main.py              # FastAPI app, lifespan, routers
  config.py            # Settings from env
  dependencies.py      # DI: db session, current user
  api/v1/              # HTTP controllers (routers)
  core/                # Security, logging, middleware, rate limit
  models/              # SQLAlchemy ORM
  schemas/             # Pydantic request/response
  repositories/        # Data access layer
  services/            # Business logic
  ai/                  # RAG, embeddings, agent, evaluation
  pipeline/            # PDF extract, clean, chunk
  db/                  # Session, base
alembic/               # Migrations
tests/                 # Pytest
```

## Run locally

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
