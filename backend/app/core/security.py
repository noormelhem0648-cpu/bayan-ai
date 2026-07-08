"""Password hashing and JWT creation / verification."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS = "access"
REFRESH = "refresh"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str, token_type: str, expires: timedelta, **claims: Any) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires,
        **claims,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, **claims: Any) -> str:
    return _create_token(
        subject, ACCESS, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), **claims
    )


def create_refresh_token(subject: str, **claims: Any) -> str:
    return _create_token(
        subject, REFRESH, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), **claims
    )


def create_email_token(subject: str, purpose: str) -> str:
    """Short-lived token for email verification / password reset."""
    return _create_token(subject, purpose, timedelta(hours=24))


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT; raises JWTError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_email_token",
    "decode_token",
    "JWTError",
    "ACCESS",
    "REFRESH",
]
