"""Dynamic academic catalog: Language, Track, Major, AcademicYear, Subject.

All human-readable names are stored per-language in a JSONB ``name_i18n`` map
(e.g. ``{"ar": "النحو", "en": "Grammar"}``). No catalog content is hard-coded;
everything is managed from the dashboards.
"""
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.types import JSONB


class Language(Base, TimestampMixin):
    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)  # ar, en, ms...
    name: Mapped[str] = mapped_column(String(80), nullable=False)      # English name
    native_name: Mapped[str] = mapped_column(String(80), nullable=False)
    direction: Mapped[str] = mapped_column(String(3), default="ltr", nullable=False)  # ltr|rtl
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Track(Base, TimestampMixin):
    """Top-level section (e.g. Arabic / Applied Arabic / Arabic for non-natives)."""

    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    description_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    majors = relationship(
        "Major", back_populates="track", cascade="all, delete-orphan"
    )


class Major(Base, TimestampMixin):
    __tablename__ = "majors"

    id: Mapped[int] = mapped_column(primary_key=True)
    track_id: Mapped[int] = mapped_column(
        ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False
    )
    name_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    track = relationship("Track", back_populates="majors")
    years = relationship(
        "AcademicYear", back_populates="major", cascade="all, delete-orphan"
    )


class AcademicYear(Base, TimestampMixin):
    __tablename__ = "academic_years"

    id: Mapped[int] = mapped_column(primary_key=True)
    major_id: Mapped[int] = mapped_column(
        ForeignKey("majors.id", ondelete="CASCADE"), nullable=False
    )
    number: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..N
    name_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    major = relationship("Major", back_populates="years")
    subjects = relationship(
        "Subject", back_populates="year", cascade="all, delete-orphan"
    )


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    year_id: Mapped[int] = mapped_column(
        ForeignKey("academic_years.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    name_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    description_i18n: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    year = relationship("AcademicYear", back_populates="subjects")
    books = relationship(
        "Book", back_populates="subject", cascade="all, delete-orphan"
    )
    index = relationship(
        "SubjectIndex",
        back_populates="subject",
        uselist=False,
        cascade="all, delete-orphan",
    )
