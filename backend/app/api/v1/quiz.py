"""Quiz / exam generation and answer checking."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_contributed_keys, get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.chat import QuizCheckRequest, QuizGenerateRequest, QuizOut
from app.services import quiz_service

router = APIRouter()


@router.post("/generate", response_model=QuizOut)
def generate_quiz(
    req: QuizGenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    extra_keys: list[str] = Depends(get_contributed_keys),
):
    return quiz_service.generate_quiz(db, user, req, extra_keys)


@router.post("/check")
def check_answer(
    req: QuizCheckRequest,
    user: User = Depends(get_current_user),
    extra_keys: list[str] = Depends(get_contributed_keys),
):
    return quiz_service.check_answer(
        req.question, req.correct_answer, req.student_answer, req.language, extra_keys
    )
