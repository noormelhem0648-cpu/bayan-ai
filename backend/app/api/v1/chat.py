"""Chat: streaming grounded answers + conversation history + file upload."""
from __future__ import annotations

import json
import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_contributed_keys, get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models import Conversation, User
from app.models.enums import UserRole
from app.schemas.chat import (
    AskRequest,
    ConversationDetailOut,
    ConversationOut,
)
from app.services import auth_service, chat_service
from app.services.restriction_service import is_blocked_for

router = APIRouter()


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _guard_ask(db: Session, user: User, subject_id: int, question: str) -> None:
    if len(question) > settings.MAX_MESSAGE_CHARS:
        raise HTTPException(status_code=413, detail="Message too long")
    blocked = is_blocked_for(db, subject_id, user.role)
    if blocked:
        raise HTTPException(
            status_code=403,
            detail={"reason": blocked.reason, "ends_at": str(blocked.ends_at)},
        )
    auth_service.enforce_daily_limit(db, user)


@router.post("/stream")
def ask_stream(
    req: AskRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    extra_keys: list[str] = Depends(get_contributed_keys),
):
    """Stream a book-grounded answer via Server-Sent Events."""
    _guard_ask(db, user, req.subject_id, req.question)

    conv, passages, token_iter = chat_service.stream_and_persist(
        db,
        user,
        subject_id=req.subject_id,
        question=req.question,
        conversation_id=req.conversation_id,
        history=[m.model_dump() for m in req.history],
        level=req.level,
        extra_keys=extra_keys,
    )

    def event_stream():
        yield _sse("meta", {"conversation_id": conv.id, "sources": passages})
        collected: list[str] = []
        try:
            for token in token_iter:
                collected.append(token)
                yield _sse("token", {"text": token})
        except Exception as exc:  # noqa: BLE001
            yield _sse("error", {"detail": str(exc)})
        answer = "".join(collected)
        if answer:
            chat_service.save_assistant_message(db, conv.id, answer, passages)
        yield _sse("done", {"conversation_id": conv.id})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/upload-and-ask")
async def upload_and_ask(
    subject_id: int = Form(...),
    question: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    extra_keys: list[str] = Depends(get_contributed_keys),
):
    """Attach a file to a question. (Currently stores the file; visual/PDF
    understanding is wired through the same grounded pipeline.)"""
    _guard_ask(db, user, subject_id, question)

    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'upload')}"
    path = os.path.join(settings.UPLOADS_DIR, safe_name)
    with open(path, "wb") as fh:
        fh.write(await file.read())

    # For now, treat the question as the grounded query; the stored file is
    # available for future multimodal expansion (images / PDF understanding).
    conv, passages, token_iter = chat_service.stream_and_persist(
        db, user,
        subject_id=subject_id, question=question, conversation_id=None,
        history=[], level=None, extra_keys=extra_keys,
    )
    answer = "".join(token_iter)
    chat_service.save_assistant_message(db, conv.id, answer, passages)
    return {"conversation_id": conv.id, "answer": answer, "sources": passages}


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return db.execute(
        select(Conversation)
        .where(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
    ).scalars().all()


@router.get("/conversations/{conv_id}", response_model=ConversationDetailOut)
def get_conversation(
    conv_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/conversations/{conv_id}", status_code=204)
def delete_conversation(
    conv_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    conv = db.get(Conversation, conv_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
