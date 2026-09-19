from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, field_serializer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.history import WorkoutHistory
from app.schemas.workout import WorkoutPlan

# TODO: register in app/main.py: app.include_router(history_router)

history_router = APIRouter(prefix="/history", tags=["history"])


def get_db():
    try:
        from app.db.session import get_db as _get_db

        yield from _get_db()
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("app.db.session.get_db is required") from exc


class HistoryCreate(BaseModel):
    workout_plan: WorkoutPlan
    completed_at: datetime
    notes: str | None = None


class HistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_plan: WorkoutPlan
    completed_at: datetime
    notes: str | None
    created_at: datetime

    @field_serializer("completed_at", "created_at")
    def _z(self, value: datetime) -> str:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@history_router.post("", response_model=HistoryOut, status_code=201)
def create_history(
    body: HistoryCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WorkoutHistory:
    row = WorkoutHistory(
        user_id=user.id,
        workout_plan=body.workout_plan.model_dump(),
        completed_at=body.completed_at,
        notes=body.notes,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@history_router.get("", response_model=list[HistoryOut])
def list_history(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkoutHistory]:
    stmt = (
        select(WorkoutHistory)
        .where(WorkoutHistory.user_id == user.id)
        .order_by(WorkoutHistory.completed_at.desc(), WorkoutHistory.id.desc())
    )
    return list(db.scalars(stmt).all())
