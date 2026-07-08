"""User, contributed API keys, and uploaded files."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import UserRole


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String(20), default=UserRole.student, nullable=False
    )

    # Chosen application language (FK -> languages.code).
    app_language: Mapped[str] = mapped_column(
        ForeignKey("languages.code", ondelete="SET NULL"), default="ar", nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Daily usage limiting.
    daily_message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_count_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    contributed_keys = relationship(
        "ContributedKey", back_populates="user", cascade="all, delete-orphan"
    )
    uploads = relationship(
        "UploadedFile", back_populates="user", cascade="all, delete-orphan"
    )


class ContributedKey(Base, TimestampMixin):
    """Gemini API keys donated by users to expand the free-tier pool."""

    __tablename__ = "contributed_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    key_value: Mapped[str] = mapped_column(Text, nullable=False)
    label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="contributed_keys")


class UploadedFile(Base, TimestampMixin):
    __tablename__ = "uploaded_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="uploads")
