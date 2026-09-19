"""Auth register → login → /auth/me round-trip tests."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("JWT_SECRET", "test-secret")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

DB_PATH = Path("test_auth.db")


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if DB_PATH.exists():
        DB_PATH.unlink()


def _client() -> TestClient:
    return TestClient(app)


def test_register_login_me_round_trip() -> None:
    client = _client()
    register = client.post(
        "/auth/register",
        json={"email": "ada@example.com", "password": "secret123", "name": "Ada"},
    )
    assert register.status_code == 201, register.text
    body = register.json()
    assert body["email"] == "ada@example.com"
    assert body["name"] == "Ada"
    assert "id" in body
    assert body["created_at"].endswith("Z")

    login = client.post(
        "/auth/login",
        json={"email": "ada@example.com", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()
    assert token["token_type"] == "bearer"
    assert token["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token['access_token']}"})
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "ada@example.com"
    assert me.json()["name"] == "Ada"


def test_password_is_hashed_not_plaintext() -> None:
    client = _client()
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "hunter2!!", "name": None},
    )
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "bob@example.com"))
        assert user is not None
        assert user.hashed_password != "hunter2!!"
        assert user.hashed_password.startswith("$2")  # bcrypt


def test_duplicate_register_conflicts() -> None:
    client = _client()
    payload = {"email": "dup@example.com", "password": "secret123", "name": None}
    assert client.post("/auth/register", json=payload).status_code == 201
    assert client.post("/auth/register", json=payload).status_code == 409


def test_login_bad_password_401() -> None:
    client = _client()
    client.post(
        "/auth/register",
        json={"email": "eve@example.com", "password": "secret123", "name": None},
    )
    res = client.post(
        "/auth/login",
        json={"email": "eve@example.com", "password": "wrong"},
    )
    assert res.status_code == 401
    assert "detail" in res.json()


def test_me_missing_token_401() -> None:
    client = _client()
    res = client.get("/auth/me")
    assert res.status_code == 401
    assert "detail" in res.json()


def test_me_invalid_token_401() -> None:
    client = _client()
    res = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401
    assert "detail" in res.json()
