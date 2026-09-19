"""Test-only stand-ins for Component A (auth) and Component B (Exercise).

Production code still imports `app.core.security.get_current_user` and
`app.models.exercise.Exercise`. This module injects those names into
sys.modules before production modules are imported.
"""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    muscle_group = Column(String(64), nullable=False)
    difficulty = Column(String(32), nullable=False)
    equipment = Column(String(128), nullable=False)
    instructions = Column(Text, nullable=True)
    illustration_slug = Column(String(64), nullable=False)
    source = Column(String(32), nullable=False)
    external_id = Column(String(128), nullable=True)


def get_current_user():
    return SimpleNamespace(id=1, email="tester@example.com", name="Tester")


def inject_dependency_modules() -> None:
    core = sys.modules.get("app.core") or ModuleType("app.core")
    security = sys.modules.get("app.core.security") or ModuleType("app.core.security")
    security.get_current_user = get_current_user
    core.security = security

    models = sys.modules.get("app.models") or ModuleType("app.models")
    exercise_mod = sys.modules.get("app.models.exercise") or ModuleType(
        "app.models.exercise"
    )
    exercise_mod.Exercise = Exercise
    models.exercise = exercise_mod

    sys.modules["app.core"] = core
    sys.modules["app.core.security"] = security
    sys.modules["app.models"] = models
    sys.modules["app.models.exercise"] = exercise_mod
