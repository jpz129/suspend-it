"""Ingest idempotency and illustration-slug tests (Component B)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models.exercise import Base, Exercise
from app.services.exercise_ingest import (
    ALLOWED_ILLUSTRATION_SLUGS,
    DEFAULT_SEED_PATH,
    ILLUSTRATIONS_DIR,
    ingest_exercises,
    map_illustration_slug,
)

SEED = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))


def _session() -> tuple[Session, object]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    return SessionLocal(), engine


def _wger_transport() -> httpx.MockTransport:
    page1 = {
        "count": 3,
        "next": "https://wger.de/api/v2/exercise/?limit=100&offset=100",
        "previous": None,
        "results": [
            {
                "id": 101,
                "category": 12,
                "muscles": [12],
                "equipment": [7],
            },
            {
                "id": 102,
                "name": "Barbell Bench Press",
                "description": "Press a barbell off the chest.",
                "category": 11,
                "equipment": [1],
            },
        ],
    }
    page2 = {
        "count": 3,
        "next": None,
        "previous": "https://wger.de/api/v2/exercise/?limit=100",
        "results": [
            {
                "id": 103,
                "name": "Bodyweight Squat",
                "description": "Sit the hips back and stand up.",
                "category": 9,
                "equipment": [],
            },
        ],
    }
    translations_page1 = {
        "count": 2,
        "next": "https://wger.de/api/v2/exercise-translation/?language=2&limit=100&offset=100",
        "previous": None,
        "results": [
            {
                "id": 9001,
                "name": "Inverted Row",
                "exercise": 101,
                "description": "<p>Pull your chest to the bar.</p>",
                "language": 2,
            }
        ],
    }
    translations_page2 = {
        "count": 2,
        "next": None,
        "previous": None,
        "results": [
            {
                "id": 9002,
                "name": "Should not be used",
                "exercise": 102,
                "description": "Barbell only",
                "language": 2,
            }
        ],
    }

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        path = request.url.path.rstrip("/")
        if path.endswith("exercise-translation"):
            if "offset=100" in url:
                return httpx.Response(200, json=translations_page2)
            return httpx.Response(200, json=translations_page1)
        if path.endswith("exercise"):
            if "offset=100" in url:
                return httpx.Response(200, json=page2)
            return httpx.Response(200, json=page1)
        return httpx.Response(404, json={"detail": f"unmocked {request.url}"})

    return httpx.MockTransport(handler)


def test_illustration_svg_files_exist_for_every_slug() -> None:
    for slug in sorted(ALLOWED_ILLUSTRATION_SLUGS):
        path = ILLUSTRATIONS_DIR / f"{slug}.svg"
        assert path.is_file(), f"missing {path}"
        text = path.read_text(encoding="utf-8")
        assert "<svg" in text
        assert 'xmlns="http://www.w3.org/2000/svg"' in text


def test_seed_covers_muscle_groups_and_uses_allowed_slugs() -> None:
    assert 15 <= len(SEED) <= 30
    groups = {item["muscle_group"] for item in SEED}
    assert {"back", "chest", "legs", "shoulders", "arms", "core"} <= groups
    difficulties = {item["difficulty"] for item in SEED}
    assert {"beginner", "intermediate", "advanced"} <= difficulties
    for item in SEED:
        assert item["source"] == "curated"
        assert item["equipment"] == "suspension trainer"
        assert item["illustration_slug"] in ALLOWED_ILLUSTRATION_SLUGS
        assert item["name"]
        assert item["instructions"]
        assert item["external_id"]


def test_map_illustration_slug_keywords_and_fallback() -> None:
    assert map_illustration_slug("TRX Face Pull", muscle_group="back") == "pull"
    assert map_illustration_slug("Inverted Row", muscle_group="back") == "row"
    assert map_illustration_slug("Chest Fly", muscle_group="chest") == "chest-fly"
    assert map_illustration_slug("Bodyweight Squat") == "squat"
    assert map_illustration_slug("Walking Lunge") == "lunge"
    assert map_illustration_slug("Front Plank") == "plank"
    assert map_illustration_slug("Russian Twist") == "twist"
    assert map_illustration_slug("Bicep Curl") == "curl"
    assert map_illustration_slug("Hanging Knee Tuck", muscle_group="core") == "core-crunch"
    assert map_illustration_slug("Romanian Deadlift") == "hinge"
    assert map_illustration_slug("Box Jump") == "jump"
    assert map_illustration_slug("Standing Chest Stretch") == "stretch"
    assert map_illustration_slug("Overhead Press") == "press"
    assert map_illustration_slug("Mystery Move", muscle_group="back") == "row"
    assert map_illustration_slug("Mystery Move", muscle_group="unknown") == "default"


def test_ingest_twice_is_idempotent_with_mocked_wger() -> None:
    session, engine = _session()
    client = httpx.Client(transport=_wger_transport())
    try:
        first = ingest_exercises(
            session,
            wger_base_url="https://wger.de/api/v2",
            client=client,
        )
        second = ingest_exercises(
            session,
            wger_base_url="https://wger.de/api/v2",
            client=client,
        )

        expected_total = len(SEED) + 2  # inverted row + bodyweight squat; barbell skipped
        assert first["total"] == expected_total
        assert second["total"] == expected_total
        assert second["inserted"] == 0
        assert first["inserted"] == expected_total

        rows = list(session.scalars(select(Exercise)).all())
        assert len(rows) == expected_total

        names = {row.name for row in rows}
        assert "TRX Row" in names
        assert "Inverted Row" in names
        assert "Bodyweight Squat" in names
        assert "Barbell Bench Press" not in names

        wger_rows = [row for row in rows if row.source == "wger"]
        assert {row.external_id for row in wger_rows} == {"101", "103"}

        inverted = next(row for row in rows if row.name == "Inverted Row")
        assert inverted.illustration_slug == "row"
        assert inverted.muscle_group == "back"
        assert inverted.equipment == "bodyweight"
        assert "Pull your chest" in inverted.instructions
        assert "<p>" not in inverted.instructions

        squat = next(row for row in rows if row.name == "Bodyweight Squat")
        assert squat.illustration_slug == "squat"
        assert squat.muscle_group == "legs"

        for row in rows:
            assert row.illustration_slug is not None
            assert row.illustration_slug in ALLOWED_ILLUSTRATION_SLUGS
            svg = ILLUSTRATIONS_DIR / f"{row.illustration_slug}.svg"
            assert svg.is_file(), f"{row.name} slug {row.illustration_slug!r} has no SVG"

        count = session.scalar(select(func.count()).select_from(Exercise))
        assert count == expected_total
    finally:
        session.close()
        engine.dispose()
        client.close()


def test_ingest_seed_only_when_wger_disabled() -> None:
    session, engine = _session()
    try:
        stats = ingest_exercises(session, fetch_wger=False)
        assert stats["total"] == len(SEED)
        assert stats["inserted"] == len(SEED)
        sources = set(session.scalars(select(Exercise.source)).all())
        assert sources == {"curated"}
    finally:
        session.close()
        engine.dispose()
