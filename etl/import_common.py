"""The import loop shared by etl/import_worldbank.py, import_who.py and import_owid.py.

For every indicator of one source in etl/config.py: read the raw file saved by
the extractor, transform, clean, upsert and write one import_log row.
"""

import logging
import sys
from collections.abc import Callable
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Country
from etl.clean import clean_observations
from etl.config import INDICATORS, SOURCES, YEAR_FROM, YEAR_TO
from etl.load import get_or_create_indicator, get_or_create_source, log_import, upsert_observations
from etl.raw_files import RAW_DIR, read_source_url

logger = logging.getLogger(__name__)

# Expected failures: bad data, a missing or unreadable file, a database error.
# Anything else is a bug and stops the script at once.
IMPORT_ERRORS = (ValueError, OSError, SQLAlchemyError)

TransformFile = Callable[[Path, str], pd.DataFrame]

# Where each extractor saves an indicator (see etl/extract_*.py).
_RAW_FILES: dict[str, Callable[[str], Path]] = {
    "who": lambda code: RAW_DIR / "who" / f"{code}_{YEAR_FROM}-{YEAR_TO}.json",
    "world_bank": lambda code: RAW_DIR / "worldbank" / f"{code}_{YEAR_FROM}-{YEAR_TO}.json",
    "owid": lambda slug: RAW_DIR / "owid" / f"{slug}_full.csv",
}


def setup_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="  %(message)s")


def known_countries(session: Session) -> set[str]:
    """ISO3 codes in the country table, loaded by etl.import_worldbank."""
    return set(session.scalars(select(Country.iso3)))


def import_source(
    session: Session,
    source_key: str,
    transform: TransformFile,
    valid_iso3: set[str],
) -> list[str]:
    """Import every indicator of ``source_key``; return the codes that failed."""
    source = SOURCES[source_key]
    source_id = get_or_create_source(session, source["name"], source["url"])
    session.commit()

    failed: list[str] = []
    for indicator in (i for i in INDICATORS if i["source"] == source_key):
        code = indicator["code"]
        path = _RAW_FILES[source_key](code)
        if not path.exists():
            print(f"{code:<24} SKIP (missing {path.name}; run python -m etl.extract)")
            continue
        try:
            raw = transform(path, code)
            cleaned = clean_observations(raw, valid_iso3)
            rejected = len(raw) - len(cleaned)
            indicator_id = get_or_create_indicator(
                session, code, indicator["name"], indicator["unit"], source_id
            )
            counts = upsert_observations(session, cleaned, indicator_id)
            log_import(session, source["name"], code, read_source_url(path), counts, rejected)
            session.commit()
        except IMPORT_ERRORS:
            session.rollback()
            logger.exception("%s: import failed", code)
            failed.append(code)
            continue
        print(
            f"{code:<24} raw={len(raw):>6} rejected={rejected:>6} "
            f"inserted={counts.inserted:>6} updated={counts.updated:>6}"
        )
    return failed


def exit_on_failure(failed: list[str]) -> None:
    if failed:
        print(f"FAILED: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
