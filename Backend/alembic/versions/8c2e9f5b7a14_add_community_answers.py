"""add normalized community answers

Revision ID: 8c2e9f5b7a14
Revises: 7a1d8f4c2e91
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c2e9f5b7a14"
down_revision: Union[str, Sequence[str], None] = "7a1d8f4c2e91"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "assessment_data",
        "skill_level",
        existing_type=sa.String(length=50),
        nullable=True,
    )
    op.alter_column(
        "assessment_data",
        "languages_known",
        existing_type=sa.String(length=255),
        nullable=True,
    )
    op.alter_column(
        "assessment_data",
        "problem_solving_comfort",
        existing_type=sa.String(length=50),
        nullable=True,
    )
    op.alter_column(
        "assessment_data",
        "main_goal",
        existing_type=sa.String(length=100),
        nullable=True,
    )
    op.alter_column(
        "assessment_data",
        "weekly_time_commitment",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.create_table(
        "community_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("membership_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["membership_id"],
            ["community_memberships.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["community_questions.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "membership_id",
            "question_id",
            name="uq_community_answers_membership_question",
        ),
    )
    op.create_index(
        op.f("ix_community_answers_id"),
        "community_answers",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_answers_membership_id"),
        "community_answers",
        ["membership_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_answers_question_id"),
        "community_answers",
        ["question_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_community_answers_question_id"),
        table_name="community_answers",
    )
    op.drop_index(
        op.f("ix_community_answers_membership_id"),
        table_name="community_answers",
    )
    op.drop_index(
        op.f("ix_community_answers_id"),
        table_name="community_answers",
    )
    op.drop_table("community_answers")

    op.alter_column(
        "assessment_data",
        "weekly_time_commitment",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.alter_column(
        "assessment_data",
        "main_goal",
        existing_type=sa.String(length=100),
        nullable=False,
    )
    op.alter_column(
        "assessment_data",
        "problem_solving_comfort",
        existing_type=sa.String(length=50),
        nullable=False,
    )
    op.alter_column(
        "assessment_data",
        "languages_known",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.alter_column(
        "assessment_data",
        "skill_level",
        existing_type=sa.String(length=50),
        nullable=False,
    )
