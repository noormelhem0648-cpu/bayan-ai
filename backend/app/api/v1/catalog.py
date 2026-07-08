"""Public, read-only catalog navigation: languages → tracks → majors → years → subjects."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AcademicYear, Language, Major, Subject, Track
from app.schemas.catalog import (
    LanguageOut,
    MajorOut,
    SubjectOut,
    TrackOut,
    YearOut,
)

router = APIRouter()


@router.get("/languages", response_model=list[LanguageOut])
def list_languages(db: Session = Depends(get_db)):
    return db.execute(
        select(Language)
        .where(Language.is_active.is_(True))
        .order_by(Language.order_index)
    ).scalars().all()


@router.get("/tracks", response_model=list[TrackOut])
def list_tracks(db: Session = Depends(get_db)):
    return db.execute(
        select(Track).where(Track.is_active.is_(True)).order_by(Track.order_index)
    ).scalars().all()


@router.get("/majors", response_model=list[MajorOut])
def list_majors(track_id: int, db: Session = Depends(get_db)):
    return db.execute(
        select(Major)
        .where(Major.track_id == track_id, Major.is_active.is_(True))
        .order_by(Major.order_index)
    ).scalars().all()


@router.get("/years", response_model=list[YearOut])
def list_years(major_id: int, db: Session = Depends(get_db)):
    return db.execute(
        select(AcademicYear)
        .where(AcademicYear.major_id == major_id, AcademicYear.is_active.is_(True))
        .order_by(AcademicYear.order_index, AcademicYear.number)
    ).scalars().all()


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(year_id: int, db: Session = Depends(get_db)):
    return db.execute(
        select(Subject)
        .where(Subject.year_id == year_id, Subject.is_active.is_(True))
        .order_by(Subject.order_index)
    ).scalars().all()
