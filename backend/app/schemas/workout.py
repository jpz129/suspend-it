from typing import Literal, Optional

from pydantic import BaseModel, Field

Difficulty = Literal["beginner", "intermediate", "advanced"]
WorkoutSource = Literal["random", "ai"]


class PlannedExercise(BaseModel):
    exercise_id: int
    name: str
    illustration_slug: str
    sets: int
    reps: str
    rest_seconds: int
    notes: Optional[str] = None


class WorkoutPlan(BaseModel):
    title: str
    duration_minutes: int
    difficulty: Difficulty
    source: WorkoutSource
    exercises: list[PlannedExercise]


class WorkoutGenerateRequest(BaseModel):
    duration_minutes: int = Field(..., ge=1)
    muscle_groups: list[str]
    difficulty: Difficulty


class AIWorkoutGenerateRequest(BaseModel):
    goals: str
    available_time_minutes: int = Field(..., ge=1)
    equipment: list[str]
    notes: Optional[str] = None
