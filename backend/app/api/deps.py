"""Shared FastAPI dependencies: DB session, current user, RBAC, key pool."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import ACCESS, JWTError, decode_token
from app.db.session import get_db
from app.models import ContributedKey, User
from app.models.enums import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

_CREDENTIALS_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not token:
        raise _CREDENTIALS_EXC
    try:
        payload = decode_token(token)
        if payload.get("type") != ACCESS:
            raise _CREDENTIALS_EXC
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise _CREDENTIALS_EXC from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_EXC
    return user


def require_role(*roles: UserRole) -> Callable[..., User]:
    """Dependency factory enforcing that the user has one of ``roles``."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return checker


require_instructor = require_role(UserRole.instructor, UserRole.admin)
require_admin = require_role(UserRole.admin)


def get_contributed_keys(db: Session = Depends(get_db)) -> list[str]:
    """Active Gemini keys donated by users, to widen the free-tier pool."""
    rows = db.execute(
        select(ContributedKey.key_value).where(ContributedKey.is_active.is_(True))
    ).scalars()
    return [k for k in rows if k]
