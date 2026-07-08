"""RAG orchestrator: retrieve subject passages, then stream a grounded answer."""
from __future__ import annotations

import logging
from collections.abc import Iterator

from app.ai.embeddings import EmbeddingProvider
from app.ai.llm import GeminiClient
from app.ai.prompts import build_context_block, build_system_prompt
from app.ai.vectorstore import SubjectVectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)


def retrieve(subject_id: int, query: str, extra_keys: list[str] | None = None) -> list[dict]:
    """Retrieve the top-k passages for a query from THIS subject's index only."""
    store = SubjectVectorStore(subject_id)
    if not store.exists():
        return []
    provider = EmbeddingProvider(extra_keys=extra_keys)
    if not provider.has_keys:
        return []
    qvec = provider.embed_query(query)
    return store.search(qvec, settings.RAG_TOP_K)


def stream_answer(
    *,
    subject_id: int,
    subject_name: str,
    language: str,
    question: str,
    history: list[dict],
    is_non_native_track: bool = False,
    level: str | None = None,
    extra_keys: list[str] | None = None,
) -> tuple[list[dict], Iterator[str]]:
    """Return (retrieved_passages, answer_token_iterator).

    Passages are returned separately so the caller can persist them as the
    message's sources for citation.
    """
    passages = retrieve(subject_id, question, extra_keys=extra_keys)

    system_prompt = build_system_prompt(
        language=language,
        subject_name=subject_name,
        is_non_native_track=is_non_native_track,
        level=level,
    )
    context = build_context_block(passages)
    user_message = f"{context}\nQUESTION: {question}"

    client = GeminiClient(extra_keys=extra_keys)
    token_iter = client.stream_chat(system_prompt, history[-8:], user_message)
    return passages, token_iter
