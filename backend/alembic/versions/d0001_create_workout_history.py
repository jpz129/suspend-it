"""create workout history

Revision ID: d0001
Revises:
Create Date: 2026-09-19

History table only (Component D). `user_id` is an indexed integer with
no database-level FK so this revision can apply before Component A's
`users` table exists. Integrators should set `down_revision` to A's
head revision once both components are merged.

"""

from alembic import op
import sqlalchemy as sa


revision = "d0001"
down_revision = "b001_create_exercises"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workout_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("workout_plan", sa.JSON(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_workout_history_user_id", "workout_history", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_workout_history_user_id", table_name="workout_history")
    op.drop_table("workout_history")
