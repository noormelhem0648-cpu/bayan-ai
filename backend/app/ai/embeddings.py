"""Gemini embedding provider (multilingual) with key rotation."""
from __future__ import annotations

import logging

import google.generativeai as genai
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    def __init__(self, extra_keys: list[str] | None = None) -> None:
        keys = list(settings.gemini_api_keys_list) + list(extra_keys or [])
        self._keys = list(dict.fromkeys(k for k in keys if k))
        self._idx = 0
        self.model = settings.GEMINI_EMBEDDING_MODEL

    @property
    def has_keys(self) -> bool:
        return bool(self._keys)

    def _advance(self) -> bool:
        if self._idx + 1 >= len(self._keys):
            return False
        self._idx += 1
        return True

    def _embed_one(self, text: str, task_type: str) -> list[float]:
        while True:
            genai.configure(api_key=self._keys[self._idx])
            try:
                res = genai.embed_content(
                    model=self.model, content=text, task_type=task_type
                )
                return res["embedding"]
            except Exception as exc:  # noqa: BLE001
                if "429" in str(exc).lower() or "quota" in str(exc).lower():
                    if self._advance():
                        continue
                raise

    def embed_documents(self, texts: list[str]) -> np.ndarray:
        vectors = [self._embed_one(t, "retrieval_document") for t in texts]
        return np.array(vectors, dtype="float32")

    def embed_query(self, text: str) -> np.ndarray:
        return np.array(
            [self._embed_one(text, "retrieval_query")], dtype="float32"
        )
