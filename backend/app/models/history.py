"""Workout history persistence (Component D).

`user_id` is an integer column with an index only — there is no
database-level foreign key to `users.id`. Component A's users table is
not present on this branch, and standalone tests use `create_all` on
this model's metadata against an empty in-memory SQLite database.
Conceptually each row still belongs to the authenticated user whose
`.id` is stored here.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, JSON, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class HistoryBase(DeclarativeBase):
    """Local declarative base for the history table.

    Component A owns the shared `app.db.session` Base. This model keeps
    its own metadata so tests can `create_all` without A's session
    module. Alembic creates the physical table independently; at
    runtime any engine/session that has `workout_history` can query it.
    """


class WorkoutHistory(HistoryBase):
    __tablename__ = "workout_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    workout_plan: Mapped[dict] = mapped_column(JSON, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
