"""Random workout generation tests."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.stubs import Exercise, SessionLocal, get_current_user, override_db

from app.api.routes.workouts import get_db, workouts_router
from app.core.security import get_current_user as auth_dep
from app.services.workout_generator import generate_random_workout

app = FastAPI()
app.include_router(workouts_router)
app.dependency_overrides[auth_dep] = get_current_user
app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def _seed(n_back: int = 8, n_legs: int = 1) -> None:
    db = SessionLocal()
    db.query(Exercise).delete()
    rows = []
    for i in range(n_back):
        rows.append(
            Exercise(
                name=f"TRX Row {i}",
                muscle_group="back",
                difficulty="beginner",
                equipment="suspension trainer",
                instructions="Row",
                illustration_slug="row",
                source="curated",
                external_id=f"row-{i}",
            )
        )
    for i in range(n_legs):
        rows.append(
            Exercise(
                name=f"TRX Squat {i}",
                muscle_group="legs",
                difficulty="advanced",
                equipment="suspension trainer",
                instructions="Squat",
                illustration_slug="squat",
                source="curated",
                external_id=f"squat-{i}",
            )
        )
    db.add_all(rows)
    db.commit()
    db.close()


def test_generate_beginner_back() -> None:
    _seed()
    res = client.post(
        "/workouts/generate",
        json={"duration_minutes": 30, "muscle_groups": ["back"], "difficulty": "beginner"},
    )
    assert res.status_code == 200, res.text
    plan = res.json()
    assert plan["source"] == "random"
    assert plan["difficulty"] == "beginner"
    assert plan["duration_minutes"] == 30
    assert plan["exercises"]
    for item in plan["exercises"]:
        assert item["sets"] == 2
        assert item["reps"] == "10"
        assert item["rest_seconds"] == 45
        assert isinstance(item["reps"], str)


def test_generate_with_few_matches() -> None:
    _seed(n_back=0, n_legs=1)
    res = client.post(
        "/workouts/generate",
        json={"duration_minutes": 45, "muscle_groups": ["legs"], "difficulty": "advanced"},
    )
    assert res.status_code == 200, res.text
    plan = res.json()
    assert plan["exercises"]
    assert all(ex["name"].startswith("TRX Squat") for ex in plan["exercises"])


def test_generate_zero_exercises_400() -> None:
    db = SessionLocal()
    db.query(Exercise).delete()
    db.commit()
    db.close()
    res = client.post(
        "/workouts/generate",
        json={"duration_minutes": 20, "muscle_groups": ["back"], "difficulty": "beginner"},
    )
    assert res.status_code == 400
    assert "detail" in res.json()


def test_service_direct_sparse_sample() -> None:
    _seed(n_back=0, n_legs=1)
    db = SessionLocal()
    plan = generate_random_workout(
        db, duration_minutes=30, muscle_groups=["legs"], difficulty="beginner"
    )
    db.close()
    assert plan.source == "random"
    assert len(plan.exercises) >= 1
