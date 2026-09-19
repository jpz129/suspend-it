"""Component D history API tests.

Stubs Component A (`get_current_user` / User) and Component C
(`WorkoutPlan`) under tests/stubs/ so this file runs without those
components on the branch. The history router is mounted on a local
FastAPI app — `app/main.py` is not edited. No shared conftest.py.
"""

from __future__ import annotations

import sys
import types
from datetime import datetime, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

STUBS_DIR = Path(__file__).resolve().parent / "stubs"
if str(STUBS_DIR.parent) not in sys.path:
    sys.path.insert(0, str(STUBS_DIR.parent))

from tests.stubs.security import User, get_current_user as stub_get_current_user
from tests.stubs.workout import WorkoutPlan as StubWorkoutPlan


def _install_stub_modules() -> None:
    """Register A/C interfaces on sys.modules before importing D's router."""
    import app as app_pkg

    core = types.ModuleType("app.core")
    core.__path__ = []  # type: ignore[attr-defined]
    sys.modules.setdefault("app.core", core)
    app_pkg.core = core  # type: ignore[attr-defined]

    security = types.ModuleType("app.core.security")
    security.User = User
    security.get_current_user = stub_get_current_user
    sys.modules["app.core.security"] = security
    core.security = security

    schemas = types.ModuleType("app.schemas")
    schemas.__path__ = []  # type: ignore[attr-defined]
    sys.modules.setdefault("app.schemas", schemas)
    app_pkg.schemas = schemas  # type: ignore[attr-defined]

    workout = types.ModuleType("app.schemas.workout")
    workout.WorkoutPlan = StubWorkoutPlan
    sys.modules["app.schemas.workout"] = workout
    schemas.workout = workout


_install_stub_modules()

from app.api.routes.history import get_current_user, get_db, history_router
from app.models.history import HistoryBase, WorkoutHistory

SAMPLE_PLAN = {
    "title": "Pull Day",
    "duration_minutes": 30,
    "difficulty": "beginner",
    "source": "random",
    "exercises": [
        {
            "exercise_id": 1,
            "name": "TRX Row",
            "illustration_slug": "row",
            "sets": 3,
            "reps": "10",
            "rest_seconds": 45,
            "notes": None,
        }
    ],
}


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    HistoryBase.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture()
def auth_user():
    return User(id=1, email="a@example.com")


@pytest.fixture()
def client(db_session, auth_user):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.expire_all()

    def override_get_current_user():
        return auth_user

    app = FastAPI()
    app.include_router(history_router)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    with TestClient(app) as test_client:
        test_client.auth_user = auth_user  # type: ignore[attr-defined]
        yield test_client


def test_post_then_get_round_trip(client):
    payload = {
        "workout_plan": SAMPLE_PLAN,
        "completed_at": "2026-01-01T00:00:00Z",
        "notes": "felt strong",
    }

    created = client.post("/history", json=payload)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["id"] == 1
    assert body["workout_plan"] == SAMPLE_PLAN
    assert body["notes"] == "felt strong"
    assert _parse_dt(body["completed_at"]) == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert body["created_at"]

    listed = client.get("/history")
    assert listed.status_code == 200, listed.text
    entries = listed.json()
    assert len(entries) == 1
    assert entries[0] == body


def test_user_b_cannot_see_user_a_entries(client, db_session):
    user_a = User(id=1, email="a@example.com")
    user_b = User(id=2, email="b@example.com")
    current = {"user": user_a}

    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.expire_all()

    def override_get_current_user():
        return current["user"]

    app = FastAPI()
    app.include_router(history_router)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as isolated_client:
        create_a = isolated_client.post(
            "/history",
            json={
                "workout_plan": SAMPLE_PLAN,
                "completed_at": "2026-01-01T00:00:00Z",
                "notes": "user a only",
            },
        )
        assert create_a.status_code == 201, create_a.text
        a_id = create_a.json()["id"]

        current["user"] = user_b
        listed_b = isolated_client.get("/history")
        assert listed_b.status_code == 200
        assert listed_b.json() == []

        create_b = isolated_client.post(
            "/history",
            json={
                "workout_plan": {**SAMPLE_PLAN, "title": "User B plan"},
                "completed_at": "2026-01-02T00:00:00Z",
                "notes": None,
            },
        )
        assert create_b.status_code == 201, create_b.text
        listed_b = isolated_client.get("/history")
        assert [row["id"] for row in listed_b.json()] == [create_b.json()["id"]]
        assert listed_b.json()[0]["notes"] is None
        assert listed_b.json()[0]["workout_plan"]["title"] == "User B plan"

        current["user"] = user_a
        listed_a = isolated_client.get("/history")
        assert [row["id"] for row in listed_a.json()] == [a_id]
        assert listed_a.json()[0]["notes"] == "user a only"

    assert db_session.query(WorkoutHistory).count() == 2


def test_list_newest_first(client):
    first = client.post(
        "/history",
        json={
            "workout_plan": {**SAMPLE_PLAN, "title": "Older"},
            "completed_at": "2026-01-01T00:00:00Z",
            "notes": None,
        },
    )
    second = client.post(
        "/history",
        json={
            "workout_plan": {**SAMPLE_PLAN, "title": "Newer"},
            "completed_at": "2026-01-02T00:00:00Z",
            "notes": None,
        },
    )
    assert first.status_code == 201
    assert second.status_code == 201

    listed = client.get("/history")
    assert listed.status_code == 200
    titles = [row["workout_plan"]["title"] for row in listed.json()]
    ids = [row["id"] for row in listed.json()]
    assert titles == ["Newer", "Older"]
    assert ids == [second.json()["id"], first.json()["id"]]
