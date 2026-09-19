"""AI workout generation routes.

# TODO: register in app/main.py: app.include_router(ai_workouts_router)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.routes.workouts import get_db
from app.core.security import get_current_user
from app.schemas.workout import AIWorkoutGenerateRequest, WorkoutPlan
from app.services.ai_workout import AIWorkoutGenerationError, generate_ai_workout

ai_workouts_router = APIRouter(tags=["workouts"])


@ai_workouts_router.post("/workouts/ai-generate", response_model=WorkoutPlan)
def generate_ai_workout_route(
    payload: AIWorkoutGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> WorkoutPlan:
    _ = current_user
    try:
        return generate_ai_workout(payload, db=db)
    except AIWorkoutGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
