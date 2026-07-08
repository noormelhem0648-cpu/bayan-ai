"""Admin dashboard: users, languages, tracks, settings, audit, backup."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models import (
    AuditLog,
    Language,
    Track,
    UsageStat,
    User,
)
from app.models.enums import UserRole
from app.schemas.auth import UserOut
from app.schemas.catalog import LanguageIn, LanguageOut, TrackIn, TrackOut
from app.schemas.system import SettingIn
from app.models import Setting

router = APIRouter(dependencies=[Depends(require_admin)])


# ---- Users ------------------------------------------------------------------
@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.execute(select(User).order_by(User.created_at.desc())).scalars().all()


@router.patch("/users/{user_id}/role", response_model=UserOut)
def set_role(user_id: int, role: UserRole, db: Session = Depends(get_db)):
    user = db.get(User, user_id) or _404("User")
    user.role = role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/active", response_model=UserOut)
def set_active(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    user = db.get(User, user_id) or _404("User")
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


# ---- Languages --------------------------------------------------------------
@router.get("/languages", response_model=list[LanguageOut])
def list_languages(db: Session = Depends(get_db)):
    return db.execute(select(Language).order_by(Language.order_index)).scalars().all()


@router.post("/languages", response_model=LanguageOut, status_code=201)
def upsert_language(data: LanguageIn, db: Session = Depends(get_db)):
    lang = db.get(Language, data.code)
    if lang:
        for k, v in data.model_dump().items():
            setattr(lang, k, v)
    else:
        lang = Language(**data.model_dump())
        db.add(lang)
    db.commit()
    db.refresh(lang)
    return lang


# ---- Tracks -----------------------------------------------------------------
@router.post("/tracks", response_model=TrackOut, status_code=201)
def create_track(data: TrackIn, db: Session = Depends(get_db)):
    t = Track(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/tracks/{track_id}", response_model=TrackOut)
def update_track(track_id: int, data: TrackIn, db: Session = Depends(get_db)):
    t = db.get(Track, track_id) or _404("Track")
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return t


# ---- Settings ---------------------------------------------------------------
@router.get("/settings")
def list_settings(db: Session = Depends(get_db)):
    return {s.key: s.value for s in db.execute(select(Setting)).scalars()}


@router.put("/settings")
def upsert_setting(data: SettingIn, db: Session = Depends(get_db)):
    s = db.get(Setting, data.key)
    if s:
        s.value = data.value
    else:
        db.add(Setting(key=data.key, value=data.value))
    db.commit()
    return {"detail": "saved"}


# ---- Observability ----------------------------------------------------------
@router.get("/audit-logs")
def audit_logs(limit: int = 100, db: Session = Depends(get_db)):
    return db.execute(
        select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    ).scalars().all()


@router.get("/ai-usage")
def ai_usage(db: Session = Depends(get_db)):
    total = db.scalar(select(func.coalesce(func.sum(UsageStat.tokens), 0)))
    events = db.scalar(select(func.count()).select_from(UsageStat))
    return {"total_tokens": total, "events": events}


def _404(entity: str):
    raise HTTPException(status_code=404, detail=f"{entity} not found")
