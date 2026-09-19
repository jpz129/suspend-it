from __future__ import annotations

import json
import os
import re
from pathlib import Path

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise

ALLOWED_SLUGS = (
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
)

BODYWEIGHT_EQUIPMENT_IDS = {7}  # wger "none" / bodyweight
BODYWEIGHT_CATEGORY_IDS = {10, 8, 14, 15}  # abs, arms, calves, cardio — used as a loose filter

_SLUG_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("row", ("row", "inverted row")),
    ("press", ("press", "push-up", "push up", "pushup", "dip")),
    ("squat", ("squat", "pistol")),
    ("lunge", ("lunge", "split squat")),
    ("plank", ("plank", "mountain climber")),
    ("twist", ("twist", "rotation", "russian twist", "woodchop", "power pull", "hip drop")),
    ("curl", ("curl", "bicep", "biceps")),
    ("pull", ("pull", "face pull", "y-fly", "t-fly", "rear delt", "lat")),
    ("chest-fly", ("fly", "flye", "chest fly")),
    ("core-crunch", ("crunch", "sit-up", "situp", "pike", "knee tucks")),
    ("hinge", ("deadlift", "hinge", "bridge", "hip press", "hamstring", "good morning")),
    ("jump", ("jump", "plyo", "hop", "burpee")),
    ("stretch", ("stretch", "mobility", "yoga")),
]


def illustration_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "static" / "illustrations"


def seed_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "trx_seed.json"


def wger_api_base() -> str:
    return os.environ.get("WGER_API_BASE", "https://wger.de/api/v2").rstrip("/")


def map_illustration_slug(
    *,
    name: str,
    muscle_group: str = "",
    category: str = "",
    extra: str = "",
) -> str:
    blob = " ".join([name, muscle_group, category, extra]).lower()
    for slug, keywords in _SLUG_KEYWORDS:
        if any(k in blob for k in keywords):
            return slug
    muscle = muscle_group.lower()
    if muscle in {"back"}:
        return "row"
    if muscle in {"chest"}:
        return "press"
    if muscle in {"legs", "glutes"}:
        return "squat"
    if muscle in {"core", "abs"}:
        return "plank"
    if muscle in {"shoulders"}:
        return "pull"
    if muscle in {"arms"}:
        return "curl"
    return "default"


def _slugify(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text or "exercise"


def _english_name(item: dict) -> str | None:
    translations = item.get("translations") or item.get("exerciseinfo", {}).get("translations") or []
    for lang_id in (2, "2"):  # English
        for t in translations:
            if str(t.get("language")) == str(lang_id) and t.get("name"):
                return t["name"]
    if item.get("name"):
        return item["name"]
    for t in translations:
        if t.get("name"):
            return t["name"]
    return None


def _instructions(item: dict) -> str:
    translations = item.get("translations") or []
    for t in translations:
        if str(t.get("language")) == "2" and t.get("description"):
            return re.sub(r"<[^>]+>", "", t["description"]).strip()
    desc = item.get("description")
    if desc:
        return re.sub(r"<[^>]+>", "", str(desc)).strip()
    return "Perform the movement with control."


def _muscle_group(item: dict) -> str:
    muscles = item.get("muscles") or []
    if muscles:
        name = (muscles[0].get("name") or muscles[0].get("name_en") or "").lower()
        mapping = {
            "chest": "chest",
            "pectoralis": "chest",
            "lats": "back",
            "latissimus": "back",
            "trapezius": "back",
            "rhomboid": "back",
            "shoulders": "shoulders",
            "deltoid": "shoulders",
            "biceps": "arms",
            "triceps": "arms",
            "abs": "core",
            "oblique": "core",
            "rectus": "core",
            "quadriceps": "legs",
            "hamstring": "legs",
            "glute": "legs",
            "calves": "legs",
            "gastroc": "legs",
        }
        for key, group in mapping.items():
            if key in name:
                return group
    category = (item.get("category") or {}).get("name", "")
    cat = category.lower()
    if "abs" in cat:
        return "core"
    if "arm" in cat:
        return "arms"
    if "back" in cat:
        return "back"
    if "chest" in cat:
        return "chest"
    if "leg" in cat or "calves" in cat:
        return "legs"
    if "shoulder" in cat:
        return "shoulders"
    return "full body"


def _difficulty(item: dict) -> str:
    name = (_english_name(item) or "").lower()
    if any(w in name for w in ("pistol", "one-arm", "single-leg", "weighted", "explosive")):
        return "advanced"
    if any(w in name for w in ("assisted", "knee", "incline")):
        return "beginner"
    return "beginner"


def _is_bodyweight(item: dict) -> bool:
    equipment = item.get("equipment") or []
    if not equipment:
        return True
    ids = {e.get("id") if isinstance(e, dict) else e for e in equipment}
    names = " ".join(
        (e.get("name") or "") if isinstance(e, dict) else "" for e in equipment
    ).lower()
    if ids & BODYWEIGHT_EQUIPMENT_IDS:
        return True
    if "none" in names or "bodyweight" in names:
        return True
    return False


def fetch_wger_exercises(client: httpx.Client | None = None) -> list[dict]:
    base = wger_api_base()
    url = f"{base}/exerciseinfo/?limit=50"
    own_client = client is None
    client = client or httpx.Client(timeout=30.0)
    collected: list[dict] = []
    try:
        while url:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()
            for item in payload.get("results") or []:
                if _is_bodyweight(item) and _english_name(item):
                    collected.append(item)
            url = payload.get("next")
    finally:
        if own_client:
            client.close()
    return collected


def wger_items_to_records(items: list[dict]) -> list[dict]:
    records = []
    for item in items:
        name = _english_name(item)
        if not name:
            continue
        muscle = _muscle_group(item)
        category = (item.get("category") or {}).get("name", "")
        slug = map_illustration_slug(name=name, muscle_group=muscle, category=category)
        records.append(
            {
                "name": name,
                "muscle_group": muscle,
                "difficulty": _difficulty(item),
                "equipment": "bodyweight",
                "instructions": _instructions(item) or "Perform the movement with control.",
                "illustration_slug": slug,
                "source": "wger",
                "external_id": str(item.get("id") or _slugify(name)),
            }
        )
    return records


def load_seed_records(path: Path | None = None) -> list[dict]:
    data = json.loads((path or seed_path()).read_text())
    records = []
    for row in data:
        slug = row.get("illustration_slug") or map_illustration_slug(
            name=row["name"], muscle_group=row.get("muscle_group", "")
        )
        if slug not in ALLOWED_SLUGS:
            slug = "default"
        records.append(
            {
                "name": row["name"],
                "muscle_group": row["muscle_group"],
                "difficulty": row["difficulty"],
                "equipment": row.get("equipment") or "suspension trainer",
                "instructions": row["instructions"],
                "illustration_slug": slug,
                "source": row.get("source") or "curated",
                "external_id": row.get("external_id") or _slugify(row["name"]),
            }
        )
    return records


def _identity(record: dict) -> tuple[str, str]:
    source = record["source"]
    external_id = record.get("external_id") or record["name"]
    return source, str(external_id)


def upsert_exercises(db: Session, records: list[dict]) -> int:
    written = 0
    for record in records:
        source, external_id = _identity(record)
        existing = db.scalar(
            select(Exercise).where(
                Exercise.source == source,
                Exercise.external_id == external_id,
            )
        )
        if existing is None:
            existing = db.scalar(
                select(Exercise).where(
                    Exercise.source == source,
                    Exercise.name == record["name"],
                )
            )
        slug = record["illustration_slug"] if record["illustration_slug"] in ALLOWED_SLUGS else "default"
        fields = {
            "name": record["name"],
            "muscle_group": record["muscle_group"],
            "difficulty": record["difficulty"],
            "equipment": record["equipment"],
            "instructions": record["instructions"],
            "illustration_slug": slug,
            "source": source,
            "external_id": external_id,
        }
        if existing is None:
            db.add(Exercise(**fields))
        else:
            for key, value in fields.items():
                setattr(existing, key, value)
        written += 1
    db.commit()
    return written


def ingest_all(db: Session, client: httpx.Client | None = None) -> int:
    wger_records = wger_items_to_records(fetch_wger_exercises(client))
    seed_records = load_seed_records()
    return upsert_exercises(db, wger_records + seed_records)
