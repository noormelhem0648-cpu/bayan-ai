"""System-prompt construction for the AI assistant.

The assistant must always answer in the user's chosen application language, must
prioritise facts found in the retrieved book passages, and must clearly separate
"from the book" from "general knowledge" without inventing sources.
"""
from __future__ import annotations

# Human-readable language names keyed by code, used to instruct the model.
LANGUAGE_NAMES: dict[str, str] = {
    "ar": "Arabic (العربية)",
    "en": "English",
    "ms": "Malay (Bahasa Melayu)",
    "id": "Indonesian (Bahasa Indonesia)",
    "zh": "Chinese (中文)",
    "am": "Amharic (አማርኛ)",
    "th": "Thai (ภาษาไทย)",
    "ko": "Korean (한국어)",
    "ru": "Russian (Русский)",
}

# Marker phrases the model is told to use, per language, so students always see a
# clear "from the book" vs "general knowledge" distinction in their own language.
CITATION_MARKERS: dict[str, tuple[str, str]] = {
    "ar": ("📖 من الكتاب", "💡 معرفة عامة"),
    "en": ("📖 From the book", "💡 General knowledge"),
    "ms": ("📖 Dari buku", "💡 Pengetahuan umum"),
    "id": ("📖 Dari buku", "💡 Pengetahuan umum"),
    "zh": ("📖 来自课本", "💡 常识"),
    "am": ("📖 ከመጽሐፉ", "💡 አጠቃላይ እውቀት"),
    "th": ("📖 จากหนังสือ", "💡 ความรู้ทั่วไป"),
    "ko": ("📖 교재에서", "💡 일반 지식"),
    "ru": ("📖 Из учебника", "💡 Общие знания"),
}


def language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, LANGUAGE_NAMES["en"])


def build_system_prompt(
    *,
    language: str,
    subject_name: str,
    is_non_native_track: bool = False,
    level: str | None = None,
) -> str:
    """Compose the system prompt for a chat turn."""
    lang = language_name(language)
    from_book, general = CITATION_MARKERS.get(language, CITATION_MARKERS["en"])

    tutor_block = ""
    if is_non_native_track:
        lvl = level or "beginner"
        tutor_block = (
            "\nYou are acting as a complete Arabic-language tutor for non-native "
            f"speakers at the '{lvl}' level. Adapt vocabulary, pace and explanation "
            "depth to that level. Cover grammar, vocabulary, conversation, "
            "pronunciation, reading, writing, listening, drills and exam prep as "
            "relevant. When teaching Arabic words, show them in Arabic script with a "
            "transliteration and a translation into the student's language.\n"
        )

    return (
        f"You are Bayan AI, a smart academic assistant for the subject "
        f"\"{subject_name}\".\n"
        f"ALWAYS reply in {lang}. Never switch languages unless the user explicitly "
        f"asks. Keep a warm, encouraging, academic tone.\n"
        f"{tutor_block}"
        "GROUNDING RULES:\n"
        "1. You are given CONTEXT passages retrieved from this subject's own books.\n"
        "2. Prioritise facts from the CONTEXT. When a fact comes from the context, "
        f"prefix it with \"{from_book}\".\n"
        "3. If the answer is NOT in the context, first tell the user it is not in the "
        f"book, then answer from general knowledge prefixed with \"{general}\".\n"
        "4. NEVER invent a unit name, page number, or citation that is not present in "
        "the context. Academic honesty is mandatory.\n"
        "5. Only use passages from THIS subject; you have no access to other subjects.\n"
    )


def build_context_block(passages: list[dict]) -> str:
    """Render retrieved passages into a CONTEXT block for the prompt."""
    if not passages:
        return "CONTEXT: (no relevant passages were found in this subject's books)\n"
    lines = ["CONTEXT (passages from this subject's books):"]
    for i, p in enumerate(passages, 1):
        src = p.get("source") or "book"
        page = p.get("page")
        loc = f" — {src}" + (f", p.{page}" if page else "")
        lines.append(f"[{i}{loc}]\n{p.get('text', '').strip()}")
    return "\n".join(lines) + "\n"
