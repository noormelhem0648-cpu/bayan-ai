"""Per-subject FAISS vector store with strict path isolation.

Each subject gets its OWN directory: ``<INDEXES_DIR>/subject_<id>/`` containing
``index.faiss`` and ``chunks.pkl``. The subject id is sanitised to digits only,
so a subject can never traverse outside its own folder or read another subject's
index. This is the RAG isolation boundary.
"""
from __future__ import annotations

import os
import pickle
import re

import faiss
import numpy as np

from app.core.config import settings

_INDEX_FILE = "index.faiss"
_CHUNKS_FILE = "chunks.pkl"


def _safe_subject_dir(subject_id: int | str) -> str:
    """Return an isolated, traversal-proof directory for a subject."""
    sid = re.sub(r"[^0-9]", "", str(subject_id))
    if not sid:
        raise ValueError("Invalid subject id for index path.")
    path = os.path.join(settings.INDEXES_DIR, f"subject_{sid}")
    os.makedirs(path, exist_ok=True)
    return path


class SubjectVectorStore:
    """FAISS index scoped to a single subject."""

    def __init__(self, subject_id: int) -> None:
        self.subject_id = subject_id
        self.dir = _safe_subject_dir(subject_id)
        self.index_path = os.path.join(self.dir, _INDEX_FILE)
        self.chunks_path = os.path.join(self.dir, _CHUNKS_FILE)

    def exists(self) -> bool:
        return os.path.exists(self.index_path) and os.path.exists(self.chunks_path)

    def build(self, vectors: np.ndarray, chunks: list[dict]) -> int:
        """(Re)build the index from vectors + their chunk metadata."""
        if vectors.ndim != 2 or vectors.shape[0] != len(chunks):
            raise ValueError("Vectors/chunks length mismatch.")
        dim = vectors.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(vectors)
        faiss.write_index(index, self.index_path)
        with open(self.chunks_path, "wb") as fh:
            pickle.dump(chunks, fh)
        return dim

    def search(self, query_vector: np.ndarray, top_k: int) -> list[dict]:
        """Return the top-k nearest chunks for a query vector."""
        if not self.exists():
            return []
        index = faiss.read_index(self.index_path)
        with open(self.chunks_path, "rb") as fh:
            chunks: list[dict] = pickle.load(fh)
        k = min(top_k, len(chunks))
        if k == 0:
            return []
        distances, ids = index.search(query_vector, k)
        results: list[dict] = []
        for dist, idx in zip(distances[0], ids[0]):
            if 0 <= idx < len(chunks):
                item = dict(chunks[idx])
                item["score"] = float(dist)
                results.append(item)
        return results

    def delete(self) -> None:
        for path in (self.index_path, self.chunks_path):
            if os.path.exists(path):
                os.remove(path)
