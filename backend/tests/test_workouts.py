"""Tests for random workout generation (service + POST /workouts/generate)."""

from __future__ import annotations

import random

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tests.stubs.inject import Base, Exercise, get_current_user, inject_dependency_modules

inject_dependency_modules()

from app.api.routes.workouts import get_db, workouts_router  # noqa: E402
from app.core.security import get_current_user as auth_dep  # noqa: E402
from app.services.workout_generator import (  # noqa: E402
    HEURISTICS,
    NoMatchingExercisesError,
    exercise_count_for_duration,
    generate_random_workout,
)


def _engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _session_factory(engine):
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def _add_exercise(session, **kwargs) -> Exercise:
    defaults = {
        "name": "TRX Row",
        "muscle_group": "back",
        "difficulty": "beginner",
        "equipment": "suspension trainer",
        "instructions": "Lean back and pull.",
        "illustration_slug": "row",
        "source": "curated",
        "external_id": None,
    }
    defaults.update(kwargs)
    row = Exercise(**defaults)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def _seed_catalog(session) -> None:
    catalog = [
        ("TRX Row", "back", "beginner", "row"),
        ("TRX Y-Fly", "back", "beginner", "pull"),
        ("TRX Squat", "legs", "beginner", "squat"),
        ("TRX Lunge", "legs", "beginner", "lunge"),
        ("TRX Push-Up", "chest", "beginner", "press"),
        ("TRX Pike", "core", "beginner", "plank"),
        ("TRX Row (int)", "back", "intermediate", "row"),
        ("TRX Pistol Squat", "legs", "intermediate", "squat"),
        ("TRX Atomic Push-Up", "chest", "advanced", "press"),
        ("TRX Burpee", "full-body", "advanced", "jump"),
    ]
    for i, (name, group, difficulty, slug) in enumerate(catalog, start=1):
        session.add(
            Exercise(
                name=name,
                muscle_group=group,
                difficulty=difficulty,
                equipment="suspension trainer",
                instructions=f"Do {name}.",
                illustration_slug=slug,
                source="curated",
                external_id=str(i),
            )
        )
    session.commit()


@pytest.fixture
def db():
    engine = _engine()
    SessionLocal = _session_factory(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def client(db):
    SessionLocal = sessionmaker(bind=db.get_bind())

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(workouts_router)
    app.dependency_overrides[auth_dep] = get_current_user
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_generate_random_workout_beginner_back_and_legs(db):
    _seed_catalog(db)
    plan = generate_random_workout(
        db,
        duration_minutes=30,
        muscle_groups=["back", "legs"],
        difficulty="beginner",
        rng=random.Random(0),
    )
    assert plan.source == "random"
    assert plan.difficulty == "beginner"
    assert plan.duration_minutes == 30
    assert plan.exercises
    expected_count = exercise_count_for_duration(30, "beginner")
    assert len(plan.exercises) == expected_count
    heuristic = HEURISTICS["beginner"]
    for item in plan.exercises:
        assert item.sets == heuristic["sets"]
        assert item.reps == heuristic["reps"]
        assert item.rest_seconds == heuristic["rest_seconds"]
        assert item.illustration_slug
        assert item.notes is None
        # reps is a string per the API contract
        assert isinstance(item.reps, str)
    groups = {db.get(Exercise, item.exercise_id).muscle_group for item in plan.exercises}
    assert groups <= {"back", "legs"}


def test_generate_scales_with_duration_and_difficulty(db):
    _seed_catalog(db)
    short = generate_random_workout(
        db,
        duration_minutes=10,
        muscle_groups=["back", "legs", "chest", "core"],
        difficulty="beginner",
        rng=random.Random(1),
    )
    long = generate_random_workout(
        db,
        duration_minutes=45,
        muscle_groups=["back", "legs", "chest", "core"],
        difficulty="beginner",
        rng=random.Random(1),
    )
    advanced = generate_random_workout(
        db,
        duration_minutes=30,
        muscle_groups=[],
        difficulty="advanced",
        rng=random.Random(1),
    )
    assert len(long.exercises) > len(short.exercises)
    assert advanced.exercises
    assert all(item.sets == HEURISTICS["advanced"]["sets"] for item in advanced.exercises)
    assert all(item.reps == "15" for item in advanced.exercises)


def test_sparse_matches_still_returns_valid_plan(db):
    _add_exercise(db, name="Only Row", muscle_group="back", difficulty="beginner")
    plan = generate_random_workout(
        db,
        duration_minutes=30,
        muscle_groups=["back"],
        difficulty="beginner",
        rng=random.Random(2),
    )
    assert plan.source == "random"
    assert len(plan.exercises) == exercise_count_for_duration(30, "beginner")
    assert all(item.name == "Only Row" for item in plan.exercises)


def test_zero_matches_raises(db):
    _add_exercise(db, muscle_group="back", difficulty="beginner")
    with pytest.raises(NoMatchingExercisesError, match="No exercises found"):
        generate_random_workout(
            db,
            duration_minutes=20,
            muscle_groups=["shoulders"],
            difficulty="advanced",
        )


def test_post_generate_returns_workout_plan(client, db):
    _seed_catalog(db)
    response = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 30,
            "muscle_groups": ["back", "legs"],
            "difficulty": "beginner",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "random"
    assert body["difficulty"] == "beginner"
    assert body["duration_minutes"] == 30
    assert isinstance(body["title"], str) and body["title"]
    assert body["exercises"]
    for item in body["exercises"]:
        assert set(item) >= {
            "exercise_id",
            "name",
            "illustration_slug",
            "sets",
            "reps",
            "rest_seconds",
            "notes",
        }
        assert isinstance(item["reps"], str)


def test_post_generate_varied_filters(client, db):
    _seed_catalog(db)
    chest = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 15,
            "muscle_groups": ["chest"],
            "difficulty": "beginner",
        },
    )
    legs = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 15,
            "muscle_groups": ["legs"],
            "difficulty": "beginner",
        },
    )
    assert chest.status_code == 200
    assert legs.status_code == 200
    chest_names = {item["name"] for item in chest.json()["exercises"]}
    legs_names = {item["name"] for item in legs.json()["exercises"]}
    assert chest_names == {"TRX Push-Up"}
    assert legs_names <= {"TRX Squat", "TRX Lunge"}


def test_post_generate_sparse_matches(client, db):
    _add_exercise(db, name="Solo Pike", muscle_group="core", difficulty="intermediate")
    response = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 25,
            "muscle_groups": ["core"],
            "difficulty": "intermediate",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "random"
    assert all(item["name"] == "Solo Pike" for item in body["exercises"])
    assert all(item["sets"] == HEURISTICS["intermediate"]["sets"] for item in body["exercises"])
    assert all(item["reps"] == "12" for item in body["exercises"])


def test_post_generate_zero_matches_400(client, db):
    _seed_catalog(db)
    response = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 20,
            "muscle_groups": ["neck"],
            "difficulty": "advanced",
        },
    )
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "No exercises found" in response.json()["detail"]


def test_post_generate_requires_auth():
    engine = _engine()
    SessionLocal = _session_factory(engine)

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def unauthorized():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app = FastAPI()
    app.include_router(workouts_router)
    app.dependency_overrides[auth_dep] = unauthorized
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        "/workouts/generate",
        json={
            "duration_minutes": 10,
            "muscle_groups": ["back"],
            "difficulty": "beginner",
        },
    )
    assert response.status_code == 401
    engine.dispose()
