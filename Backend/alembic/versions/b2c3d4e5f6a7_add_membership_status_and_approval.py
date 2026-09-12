"""add membership status, reviewed_at, and reviewer_id

Revision ID: b2c3d4e5f6a7
Revises: f7e8d9c0b1a2
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "f7e8d9c0b1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Existing memberships remain 'approved'
    op.add_column(
        "community_memberships",
        sa.Column("status", sa.String(length=50), nullable=False, server_default="approved"),
    )
    # New rows will default to 'pending'
    op.alter_column(
        "community_memberships",
        "status",
        server_default="pending",
    )
    op.add_column(
        "community_memberships",
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "community_memberships",
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("community_memberships", "reviewer_id")
    op.drop_column("community_memberships", "reviewed_at")
    op.drop_column("community_memberships", "status")
