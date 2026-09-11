"""create community questions

Revision ID: 7a1d8f4c2e91
Revises: 0e8c4d6ef164
"""

from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


revision: str = "7a1d8f4c2e91"
down_revision: Union[str, Sequence[str], None] = "0e8c4d6ef164"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "community_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("community_id", sa.Integer(), nullable=False),
        sa.Column("question_key", sa.String(length=100), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=30), nullable=False),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "community_id",
            "question_key",
            name="uq_community_questions_community_key",
        ),
    )
    op.create_index(
        op.f("ix_community_questions_id"),
        "community_questions",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_community_questions_community_id"),
        "community_questions",
        ["community_id"],
        unique=False,
    )

    questions = sa.table(
        "community_questions",
        sa.column("community_id", sa.Integer()),
        sa.column("question_key", sa.String()),
        sa.column("prompt", sa.Text()),
        sa.column("question_type", sa.String()),
        sa.column("options", sa.JSON()),
        sa.column("order", sa.Integer()),
        sa.column("is_required", sa.Boolean()),
        sa.column("is_active", sa.Boolean()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    communities = sa.table(
        "communities",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
    )
    if context.is_offline_mode():
        # Seed rows depend on existing community IDs and are applied during
        # online upgrades; offline SQL still validates the schema migration.
        return
    bind = op.get_bind()
    community_rows = bind.execute(
        sa.select(communities.c.id, communities.c.name)
        .where(communities.c.name.in_(["Programming", "Web Development"]))
    ).all()
    now = sa.func.now()

    question_sets = {
        "Programming": [
            (
                "skill_level",
                "What is your current programming level?",
                [
                    {"value": "beginner", "label": "Beginner"},
                    {"value": "intermediate", "label": "Intermediate"},
                    {"value": "advanced", "label": "Advanced"},
                ],
            ),
            (
                "languages_known",
                "Which programming languages do you know?",
                [
                    {"value": "cpp", "label": "C++"},
                    {"value": "python", "label": "Python"},
                    {"value": "java", "label": "Java"},
                    {"value": "javascript", "label": "JavaScript"},
                    {"value": "c", "label": "C"},
                    {"value": "other", "label": "Other"},
                ],
            ),
            (
                "problem_solving_comfort",
                "How comfortable are you with problem solving?",
                [
                    {"value": "new", "label": "New to it"},
                    {"value": "basic", "label": "Basic"},
                    {"value": "comfortable", "label": "Comfortable"},
                    {"value": "advanced", "label": "Advanced"},
                ],
            ),
            (
                "main_goal",
                "What is your main goal?",
                [
                    {"value": "learn", "label": "Learn programming"},
                    {"value": "problem-solving", "label": "Improve problem solving"},
                    {"value": "competitive", "label": "Competitive programming"},
                    {"value": "projects", "label": "Build projects"},
                ],
            ),
            (
                "weekly_time_commitment",
                "How much time can you commit each week?",
                [
                    {"value": "1-3", "label": "1-3 hours"},
                    {"value": "4-7", "label": "4-7 hours"},
                    {"value": "8-12", "label": "8-12 hours"},
                    {"value": "12+", "label": "12+ hours"},
                ],
            ),
        ],
        "Web Development": [
            (
                "skill_level",
                "What is your current web development experience level?",
                [
                    {"value": "beginner", "label": "Beginner"},
                    {"value": "intermediate", "label": "Intermediate"},
                    {"value": "advanced", "label": "Advanced"},
                ],
            ),
            (
                "technologies_known",
                "Which web technologies have you used?",
                [
                    {"value": "html-css", "label": "HTML & CSS"},
                    {"value": "javascript", "label": "JavaScript"},
                    {"value": "react", "label": "React"},
                    {"value": "nodejs", "label": "Node.js"},
                    {"value": "backend", "label": "Backend"},
                    {"value": "database", "label": "Database"},
                ],
            ),
            (
                "main_goal",
                "What is your main web development goal?",
                [
                    {"value": "learn", "label": "Learn the fundamentals"},
                    {"value": "job", "label": "Prepare for a job"},
                    {"value": "projects", "label": "Build projects"},
                    {"value": "collaborate", "label": "Collaborate with others"},
                ],
            ),
            (
                "weekly_time_commitment",
                "How much time can you commit each week?",
                [
                    {"value": "1-2", "label": "1-2 hours"},
                    {"value": "3-5", "label": "3-5 hours"},
                    {"value": "5-10", "label": "5-10 hours"},
                    {"value": "10+", "label": "10+ hours"},
                ],
            ),
        ],
    }

    for community_id, community_name in community_rows:
        for order, (key, prompt, options) in enumerate(
            question_sets[community_name],
            start=1,
        ):
            bind.execute(
                questions.insert().values(
                    community_id=community_id,
                    question_key=key,
                    prompt=prompt,
                    question_type="multi_choice" if key == "languages_known" or key == "technologies_known" else "single_choice",
                    options=options,
                    order=order,
                    is_required=True,
                    is_active=True,
                    created_at=now,
                    updated_at=now,
                )
            )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_community_questions_community_id"),
        table_name="community_questions",
    )
    op.drop_index(
        op.f("ix_community_questions_id"),
        table_name="community_questions",
    )
    op.drop_table("community_questions")
