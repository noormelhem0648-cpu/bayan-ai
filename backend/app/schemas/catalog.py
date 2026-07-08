"""Catalog schemas (tracks, majors, years, subjects, languages, books)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

I18n = dict[str, str]


class LanguageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str
    name: str
    native_name: str
    direction: str
    is_active: bool


class LanguageIn(BaseModel):
    code: str = Field(max_length=10)
    name: str
    native_name: str
    direction: str = "ltr"
    is_active: bool = True
    order_index: int = 0


class TrackIn(BaseModel):
    slug: str
    name_i18n: I18n
    description_i18n: I18n = Field(default_factory=dict)
    order_index: int = 0
    is_active: bool = True


class TrackOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name_i18n: I18n
    description_i18n: I18n
    order_index: int
    is_active: bool


class MajorIn(BaseModel):
    track_id: int
    name_i18n: I18n
    order_index: int = 0
    is_active: bool = True


class MajorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    track_id: int
    name_i18n: I18n
    order_index: int
    is_active: bool


class YearIn(BaseModel):
    major_id: int
    number: int
    name_i18n: I18n
    order_index: int = 0
    is_active: bool = True


class YearOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    major_id: int
    number: int
    name_i18n: I18n
    order_index: int
    is_active: bool


class SubjectIn(BaseModel):
    year_id: int
    code: str
    name_i18n: I18n
    description_i18n: I18n = Field(default_factory=dict)
    order_index: int = 0
    is_active: bool = True


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    year_id: int
    code: str
    name_i18n: I18n
    description_i18n: I18n
    order_index: int
    is_active: bool


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    subject_id: int
    title: str
    author: str | None
    is_active: bool
