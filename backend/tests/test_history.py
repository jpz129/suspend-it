"""History POST/GET round-trip and per-user isolation."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass

import app  # real package
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _ensure(name: str) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    mod.__path__ = []  # type: ignore[attr-defined]
    sys.modules[name] = mod
    parent_name, _, child = name.rpartition(".")
    if parent_name:
        setattr(sys.modules[parent_name], child, mod)
    return mod


class WorkoutExercise(BaseModel):
    exercise_id: int
    name: str
    illustration_slug: str
    sets: int
    reps: str
    rest_seconds: int
    notes: str | None = None


class WorkoutPlan(BaseModel):
    title: str
    duration_minutes: int
    difficulty: str
    source: str
    exercises: list[WorkoutExercise] = Field(min_length=1)


_ensure("app.core")
_ensure("app.schemas")
_ensure("app.db")

workout_mod = types.ModuleType("app.schemas.workout")
workout_mod.WorkoutPlan = WorkoutPlan
workout_mod.WorkoutExercise = WorkoutExercise
sys.modules["app.schemas.workout"] = workout_mod
app.schemas.workout = workout_mod  # type: ignore[attr-defined]


@dataclass
class User:
    id: int
    email: str = "a@example.com"


CURRENT: dict = {"user": User(id=1)}


def get_current_user() -> User:
    return CURRENT["user"]


security = types.ModuleType("app.core.security")
security.get_current_user = get_current_user
sys.modules["app.core.security"] = security
app.core.security = security  # type: ignore[attr-defined]

session_mod = types.ModuleType("app.db.session")
session_mod.get_db = lambda: None
sys.modules["app.db.session"] = session_mod

from app.api.routes.history import get_db, history_router  # noqa: E402
from app.core.security import get_current_user as auth_dep  # noqa: E402
from app.models.history import Base, WorkoutHistory  # noqa: E402

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def _override_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app_api = FastAPI()
app_api.include_router(history_router)
app_api.dependency_overrides[auth_dep] = lambda: CURRENT["user"]
app_api.dependency_overrides[get_db] = _override_db
client = TestClient(app_api)

PLAN = {
    "title": "Morning draw",
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


def test_post_then_get_round_trip() -> None:
    CURRENT["user"] = User(id=1)
    created = client.post(
        "/history",
        json={
            "workout_plan": PLAN,
            "completed_at": "2026-01-01T00:00:00Z",
            "notes": "felt strong",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["notes"] == "felt strong"
    assert body["workout_plan"]["title"] == "Morning draw"
    listed = client.get("/history")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == body["id"]


def test_only_own_entries_and_newest_first() -> None:
    db = SessionLocal()
    db.query(WorkoutHistory).delete()
    db.commit()
    db.close()

    CURRENT["user"] = User(id=1)
    client.post(
        "/history",
        json={"workout_plan": PLAN, "completed_at": "2026-01-01T00:00:00Z", "notes": "older"},
    )
    client.post(
        "/history",
        json={"workout_plan": PLAN, "completed_at": "2026-02-01T00:00:00Z", "notes": "newer"},
    )

    CURRENT["user"] = User(id=2)
    client.post(
        "/history",
        json={"workout_plan": PLAN, "completed_at": "2026-03-01T00:00:00Z", "notes": "user2"},
    )

    CURRENT["user"] = User(id=1)
    mine = client.get("/history").json()
    assert [row["notes"] for row in mine] == ["newer", "older"]

    CURRENT["user"] = User(id=2)
    theirs = client.get("/history").json()
    assert [row["notes"] for row in theirs] == ["user2"]
