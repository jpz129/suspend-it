"""Public exercise catalog routes (Component B).

Exercises are listed in the API contract as unauthenticated.

# TODO: register in app/main.py: app.include_router(exercises_router)
"""

from __future__ import annotations

import os
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.exercise import Exercise

try:
    from app.db.session import get_db as get_db  # type: ignore[import-not-found]
except ImportError:

    def get_db() -> Generator[Session, None, None]:
        """Standalone session factory used until Component A ships ``app.db.session``."""
        from sqlalchemy import create_engine

        database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        engine = create_engine(database_url, connect_args=connect_args)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


# TODO: register in app/main.py: app.include_router(exercises_router)
exercises_router = APIRouter(tags=["exercises"])


class ExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    muscle_group: str
    difficulty: str
    equipment: str
    instructions: str
    illustration_slug: str
    source: str


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


@exercises_router.get("/exercises", response_model=list[ExerciseOut])
def list_exercises(
    muscle_group: str | None = Query(None),
    difficulty: str | None = Query(None),
    equipment: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[Exercise]:
    muscle_group = _blank_to_none(muscle_group)
    difficulty = _blank_to_none(difficulty)
    equipment = _blank_to_none(equipment)
    search = _blank_to_none(search)

    stmt = select(Exercise)
    if muscle_group:
        stmt = stmt.where(func.lower(Exercise.muscle_group) == muscle_group.lower())
    if difficulty:
        stmt = stmt.where(func.lower(Exercise.difficulty) == difficulty.lower())
    if equipment:
        stmt = stmt.where(func.lower(Exercise.equipment) == equipment.lower())
    if search:
        stmt = stmt.where(Exercise.name.ilike(f"%{search}%"))
    stmt = stmt.order_by(Exercise.name.asc(), Exercise.id.asc())
    return list(db.scalars(stmt).all())


@exercises_router.get("/exercises/{exercise_id}", response_model=ExerciseOut)
def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
