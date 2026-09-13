"""add user role

Revision ID: 5d5f0d4c4b11
Revises: c7e9b3d1a2f4
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5d5f0d4c4b11"
down_revision: Union[str, Sequence[str], None] = "c7e9b3d1a2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=50), nullable=True, server_default="member")
    )
    op.execute("UPDATE users SET role = 'member' WHERE role IS NULL")
    op.alter_column("users", "role", nullable=False, server_default="member")


def downgrade() -> None:
    op.drop_column("users", "role")
