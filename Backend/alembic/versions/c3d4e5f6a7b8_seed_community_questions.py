"""seed community questions for programming and web development

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
"""

from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if context.is_offline_mode():
        return

    bind = op.get_bind()

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

    prog_rows = bind.execute(
        sa.select(communities.c.id, communities.c.name)
        .where(communities.c.name.ilike("%programming%"))
    ).all()

    web_rows = bind.execute(
        sa.select(communities.c.id, communities.c.name)
        .where(communities.c.name.ilike("%web%"))
    ).all()

    prog_questions = [
        (
            "skill_level",
            "What is your current programming level?",
            "single_choice",
            [
                {"value": "beginner", "label": "Beginner (New to programming)"},
                {"value": "intermediate", "label": "Intermediate (Know syntax, basics)"},
                {"value": "advanced", "label": "Advanced (Comfortable with DSA, projects)"},
            ],
        ),
        (
            "languages_known",
            "Which programming languages do you know?",
            "multi_choice",
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
            "single_choice",
            [
                {"value": "new", "label": "I'm completely new to problem solving"},
                {"value": "basic", "label": "I can solve basic problems"},
                {"value": "comfortable", "label": "I can solve intermediate problems"},
                {"value": "advanced", "label": "I regularly solve challenging problems"},
            ],
        ),
        (
            "main_goal",
            "What is your main goal in this community?",
            "single_choice",
            [
                {"value": "learn", "label": "Learn Programming"},
                {"value": "problem-solving", "label": "Improve Problem Solving"},
                {"value": "competitive", "label": "Competitive Programming"},
                {"value": "projects", "label": "Build Projects"},
            ],
        ),
        (
            "weekly_time_commitment",
            "How much time can you spend learning each week?",
            "single_choice",
            [
                {"value": "1-3", "label": "1–3 hrs per week"},
                {"value": "4-7", "label": "4–7 hrs per week"},
                {"value": "8-12", "label": "8–12 hrs per week"},
                {"value": "12+", "label": "12+ hrs per week"},
            ],
        ),
    ]

    web_questions = [
        (
            "skill_level",
            "What is your current web development experience level?",
            "single_choice",
            [
                {"value": "beginner", "label": "Beginner (New to web development)"},
                {"value": "intermediate", "label": "Intermediate (Built simple websites)"},
                {"value": "advanced", "label": "Advanced (Comfortable with frameworks & backend)"},
            ],
        ),
        (
            "technologies_known",
            "Which web technologies have you used?",
            "multi_choice",
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
            "single_choice",
            [
                {"value": "learn", "label": "Learn Web Development"},
                {"value": "job", "label": "Prepare for a Job"},
                {"value": "projects", "label": "Build Projects"},
                {"value": "collaborate", "label": "Collaborate"},
            ],
        ),
        (
            "weekly_time_commitment",
            "How much time can you spend learning each week?",
            "single_choice",
            [
                {"value": "1-2", "label": "1–2 hrs weekly"},
                {"value": "3-5", "label": "3–5 hrs weekly"},
                {"value": "5-10", "label": "5–10 hrs weekly"},
                {"value": "10+", "label": "10+ hrs weekly"},
            ],
        ),
    ]

    now = sa.func.now()

    for c_id, _ in prog_rows:
        for order, (key, prompt, qtype, options) in enumerate(prog_questions, start=1):
            exists = bind.execute(
                sa.select(questions.c.community_id).where(
                    sa.and_(
                        questions.c.community_id == c_id,
                        questions.c.question_key == key,
                    )
                )
            ).scalar()
            if not exists:
                bind.execute(
                    questions.insert().values(
                        community_id=c_id,
                        question_key=key,
                        prompt=prompt,
                        question_type=qtype,
                        options=options,
                        order=order,
                        is_required=True,
                        is_active=True,
                        created_at=now,
                        updated_at=now,
                    )
                )

    for c_id, _ in web_rows:
        for order, (key, prompt, qtype, options) in enumerate(web_questions, start=1):
            exists = bind.execute(
                sa.select(questions.c.community_id).where(
                    sa.and_(
                        questions.c.community_id == c_id,
                        questions.c.question_key == key,
                    )
                )
            ).scalar()
            if not exists:
                bind.execute(
                    questions.insert().values(
                        community_id=c_id,
                        question_key=key,
                        prompt=prompt,
                        question_type=qtype,
                        options=options,
                        order=order,
                        is_required=True,
                        is_active=True,
                        created_at=now,
                        updated_at=now,
                    )
                )


def downgrade() -> None:
    pass
