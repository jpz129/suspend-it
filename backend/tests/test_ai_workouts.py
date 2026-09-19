"""Tests for AI workout generation (service + POST /workouts/ai-generate)."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from tests.stubs.inject import Base, Exercise, get_current_user, inject_dependency_modules

inject_dependency_modules()

from app.api.routes.ai_workouts import ai_workouts_router  # noqa: E402
from app.api.routes.workouts import get_db  # noqa: E402
from app.core.security import get_current_user as auth_dep  # noqa: E402
from app.schemas.workout import AIWorkoutGenerateRequest, WorkoutPlan  # noqa: E402
from app.services.ai_workout import (  # noqa: E402
    AIWorkoutGenerationError,
    generate_ai_workout,
    parse_workout_plan,
)


VALID_PLAN = {
    "title": "TRX Strength Builder",
    "duration_minutes": 20,
    "difficulty": "intermediate",
    "source": "ai",
    "exercises": [
        {
            "exercise_id": 1,
            "name": "TRX Row",
            "illustration_slug": "row",
            "sets": 3,
            "reps": "12",
            "rest_seconds": 40,
            "notes": "Keep a straight line.",
        },
        {
            "exercise_id": 2,
            "name": "TRX Squat",
            "illustration_slug": "squat",
            "sets": 3,
            "reps": "10",
            "rest_seconds": 40,
            "notes": None,
        },
    ],
}


def _llm_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
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


@pytest.fixture
def db():
    engine = _engine()
    SessionLocal = _session_factory(engine)
    session = SessionLocal()
    session.add(
        Exercise(
            name="TRX Row",
            muscle_group="back",
            difficulty="beginner",
            equipment="suspension trainer",
            instructions="Pull.",
            illustration_slug="row",
            source="curated",
            external_id="1",
        )
    )
    session.commit()
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
    app.include_router(ai_workouts_router)
    app.dependency_overrides[auth_dep] = get_current_user
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _request(**kwargs) -> AIWorkoutGenerateRequest:
    payload = {
        "goals": "build pulling strength",
        "available_time_minutes": 20,
        "equipment": ["TRX"],
        "notes": None,
    }
    payload.update(kwargs)
    return AIWorkoutGenerateRequest(**payload)


def test_parse_workout_plan_accepts_fenced_json():
    raw = "Here you go:\n```json\n" + json.dumps(VALID_PLAN) + "\n```"
    plan = parse_workout_plan(raw)
    assert plan.source == "ai"
    assert plan.exercises[0].reps == "12"


def test_parse_rejects_wrong_source():
    bad = dict(VALID_PLAN, source="random")
    with pytest.raises(ValueError, match='source must be "ai"'):
        parse_workout_plan(json.dumps(bad))


def test_generate_ai_workout_success_path(db):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.return_value = _llm_response(json.dumps(VALID_PLAN))
        plan = generate_ai_workout(_request(), db=db)
    assert isinstance(plan, WorkoutPlan)
    assert plan.source == "ai"
    assert plan.title == "TRX Strength Builder"
    assert len(plan.exercises) == 2
    assert mock_completion.call_count == 1
    _, kwargs = mock_completion.call_args
    assert kwargs["model"].startswith("anthropic/")
    assert kwargs["messages"][0]["role"] == "system"


def test_generate_ai_workout_retries_after_invalid_json(db):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.side_effect = [
            _llm_response("sorry, not json"),
            _llm_response(json.dumps(VALID_PLAN)),
        ]
        plan = generate_ai_workout(_request(), db=db)
    assert plan.source == "ai"
    assert plan.duration_minutes == 20
    assert mock_completion.call_count == 2


def test_generate_ai_workout_double_failure_raises(db):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.side_effect = [
            _llm_response("{not json"),
            _llm_response(json.dumps({"title": "nope"})),
        ]
        with pytest.raises(AIWorkoutGenerationError, match="failed after retry"):
            generate_ai_workout(_request(), db=db)
    assert mock_completion.call_count == 2


def test_post_ai_generate_success(client):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.return_value = _llm_response(json.dumps(VALID_PLAN))
        response = client.post(
            "/workouts/ai-generate",
            json={
                "goals": "build pulling strength",
                "available_time_minutes": 20,
                "equipment": ["TRX"],
                "notes": None,
            },
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["source"] == "ai"
    assert body["difficulty"] == "intermediate"
    assert isinstance(body["exercises"][0]["reps"], str)
    assert mock_completion.call_count == 1


def test_post_ai_generate_invalid_then_retry_success(client):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.side_effect = [
            _llm_response("definitely not json"),
            _llm_response(json.dumps(VALID_PLAN)),
        ]
        response = client.post(
            "/workouts/ai-generate",
            json={
                "goals": "core stability",
                "available_time_minutes": 20,
                "equipment": ["TRX"],
                "notes": "no jumping",
            },
        )
    assert response.status_code == 200, response.text
    assert response.json()["source"] == "ai"
    assert mock_completion.call_count == 2


def test_post_ai_generate_double_failure_502(client):
    with patch("app.services.ai_workout.litellm.completion") as mock_completion:
        mock_completion.side_effect = [
            _llm_response("nope"),
            _llm_response("still nope"),
        ]
        response = client.post(
            "/workouts/ai-generate",
            json={
                "goals": "endurance",
                "available_time_minutes": 15,
                "equipment": ["TRX"],
            },
        )
    assert response.status_code == 502
    assert "detail" in response.json()
    assert "failed after retry" in response.json()["detail"]
    assert mock_completion.call_count == 2


def test_post_ai_generate_requires_auth():
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
    app.include_router(ai_workouts_router)
    app.dependency_overrides[auth_dep] = unauthorized
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    response = client.post(
        "/workouts/ai-generate",
        json={
            "goals": "strength",
            "available_time_minutes": 20,
            "equipment": ["TRX"],
        },
    )
    assert response.status_code == 401
    engine.dispose()
