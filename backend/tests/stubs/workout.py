"""Stub of Component C's WorkoutPlan matching the published API schema."""

from typing import Literal

from pydantic import BaseModel


class PlannedExercise(BaseModel):
    exercise_id: int
    name: str
    illustration_slug: str
    sets: int
    reps: str
    rest_seconds: int
    notes: str | None = None


class WorkoutPlan(BaseModel):
    title: str
    duration_minutes: int
    difficulty: Literal["beginner", "intermediate", "advanced"]
    source: Literal["random", "ai"]
    exercises: list[PlannedExercise]
