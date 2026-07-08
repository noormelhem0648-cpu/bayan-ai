"""Quiz / exam generation and answer checking, grounded in subject books."""
from __future__ import annotations

import json
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai import rag
from app.ai.llm import GeminiClient
from app.ai.prompts import language_name
from app.models import Subject, User
from app.schemas.chat import QuizGenerateRequest


def _subject(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


def _parse_json_block(text: str) -> list[dict]:
    """Extract a JSON array from a model response, tolerating code fences."""
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        raise HTTPException(status_code=502, detail="AI returned no valid quiz")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned malformed quiz") from None


def generate_quiz(
    db: Session, user: User, req: QuizGenerateRequest, extra_keys: list[str]
) -> dict:
    subject = _subject(db, req.subject_id)
    language = user.app_language or "ar"
    lang = language_name(language)

    topic = req.topic or "the subject's core material"
    passages = rag.retrieve(req.subject_id, topic, extra_keys=extra_keys)
    context = "\n\n".join(p["text"] for p in passages[:5])

    system = (
        f"You are a quiz generator for the subject. Write everything in {lang}. "
        "Ground questions in the provided CONTEXT when available; otherwise use "
        "general subject knowledge. Respond with ONLY a JSON array."
    )
    user_msg = (
        f"CONTEXT:\n{context or '(none)'}\n\n"
        f"Generate {req.count} '{req.question_type.value}' questions at "
        f"'{req.difficulty.value}' difficulty about: {topic}.\n"
        "Each item must be an object with keys: type, text, options (array; empty "
        "for non-mcq), answer, explanation. Return ONLY the JSON array."
    )

    client = GeminiClient(extra_keys=extra_keys)
    raw = client.complete(system, user_msg)
    questions = _parse_json_block(raw)

    return {
        "subject_id": req.subject_id,
        "difficulty": req.difficulty,
        "language": language,
        "questions": questions,
    }


def check_answer(
    question: str, correct: str, student: str, language: str, extra_keys: list[str]
) -> dict:
    lang = language_name(language)
    system = (
        f"You grade a student's answer. Reply in {lang}. Return ONLY a JSON object "
        'with keys: is_correct (boolean), feedback (string).'
    )
    user_msg = (
        f"Question: {question}\nCorrect answer: {correct}\n"
        f"Student answer: {student}\nGrade it."
    )
    client = GeminiClient(extra_keys=extra_keys)
    raw = client.complete(system, user_msg)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {"is_correct": False, "feedback": raw.strip()}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {"is_correct": False, "feedback": raw.strip()}
