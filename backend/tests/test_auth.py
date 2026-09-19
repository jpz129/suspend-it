import os
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.core.security import get_current_user  # noqa: E402
from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402


@pytest.fixture()
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def SessionLocal(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture()
def client(SessionLocal):
    def _get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_get_current_user_is_exported():
    assert callable(get_current_user)
    assert get_current_user.__module__ == "app.core.security"


def test_register_login_me_round_trip(client):
    register = client.post(
        "/auth/register",
        json={"email": "alice@example.com", "password": "secret123", "name": "Alice"},
    )
    assert register.status_code == 201, register.text
    body = register.json()
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"
    assert "id" in body
    assert body["created_at"].endswith("Z")
    assert "password" not in body
    assert "hashed_password" not in body

    login = client.post(
        "/auth/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert login.status_code == 200, login.text
    token_body = login.json()
    assert token_body["token_type"] == "bearer"
    assert token_body["access_token"]

    me = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token_body['access_token']}"},
    )
    assert me.status_code == 200, me.text
    me_body = me.json()
    assert me_body["id"] == body["id"]
    assert me_body["email"] == "alice@example.com"
    assert me_body["name"] == "Alice"


def test_password_is_hashed_not_plaintext(client, SessionLocal):
    password = "plaintext-password"
    response = client.post(
        "/auth/register",
        json={"email": "hashme@example.com", "password": password, "name": None},
    )
    assert response.status_code == 201, response.text

    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.email == "hashme@example.com")).scalar_one()
        assert user.hashed_password != password
        assert password not in user.hashed_password
        assert user.hashed_password.startswith("$2")
    finally:
        db.close()


def test_duplicate_email_returns_409(client):
    payload = {"email": "dup@example.com", "password": "secret123", "name": None}
    first = client.post("/auth/register", json=payload)
    assert first.status_code == 201
    second = client.post("/auth/register", json=payload)
    assert second.status_code == 409
    assert "detail" in second.json()


def test_login_bad_credentials_returns_401(client):
    client.post(
        "/auth/register",
        json={"email": "bob@example.com", "password": "right-password", "name": "Bob"},
    )
    wrong = client.post(
        "/auth/login",
        json={"email": "bob@example.com", "password": "wrong-password"},
    )
    assert wrong.status_code == 401
    assert "detail" in wrong.json()

    missing = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "right-password"},
    )
    assert missing.status_code == 401


def test_me_missing_token_returns_401(client):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()


def test_me_invalid_token_returns_401(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_alembic_upgrade_head_creates_users_table(tmp_path):
    db_path = tmp_path / "alembic.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_path}", "JWT_SECRET": "test-secret"}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert db_path.exists()
    conn = sqlite3.connect(db_path)
    try:
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        assert "users" in tables
        columns = {
            row[1] for row in conn.execute("PRAGMA table_info(users)")
        }
        assert columns == {"id", "email", "hashed_password", "name", "created_at"}
    finally:
        conn.close()


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def test_live_uvicorn_register_login_me(tmp_path):
    db_path = tmp_path / "live.db"
    env = {
        **os.environ,
        "DATABASE_URL": f"sqlite:///{db_path}",
        "JWT_SECRET": "live-secret",
        "PYTHONPATH": str(BACKEND_ROOT),
    }
    upgrade = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert upgrade.returncode == 0, upgrade.stdout + upgrade.stderr

    port = _free_port()
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=BACKEND_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.time() + 20
        last_error = None
        while time.time() < deadline:
            if proc.poll() is not None:
                stdout, stderr = proc.communicate()
                raise AssertionError(f"uvicorn exited early: {stdout}\n{stderr}")
            try:
                httpx.get(f"{base}/openapi.json", timeout=0.5)
                break
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
                last_error = exc
                time.sleep(0.2)
        else:
            raise AssertionError(f"uvicorn did not start: {last_error}")

        register = httpx.post(
            f"{base}/auth/register",
            json={"email": "live@example.com", "password": "live-pass", "name": "Live"},
            timeout=10,
        )
        assert register.status_code == 201, register.text
        login = httpx.post(
            f"{base}/auth/login",
            json={"email": "live@example.com", "password": "live-pass"},
            timeout=10,
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        assert login.json()["token_type"] == "bearer"
        me = httpx.get(
            f"{base}/auth/me",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        assert me.status_code == 200, me.text
        assert me.json()["email"] == "live@example.com"

        missing = httpx.get(f"{base}/auth/me", timeout=10)
        assert missing.status_code == 401
        invalid = httpx.get(
            f"{base}/auth/me",
            headers={"Authorization": "Bearer invalid"},
            timeout=10,
        )
        assert invalid.status_code == 401

        conn = sqlite3.connect(db_path)
        try:
            hashed = conn.execute(
                "SELECT hashed_password FROM users WHERE email = ?",
                ("live@example.com",),
            ).fetchone()[0]
            assert hashed != "live-pass"
            assert hashed.startswith("$2")
        finally:
            conn.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
