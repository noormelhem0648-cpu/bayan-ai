"""Smoke tests: app boots, health works, auth + catalog flow behaves.

Uses an in-memory SQLite DB so no PostgreSQL is required for CI. (JSONB columns
degrade to JSON on SQLite, which is fine for these tests.)
"""
from __future__ import annotations

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db import session as db_session


@pytest.fixture(scope="module")
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    db_session.engine = engine
    db_session.SessionLocal.configure(bind=engine)
    Base.metadata.create_all(bind=engine)

    from app.main import app

    with TestClient(app) as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_languages_seeded(client):
    res = client.get("/api/v1/catalog/languages")
    assert res.status_code == 200
    codes = {l["code"] for l in res.json()}
    assert {"ar", "en", "zh", "ru", "ko"}.issubset(codes)


def test_tracks_seeded(client):
    res = client.get("/api/v1/catalog/tracks")
    slugs = {t["slug"] for t in res.json()}
    assert {"arabic", "applied-arabic", "non-natives"}.issubset(slugs)


def test_register_login_me(client):
    reg = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test", "email": "t@example.com",
            "password": "password123", "app_language": "en",
        },
    )
    assert reg.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "t@example.com", "password": "password123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "t@example.com"


def test_protected_requires_auth(client):
    assert client.get("/api/v1/chat/conversations").status_code == 401
