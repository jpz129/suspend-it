from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.services.workout_generator import generate_random_workout

# TODO: register in app/main.py: app.include_router(workouts_router)

workouts_router = APIRouter(prefix="/workouts", tags=["workouts"])


def get_db():
    try:
        from app.db.session import get_db as _get_db

        yield from _get_db()
    except ImportError as exc:  # pragma: no cover - production uses A's session
        raise RuntimeError("app.db.session.get_db is required") from exc


class GenerateRequest(BaseModel):
    duration_minutes: int = Field(ge=5, le=180)
    muscle_groups: list[str] = Field(default_factory=list)
    difficulty: str = "beginner"


@workouts_router.post("/generate")
def generate_workout(
    body: GenerateRequest,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_random_workout(
        db,
        duration_minutes=body.duration_minutes,
        muscle_groups=body.muscle_groups,
        difficulty=body.difficulty,
    )
