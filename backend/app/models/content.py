"""Books, their source files, and the per-subject FAISS index metadata."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import IndexStatus


class Book(Base, TimestampMixin):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    subject = relationship("Subject", back_populates="books")
    files = relationship(
        "BookFile", back_populates="book", cascade="all, delete-orphan"
    )


class BookFile(Base, TimestampMixin):
    __tablename__ = "book_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), default="application/pdf")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    page_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    book = relationship("Book", back_populates="files")


class SubjectIndex(Base, TimestampMixin):
    """One FAISS index per subject — the isolation boundary for RAG."""

    __tablename__ = "subject_indexes"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    status: Mapped[IndexStatus] = mapped_column(
        String(20), default=IndexStatus.pending, nullable=False
    )
    embedding_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    built_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    subject = relationship("Subject", back_populates="index")
