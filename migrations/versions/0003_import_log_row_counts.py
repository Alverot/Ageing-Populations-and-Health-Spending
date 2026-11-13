"""Add inserted, updated and rejected row counts to import_log.

Revision ID: 0003_import_log_row_counts
Revises: 0002_observation_is_outlier
Create Date: 2026-11-13
"""
import sqlalchemy as sa
from alembic import op

revision = "0003_import_log_row_counts"
down_revision = "0002_observation_is_outlier"
branch_labels = None
depends_on = None

_COLUMNS = ("rows_inserted", "rows_updated", "rows_rejected")


def upgrade() -> None:
    for name in _COLUMNS:
        op.add_column(
            "import_log",
            sa.Column(name, sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    for name in reversed(_COLUMNS):
        op.drop_column("import_log", name)
