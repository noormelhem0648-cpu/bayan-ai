"""System schemas: restrictions, contributed keys, settings."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RestrictionIn(BaseModel):
    subject_id: int
    reason: str | None = None
    starts_at: datetime | None = None  # None = starts now
    ends_at: datetime | None = None    # None = open-ended
    is_active: bool = True


class RestrictionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    reason: str | None
    starts_at: datetime | None
    ends_at: datetime | None
    is_active: bool
    created_at: datetime


class RestrictionCheckOut(BaseModel):
    blocked: bool
    reason: str | None = None
    ends_at: datetime | None = None


class ContributeKeyRequest(BaseModel):
    key_value: str
    label: str | None = None


class SettingIn(BaseModel):
    key: str
    value: dict
