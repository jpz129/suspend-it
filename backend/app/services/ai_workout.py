from __future__ import annotations

import json
import os
import re

import litellm
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.schemas.workout import WorkoutPlan

SYSTEM_PROMPT = """You are a suspension-trainer (TRX) workout coach.
Return ONLY valid JSON matching this schema exactly (no markdown):
{
  "title": string,
  "duration_minutes": number,
  "difficulty": "beginner" | "intermediate" | "advanced",
  "source": "ai",
  "exercises": [
    {
      "exercise_id": number,
      "name": string,
      "illustration_slug": string,
      "sets": number,
      "reps": string,
      "rest_seconds": number,
      "notes": string | null
    }
  ]
}
Rules:
- source must be "ai"
- reps must be a string
- Only use exercises from the provided catalog; copy exercise_id, name, illustration_slug exactly
- Fill duration_minutes from the requested available time
"""


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    return json.loads(text)


def _catalog_blob(exercises: list[Exercise]) -> str:
    rows = [
        {
            "exercise_id": e.id,
            "name": e.name,
            "illustration_slug": e.illustration_slug,
            "muscle_group": e.muscle_group,
            "difficulty": e.difficulty,
        }
        for e in exercises
    ]
    return json.dumps(rows)


def _complete(user_prompt: str) -> str:
    response = litellm.completion(
        model=os.environ.get("LITELLM_MODEL", "anthropic/claude-sonnet-4-5"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        api_key=os.environ.get("ANTHROPIC_API_KEY") or None,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


def generate_ai_workout(
    db: Session,
    *,
    goals: str,
    available_time_minutes: int,
    equipment: list[str],
    notes: str | None = None,
) -> WorkoutPlan:
    catalog = list(db.scalars(select(Exercise)).all())
    user_prompt = (
        f"Goals: {goals}\n"
        f"Available time minutes: {available_time_minutes}\n"
        f"Equipment: {', '.join(equipment) or 'TRX'}\n"
        f"Notes: {notes or 'none'}\n"
        f"Catalog: {_catalog_blob(catalog)}\n"
    )

    last_error = "LLM returned invalid workout JSON"
    for _attempt in range(2):
        try:
            raw = _complete(user_prompt)
            data = _extract_json(raw)
            data["source"] = "ai"
            data["duration_minutes"] = data.get("duration_minutes", available_time_minutes)
            return WorkoutPlan.model_validate(data)
        except Exception as exc:  # parse / validation
            last_error = str(exc)

    raise HTTPException(status_code=502, detail=f"AI workout failed after retry: {last_error}")
