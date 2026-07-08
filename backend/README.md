# Bayan AI — Backend (FastAPI)

Clean-architecture FastAPI service: JWT auth, dynamic catalog, per-subject RAG
(FAISS + Gemini), quizzes, and exam-time restrictions.

## Layout
```
app/
├── main.py            FastAPI app + lifespan (tables + seed)
├── core/              config, security (JWT/bcrypt)
├── db/                base, session, seed
├── models/            SQLAlchemy models (all tables)
├── schemas/           Pydantic request/response
├── services/          business logic (auth, chat, quiz, restrictions, email)
├── repositories/      (reserved for heavier data-access needs)
├── api/               deps + v1 routers
└── ai/                prompts, llm (Gemini + key rotation), embeddings,
                       vectorstore (per-subject FAISS), ingest, rag orchestrator
```

## Run (recommended: Docker, Python 3.11)
```bash
docker compose up --build            # from the repo root — db + backend + frontend
```

## Run locally (Python 3.11)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                 # then set GEMINI_API_KEYS + DATABASE_URL
uvicorn app.main:app --reload
```
Docs at http://localhost:8000/docs · health at `/health`.

> Note: dependencies are pinned for Python 3.11 (the Docker image). Newer Python
> versions may lack matching wheels for `faiss-cpu` / `pydantic`.

## Migrations (Alembic)
```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```
(`create_all` on startup is a dev safety net; Alembic is the production path.)

## Tests
```bash
pip install pytest
pytest            # in-memory SQLite; no PostgreSQL or Gemini key required
```

## Default admin (seeded)
`admin@bayan.ai` / `Admin@12345` — change immediately in any real deployment.

## RAG isolation
Each subject has its own FAISS directory `data/indexes/subject_<id>/`. The id is
sanitised to digits only, so no subject can read another's index.
