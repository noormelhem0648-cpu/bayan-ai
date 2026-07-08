"""Quizzes, exams, their questions, and student attempts."""
from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.types import JSONB
from app.models.enums import QuestionType, QuizDifficulty


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), default="Quiz", nullable=False)
    difficulty: Mapped[QuizDifficulty] = mapped_column(
        String(20), default=QuizDifficulty.beginner, nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), default="ar", nullable=False)
    is_exam: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    questions = relationship(
        "Question", back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[QuestionType] = mapped_column(
        String(20), default=QuestionType.mcq, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    quiz = relationship("Quiz", back_populates="questions")


class Exam(Base, TimestampMixin):
    """A scheduled, graded assessment tied to a subject."""

    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="ar", nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    questions = relationship(
        "ExamQuestion", back_populates="exam", cascade="all, delete-orphan"
    )


class ExamQuestion(Base, TimestampMixin):
    __tablename__ = "exam_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(
        ForeignKey("exams.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[QuestionType] = mapped_column(
        String(20), default=QuestionType.mcq, nullable=False
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list | None] = mapped_column(JSONB, default=list, nullable=True)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    exam = relationship("Exam", back_populates="questions")


class QuizAttempt(Base, TimestampMixin):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    quiz_id: Mapped[int | None] = mapped_column(
        ForeignKey("quizzes.id", ondelete="SET NULL"), nullable=True
    )
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    answers: Mapped[dict | None] = mapped_column(JSONB, default=dict, nullable=True)
