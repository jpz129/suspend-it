"""Ingest wger bodyweight exercises plus the curated TRX seed.

Idempotent upsert key: ``(source, external_id)`` when ``external_id`` is
present, otherwise ``(source, name)``. Illustration slugs are chosen from
the fixed Component B list (never invented).
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise

ALLOWED_ILLUSTRATION_SLUGS: frozenset[str] = frozenset(
    {
        "row",
        "press",
        "squat",
        "lunge",
        "plank",
        "twist",
        "curl",
        "pull",
        "chest-fly",
        "core-crunch",
        "hinge",
        "jump",
        "stretch",
        "default",
    }
)

DEFAULT_WGER_API_BASE = "https://wger.de/api/v2"
BODYWEIGHT_EQUIPMENT_ID = 7
ENGLISH_LANGUAGE_ID = 2

# wger category id -> our muscle_group values
CATEGORY_ID_TO_MUSCLE: dict[int, str] = {
    10: "core",  # Abs
    8: "arms",
    12: "back",
    14: "legs",  # Calves
    15: "core",  # Cardio
    11: "chest",
    9: "legs",
    13: "shoulders",
}

CATEGORY_NAME_TO_MUSCLE: dict[str, str] = {
    "abs": "core",
    "abdominals": "core",
    "arms": "arms",
    "back": "back",
    "calves": "legs",
    "cardio": "core",
    "chest": "chest",
    "legs": "legs",
    "shoulders": "shoulders",
    "core": "core",
}

MUSCLE_GROUP_FALLBACK_SLUG: dict[str, str] = {
    "back": "row",
    "chest": "press",
    "legs": "squat",
    "shoulders": "press",
    "arms": "curl",
    "core": "plank",
}

# More specific phrases first. Each tuple is (needles, slug).
_NAME_SLUG_KEYWORDS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("face pull", "face-pull"), "pull"),
    (("chest fly", "chest-fly", "pec fly", "flye"), "chest-fly"),
    (("mountain climber",), "plank"),
    (("pull-up", "pullup", "pull up", "chin-up", "chinup", "pulldown", "lat pull"), "pull"),
    (("push-up", "pushup", "push up", "press", "dip"), "press"),
    (("row", "inverted row"), "row"),
    (("squat",), "squat"),
    (("lunge",), "lunge"),
    (("plank",), "plank"),
    (("twist", "russian twist", "woodchop", "oblique", "rotation", "rotational"), "twist"),
    (("curl", "bicep"), "curl"),
    (("crunch", "sit-up", "situp", "sit up", "pike", "knee tuck", "leg raise"), "core-crunch"),
    (("deadlift", "hinge", "good morning", "hip raise", "hip thrust", "hamstring"), "hinge"),
    (("jump", "hop", "plyo", "burpee"), "jump"),
    (("stretch", "mobility"), "stretch"),
    (("pull",), "pull"),
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")

_BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SEED_PATH = Path(__file__).resolve().parent.parent / "data" / "trx_seed.json"
ILLUSTRATIONS_DIR = _BACKEND_ROOT / "static" / "illustrations"

_ADVANCED_NAME_HINTS = (
    "pistol",
    "one-arm",
    "one arm",
    "single-arm",
    "single arm",
    "archer",
    "muscle-up",
    "planche",
    "handstand",
    "dragon",
    "weighted",
    "explosive",
)
_BEGINNER_NAME_HINTS = (
    "beginner",
    "assisted",
    "knee",
    "wall",
    "incline",
    "negative",
)


def strip_html(text: str) -> str:
    cleaned = _HTML_TAG_RE.sub(" ", text or "")
    return _WS_RE.sub(" ", cleaned).strip()


def map_illustration_slug(
    name: str,
    muscle_group: str | None = None,
    category: str | None = None,
) -> str:
    """Map an exercise to the closest allowed illustration slug."""
    haystack = f"{name} {muscle_group or ''} {category or ''}".lower()
    for needles, slug in _NAME_SLUG_KEYWORDS:
        if any(needle in haystack for needle in needles):
            return slug if slug in ALLOWED_ILLUSTRATION_SLUGS else "default"
    fallback = MUSCLE_GROUP_FALLBACK_SLUG.get((muscle_group or "").lower())
    if fallback in ALLOWED_ILLUSTRATION_SLUGS:
        return fallback
    return "default"


def _coerce_external_id(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _is_bodyweight(raw: dict[str, Any]) -> bool:
    equipment = raw.get("equipment")
    if equipment is None:
        return False
    if equipment == []:
        return True
    if not isinstance(equipment, list):
        equipment = [equipment]
    for item in equipment:
        if item == BODYWEIGHT_EQUIPMENT_ID:
            return True
        if isinstance(item, dict) and item.get("id") == BODYWEIGHT_EQUIPMENT_ID:
            return True
        if isinstance(item, str) and "bodyweight" in item.lower():
            return True
        if isinstance(item, str) and item.lower() in {"none", "no equipment"}:
            return True
    return False


def _muscle_group_from_wger(raw: dict[str, Any]) -> str:
    category = raw.get("category")
    cat_id: int | None = None
    cat_name = ""
    if isinstance(category, dict):
        cat_id = category.get("id") if isinstance(category.get("id"), int) else None
        cat_name = str(category.get("name") or "").lower()
    elif isinstance(category, int):
        cat_id = category
    if cat_id in CATEGORY_ID_TO_MUSCLE:
        return CATEGORY_ID_TO_MUSCLE[cat_id]
    if cat_name in CATEGORY_NAME_TO_MUSCLE:
        return CATEGORY_NAME_TO_MUSCLE[cat_name]
    return "core"


def _difficulty_from_name(name: str) -> str:
    lowered = name.lower()
    if any(hint in lowered for hint in _ADVANCED_NAME_HINTS):
        return "advanced"
    if any(hint in lowered for hint in _BEGINNER_NAME_HINTS):
        return "beginner"
    return "intermediate"


def _english_name_and_instructions(
    raw: dict[str, Any],
    translations_by_exercise_id: dict[int, dict[str, Any]],
) -> tuple[str | None, str]:
    if raw.get("name"):
        return str(raw["name"]), strip_html(
            str(raw.get("description") or raw.get("instructions") or "")
        )
    for translation in raw.get("translations") or []:
        language = translation.get("language")
        if language in (ENGLISH_LANGUAGE_ID, str(ENGLISH_LANGUAGE_ID), "en"):
            name = translation.get("name")
            if name:
                return str(name), strip_html(str(translation.get("description") or ""))
    exercise_id = raw.get("id")
    if isinstance(exercise_id, int) and exercise_id in translations_by_exercise_id:
        translation = translations_by_exercise_id[exercise_id]
        name = translation.get("name")
        if name:
            return str(name), strip_html(str(translation.get("description") or ""))
    return None, ""


def fetch_paginated(
    client: httpx.Client,
    url: str,
    params: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Follow wger ``next`` links until exhausted."""
    items: list[dict[str, Any]] = []
    next_url: str | None = url
    next_params = params
    while next_url:
        response = client.get(next_url, params=next_params, timeout=30.0)
        response.raise_for_status()
        payload = response.json()
        results = payload.get("results")
        if isinstance(results, list):
            items.extend(item for item in results if isinstance(item, dict))
        next_url = payload.get("next")
        next_params = None
    return items


def fetch_wger_exercises(
    client: httpx.Client,
    base_url: str,
) -> list[dict[str, Any]]:
    """Paginate ``/exercise/`` and keep bodyweight / no-equipment rows."""
    base = base_url.rstrip("/")
    raw_exercises = fetch_paginated(
        client,
        f"{base}/exercise/",
        params={"limit": 100},
    )
    return [item for item in raw_exercises if _is_bodyweight(item)]


def fetch_wger_translations(
    client: httpx.Client,
    base_url: str,
) -> dict[int, dict[str, Any]]:
    """English name/description keyed by wger exercise id.

    Current wger ``/exercise/`` payloads omit name/description; those live
    on ``/exercise-translation/``.
    """
    base = base_url.rstrip("/")
    rows = fetch_paginated(
        client,
        f"{base}/exercise-translation/",
        params={"language": ENGLISH_LANGUAGE_ID, "limit": 100},
    )
    by_id: dict[int, dict[str, Any]] = {}
    for row in rows:
        exercise_id = row.get("exercise")
        if isinstance(exercise_id, int) and exercise_id not in by_id:
            by_id[exercise_id] = row
    return by_id


def load_seed(path: Path | None = None) -> list[dict[str, Any]]:
    seed_path = path or DEFAULT_SEED_PATH
    with seed_path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError(f"Seed file {seed_path} must be a JSON array")
    return [item for item in payload if isinstance(item, dict)]


def _normalize_seed_row(raw: dict[str, Any]) -> dict[str, Any] | None:
    name = str(raw.get("name") or "").strip()
    if not name:
        return None
    slug = str(raw.get("illustration_slug") or "default").strip()
    if slug not in ALLOWED_ILLUSTRATION_SLUGS:
        slug = "default"
    return {
        "name": name,
        "muscle_group": str(raw.get("muscle_group") or "core").strip().lower(),
        "difficulty": str(raw.get("difficulty") or "intermediate").strip().lower(),
        "equipment": str(raw.get("equipment") or "suspension trainer").strip(),
        "instructions": str(raw.get("instructions") or "").strip(),
        "illustration_slug": slug,
        "source": str(raw.get("source") or "curated").strip() or "curated",
        "external_id": _coerce_external_id(raw.get("external_id")),
    }


def _normalize_wger_row(
    raw: dict[str, Any],
    translations_by_exercise_id: dict[int, dict[str, Any]],
) -> dict[str, Any] | None:
    name, instructions = _english_name_and_instructions(raw, translations_by_exercise_id)
    if not name:
        return None
    muscle_group = _muscle_group_from_wger(raw)
    category_name = ""
    category = raw.get("category")
    if isinstance(category, dict):
        category_name = str(category.get("name") or "")
    slug = map_illustration_slug(name, muscle_group=muscle_group, category=category_name)
    external_id = raw.get("id")
    return {
        "name": name,
        "muscle_group": muscle_group,
        "difficulty": _difficulty_from_name(name),
        "equipment": "bodyweight",
        "instructions": instructions or name,
        "illustration_slug": slug,
        "source": "wger",
        "external_id": _coerce_external_id(external_id),
    }


def _find_existing(
    session: Session,
    *,
    source: str,
    external_id: str | None,
    name: str,
) -> Exercise | None:
    if external_id:
        found = session.scalar(
            select(Exercise).where(
                Exercise.source == source,
                Exercise.external_id == external_id,
            )
        )
        if found is not None:
            return found
    return session.scalar(
        select(Exercise).where(
            Exercise.source == source,
            Exercise.name == name,
        )
    )


def upsert_exercise(session: Session, data: dict[str, Any]) -> str:
    """Insert or update one exercise. Returns ``inserted`` or ``updated``."""
    slug = data.get("illustration_slug") or "default"
    if slug not in ALLOWED_ILLUSTRATION_SLUGS:
        slug = "default"
    data = {**data, "illustration_slug": slug}

    existing = _find_existing(
        session,
        source=data["source"],
        external_id=data.get("external_id"),
        name=data["name"],
    )
    fields = (
        "name",
        "muscle_group",
        "difficulty",
        "equipment",
        "instructions",
        "illustration_slug",
        "source",
        "external_id",
    )
    if existing is None:
        session.add(Exercise(**{field: data.get(field) for field in fields}))
        return "inserted"
    for field in fields:
        setattr(existing, field, data.get(field))
    return "updated"


def ingest_exercises(
    session: Session,
    *,
    wger_base_url: str | None = None,
    seed_path: Path | None = None,
    client: httpx.Client | None = None,
    fetch_wger: bool = True,
) -> dict[str, int]:
    """Merge curated seed + wger bodyweight exercises. Idempotent."""
    inserted = 0
    updated = 0

    for raw in load_seed(seed_path):
        row = _normalize_seed_row(raw)
        if row is None:
            continue
        action = upsert_exercise(session, row)
        if action == "inserted":
            inserted += 1
        else:
            updated += 1

    if fetch_wger:
        base = (wger_base_url or os.getenv("WGER_API_BASE") or DEFAULT_WGER_API_BASE).rstrip(
            "/"
        )
        owns_client = client is None
        http_client = client or httpx.Client(timeout=30.0, follow_redirects=True)
        try:
            wger_rows = fetch_wger_exercises(http_client, base)
            needs_translations = any(not row.get("name") for row in wger_rows)
            translations = (
                fetch_wger_translations(http_client, base) if needs_translations else {}
            )
            for raw in wger_rows:
                row = _normalize_wger_row(raw, translations)
                if row is None:
                    continue
                action = upsert_exercise(session, row)
                if action == "inserted":
                    inserted += 1
                else:
                    updated += 1
        finally:
            if owns_client:
                http_client.close()

    session.commit()
    total = int(session.scalar(select(func.count()).select_from(Exercise)) or 0)
    return {"inserted": inserted, "updated": updated, "total": total}
