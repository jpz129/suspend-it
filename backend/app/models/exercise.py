from __future__ import annotations

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


try:
    from app.db.session import Base
except ImportError:  # Component A not present on this branch

    class Base(DeclarativeBase):
        pass


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    equipment: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    illustration_slug: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
