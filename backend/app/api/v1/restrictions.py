"""Subject restriction checks (student) and management (instructor)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_instructor
from app.db.session import get_db
from app.models import Restriction, User
from app.schemas.system import RestrictionCheckOut, RestrictionIn, RestrictionOut
from app.services.restriction_service import active_restriction, is_blocked_for

router = APIRouter()


@router.get("/check/{subject_id}", response_model=RestrictionCheckOut)
def check(
    subject_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    r = is_blocked_for(db, subject_id, user.role)
    if not r:
        return RestrictionCheckOut(blocked=False)
    return RestrictionCheckOut(blocked=True, reason=r.reason, ends_at=r.ends_at)


@router.get("", response_model=list[RestrictionOut])
def list_restrictions(
    db: Session = Depends(get_db), _: User = Depends(require_instructor)
):
    return db.execute(
        select(Restriction).order_by(Restriction.created_at.desc())
    ).scalars().all()


@router.post("", response_model=RestrictionOut, status_code=201)
def create_restriction(
    data: RestrictionIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_instructor),
):
    r = Restriction(
        subject_id=data.subject_id,
        reason=data.reason,
        starts_at=data.starts_at,
        ends_at=data.ends_at,
        is_active=data.is_active,
        created_by=user.id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{restriction_id}", status_code=204)
def delete_restriction(
    restriction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_instructor),
):
    r = db.get(Restriction, restriction_id)
    if r:
        db.delete(r)
        db.commit()
