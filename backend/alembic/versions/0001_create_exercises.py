"""create exercises table

Revision ID: 0001_exercises
Revises:
Create Date: 2026-09-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_exercises"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("muscle_group", sa.String(length=64), nullable=False),
        sa.Column("difficulty", sa.String(length=32), nullable=False),
        sa.Column("equipment", sa.String(length=64), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("illustration_slug", sa.String(length=64), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exercises_muscle_group", "exercises", ["muscle_group"])
    op.create_index("ix_exercises_difficulty", "exercises", ["difficulty"])
    op.create_index("ix_exercises_equipment", "exercises", ["equipment"])
    op.create_index("ix_exercises_source", "exercises", ["source"])


def downgrade() -> None:
    op.drop_index("ix_exercises_source", table_name="exercises")
    op.drop_index("ix_exercises_equipment", table_name="exercises")
    op.drop_index("ix_exercises_difficulty", table_name="exercises")
    op.drop_index("ix_exercises_muscle_group", table_name="exercises")
    op.drop_table("exercises")
