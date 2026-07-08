"""Portable column types.

``JSONB`` renders as real PostgreSQL JSONB in production, and falls back to the
generic JSON type on other backends (e.g. SQLite for local dev / tests).
"""
from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as _PG_JSONB

# A generic JSON type that becomes JSONB only on PostgreSQL.
JSONB = JSON().with_variant(_PG_JSONB(), "postgresql")
