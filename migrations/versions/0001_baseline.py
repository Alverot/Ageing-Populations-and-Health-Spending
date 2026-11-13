"""Baseline: the five tables from Lab 1 (db/schema.sql).

Revision ID: 0001_baseline
Revises:
Create Date: 2026-11-13
"""
import sqlalchemy as sa
from alembic import op

revision = "0001_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "source",
        sa.Column("source_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("url", sa.Text()),
    )
    op.create_table(
        "country",
        sa.Column("iso3", sa.String(3), primary_key=True),
        sa.Column("iso2", sa.String(2)),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("region", sa.String(100)),
        sa.Column("income_group", sa.String(50)),
    )
    op.create_table(
        "indicator",
        sa.Column("indicator_id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("unit", sa.String(50)),
        sa.Column("source_id", sa.Integer(),
                  sa.ForeignKey("source.source_id"), nullable=False),
    )
    op.create_table(
        "observation",
        sa.Column("observation_id", sa.BigInteger(), primary_key=True),
        sa.Column("country_iso3", sa.String(3),
                  sa.ForeignKey("country.iso3"), nullable=False),
        sa.Column("indicator_id", sa.Integer(),
                  sa.ForeignKey("indicator.indicator_id"), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("sex", sa.String(10), nullable=False,
                  server_default="BTSX"),
        sa.Column("value", sa.Numeric(18, 4)),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
        sa.UniqueConstraint("country_iso3", "indicator_id", "year", "sex",
                            name="uq_observation"),
    )
    op.create_index("ix_observation_indicator_year", "observation",
                    ["indicator_id", "year"])
    op.create_table(
        "import_log",
        sa.Column("import_id", sa.Integer(), primary_key=True),
        sa.Column("source_name", sa.String(100), nullable=False),
        sa.Column("indicator_code", sa.String(50), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("rows_loaded", sa.Integer(), nullable=False),
        sa.Column("imported_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("import_log")
    op.drop_index("ix_observation_indicator_year", table_name="observation")
    op.drop_table("observation")
    op.drop_table("indicator")
    op.drop_table("country")
    op.drop_table("source")
