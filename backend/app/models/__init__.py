"""SQLAlchemy models — importing this package registers every table on Base."""
from app.models.assessment import (
    Exam,
    ExamQuestion,
    Question,
    Quiz,
    QuizAttempt,
)
from app.models.catalog import AcademicYear, Language, Major, Subject, Track
from app.models.chat import Conversation, Message
from app.models.content import Book, BookFile, SubjectIndex
from app.models.enums import (
    IndexStatus,
    QuestionType,
    QuizDifficulty,
    UserRole,
)
from app.models.system import AuditLog, Notification, Restriction, Setting, UsageStat
from app.models.user import ContributedKey, UploadedFile, User

__all__ = [
    "AcademicYear",
    "AuditLog",
    "Book",
    "BookFile",
    "ContributedKey",
    "Conversation",
    "Exam",
    "ExamQuestion",
    "IndexStatus",
    "Language",
    "Major",
    "Message",
    "Notification",
    "Question",
    "Quiz",
    "QuizAttempt",
    "QuizDifficulty",
    "QuestionType",
    "Restriction",
    "Setting",
    "Subject",
    "SubjectIndex",
    "Track",
    "UsageStat",
    "UploadedFile",
    "User",
    "UserRole",
]
