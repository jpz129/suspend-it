"""Random workout generation routes.

# TODO: register in app/main.py: app.include_router(workouts_router)
"""

from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.schemas.workout import WorkoutGenerateRequest, WorkoutPlan
from app.services.workout_generator import (
    NoMatchingExercisesError,
    generate_random_workout,
)

workouts_router = APIRouter(tags=["workouts"])


def get_db() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session from Component A's session factory.

    Tests override this dependency; do not call it without a real or stubbed
    `app.db.session.get_db`.
    """
    from app.db.session import get_db as app_get_db

    yield from app_get_db()


@workouts_router.post("/workouts/generate", response_model=WorkoutPlan)
def generate_workout(
    payload: WorkoutGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> WorkoutPlan:
    _ = current_user
    try:
        return generate_random_workout(
            db,
            duration_minutes=payload.duration_minutes,
            muscle_groups=payload.muscle_groups,
            difficulty=payload.difficulty,
        )
    except NoMatchingExercisesError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
