"""Standalone tests for GET /exercises (Component B).

Mounts the exercises router on a tiny FastAPI app; does not import
``app.main`` (owned by the integration step / Component A).
"""

from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.api.routes.exercises import exercises_router, get_db
from app.models.exercise import Base, Exercise


def _session_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False), engine


def _add_exercise(db: Session, **kwargs) -> Exercise:
    defaults = {
        "name": "TRX Row",
        "muscle_group": "back",
        "difficulty": "beginner",
        "equipment": "suspension trainer",
        "instructions": "Pull your chest to the handles.",
        "illustration_slug": "row",
        "source": "curated",
        "external_id": "trx-row",
    }
    defaults.update(kwargs)
    row = Exercise(**defaults)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    SessionLocal, engine = _session_factory()
    db = SessionLocal()
    _add_exercise(db, name="TRX Row", muscle_group="back", difficulty="beginner", external_id="trx-row")
    _add_exercise(
        db,
        name="TRX Squat",
        muscle_group="legs",
        difficulty="beginner",
        illustration_slug="squat",
        external_id="trx-squat",
    )
    _add_exercise(
        db,
        name="TRX Pike",
        muscle_group="core",
        difficulty="intermediate",
        illustration_slug="core-crunch",
        external_id="trx-pike",
    )
    _add_exercise(
        db,
        name="Bodyweight Push-up",
        muscle_group="chest",
        difficulty="beginner",
        equipment="bodyweight",
        illustration_slug="press",
        source="wger",
        external_id="57",
    )
    db.close()

    def override_get_db() -> Generator[Session, None, None]:
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(exercises_router)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


def test_list_exercises_returns_all(client: TestClient) -> None:
    response = client.get("/exercises")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 4
    names = {item["name"] for item in payload}
    assert names == {"TRX Row", "TRX Squat", "TRX Pike", "Bodyweight Push-up"}
    row = next(item for item in payload if item["name"] == "TRX Row")
    assert row["muscle_group"] == "back"
    assert row["difficulty"] == "beginner"
    assert row["equipment"] == "suspension trainer"
    assert row["illustration_slug"] == "row"
    assert row["source"] == "curated"
    assert "external_id" not in row


def test_filter_muscle_group(client: TestClient) -> None:
    response = client.get("/exercises", params={"muscle_group": "legs"})
    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["TRX Squat"]


def test_filter_difficulty(client: TestClient) -> None:
    response = client.get("/exercises", params={"difficulty": "intermediate"})
    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["TRX Pike"]


def test_filter_equipment(client: TestClient) -> None:
    response = client.get("/exercises", params={"equipment": "bodyweight"})
    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["Bodyweight Push-up"]


def test_search_by_name_substring(client: TestClient) -> None:
    response = client.get("/exercises", params={"search": "pike"})
    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["TRX Pike"]


def test_combined_filters(client: TestClient) -> None:
    response = client.get(
        "/exercises",
        params={"muscle_group": "back", "difficulty": "beginner", "search": "row"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["TRX Row"]


def test_filters_are_case_insensitive(client: TestClient) -> None:
    response = client.get("/exercises", params={"muscle_group": "BACK"})
    assert response.status_code == 200
    assert [item["name"] for item in response.json()] == ["TRX Row"]


def test_empty_filter_values_are_ignored(client: TestClient) -> None:
    response = client.get("/exercises", params={"muscle_group": "", "search": ""})
    assert response.status_code == 200
    assert len(response.json()) == 4


def test_get_exercise_by_id(client: TestClient) -> None:
    listed = client.get("/exercises").json()
    target = next(item for item in listed if item["name"] == "TRX Squat")
    response = client.get(f"/exercises/{target['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "TRX Squat"
    assert body["illustration_slug"] == "squat"


def test_get_exercise_404(client: TestClient) -> None:
    response = client.get("/exercises/99999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Exercise not found"}


def test_router_todo_mentions_main_registration() -> None:
    source = (BACKEND_ROOT / "app" / "api" / "routes" / "exercises.py").read_text(
        encoding="utf-8"
    )
    assert "TODO: register in app/main.py: app.include_router(exercises_router)" in source
