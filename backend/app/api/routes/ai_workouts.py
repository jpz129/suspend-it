from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.services.ai_workout import generate_ai_workout

# TODO: register in app/main.py: app.include_router(ai_workouts_router)

ai_workouts_router = APIRouter(prefix="/workouts", tags=["workouts"])


def get_db():
    try:
        from app.db.session import get_db as _get_db

        yield from _get_db()
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("app.db.session.get_db is required") from exc


class AIGenerateRequest(BaseModel):
    goals: str
    available_time_minutes: int = Field(ge=5, le=180)
    equipment: list[str] = Field(default_factory=lambda: ["TRX"])
    notes: str | None = None


@ai_workouts_router.post("/ai-generate")
def ai_generate_workout(
    body: AIGenerateRequest,
    _user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return generate_ai_workout(
        db,
        goals=body.goals,
        available_time_minutes=body.available_time_minutes,
        equipment=body.equipment,
        notes=body.notes,
    )
