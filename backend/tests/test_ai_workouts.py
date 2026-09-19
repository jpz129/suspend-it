"""AI workout generation: success, retry, and double-failure."""

import json
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.stubs import Exercise, SessionLocal, get_current_user, override_db

from app.api.routes.ai_workouts import ai_workouts_router, get_db
from app.core.security import get_current_user as auth_dep

app = FastAPI()
app.include_router(ai_workouts_router)
app.dependency_overrides[auth_dep] = get_current_user
app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def _seed() -> None:
    db = SessionLocal()
    if db.query(Exercise).count() == 0:
        db.add(
            Exercise(
                name="TRX Row",
                muscle_group="back",
                difficulty="beginner",
                equipment="suspension trainer",
                instructions="Row",
                illustration_slug="row",
                source="curated",
                external_id="trx-row",
            )
        )
        db.commit()
    db.close()


VALID_PLAN = {
    "title": "AI pull session",
    "duration_minutes": 20,
    "difficulty": "beginner",
    "source": "ai",
    "exercises": [
        {
            "exercise_id": 1,
            "name": "TRX Row",
            "illustration_slug": "row",
            "sets": 3,
            "reps": "10",
            "rest_seconds": 45,
            "notes": "Keep ribs down",
        }
    ],
}


def _llm(content: str) -> MagicMock:
    msg = MagicMock()
    msg.choices = [MagicMock(message=MagicMock(content=content))]
    return msg


def test_ai_generate_success() -> None:
    _seed()
    with patch("app.services.ai_workout.litellm.completion", return_value=_llm(json.dumps(VALID_PLAN))):
        res = client.post(
            "/workouts/ai-generate",
            json={
                "goals": "build a stronger back",
                "available_time_minutes": 20,
                "equipment": ["TRX"],
                "notes": None,
            },
        )
    assert res.status_code == 200, res.text
    assert res.json()["source"] == "ai"
    assert res.json()["exercises"][0]["reps"] == "10"


def test_ai_generate_retries_once_then_succeeds() -> None:
    _seed()
    with patch(
        "app.services.ai_workout.litellm.completion",
        side_effect=[_llm("not-json"), _llm(json.dumps(VALID_PLAN))],
    ) as mocked:
        res = client.post(
            "/workouts/ai-generate",
            json={"goals": "strength", "available_time_minutes": 20, "equipment": ["TRX"]},
        )
    assert res.status_code == 200, res.text
    assert mocked.call_count == 2


def test_ai_generate_fails_after_retry() -> None:
    _seed()
    with patch("app.services.ai_workout.litellm.completion", return_value=_llm("{bad")):
        res = client.post(
            "/workouts/ai-generate",
            json={"goals": "strength", "available_time_minutes": 20, "equipment": ["TRX"]},
        )
    assert res.status_code == 502
    assert "detail" in res.json()
