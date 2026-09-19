from __future__ import annotations

import math
import random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.schemas.workout import WorkoutPlan

HEURISTICS = {
    "beginner": {"sets": 2, "reps": "10", "rest_seconds": 45, "work_seconds": 30},
    "intermediate": {"sets": 3, "reps": "12", "rest_seconds": 40, "work_seconds": 35},
    "advanced": {"sets": 4, "reps": "15", "rest_seconds": 30, "work_seconds": 40},
}


def _slot_minutes(difficulty: str) -> float:
    h = HEURISTICS[difficulty]
    seconds = h["sets"] * (h["work_seconds"] + h["rest_seconds"])
    return max(seconds / 60.0, 2.0)


def generate_random_workout(
    db: Session,
    *,
    duration_minutes: int,
    muscle_groups: list[str],
    difficulty: str,
    rng: random.Random | None = None,
) -> WorkoutPlan:
    rng = rng or random.Random()
    stmt = select(Exercise)
    if muscle_groups:
        stmt = stmt.where(Exercise.muscle_group.in_(muscle_groups))
    if difficulty:
        stmt = stmt.where(Exercise.difficulty == difficulty)
    matches = list(db.scalars(stmt).all())
    if not matches and difficulty:
        stmt = select(Exercise)
        if muscle_groups:
            stmt = stmt.where(Exercise.muscle_group.in_(muscle_groups))
        matches = list(db.scalars(stmt).all())
    if not matches:
        matches = list(db.scalars(select(Exercise)).all())
    if not matches:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="No exercises available to build a workout")

    needed = max(1, math.ceil(duration_minutes / _slot_minutes(difficulty)))
    picked: list[Exercise] = []
    pool = matches[:]
    rng.shuffle(pool)
    while len(picked) < needed:
        if not pool:
            pool = matches[:]
            rng.shuffle(pool)
        picked.append(pool.pop())

    h = HEURISTICS[difficulty]
    groups = ", ".join(muscle_groups) if muscle_groups else "full body"
    return WorkoutPlan(
        title=f"{difficulty.title()} {groups} draw",
        duration_minutes=duration_minutes,
        difficulty=difficulty,  # type: ignore[arg-type]
        source="random",
        exercises=[
            {
                "exercise_id": ex.id,
                "name": ex.name,
                "illustration_slug": ex.illustration_slug,
                "sets": h["sets"],
                "reps": h["reps"],
                "rest_seconds": h["rest_seconds"],
                "notes": None,
            }
            for ex in picked
        ],
    )
