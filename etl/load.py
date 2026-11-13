"""Write cleaned data to PostgreSQL.

Observations and countries are upserted (INSERT ... ON CONFLICT DO UPDATE), so
running an import again updates the existing rows instead of adding duplicates.
"""

from typing import NamedTuple

import pandas as pd
from sqlalchemy import func, literal_column, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.models import Country, ImportLog, Indicator, Observation, Source


class UpsertCounts(NamedTuple):
    inserted: int
    updated: int

    @property
    def loaded(self) -> int:
        return self.inserted + self.updated


def get_or_create_source(session: Session, name: str, url: str) -> int:
    source = session.scalar(select(Source).where(Source.name == name))
    if source is None:
        source = Source(name=name, url=url)
        session.add(source)
        session.flush()
    return source.source_id


def get_or_create_indicator(
    session: Session, code: str, name: str, unit: str, source_id: int
) -> int:
    indicator = session.scalar(select(Indicator).where(Indicator.code == code))
    if indicator is None:
        indicator = Indicator(code=code, name=name, unit=unit, source_id=source_id)
        session.add(indicator)
        session.flush()
    return indicator.indicator_id


def upsert_countries(session: Session, countries: pd.DataFrame) -> None:
    if countries.empty:
        return
    stmt = insert(Country).values(countries.to_dict("records"))
    stmt = stmt.on_conflict_do_update(
        index_elements=["iso3"],
        set_={col: stmt.excluded[col] for col in ("iso2", "name", "region", "income_group")},
    )
    session.execute(stmt)


def upsert_observations(
    session: Session,
    observations: pd.DataFrame,
    indicator_id: int,
    chunk_size: int = 5000,
) -> UpsertCounts:
    """Insert new observations and update existing ones on the natural key."""
    if observations.empty:
        return UpsertCounts(0, 0)

    # The observation table stores indicator_id (foreign key), not the code.
    rows = (
        observations.drop(columns=["indicator_code"])
        .assign(indicator_id=indicator_id)
        .to_dict("records")
    )
    inserted = updated = 0
    for start in range(0, len(rows), chunk_size):
        stmt = insert(Observation).values(rows[start : start + chunk_size])
        stmt = stmt.on_conflict_do_update(
            constraint="uq_observation",
            set_={
                "value": stmt.excluded.value,
                "is_outlier": stmt.excluded.is_outlier,
                "imported_at": func.now(),
            },
        )
        # PostgreSQL sets xmax = 0 only on rows that were newly inserted.
        stmt = stmt.returning(literal_column("(xmax = 0)"))
        for (was_inserted,) in session.execute(stmt):
            if was_inserted:
                inserted += 1
            else:
                updated += 1
    return UpsertCounts(inserted, updated)


def log_import(
    session: Session,
    source_name: str,
    indicator_code: str,
    url: str,
    counts: UpsertCounts,
    rows_rejected: int,
) -> None:
    session.add(
        ImportLog(
            source_name=source_name,
            indicator_code=indicator_code,
            url=url,
            rows_loaded=counts.loaded,
            rows_inserted=counts.inserted,
            rows_updated=counts.updated,
            rows_rejected=rows_rejected,
        )
    )
