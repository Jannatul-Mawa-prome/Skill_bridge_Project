"""add membership status

Revision ID: c7e9b3d1a2f4
Revises: cecb98231ef1
Create Date: 2026-09-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7e9b3d1a2f4"
down_revision: Union[str, Sequence[str], None] = "cecb98231ef1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "community_memberships",
        sa.Column("status", sa.String(length=20), nullable=True, server_default="pending")
    )
    op.execute(
        "UPDATE community_memberships SET status = 'approved' WHERE status IS NULL"
    )
    op.alter_column("community_memberships", "status", nullable=False, server_default="pending")


def downgrade() -> None:
    op.drop_column("community_memberships", "status")
