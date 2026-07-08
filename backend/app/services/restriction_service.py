"""Subject restriction (exam-time blocking) logic."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Restriction
from app.models.enums import UserRole


def active_restriction(db: Session, subject_id: int) -> Restriction | None:
    """Return the currently-effective restriction for a subject, if any."""
    now = datetime.now(timezone.utc)
    rows = db.execute(
        select(Restriction).where(
            Restriction.subject_id == subject_id,
            Restriction.is_active.is_(True),
        )
    ).scalars()
    for r in rows:
        starts_ok = r.starts_at is None or r.starts_at <= now
        ends_ok = r.ends_at is None or now < r.ends_at
        if starts_ok and ends_ok:
            return r
    return None


def is_blocked_for(db: Session, subject_id: int, role: UserRole) -> Restriction | None:
    """Instructors/admins are never blocked (they may preview as a student)."""
    if role in (UserRole.instructor, UserRole.admin):
        return None
    return active_restriction(db, subject_id)
