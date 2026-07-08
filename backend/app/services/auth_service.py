"""Authentication business logic."""
from __future__ import annotations

from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_email_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.models.enums import UserRole
from app.schemas.auth import RegisterRequest
from app.services.email_service import send_reset_email, send_verification_email


def _by_email(db: Session, email: str) -> User | None:
    return db.execute(select(User).where(User.email == email)).scalar_one_or_none()


def register(db: Session, data: RegisterRequest) -> User:
    if _by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    user = User(
        name=data.name,
        email=str(data.email),
        hashed_password=hash_password(data.password),
        app_language=data.app_language,
        role=UserRole.student,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_verification_email(user.email, create_email_token(str(user.id), "verify"))
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = _by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled"
        )
    return user


def issue_tokens(user: User) -> dict[str, str]:
    claims = {"role": user.role.value if hasattr(user.role, "value") else user.role}
    return {
        "access_token": create_access_token(str(user.id), **claims),
        "refresh_token": create_refresh_token(str(user.id)),
    }


def refresh_tokens(db: Session, refresh_token: str) -> dict[str, str]:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
        user = db.get(User, int(payload["sub"]))
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        ) from None
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )
    return issue_tokens(user)


def verify_email(db: Session, token: str) -> None:
    try:
        payload = decode_token(token)
        assert payload.get("type") == "verify"
        user = db.get(User, int(payload["sub"]))
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid or expired token") from None
    if user:
        user.is_verified = True
        db.commit()


def forgot_password(db: Session, email: str) -> None:
    user = _by_email(db, email)
    # Always respond success to avoid leaking which emails exist.
    if user:
        send_reset_email(user.email, create_email_token(str(user.id), "reset"))


def reset_password(db: Session, token: str, new_password: str) -> None:
    try:
        payload = decode_token(token)
        assert payload.get("type") == "reset"
        user = db.get(User, int(payload["sub"]))
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid or expired token") from None
    if not user:
        raise HTTPException(status_code=400, detail="Invalid token")
    user.hashed_password = hash_password(new_password)
    db.commit()


def enforce_daily_limit(db: Session, user: User) -> None:
    """Reset the counter each day and block once the daily cap is reached."""
    today = date.today()
    if user.daily_count_date != today:
        user.daily_count_date = today
        user.daily_message_count = 0
    if user.daily_message_count >= settings.DAILY_MESSAGE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily message limit reached",
        )
    user.daily_message_count += 1
    db.commit()
