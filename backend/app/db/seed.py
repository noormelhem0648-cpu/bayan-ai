"""Seed baseline data: the 9 languages, the 3 tracks, and a default admin.

Idempotent — safe to run on every startup. Content here is *bootstrap* data only;
everything remains editable from the dashboards afterwards.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import Language, Track, User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)

LANGUAGES = [
    ("ar", "Arabic", "العربية", "rtl"),
    ("en", "English", "English", "ltr"),
    ("ms", "Malay", "Bahasa Melayu", "ltr"),
    ("id", "Indonesian", "Bahasa Indonesia", "ltr"),
    ("zh", "Chinese", "中文", "ltr"),
    ("am", "Amharic", "አማርኛ", "rtl"),
    ("th", "Thai", "ภาษาไทย", "ltr"),
    ("ko", "Korean", "한국어", "ltr"),
    ("ru", "Russian", "Русский", "ltr"),
]

TRACKS = [
    (
        "arabic",
        {
            "ar": "اللغة العربية", "en": "Arabic Language", "ms": "Bahasa Arab",
            "id": "Bahasa Arab", "zh": "阿拉伯语", "am": "የአረብኛ ቋንቋ",
            "th": "ภาษาอาหรับ", "ko": "아랍어", "ru": "Арабский язык",
        },
    ),
    (
        "applied-arabic",
        {
            "ar": "اللغة العربية التطبيقية", "en": "Applied Arabic",
            "ms": "Bahasa Arab Gunaan", "id": "Bahasa Arab Terapan",
            "zh": "应用阿拉伯语", "am": "ተግባራዊ አረብኛ", "th": "ภาษาอาหรับประยุกต์",
            "ko": "응용 아랍어", "ru": "Прикладной арабский",
        },
    ),
    (
        "non-natives",
        {
            "ar": "تعليم العربية للناطقين بغيرها",
            "en": "Arabic for Non-Native Speakers",
            "ms": "Bahasa Arab untuk Bukan Penutur Asli",
            "id": "Bahasa Arab untuk Penutur Asing", "zh": "面向非母语者的阿拉伯语",
            "am": "አረብኛ ለሌሎች ተናጋሪዎች", "th": "ภาษาอาหรับสำหรับผู้ที่ไม่ใช่เจ้าของภาษา",
            "ko": "비원어민을 위한 아랍어", "ru": "Арабский для иностранцев",
        },
    ),
]


def seed(db: Session) -> None:
    for i, (code, name, native, direction) in enumerate(LANGUAGES):
        if not db.get(Language, code):
            db.add(
                Language(
                    code=code, name=name, native_name=native,
                    direction=direction, order_index=i, is_active=True,
                )
            )

    for i, (slug, names) in enumerate(TRACKS):
        exists = db.execute(select(Track).where(Track.slug == slug)).scalar_one_or_none()
        if not exists:
            db.add(Track(slug=slug, name_i18n=names, order_index=i, is_active=True))

    admin_email = "admin@bayan.ai"
    if not db.execute(
        select(User).where(User.email == admin_email)
    ).scalar_one_or_none():
        db.add(
            User(
                name="Administrator", email=admin_email,
                hashed_password=hash_password("Admin@12345"),
                role=UserRole.admin, app_language="ar",
                is_active=True, is_verified=True,
            )
        )
        logger.info("Seeded default admin: %s / Admin@12345", admin_email)

    db.commit()
