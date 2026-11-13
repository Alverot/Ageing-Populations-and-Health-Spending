"""Import the country list and the World Bank indicators.

Run this before etl.import_who and etl.import_owid: they take the list of
valid countries from the country table that this script fills.

    python -m etl.import_worldbank
"""

from sqlalchemy.orm import Session

from app.database import engine
from etl.import_common import exit_on_failure, import_source, setup_logging
from etl.load import upsert_countries
from etl.raw_files import RAW_DIR
from etl.transform_worldbank import (
    transform_worldbank_country_file,
    transform_worldbank_indicator_file,
)

COUNTRIES_FILE = RAW_DIR / "worldbank" / "countries.json"


def main() -> None:
    setup_logging()
    if not COUNTRIES_FILE.exists():
        raise SystemExit(f"missing {COUNTRIES_FILE}; run python -m etl.extract first")
    with Session(engine) as session:
        countries = transform_worldbank_country_file(COUNTRIES_FILE)
        upsert_countries(session, countries)
        session.commit()
        print(f"{'countries':<24} upserted={len(countries)}")
        failed = import_source(
            session, "world_bank", transform_worldbank_indicator_file, set(countries["iso3"])
        )
    exit_on_failure(failed)


if __name__ == "__main__":
    main()
