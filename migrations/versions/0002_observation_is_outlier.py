"""Add observation.is_outlier for the IQR outlier flag (Task 2.2).

Revision ID: 0002_observation_is_outlier
Revises: 0001_baseline
Create Date: 2026-11-13
"""
import sqlalchemy as sa
from alembic import op

revision = "0002_observation_is_outlier"
down_revision = "0001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "observation",
        sa.Column("is_outlier", sa.Boolean(), nullable=False,
                  server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("observation", "is_outlier")
