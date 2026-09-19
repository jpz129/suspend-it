from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise

# TODO: register in app/main.py: app.include_router(exercises_router)

exercises_router = APIRouter(prefix="/exercises", tags=["exercises"])


def get_db():
    """Standalone session factory; integration replaces this with app.db.session.get_db."""
    try:
        from app.db.session import get_db as _get_db

        yield from _get_db()
    except ImportError:
        from app.models.exercise import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import os

        url = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
        kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
        engine = create_engine(url, **kwargs)
        SessionLocal = sessionmaker(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


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


@exercises_router.get("", response_model=list[ExerciseOut])
def list_exercises(
    muscle_group: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    equipment: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[Exercise]:
    stmt = select(Exercise)
    if muscle_group:
        stmt = stmt.where(Exercise.muscle_group == muscle_group)
    if difficulty:
        stmt = stmt.where(Exercise.difficulty == difficulty)
    if equipment:
        stmt = stmt.where(Exercise.equipment == equipment)
    if search:
        stmt = stmt.where(Exercise.name.ilike(f"%{search}%"))
    return list(db.scalars(stmt.order_by(Exercise.id)).all())


@exercises_router.get("/{exercise_id}", response_model=ExerciseOut)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)) -> Exercise:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
