"""Initial schema

Revision ID: 20260415_0001
Revises:
Create Date: 2026-04-15 16:05:00
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260415_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


lesson_status = sa.Enum("planned", "completed", "cancelled", name="lesson_status")


def upgrade() -> None:
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("default_rate", sa.Float(), nullable=False),
    )

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("name", name="uq_subjects_name"),
    )

    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("rate", sa.Float(), nullable=False),
        sa.Column("prepayment_amount", sa.Float(), nullable=False, server_default="0"),
        sa.Column("status", lesson_status, nullable=False, server_default="planned"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            name="fk_lessons_student_id_students",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["subject_id"],
            ["subjects.id"],
            name="fk_lessons_subject_id_subjects",
            ondelete="RESTRICT",
        ),
    )

    op.create_index("ix_lessons_date", "lessons", ["date"])
    op.create_index("ix_lessons_student_id", "lessons", ["student_id"])
    op.create_index("ix_lessons_status", "lessons", ["status"])


def downgrade() -> None:
    op.drop_index("ix_lessons_status", table_name="lessons")
    op.drop_index("ix_lessons_student_id", table_name="lessons")
    op.drop_index("ix_lessons_date", table_name="lessons")
    op.drop_table("lessons")
    op.drop_table("subjects")
    op.drop_table("students")
    lesson_status.drop(op.get_bind(), checkfirst=False)
