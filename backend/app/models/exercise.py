"""Exercise SQLAlchemy model (Component B).

Fixed interface for Component C: import ``Exercise`` from
``app.models.exercise``. Columns: id, name, muscle_group, difficulty,
equipment, instructions, illustration_slug, source, external_id.
"""

from __future__ import annotations

from sqlalchemy import Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Local metadata registry so Component B tests can ``create_all``

    without Component A's shared ``app.db.session`` Base.
    """


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(50), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    equipment: Mapped[str] = mapped_column(String(100), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    illustration_slug: Mapped[str] = mapped_column(String(50), nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_exercises_source_external_id",
        ),
        Index("ix_exercises_source_name", "source", "name"),
        Index("ix_exercises_muscle_group", "muscle_group"),
        Index("ix_exercises_difficulty", "difficulty"),
        Index("ix_exercises_name", "name"),
    )

    def __repr__(self) -> str:
        return (
            f"<Exercise id={self.id!r} name={self.name!r} "
            f"source={self.source!r} slug={self.illustration_slug!r}>"
        )
