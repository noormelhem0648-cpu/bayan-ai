"""Database engine, session factory, and FastAPI dependency."""
from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _normalize_db_url(url: str) -> str:
    """Managed hosts (Render/Heroku) hand out ``postgres://`` URLs, which
    SQLAlchemy 2.0 rejects. Normalize to an explicit psycopg2 driver."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


# SQLite needs a special connect arg for multi-threaded use; Postgres uses a pool.
_db_url = _normalize_db_url(settings.DATABASE_URL)
_engine_kwargs = {"pool_pre_ping": True, "future": True}
if _db_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(_db_url, **_engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session, ensuring it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
