"""Random workout generator — filters Exercise rows and fills a time budget."""

from __future__ import annotations

import random
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.schemas.workout import Difficulty, PlannedExercise, WorkoutPlan

# seconds of work per set (time under tension / performing reps)
_WORK_SECONDS = {
    "beginner": 30,
    "intermediate": 35,
    "advanced": 40,
}

HEURISTICS: dict[str, dict[str, int | str]] = {
    "beginner": {"sets": 2, "reps": "10", "rest_seconds": 45},
    "intermediate": {"sets": 3, "reps": "12", "rest_seconds": 40},
    "advanced": {"sets": 4, "reps": "15", "rest_seconds": 30},
}


class NoMatchingExercisesError(ValueError):
    """Raised when the catalog has zero rows matching the requested filters."""


def seconds_per_exercise(difficulty: Difficulty) -> int:
    heuristic = HEURISTICS[difficulty]
    sets = int(heuristic["sets"])
    rest = int(heuristic["rest_seconds"])
    work = _WORK_SECONDS[difficulty]
    return sets * (work + rest)


def exercise_count_for_duration(duration_minutes: int, difficulty: Difficulty) -> int:
    per_exercise = seconds_per_exercise(difficulty)
    return max(1, (duration_minutes * 60) // per_exercise)


def generate_random_workout(
    db: Session,
    *,
    duration_minutes: int,
    muscle_groups: Sequence[str],
    difficulty: Difficulty,
    rng: random.Random | None = None,
) -> WorkoutPlan:
    """Build a WorkoutPlan by sampling matching exercises to fill duration_minutes.

    If fewer exercises match than needed, samples with replacement so the
    response is still a valid plan. Zero matches raises NoMatchingExercisesError.
    """
    rng = rng or random.Random()
    matches = _query_exercises(db, muscle_groups, difficulty)
    if not matches:
        groups = ", ".join(muscle_groups) if muscle_groups else "any"
        raise NoMatchingExercisesError(
            f"No exercises found for muscle groups [{groups}] at {difficulty} difficulty"
        )

    count = exercise_count_for_duration(duration_minutes, difficulty)
    picked = _sample_exercises(matches, count, rng)
    heuristic = HEURISTICS[difficulty]
    planned = [
        PlannedExercise(
            exercise_id=ex.id,
            name=ex.name,
            illustration_slug=ex.illustration_slug,
            sets=int(heuristic["sets"]),
            reps=str(heuristic["reps"]),
            rest_seconds=int(heuristic["rest_seconds"]),
            notes=None,
        )
        for ex in picked
    ]
    title = _title(difficulty, muscle_groups)
    return WorkoutPlan(
        title=title,
        duration_minutes=duration_minutes,
        difficulty=difficulty,
        source="random",
        exercises=planned,
    )


def _query_exercises(
    db: Session,
    muscle_groups: Sequence[str],
    difficulty: Difficulty,
) -> list[Exercise]:
    stmt = select(Exercise).where(Exercise.difficulty == difficulty)
    cleaned = [g.strip() for g in muscle_groups if g and g.strip()]
    if cleaned:
        stmt = stmt.where(Exercise.muscle_group.in_(cleaned))
    return list(db.scalars(stmt).all())


def _sample_exercises(
    matches: list[Exercise],
    count: int,
    rng: random.Random,
) -> list[Exercise]:
    if len(matches) >= count:
        return rng.sample(matches, count)
    picked = list(matches)
    rng.shuffle(picked)
    while len(picked) < count:
        picked.append(rng.choice(matches))
    return picked


def _title(difficulty: Difficulty, muscle_groups: Sequence[str]) -> str:
    cleaned = [g.strip() for g in muscle_groups if g and g.strip()]
    if not cleaned:
        focus = "Full Body"
    elif len(cleaned) == 1:
        focus = cleaned[0].replace("-", " ").title()
    else:
        focus = " & ".join(g.replace("-", " ").title() for g in cleaned)
    return f"{difficulty.capitalize()} {focus} Workout"
