"""Document ingestion: extract text, chunk it, and build a subject's FAISS index.

Currently supports PDF. The extractor is pluggable so DOCX / PPTX / TXT / images
can be added later without touching the chunking or indexing logic.
"""
from __future__ import annotations

import logging

from pypdf import PdfReader

from app.ai.embeddings import EmbeddingProvider
from app.ai.vectorstore import SubjectVectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)


def extract_pdf_pages(path: str) -> list[tuple[int, str]]:
    """Return a list of (page_number, text) for a PDF."""
    reader = PdfReader(path)
    pages: list[tuple[int, str]] = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append((i, text))
    return pages


def chunk_text(
    text: str, size: int | None = None, overlap: int | None = None
) -> list[str]:
    """Split text into overlapping character windows on word boundaries."""
    size = size or settings.RAG_CHUNK_SIZE
    overlap = overlap or settings.RAG_CHUNK_OVERLAP
    words = text.split()
    chunks: list[str] = []
    current: list[str] = []
    length = 0
    for word in words:
        current.append(word)
        length += len(word) + 1
        if length >= size:
            chunks.append(" ".join(current))
            # Keep the last `overlap` characters worth of words for continuity.
            back, kept = 0, []
            for w in reversed(current):
                back += len(w) + 1
                kept.insert(0, w)
                if back >= overlap:
                    break
            current, length = kept, back
    if current:
        chunks.append(" ".join(current))
    return chunks


def build_chunks_for_files(files: list[dict]) -> list[dict]:
    """Turn a list of {path, source, mime} into indexable chunk dicts."""
    chunks: list[dict] = []
    for f in files:
        mime = f.get("mime", "application/pdf")
        source = f.get("source", "book")
        if mime == "application/pdf" or f["path"].lower().endswith(".pdf"):
            for page_no, page_text in extract_pdf_pages(f["path"]):
                for piece in chunk_text(page_text):
                    chunks.append(
                        {"text": piece, "source": source, "page": page_no}
                    )
        else:
            logger.warning("Unsupported file type for ingest: %s", f["path"])
    return chunks


def build_subject_index(
    subject_id: int, files: list[dict], extra_keys: list[str] | None = None
) -> dict:
    """Full pipeline: extract → chunk → embed → write FAISS. Returns stats."""
    chunks = build_chunks_for_files(files)
    if not chunks:
        raise ValueError("No extractable text found in the provided files.")

    provider = EmbeddingProvider(extra_keys=extra_keys)
    if not provider.has_keys:
        raise RuntimeError("No Gemini API keys available for embeddings.")

    vectors = provider.embed_documents([c["text"] for c in chunks])
    store = SubjectVectorStore(subject_id)
    dim = store.build(vectors, chunks)
    return {
        "chunk_count": len(chunks),
        "dimensions": dim,
        "embedding_model": provider.model,
    }
