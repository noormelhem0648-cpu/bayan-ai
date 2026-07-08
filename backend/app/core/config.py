"""Application settings, loaded from environment / .env (Pydantic Settings)."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    APP_NAME: str = "Bayan AI"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    # NoDecode: accept a plain comma-separated string from env (not JSON); the
    # validator below splits it. Without this, pydantic-settings tries json.loads
    # on the raw value and crashes on non-JSON input.
    BACKEND_CORS_ORIGINS: Annotated[list[str], NoDecode] = Field(default_factory=list)

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://bayan:bayan@localhost:5432/bayan_ai"

    # Security
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI (Gemini)
    GEMINI_API_KEYS: Annotated[list[str], NoDecode] = Field(default_factory=list)
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

    @field_validator("BACKEND_CORS_ORIGINS", "GEMINI_API_KEYS", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
