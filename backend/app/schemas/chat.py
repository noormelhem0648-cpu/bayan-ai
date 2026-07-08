"""Chat and assessment schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import QuestionType, QuizDifficulty


class ChatMessageIn(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    subject_id: int
    question: str = Field(min_length=1, max_length=4000)
    conversation_id: int | None = None
    history: list[ChatMessageIn] = Field(default_factory=list)
    level: str | None = None  # for the non-native track: beginner/intermediate/advanced


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    sources: list | None
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int | None
    title: str
    language: str
    created_at: datetime


class ConversationDetailOut(ConversationOut):
    messages: list[MessageOut] = Field(default_factory=list)


class QuizGenerateRequest(BaseModel):
    subject_id: int
    difficulty: QuizDifficulty = QuizDifficulty.beginner
    question_type: QuestionType = QuestionType.mcq
    count: int = Field(default=5, ge=1, le=20)
    topic: str | None = None


class QuizQuestionOut(BaseModel):
    type: QuestionType
    text: str
    options: list[str] = Field(default_factory=list)
    answer: str
    explanation: str | None = None


class QuizOut(BaseModel):
    subject_id: int
    difficulty: QuizDifficulty
    language: str
    questions: list[QuizQuestionOut]


class QuizCheckRequest(BaseModel):
    question: str
    correct_answer: str
    student_answer: str
    language: str = "ar"
