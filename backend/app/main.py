"""Bayan AI — FastAPI application entrypoint."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.seed import seed
from app.db.session import SessionLocal, engine

# Ensure all models are registered on Base before create_all.
import app.models  # noqa: F401,E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.INDEXES_DIR, exist_ok=True)
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    # In production, migrations are managed by Alembic; create_all is a dev safety net.
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed(db)
    logger.info("Bayan AI backend ready.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Bayan AI — your smart companion for learning Arabic.",
    lifespan=lifespan,
)

# Auth is header-based (Bearer tokens), so we don't need cookie credentials.
# Keeping allow_credentials=False lets us safely allow all origins by default,
# which makes deployment frictionless (no need to pre-configure the exact URL).
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "app": settings.APP_NAME}
