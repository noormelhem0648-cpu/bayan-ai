"""Authentication routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenPair,
    UpdateProfileRequest,
    UserOut,
    VerifyEmailRequest,
)
from app.services import auth_service
from fastapi import HTTPException

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, str(data.email), data.password)
    return auth_service.issue_tokens(user)


@router.post("/login/oauth", response_model=TokenPair, include_in_schema=False)
def login_oauth(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """OAuth2 password flow endpoint (used by Swagger's Authorize button)."""
    user = auth_service.authenticate(db, form.username, form.password)
    return auth_service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    return auth_service.refresh_tokens(db, data.refresh_token)


@router.post("/verify-email")
def verify_email(data: VerifyEmailRequest, db: Session = Depends(get_db)):
    auth_service.verify_email(db, data.token)
    return {"detail": "Email verified"}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.forgot_password(db, str(data.email))
    return {"detail": "If the email exists, a reset link was sent"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    auth_service.reset_password(db, data.token, data.new_password)
    return {"detail": "Password updated"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if data.name is not None:
        user.name = data.name
    if data.app_language is not None:
        user.app_language = data.app_language
    db.commit()
    db.refresh(user)
    return user


@router.post("/me/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"detail": "Password changed"}
