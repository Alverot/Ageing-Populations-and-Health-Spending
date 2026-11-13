"""Turn saved World Bank files into the observation table and the country list."""

from pathlib import Path

import pandas as pd

from etl.json_types import JsonRecord, read_json_records, require_keys

_OBSERVATION_COLUMNS = ["country_iso3", "indicator_code", "year", "sex", "value"]
_COUNTRY_COLUMNS = ["iso3", "iso2", "name", "region", "income_group"]
_OBSERVATION_KEYS = ("countryiso3code", "date", "value")
_COUNTRY_KEYS = ("id", "iso2Code", "name", "region", "incomeLevel")
_AGGREGATES_REGION = "Aggregates"


def _text(record: JsonRecord, key: str) -> str:
    value = record[key]
    if not isinstance(value, str):
        raise ValueError(f"World Bank {key!r} is not a string: {record!r}")
    return value.strip()


def _nested_text(record: JsonRecord, key: str) -> str:
    # e.g. "region": {"id": "ECS", "iso2code": "Z7", "value": "Europe & Central Asia"}
    value = record[key]
    if not isinstance(value, dict):
        raise ValueError(f"World Bank {key!r} is not an object: {record!r}")
    return _text(value, "value")


def transform_worldbank_indicator_records(
    records: list[JsonRecord], code: str
) -> pd.DataFrame:
    """Map World Bank fields to the normalized columns (no sex split)."""
    if not records:
        return pd.DataFrame(columns=_OBSERVATION_COLUMNS)

    for record in records:
        require_keys(record, _OBSERVATION_KEYS, f"World Bank {code}")

    return pd.DataFrame(
        {
            "country_iso3": [r["countryiso3code"] for r in records],
            "indicator_code": code,
            "year": [r["date"] for r in records],
            "sex": None,
            "value": [r["value"] for r in records],
        }
    )


def transform_worldbank_indicator_file(path: Path, code: str) -> pd.DataFrame:
    """Read an indicator file saved by etl.extract_worldbank and normalize it."""
    return transform_worldbank_indicator_records(read_json_records(path), code)


def transform_worldbank_country_records(records: list[JsonRecord]) -> pd.DataFrame:
    """Build the country table, leaving out regional and income aggregates."""
    if not records:
        return pd.DataFrame(columns=_COUNTRY_COLUMNS)

    for record in records:
        require_keys(record, _COUNTRY_KEYS, "World Bank country")

    # All aggregates (World, Euro area, High income, ...) share this region.
    return pd.DataFrame(
        [
            {
                "iso3": _text(c, "id"),
                "iso2": _text(c, "iso2Code"),
                "name": _text(c, "name"),
                "region": _nested_text(c, "region"),
                "income_group": _nested_text(c, "incomeLevel"),
            }
            for c in records
            if _nested_text(c, "region") != _AGGREGATES_REGION
        ],
        columns=_COUNTRY_COLUMNS,
    )


def transform_worldbank_country_file(path: Path) -> pd.DataFrame:
    """Read countries.json saved by etl.extract_worldbank and build the country table."""
    return transform_worldbank_country_records(read_json_records(path))
