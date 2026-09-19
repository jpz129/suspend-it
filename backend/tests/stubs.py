"""Shared A/B interface stubs for Component C tests. Import this first."""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass

from sqlalchemy import Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    muscle_group: Mapped[str] = mapped_column(String(64))
    difficulty: Mapped[str] = mapped_column(String(32))
    equipment: Mapped[str] = mapped_column(String(64))
    instructions: Mapped[str] = mapped_column(Text)
    illustration_slug: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(32))
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)


@dataclass
class User:
    id: int = 1
    email: str = "tester@example.com"


def get_current_user() -> User:
    return User()


import app  # real package (pythonpath includes backend/)

def _ensure(name: str) -> types.ModuleType:
    if name in sys.modules:
        return sys.modules[name]
    mod = types.ModuleType(name)
    mod.__path__ = []  # type: ignore[attr-defined]
    sys.modules[name] = mod
    parent_name, _, child = name.rpartition(".")
    if parent_name:
        setattr(sys.modules[parent_name], child, mod)
    return mod


_ensure("app.core")
_ensure("app.models")
_ensure("app.db")

if "app.core.security" not in sys.modules:
    security = types.ModuleType("app.core.security")
    security.get_current_user = get_current_user
    sys.modules["app.core.security"] = security

if "app.models.exercise" not in sys.modules:
    exercise_mod = types.ModuleType("app.models.exercise")
    exercise_mod.Exercise = Exercise
    sys.modules["app.models.exercise"] = exercise_mod

if "app.db.session" not in sys.modules:
    session_mod = types.ModuleType("app.db.session")

    def _unused_get_db():
        raise RuntimeError("overridden")

    session_mod.get_db = _unused_get_db
    sys.modules["app.db.session"] = session_mod

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


def override_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
