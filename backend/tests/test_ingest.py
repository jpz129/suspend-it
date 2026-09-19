"""Ingest is idempotent and always maps to a real illustration slug."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.models.exercise import Base, Exercise
from app.services.exercise_ingest import ALLOWED_SLUGS, ingest_all, illustration_dir, load_seed_records

os.environ.setdefault("DATABASE_URL", "sqlite://")


WGER_PAGE_1 = {
    "count": 2,
    "next": "https://wger.de/api/v2/exerciseinfo/?limit=50&offset=50",
    "results": [
        {
            "id": 101,
            "category": {"id": 8, "name": "Arms"},
            "equipment": [{"id": 7, "name": "none (bodyweight exercise)"}],
            "muscles": [{"name": "Biceps brachii"}],
            "translations": [
                {
                    "language": 2,
                    "name": "Bodyweight Curl",
                    "description": "<p>Curl the arms.</p>",
                }
            ],
        }
    ],
}

WGER_PAGE_2 = {
    "count": 2,
    "next": None,
    "results": [
        {
            "id": 202,
            "category": {"id": 10, "name": "Abs"},
            "equipment": [],
            "muscles": [{"name": "Rectus abdominis"}],
            "translations": [
                {"language": 2, "name": "Crunch", "description": "Curl the trunk."}
            ],
        }
    ],
}


def _session() -> Session:
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _handler(request: httpx.Request) -> httpx.Response:
    if "offset=50" in str(request.url):
        return httpx.Response(200, json=WGER_PAGE_2)
    return httpx.Response(200, json=WGER_PAGE_1)


def test_ingest_twice_does_not_duplicate() -> None:
    db = _session()
    transport = httpx.MockTransport(_handler)
    with httpx.Client(transport=transport) as client:
        ingest_all(db, client=client)
        first = db.scalar(select(func.count()).select_from(Exercise))
        ingest_all(db, client=client)
        second = db.scalar(select(func.count()).select_from(Exercise))
    assert first == second
    assert first == len(load_seed_records()) + 2


def test_every_row_has_real_illustration_slug() -> None:
    db = _session()
    transport = httpx.MockTransport(_handler)
    with httpx.Client(transport=transport) as client:
        ingest_all(db, client=client)
    rows = list(db.scalars(select(Exercise)))
    assert rows
    illustrations = illustration_dir()
    for row in rows:
        assert row.illustration_slug
        assert row.illustration_slug in ALLOWED_SLUGS
        assert (illustrations / f"{row.illustration_slug}.svg").is_file()


def test_all_placeholder_svgs_exist() -> None:
    illustrations = illustration_dir()
    for slug in ALLOWED_SLUGS:
        path = illustrations / f"{slug}.svg"
        assert path.is_file(), path
        assert "<svg" in path.read_text()
