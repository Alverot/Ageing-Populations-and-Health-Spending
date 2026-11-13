"""Clean the normalized observations before they are stored.

Each rule answers one of the data challenges from section 1.5 of Lab 1.
Every rule that removes rows goes through _drop(), which logs how many rows
were removed and why. Outliers are only flagged (is_outlier), not removed.
"""

import logging
from typing import NamedTuple

import pandas as pd

from app.models import Sex
from etl.config import YEAR_FROM, YEAR_TO

logger = logging.getLogger(__name__)

_OUTPUT_COLUMNS = ["country_iso3", "indicator_code", "year", "sex", "value", "is_outlier"]
_KEY_COLUMNS = ["country_iso3", "indicator_code", "year", "sex"]

# WHO writes "SEX_BTSX" etc.; built from the Sex enum so the two always match.
_SEX_MAP = {f"SEX_{sex.value}": sex.value for sex in Sex}
_VALID_SEX = {sex.value for sex in Sex}

_IQR_FACTOR = 1.5


class _Bounds(NamedTuple):
    """Plausible value range: ``high`` is inclusive, ``low`` only if ``low_inclusive``."""

    low: float
    high: float
    low_inclusive: bool = True


# Plausible limits per indicator; values outside them are dropped. A value of
# exactly 0 is not a real measurement for GDP, health spending per person or
# life expectancy, so those lower bounds are exclusive.
_INDICATOR_BOUNDS = {
    "SP.POP.65UP.TO.ZS": _Bounds(0, 100),
    "NY.GDP.PCAP.CD": _Bounds(0, 500_000, low_inclusive=False),
    "SH.MED.BEDS.ZS": _Bounds(0, 50),
    "GHED_CHE_pc_US_SHA2011": _Bounds(0, 50_000, low_inclusive=False),
    "GHED_CHEGDP_SHA2011": _Bounds(0, 100),
    "GHED_OOPSCHE_SHA2011": _Bounds(0, 100),
    "WHOSIS_000001": _Bounds(0, 120, low_inclusive=False),
    "WHOSIS_000002": _Bounds(0, 120, low_inclusive=False),
    "life-expectancy": _Bounds(0, 120, low_inclusive=False),
}


def _drop(cleaned: pd.DataFrame, mask: pd.Series, reason: str) -> pd.DataFrame:
    """Drop the rows where ``mask`` is true, logging how many and why."""
    dropped = int(mask.sum())
    if dropped:
        logger.info("dropped %d observation rows: %s", dropped, reason)
    return cleaned[~mask]


def _out_of_bounds(cleaned: pd.DataFrame) -> pd.Series:
    mask = pd.Series(False, index=cleaned.index)
    value = cleaned["value"]
    for code, bounds in _INDICATOR_BOUNDS.items():
        too_low = value < bounds.low if bounds.low_inclusive else value <= bounds.low
        mask |= (cleaned["indicator_code"] == code) & (too_low | (value > bounds.high))
    return mask


def _iqr_outliers(cleaned: pd.DataFrame) -> pd.Series:
    """True for values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR of their indicator."""
    grouped = cleaned.groupby("indicator_code")["value"]
    q1 = grouped.transform(lambda v: v.quantile(0.25))
    q3 = grouped.transform(lambda v: v.quantile(0.75))
    iqr = q3 - q1
    value = cleaned["value"]
    return (value < q1 - _IQR_FACTOR * iqr) | (value > q3 + _IQR_FACTOR * iqr)


def clean_observations(
    normalized: pd.DataFrame,
    valid_iso3: set[str],
    *,
    year_window: tuple[int, int] = (YEAR_FROM, YEAR_TO),
) -> pd.DataFrame:
    """Apply every cleaning rule and add the is_outlier flag."""
    if normalized.empty:
        return pd.DataFrame(columns=_OUTPUT_COLUMNS)

    cleaned = normalized.copy()

    # Standardize identifiers, then keep only real countries.
    cleaned["country_iso3"] = cleaned["country_iso3"].astype("string").str.strip().str.upper()
    cleaned = _drop(
        cleaned,
        ~cleaned["country_iso3"].isin(valid_iso3).fillna(False).astype(bool),
        "not a known country (aggregate, region or missing code)",
    )

    # Type conversion and missing values (never stored as 0).
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
    cleaned["value"] = pd.to_numeric(cleaned["value"], errors="coerce")
    cleaned = _drop(
        cleaned,
        cleaned["year"].isna() | cleaned["value"].isna(),
        "missing or non-numeric year/value",
    )
    # astype(int) would turn 2010.5 into 2010 and overwrite the real 2010 row.
    cleaned = _drop(cleaned, cleaned["year"] % 1 != 0, "year is not a whole number")
    cleaned["year"] = cleaned["year"].astype(int)

    year_low, year_high = year_window
    cleaned = _drop(
        cleaned,
        (cleaned["year"] < year_low) | (cleaned["year"] > year_high),
        f"year outside {year_low}-{year_high}",
    )

    # Harmonize sex codes; sources without a sex split mean both sexes.
    cleaned["sex"] = cleaned["sex"].fillna(Sex.BOTH.value).replace(_SEX_MAP)
    cleaned = _drop(cleaned, ~cleaned["sex"].isin(_VALID_SEX), "unknown sex code")

    cleaned = _drop(cleaned, _out_of_bounds(cleaned), "value outside plausible bounds")

    cleaned = _drop(
        cleaned,
        cleaned.duplicated(subset=_KEY_COLUMNS, keep="last"),
        "duplicate (country, indicator, year, sex); kept the last",
    )

    # Task 2.2: flag (not drop) statistical outliers per indicator.
    cleaned["is_outlier"] = _iqr_outliers(cleaned)
    flagged = int(cleaned["is_outlier"].sum())
    if flagged:
        logger.info("flagged %d observation rows as IQR outliers", flagged)

    return cleaned[_OUTPUT_COLUMNS]
