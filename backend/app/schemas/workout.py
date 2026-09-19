from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Difficulty = Literal["beginner", "intermediate", "advanced"]
Source = Literal["random", "ai"]


class WorkoutExercise(BaseModel):
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
    difficulty: Difficulty
    source: Source
    exercises: list[WorkoutExercise] = Field(min_length=1)
