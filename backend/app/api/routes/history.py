"""History API routes (Component D).

# TODO: register in app/main.py: app.include_router(history_router)
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.history import WorkoutHistory
from app.schemas.workout import WorkoutPlan

history_router = APIRouter(tags=["history"])


def get_db():
    """Yield a SQLAlchemy session.

    Production delegates to Component A's `app.db.session.get_db`. Tests
    override this dependency with an in-memory SQLite session, so this
    body is not executed in unit tests (A's session module is absent
    on this branch).
    """
    from app.db.session import get_db as _get_db

    yield from _get_db()


class HistoryCreate(BaseModel):
    workout_plan: WorkoutPlan
    completed_at: datetime
    notes: str | None = None


class HistoryEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_plan: WorkoutPlan
    completed_at: datetime
    notes: str | None
    created_at: datetime


def _as_utc(dt: datetime) -> datetime:
    """SQLite may round-trip timezone-aware values as naive; treat those as UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _to_entry(row: WorkoutHistory) -> HistoryEntry:
    return HistoryEntry(
        id=row.id,
        workout_plan=row.workout_plan,
        completed_at=_as_utc(row.completed_at),
        notes=row.notes,
        created_at=_as_utc(row.created_at),
    )


@history_router.post("/history", status_code=201, response_model=HistoryEntry)
def create_history(
    payload: HistoryCreate,
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> HistoryEntry:
    row = WorkoutHistory(
        user_id=current_user.id,
        workout_plan=payload.workout_plan.model_dump(mode="json"),
        completed_at=payload.completed_at,
        notes=payload.notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_entry(row)


@history_router.get("/history", response_model=list[HistoryEntry])
def list_history(
    current_user: Annotated[object, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[HistoryEntry]:
    stmt = (
        select(WorkoutHistory)
        .where(WorkoutHistory.user_id == current_user.id)
        .order_by(WorkoutHistory.created_at.desc(), WorkoutHistory.id.desc())
    )
    rows = db.scalars(stmt).all()
    return [_to_entry(row) for row in rows]
