"""Chat orchestration: conversation persistence + RAG streaming."""
from __future__ import annotations

from collections.abc import Iterator

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai import rag
from app.models import Conversation, Message, Subject, User

NON_NATIVE_TRACK_SLUG = "non-natives"


def _subject_or_404(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if not subject or not subject.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return subject


def subject_display_name(subject: Subject, language: str) -> str:
    names = subject.name_i18n or {}
    return names.get(language) or names.get("ar") or names.get("en") or subject.code


def is_non_native(subject: Subject) -> bool:
    year = subject.year
    if year and year.major and year.major.track:
        return year.major.track.slug == NON_NATIVE_TRACK_SLUG
    return False


def get_or_create_conversation(
    db: Session, user: User, subject_id: int, conversation_id: int | None, language: str
) -> Conversation:
    if conversation_id:
        conv = db.get(Conversation, conversation_id)
        if not conv or conv.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conv
    conv = Conversation(
        user_id=user.id, subject_id=subject_id, language=language, title="New chat"
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def stream_and_persist(
    db: Session,
    user: User,
    *,
    subject_id: int,
    question: str,
    conversation_id: int | None,
    history: list[dict],
    level: str | None,
    extra_keys: list[str],
) -> tuple[Conversation, list[dict], Iterator[str]]:
    """Prepare a grounded streaming answer and return a persistence callback via
    the returned iterator's consumption (the router saves after streaming)."""
    subject = _subject_or_404(db, subject_id)
    language = user.app_language or "ar"

    conv = get_or_create_conversation(db, user, subject_id, conversation_id, language)

    # Persist the user's message immediately.
    db.add(Message(conversation_id=conv.id, role="user", content=question))
    if conv.title == "New chat":
        conv.title = question[:60]
    db.commit()

    passages, token_iter = rag.stream_answer(
        subject_id=subject_id,
        subject_name=subject_display_name(subject, language),
        language=language,
        question=question,
        history=history,
        is_non_native_track=is_non_native(subject),
        level=level,
        extra_keys=extra_keys,
    )
    return conv, passages, token_iter


def save_assistant_message(
    db: Session, conversation_id: int, content: str, sources: list[dict]
) -> None:
    db.add(
        Message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            sources=sources,
        )
    )
    db.commit()
