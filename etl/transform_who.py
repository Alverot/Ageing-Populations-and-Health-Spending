"""Turn a saved WHO GHO file into the normalized observation table."""

from pathlib import Path

import pandas as pd

from etl.json_types import JsonRecord, read_json_records, require_keys

_NORMALIZED_COLUMNS = ["country_iso3", "indicator_code", "year", "sex", "value"]
_REQUIRED_KEYS = ("SpatialDim", "TimeDim", "NumericValue")
_SEX_DIMENSION = "SEX"


def transform_who_rows(rows: list[JsonRecord], code: str) -> pd.DataFrame:
    """Map WHO fields to country_iso3, indicator_code, year, sex and value."""
    if not rows:
        return pd.DataFrame(columns=_NORMALIZED_COLUMNS)

    for row in rows:
        require_keys(row, _REQUIRED_KEYS, f"WHO {code}")

    raw = pd.DataFrame(rows)

    # Dim1 is the sex only when Dim1Type says so; for other indicators it can
    # be an age group or a residence area. Keep rows without Dim1 (both sexes)
    # and rows where Dim1 is the sex; leave out the rest.
    if "Dim1" in raw and "Dim1Type" in raw:
        dim1_type = raw["Dim1Type"]
        raw = raw[dim1_type.isna() | (dim1_type == _SEX_DIMENSION)]
        sex = raw["Dim1"].where(raw["Dim1Type"] == _SEX_DIMENSION)
    else:
        sex = None

    return pd.DataFrame(
        {
            "country_iso3": raw["SpatialDim"],
            "indicator_code": code,
            "year": raw["TimeDim"],
            "sex": sex,
            "value": raw["NumericValue"],
        }
    )


def transform_who_file(path: Path, code: str) -> pd.DataFrame:
    """Read a file saved by etl.extract_who and normalize it."""
    return transform_who_rows(read_json_records(path), code)
