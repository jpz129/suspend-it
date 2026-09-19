#!/usr/bin/env python3
"""Ingest wger + curated TRX seed into the exercises table. Idempotent."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.exercise import Base
from app.services.exercise_ingest import ingest_all


def main() -> None:
    url = os.environ.get("DATABASE_URL", "sqlite:///./app.db")
    kwargs = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    with SessionLocal() as db:
        count = ingest_all(db)
    print(f"upserted {count} exercise records")


if __name__ == "__main__":
    main()
