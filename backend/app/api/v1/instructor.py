"""Instructor dashboard: manage majors/years/subjects, books, indexes, stats."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import ingest
from app.ai.vectorstore import SubjectVectorStore
from app.api.deps import get_contributed_keys, require_instructor
from app.core.config import settings
from app.db.session import get_db
from app.models import (
    AcademicYear,
    Book,
    BookFile,
    Conversation,
    Major,
    Message,
    Subject,
    SubjectIndex,
    User,
)
from app.models.enums import IndexStatus
from app.schemas.catalog import (
    BookOut,
    MajorIn,
    MajorOut,
    SubjectIn,
    SubjectOut,
    YearIn,
    YearOut,
)

router = APIRouter(dependencies=[Depends(require_instructor)])


# ---- Majors -----------------------------------------------------------------
@router.post("/majors", response_model=MajorOut, status_code=201)
def create_major(data: MajorIn, db: Session = Depends(get_db)):
    m = Major(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/majors/{major_id}", response_model=MajorOut)
def update_major(major_id: int, data: MajorIn, db: Session = Depends(get_db)):
    m = db.get(Major, major_id) or _404("Major")
    for k, v in data.model_dump().items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return m


# ---- Years ------------------------------------------------------------------
@router.post("/years", response_model=YearOut, status_code=201)
def create_year(data: YearIn, db: Session = Depends(get_db)):
    y = AcademicYear(**data.model_dump())
    db.add(y)
    db.commit()
    db.refresh(y)
    return y


# ---- Subjects ---------------------------------------------------------------
@router.post("/subjects", response_model=SubjectOut, status_code=201)
def create_subject(data: SubjectIn, db: Session = Depends(get_db)):
    s = Subject(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(subject_id: int, data: SubjectIn, db: Session = Depends(get_db)):
    s = db.get(Subject, subject_id) or _404("Subject")
    for k, v in data.model_dump().items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    s = db.get(Subject, subject_id)
    if s:
        SubjectVectorStore(subject_id).delete()
        db.delete(s)
        db.commit()


# ---- Books ------------------------------------------------------------------
@router.get("/subjects/{subject_id}/books", response_model=list[BookOut])
def list_books(subject_id: int, db: Session = Depends(get_db)):
    return db.execute(
        select(Book).where(Book.subject_id == subject_id)
    ).scalars().all()


@router.post("/subjects/{subject_id}/books", response_model=BookOut, status_code=201)
async def upload_book(
    subject_id: int,
    title: str = Form(...),
    author: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not db.get(Subject, subject_id):
        _404("Subject")
    book = Book(subject_id=subject_id, title=title, author=author)
    db.add(book)
    db.flush()

    books_dir = os.path.join(settings.UPLOADS_DIR, "books", str(subject_id))
    os.makedirs(books_dir, exist_ok=True)
    safe = f"{uuid.uuid4().hex}_{os.path.basename(file.filename or 'book.pdf')}"
    path = os.path.join(books_dir, safe)
    content = await file.read()
    with open(path, "wb") as fh:
        fh.write(content)

    db.add(
        BookFile(
            book_id=book.id,
            filename=file.filename or safe,
            storage_path=path,
            mime_type=file.content_type or "application/pdf",
            size_bytes=len(content),
        )
    )
    _mark_index(db, subject_id, IndexStatus.stale)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        return
    subject_id = book.subject_id
    for bf in book.files:
        if os.path.exists(bf.storage_path):
            os.remove(bf.storage_path)
    db.delete(book)
    _mark_index(db, subject_id, IndexStatus.stale)
    db.commit()


@router.post("/subjects/{subject_id}/reindex")
def reindex_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    extra_keys: list[str] = Depends(get_contributed_keys),
):
    """Rebuild the subject's FAISS index from all its active book files."""
    files = db.execute(
        select(BookFile)
        .join(Book, Book.id == BookFile.book_id)
        .where(Book.subject_id == subject_id, Book.is_active.is_(True))
    ).scalars().all()
    if not files:
        raise HTTPException(status_code=400, detail="No book files to index")

    idx = _get_or_create_index(db, subject_id)
    idx.status = IndexStatus.building
    db.commit()
    try:
        payload = [
            {"path": f.storage_path, "mime": f.mime_type, "source": f.filename}
            for f in files
        ]
        stats = ingest.build_subject_index(subject_id, payload, extra_keys=extra_keys)
        idx.status = IndexStatus.ready
        idx.chunk_count = stats["chunk_count"]
        idx.dimensions = stats["dimensions"]
        idx.embedding_model = stats["embedding_model"]
        idx.error = None
        idx.built_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "ready", **stats}
    except Exception as exc:  # noqa: BLE001
        idx.status = IndexStatus.failed
        idx.error = str(exc)[:500]
        db.commit()
        raise HTTPException(status_code=500, detail=f"Indexing failed: {exc}") from exc


# ---- Stats ------------------------------------------------------------------
@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "students": db.scalar(select(func.count()).select_from(User)),
        "subjects": db.scalar(select(func.count()).select_from(Subject)),
        "conversations": db.scalar(select(func.count()).select_from(Conversation)),
        "messages": db.scalar(select(func.count()).select_from(Message)),
    }


# ---- helpers ----------------------------------------------------------------
def _404(entity: str):
    raise HTTPException(status_code=404, detail=f"{entity} not found")


def _get_or_create_index(db: Session, subject_id: int) -> SubjectIndex:
    idx = db.execute(
        select(SubjectIndex).where(SubjectIndex.subject_id == subject_id)
    ).scalar_one_or_none()
    if not idx:
        idx = SubjectIndex(subject_id=subject_id, status=IndexStatus.pending)
        db.add(idx)
        db.flush()
    return idx


def _mark_index(db: Session, subject_id: int, status: IndexStatus) -> None:
    _get_or_create_index(db, subject_id).status = status
