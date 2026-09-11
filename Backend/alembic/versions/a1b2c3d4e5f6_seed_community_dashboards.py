"""seed community-specific roadmap and resources

Revision ID: a1b2c3d4e5f6
Revises: 9d4f2a7b6c10
"""

from typing import Sequence, Union

from alembic import context, op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9d4f2a7b6c10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if context.is_offline_mode():
        return

    bind = op.get_bind()
    communities = sa.table(
        "communities",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String()),
    )
    roadmaps = sa.table(
        "roadmaps",
        sa.column("id", sa.Integer()),
        sa.column("community_id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("total_modules", sa.Integer()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    modules = sa.table(
        "modules",
        sa.column("id", sa.Integer()),
        sa.column("roadmap_id", sa.Integer()),
        sa.column("order", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("description", sa.Text()),
    )
    tasks = sa.table(
        "tasks",
        sa.column("id", sa.Integer()),
        sa.column("module_id", sa.Integer()),
        sa.column("order", sa.Integer()),
        sa.column("title", sa.String()),
    )
    resources = sa.table(
        "resources",
        sa.column("community_id", sa.Integer()),
        sa.column("title", sa.String()),
        sa.column("resource_type", sa.String()),
        sa.column("difficulty", sa.String()),
        sa.column("url", sa.String()),
        sa.column("description", sa.String()),
    )

    roadmap_data = {
        "Programming": [
            ("Programming Foundations", "Build a strong foundation in programming.", ["Variables and control flow", "Functions and modular code", "Data structures"]),
            ("Problem Solving", "Practice algorithms and computational thinking.", ["Complexity analysis", "Searching and sorting", "Solve five practice problems"]),
            ("Projects", "Apply programming skills to practical projects.", ["Plan a console application", "Build and test a project", "Document your solution"]),
        ],
        "Web Development": [
            ("Web Foundations", "Learn the building blocks of the web.", ["Semantic HTML", "Responsive CSS", "Accessibility basics"]),
            ("Frontend Development", "Build interactive browser experiences.", ["JavaScript fundamentals", "DOM and browser APIs", "Build a responsive interface"]),
            ("Backend and Deployment", "Connect applications to services and users.", ["REST API fundamentals", "Database integration", "Deploy a full-stack project"]),
        ],
    }
    resource_data = {
        "Programming": [
            ("Python Documentation", "Article", "Beginner", "https://docs.python.org/3/", "Official Python language documentation."),
            ("CP-Algorithms", "Article", "Intermediate", "https://cp-algorithms.com/", "Algorithm and data structure references."),
            ("Git Documentation", "Article", "Beginner", "https://git-scm.com/docs", "Reference for version control workflows."),
        ],
        "Web Development": [
            ("MDN Web Docs", "Article", "Beginner", "https://developer.mozilla.org/en-US/docs/Learn", "Practical HTML, CSS, and JavaScript learning materials."),
            ("web.dev Learn", "Course", "Intermediate", "https://web.dev/learn/", "Modern web development courses."),
            ("React Documentation", "Article", "Intermediate", "https://react.dev/learn", "Official React learning path."),
        ],
    }

    community_rows = bind.execute(
        sa.select(communities.c.id, communities.c.name)
        .where(communities.c.name.in_(roadmap_data))
    ).all()
    for community_id, community_name in community_rows:
        existing = bind.execute(
            sa.select(roadmaps.c.id)
            .where(roadmaps.c.community_id == community_id)
        ).first()
        if not existing:
            now = sa.func.now()
            roadmap_id = bind.execute(
                roadmaps.insert().returning(roadmaps.c.id).values(
                    community_id=community_id,
                    title=f"{community_name} Learning Roadmap",
                    description=f"A guided roadmap for {community_name.lower()} learners.",
                    total_modules=len(roadmap_data[community_name]),
                    created_at=now,
                    updated_at=now,
                )
            ).scalar_one()
            for module_order, (title, description, module_tasks) in enumerate(
                roadmap_data[community_name], start=1
            ):
                module_id = bind.execute(
                    modules.insert().returning(modules.c.id).values(
                        roadmap_id=roadmap_id,
                        order=module_order,
                        title=title,
                        description=description,
                    )
                ).scalar_one()
                for task_order, task_title in enumerate(module_tasks, start=1):
                    bind.execute(
                        tasks.insert().values(
                            module_id=module_id,
                            order=task_order,
                            title=task_title,
                        )
                    )

        resource_exists = bind.execute(
            sa.select(resources.c.title)
            .where(resources.c.community_id == community_id)
        ).first()
        if not resource_exists:
            for title, resource_type, difficulty, url, description in resource_data[community_name]:
                bind.execute(
                    resources.insert().values(
                        community_id=community_id,
                        title=title,
                        resource_type=resource_type,
                        difficulty=difficulty,
                        url=url,
                        description=description,
                    )
                )


def downgrade() -> None:
    bind = op.get_bind()
    community_ids = sa.select(
        sa.table(
            "communities",
            sa.column("id", sa.Integer()),
            sa.column("name", sa.String()),
        ).c.id
    ).where(
        sa.table(
            "communities",
            sa.column("id", sa.Integer()),
            sa.column("name", sa.String()),
        ).c.name.in_(["Programming", "Web Development"])
    )
    resource_table = sa.table(
        "resources",
        sa.column("community_id", sa.Integer()),
    )
    roadmap_table = sa.table(
        "roadmaps",
        sa.column("id", sa.Integer()),
        sa.column("community_id", sa.Integer()),
    )
    module_table = sa.table(
        "modules",
        sa.column("id", sa.Integer()),
        sa.column("roadmap_id", sa.Integer()),
    )
    task_table = sa.table(
        "tasks",
        sa.column("module_id", sa.Integer()),
    )
    roadmap_ids = sa.select(roadmap_table.c.id).where(
        roadmap_table.c.community_id.in_(community_ids)
    )
    module_ids = sa.select(module_table.c.id).where(
        module_table.c.roadmap_id.in_(roadmap_ids)
    )
    bind.execute(sa.delete(task_table).where(task_table.c.module_id.in_(module_ids)))
    bind.execute(sa.delete(module_table).where(module_table.c.roadmap_id.in_(roadmap_ids)))
    bind.execute(sa.delete(roadmap_table).where(roadmap_table.c.id.in_(roadmap_ids)))
    bind.execute(sa.delete(resource_table).where(resource_table.c.community_id.in_(community_ids)))
