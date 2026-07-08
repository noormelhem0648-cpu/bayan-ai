"""Google Gemini client with automatic API-key rotation.

Keys come from settings (env) plus any active keys contributed by users. When a
key hits its quota (HTTP 429 / ResourceExhausted), we transparently advance to the
next key in the pool.
"""
from __future__ import annotations

import logging
from collections.abc import Iterator, Sequence

import google.generativeai as genai

from app.core.config import settings

logger = logging.getLogger(__name__)


class NoKeysAvailableError(RuntimeError):
    """Raised when no Gemini API key can satisfy a request."""


class GeminiClient:
    """Thin wrapper around google-generativeai that rotates keys on quota errors."""

    def __init__(self, extra_keys: Sequence[str] | None = None) -> None:
        keys = list(settings.GEMINI_API_KEYS) + list(extra_keys or [])
        # De-duplicate while preserving order.
        self._keys = list(dict.fromkeys(k for k in keys if k))
        self._idx = 0

    @property
    def has_keys(self) -> bool:
        return bool(self._keys)

    def _configure_current(self) -> None:
        genai.configure(api_key=self._keys[self._idx])

    def _is_quota_error(self, exc: Exception) -> bool:
        name = exc.__class__.__name__.lower()
        text = str(exc).lower()
        return (
            "resourceexhausted" in name
            or "429" in text
            or "quota" in text
            or "rate limit" in text
        )

    def _advance(self) -> bool:
        """Move to the next key; return False if the pool is exhausted."""
        if self._idx + 1 >= len(self._keys):
            return False
        self._idx += 1
        logger.warning("Gemini key rotated to index %s", self._idx)
        return True

    def stream_chat(
        self, system_prompt: str, history: list[dict], user_message: str
    ) -> Iterator[str]:
        """Yield answer text chunks, rotating keys on quota errors."""
        if not self.has_keys:
            raise NoKeysAvailableError("No Gemini API keys configured.")

        # Gemini expects roles "user" / "model" (not "assistant").
        contents = [
            {
                "role": "model" if h["role"] in ("assistant", "model") else "user",
                "parts": [h["content"]],
            }
            for h in history
            if h.get("content")
        ]
        contents.append({"role": "user", "parts": [user_message]})

        while True:
            self._configure_current()
            try:
                model = genai.GenerativeModel(
                    settings.GEMINI_CHAT_MODEL, system_instruction=system_prompt
                )
                for chunk in model.generate_content(contents, stream=True):
                    if getattr(chunk, "text", None):
                        yield chunk.text
                return
            except Exception as exc:  # noqa: BLE001 - we classify below
                if self._is_quota_error(exc) and self._advance():
                    continue
                logger.exception("Gemini generation failed")
                raise

    def complete(self, system_prompt: str, user_message: str) -> str:
        """Non-streaming completion (used for quiz/exam generation)."""
        return "".join(self.stream_chat(system_prompt, [], user_message))
