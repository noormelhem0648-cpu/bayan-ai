# Bayan AI — رفيقك الذكي لتعلّم اللغة العربية

An AI-powered, multilingual (9 languages) Arabic-learning platform built on a RAG
architecture. Answers are grounded in each subject's own books first, then general
knowledge — always in the user's chosen application language.

## Stack
- **Frontend:** React (Vite) + react-i18next + TailwindCSS + Zustand — RTL/LTR, dark/light
- **Backend:** FastAPI + SQLAlchemy 2.0 + Alembic (Clean Architecture, SOLID)
- **Database:** PostgreSQL
- **Vector search:** FAISS (an isolated index per subject)
- **AI:** Google Gemini (generation + embeddings), with API-key rotation
- **Auth:** JWT (access + refresh) + bcrypt + email verification + RBAC

## Structure
```
AL Bayan AI/
├── backend/      FastAPI app, RAG engine, DB models, migrations
├── frontend/     React SPA, i18n, pages, UI kit
├── docker-compose.yml
└── README.md
```

## Three top-level tracks (fully dynamic, DB-driven — no hard-coded content)
1. اللغة العربية — Arabic Language
2. اللغة العربية التطبيقية — Applied Arabic
3. تعليم العربية للناطقين بغيرها — Arabic for Non-Native Speakers

Flow: Track → Major → Academic Year → Subject → AI Assistant

## Supported UI languages
Arabic, English, Malay, Indonesian, Chinese, Amharic, Thai, Korean, Russian.

## Local development
```bash
docker compose up --build          # db + backend + frontend
# or run each service manually — see backend/README and frontend/README
```

## Deployment
- Frontend → Vercel
- Backend → Render (Docker) with a persistent disk for FAISS indexes
- Database → managed PostgreSQL
