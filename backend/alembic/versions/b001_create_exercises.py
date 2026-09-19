"""create exercises table

Revision ID: b001_create_exercises
Revises:
Create Date: 2026-09-19
"""

from alembic import op
import sqlalchemy as sa

revision = "b001_create_exercises"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("muscle_group", sa.String(length=50), nullable=False),
        sa.Column("difficulty", sa.String(length=20), nullable=False),
        sa.Column("equipment", sa.String(length=100), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("illustration_slug", sa.String(length=50), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("external_id", sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source", "external_id", name="uq_exercises_source_external_id"),
    )
    op.create_index("ix_exercises_source_name", "exercises", ["source", "name"])
    op.create_index("ix_exercises_muscle_group", "exercises", ["muscle_group"])
    op.create_index("ix_exercises_difficulty", "exercises", ["difficulty"])
    op.create_index("ix_exercises_name", "exercises", ["name"])


def downgrade() -> None:
    op.drop_index("ix_exercises_name", table_name="exercises")
    op.drop_index("ix_exercises_difficulty", table_name="exercises")
    op.drop_index("ix_exercises_muscle_group", table_name="exercises")
    op.drop_index("ix_exercises_source_name", table_name="exercises")
    op.drop_table("exercises")
