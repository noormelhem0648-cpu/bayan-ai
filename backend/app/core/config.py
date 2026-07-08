"""Application settings, loaded from environment / .env (Pydantic Settings)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    APP_NAME: str = "Bayan AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    # Kept as plain strings (comma-separated) so pydantic-settings never tries to
    # JSON-decode them from env vars. Use the *_list properties below for the list.
    BACKEND_CORS_ORIGINS: str = ""

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://bayan:bayan@localhost:5432/bayan_ai"

    # Security
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI (Gemini) — comma-separated for automatic key rotation.
    GEMINI_API_KEYS: str = ""
    GEMINI_CHAT_MODEL: str = "gemini-2.0-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # RAG
    RAG_TOP_K: int = 5
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 150
    INDEXES_DIR: str = "./data/indexes"
    UPLOADS_DIR: str = "./data/uploads"

    # Limits
    DAILY_MESSAGE_LIMIT: int = 100
    MAX_MESSAGE_CHARS: int = 4000

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@bayan.ai"
    FRONTEND_URL: str = "http://localhost:5173"

    @property
    def gemini_api_keys_list(self) -> list[str]:
        return _split_csv(self.GEMINI_API_KEYS)

    @property
    def cors_origins_list(self) -> list[str]:
        return _split_csv(self.BACKEND_CORS_ORIGINS)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
