"""Enumerations used across models (stored as strings)."""
from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    student = "student"
    instructor = "instructor"
    admin = "admin"


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    true_false = "true_false"
    fill_blank = "fill_blank"
    short_answer = "short_answer"


class QuizDifficulty(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class IndexStatus(str, enum.Enum):
    pending = "pending"
    building = "building"
    ready = "ready"
    failed = "failed"
    stale = "stale"
