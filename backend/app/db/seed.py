"""Seed baseline data: the 9 languages, the 3 tracks, and a default admin.

Idempotent — safe to run on every startup. Content here is *bootstrap* data only;
everything remains editable from the dashboards afterwards.
"""
from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import AcademicYear, Language, Major, Track, User
from app.models.enums import UserRole

logger = logging.getLogger(__name__)

# Years shown under the "Arabic" and "Applied Arabic" tracks.
YEAR_NAMES: dict[int, dict] = {
    1: {"ar": "السنة الأولى", "en": "First Year"},
    2: {"ar": "السنة الثانية", "en": "Second Year"},
    3: {"ar": "السنة الثالثة", "en": "Third Year"},
    4: {"ar": "السنة الرابعة", "en": "Fourth Year"},
}

# Levels 1..7 shown under the "Arabic for non-native speakers" track.
LEVEL_NAMES: dict[int, dict] = {
    n: {"ar": f"المستوى {a}", "en": f"Level {n}"}
    for n, a in enumerate(
        ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع"], start=1
    )
}

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

    db.flush()

    # Each track gets one (hidden) program, so the UI can go straight from the
    # track to its years/levels. Arabic & Applied → years 1..4; non-natives → 1..7.
    _seed_program(db, "arabic", YEAR_NAMES)
    _seed_program(db, "applied-arabic", YEAR_NAMES)
    _seed_program(db, "non-natives", LEVEL_NAMES)

    db.commit()


def _seed_program(db: Session, track_slug: str, number_names: dict[int, dict]) -> None:
    """Ensure a track has one program with the given numbered years/levels."""
    track = db.execute(
        select(Track).where(Track.slug == track_slug)
    ).scalar_one_or_none()
    if not track:
        return

    major = db.execute(
        select(Major).where(Major.track_id == track.id)
    ).scalar_one_or_none()
    if not major:
        major = Major(
            track_id=track.id,
            name_i18n={"ar": "البرنامج", "en": "Program"},
            order_index=0,
            is_active=True,
        )
        db.add(major)
        db.flush()

    for number, names in number_names.items():
        exists = db.execute(
            select(AcademicYear).where(
                AcademicYear.major_id == major.id, AcademicYear.number == number
            )
        ).scalar_one_or_none()
        if not exists:
            db.add(
                AcademicYear(
                    major_id=major.id,
                    number=number,
                    name_i18n=names,
                    order_index=number,
                    is_active=True,
                )
            )
