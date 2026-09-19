"""Exercise list/detail API filters."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.exercises import exercises_router, get_db
from app.models.exercise import Base, Exercise

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def _override_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
app.include_router(exercises_router)
app.dependency_overrides[get_db] = _override_db
client = TestClient(app)


def setup_module() -> None:
    db = TestingSession()
    db.add_all(
        [
            Exercise(
                name="TRX Row",
                muscle_group="back",
                difficulty="beginner",
                equipment="suspension trainer",
                instructions="Row.",
                illustration_slug="row",
                source="curated",
                external_id="trx-row",
            ),
            Exercise(
                name="TRX Squat",
                muscle_group="legs",
                difficulty="beginner",
                equipment="suspension trainer",
                instructions="Squat.",
                illustration_slug="squat",
                source="curated",
                external_id="trx-squat",
            ),
            Exercise(
                name="Push-Up",
                muscle_group="chest",
                difficulty="intermediate",
                equipment="bodyweight",
                instructions="Press.",
                illustration_slug="press",
                source="wger",
                external_id="1",
            ),
        ]
    )
    db.commit()
    db.close()


def test_list_all() -> None:
    res = client.get("/exercises")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_filter_muscle_group() -> None:
    res = client.get("/exercises", params={"muscle_group": "back"})
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["name"] == "TRX Row"
    assert data[0]["illustration_slug"] == "row"


def test_search() -> None:
    res = client.get("/exercises", params={"search": "squat"})
    assert res.status_code == 200
    assert res.json()[0]["name"] == "TRX Squat"


def test_get_by_id_and_404() -> None:
    ok = client.get("/exercises/1")
    assert ok.status_code == 200
    missing = client.get("/exercises/999")
    assert missing.status_code == 404
    assert "detail" in missing.json()
