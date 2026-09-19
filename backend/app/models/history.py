from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


try:
    from app.db.session import Base
except ImportError:  # Component A not present on this branch

    class Base(DeclarativeBase):
        pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkoutHistory(Base):
    __tablename__ = "workout_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    workout_plan: Mapped[dict] = mapped_column(JSON, nullable=False)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
