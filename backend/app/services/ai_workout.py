"""AI workout generator — LiteLLM → Anthropic, validated WorkoutPlan JSON."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Sequence

import litellm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.schemas.workout import AIWorkoutGenerateRequest, WorkoutPlan

AI_MODEL = os.environ.get("LITELLM_MODEL", "anthropic/claude-sonnet-4-5")

SYSTEM_PROMPT = """You are a TRX/suspension-trainer workout coach.
Return a single JSON object that matches this schema EXACTLY (no markdown, no commentary):

{
  "title": "string",
  "duration_minutes": <integer>,
  "difficulty": "beginner" | "intermediate" | "advanced",
  "source": "ai",
  "exercises": [
    {
      "exercise_id": <integer>,
      "name": "string",
      "illustration_slug": "string",
      "sets": <integer>,
      "reps": "string",
      "rest_seconds": <integer>,
      "notes": "string or null"
    }
  ]
}

Rules:
- "source" MUST be the string "ai".
- "difficulty" MUST be one of: beginner, intermediate, advanced.
- "reps" MUST be a string (e.g. "10"), never a number.
- Prefer exercises from the provided catalog so exercise_id, name, and
  illustration_slug stay consistent. If the catalog is empty, invent a
  reasonable TRX plan and use positive integer exercise_id values.
- illustration_slug must be one of: row, press, squat, lunge, plank, twist,
  curl, pull, chest-fly, core-crunch, hinge, jump, stretch, default.
- Include enough exercises to fill available_time_minutes.
- Output ONLY the JSON object.
"""


class AIWorkoutGenerationError(RuntimeError):
    """Raised when the LLM cannot produce a valid WorkoutPlan after retry."""


def generate_ai_workout(
    request: AIWorkoutGenerateRequest,
    db: Session | None = None,
) -> WorkoutPlan:
    catalog = _exercise_catalog(db) if db is not None else []
    user_prompt = _user_prompt(request, catalog)
    last_error: Exception | None = None
    for attempt in range(2):
        prompt = user_prompt
        if attempt == 1:
            prompt += (
                "\n\nYour previous reply was not valid WorkoutPlan JSON. "
                "Reply with ONLY a valid JSON object matching the schema. "
                'source must be "ai". reps must be a string.'
            )
        try:
            raw = _complete(prompt)
            return parse_workout_plan(raw)
        except Exception as exc:  # parse, validation, or provider error
            last_error = exc
            continue
    raise AIWorkoutGenerationError(
        f"AI workout generation failed after retry: {last_error}"
    )


def parse_workout_plan(raw: str) -> WorkoutPlan:
    data = _extract_json(raw)
    plan = WorkoutPlan.model_validate(data)
    if plan.source != "ai":
        raise ValueError('WorkoutPlan.source must be "ai"')
    if not plan.exercises:
        raise ValueError("WorkoutPlan.exercises must be non-empty")
    return plan


def _complete(user_prompt: str) -> str:
    response = litellm.completion(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        api_key=os.environ.get("ANTHROPIC_API_KEY") or None,
        temperature=0.2,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    if isinstance(content, list):
        # Anthropic-style content blocks
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("text"):
                parts.append(block["text"])
            elif hasattr(block, "text"):
                parts.append(block.text)
        content = "".join(parts)
    if not content or not str(content).strip():
        raise ValueError("LLM returned empty content")
    return str(content)


def _extract_json(raw: str) -> Any:
    text = raw.strip()
    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def _exercise_catalog(db: Session, limit: int = 80) -> list[dict[str, Any]]:
    rows = list(db.scalars(select(Exercise).limit(limit)).all())
    return [
        {
            "id": row.id,
            "name": row.name,
            "muscle_group": row.muscle_group,
            "difficulty": row.difficulty,
            "equipment": row.equipment,
            "illustration_slug": row.illustration_slug,
        }
        for row in rows
    ]


def _user_prompt(
    request: AIWorkoutGenerateRequest,
    catalog: Sequence[dict[str, Any]],
) -> str:
    notes = request.notes or "none"
    equipment = ", ".join(request.equipment) if request.equipment else "TRX / suspension trainer"
    catalog_json = json.dumps(list(catalog), indent=2)
    return (
        f"Goals: {request.goals}\n"
        f"Available time (minutes): {request.available_time_minutes}\n"
        f"Equipment: {equipment}\n"
        f"Notes: {notes}\n"
        f"duration_minutes in the JSON must equal {request.available_time_minutes}.\n"
        f"Exercise catalog:\n{catalog_json}\n"
    )
