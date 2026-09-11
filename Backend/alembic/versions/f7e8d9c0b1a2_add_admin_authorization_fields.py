"""add administrator authorization and moderation status fields

Revision ID: f7e8d9c0b1a2
Revises: a1b2c3d4e5f6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7e8d9c0b1a2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "communities",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "community_memberships",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    # Defaults are only needed while existing rows are backfilled.
    op.alter_column("users", "is_admin", server_default=None)
    op.alter_column("communities", "is_active", server_default=None)
    op.alter_column("community_memberships", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_column("community_memberships", "is_active")
    op.drop_column("communities", "is_active")
    op.drop_column("users", "is_admin")
