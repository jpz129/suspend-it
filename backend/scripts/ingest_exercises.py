#!/usr/bin/env python3
"""Ingest wger + curated TRX seed into the exercises table.

Not run on app boot — invoke explicitly:

    cd backend && python scripts/ingest_exercises.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
os.chdir(BACKEND_ROOT)

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.models.exercise import Base  # noqa: E402
from app.services.exercise_ingest import ingest_exercises  # noqa: E402


def main() -> None:
    database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    engine = create_engine(database_url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        stats = ingest_exercises(
            session,
            wger_base_url=os.getenv("WGER_API_BASE"),
        )
        print(
            "Ingest complete: "
            f"inserted={stats['inserted']} "
            f"updated={stats['updated']} "
            f"total={stats['total']}"
        )
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    main()
