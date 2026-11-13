"""Import the WHO GHO indicators listed in etl/config.py.

Needs the country table: run python -m etl.import_worldbank first.

    python -m etl.import_who
"""

from sqlalchemy.orm import Session

from app.database import engine
from etl.import_common import exit_on_failure, import_source, known_countries, setup_logging
from etl.transform_who import transform_who_file


def main() -> None:
    setup_logging()
    with Session(engine) as session:
        valid_iso3 = known_countries(session)
        if not valid_iso3:
            raise SystemExit("the country table is empty; run python -m etl.import_worldbank first")
        failed = import_source(session, "who", transform_who_file, valid_iso3)
    exit_on_failure(failed)


if __name__ == "__main__":
    main()
