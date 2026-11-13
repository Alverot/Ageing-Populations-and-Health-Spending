"""Download indicators from the WHO Global Health Observatory OData API."""

import json
from pathlib import Path

import requests

from etl.config import SOURCES, YEAR_FROM, YEAR_TO
from etl.json_types import JsonRecord
from etl.raw_files import RAW_DIR, save_raw

BASE_URL = SOURCES["who"]["api_url"]
HTTP_TIMEOUT_S = 120
_DEFAULT_RAW_DIR = RAW_DIR / "who"


class WhoApiError(RuntimeError):
    """The WHO GHO API returned a response we cannot interpret."""


def _download_rows(code: str, filter_expr: str) -> tuple[list[JsonRecord], str]:
    """Download every row of ``code`` matching ``filter_expr``, page by page."""
    params: dict[str, str] | None = {"$filter": filter_expr}
    rows: list[JsonRecord] = []
    request_url: str | None = None
    next_url: str | None = f"{BASE_URL}/{code}"
    while next_url:
        response = requests.get(next_url, params=params, timeout=HTTP_TIMEOUT_S)
        response.raise_for_status()
        # The full URL of the first request (with $filter) identifies the data.
        request_url = request_url or response.url
        payload: object = response.json()
        if not isinstance(payload, dict):
            raise WhoApiError(f"{next_url}: expected a JSON object, got {payload!r}")
        value = payload.get("value", [])
        if not isinstance(value, list):
            raise WhoApiError(f"{next_url}: 'value' is not a list: {value!r}")
        rows.extend(value)
        next_link = payload.get("@odata.nextLink")
        next_url = next_link if isinstance(next_link, str) else None
        # nextLink already contains the $filter, so don't send it again.
        params = None

    assert request_url is not None  # the loop always runs at least once
    return rows, request_url


def _save_rows(output_dir: Path, filename: str, rows: list[JsonRecord], url: str) -> Path:
    return save_raw(output_dir, filename, json.dumps(rows).encode("utf-8"), url)


def download_who_indicator(
    code: str,
    year_from: int = YEAR_FROM,
    year_to: int = YEAR_TO,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one indicator for every country in the year window."""
    rows, url = _download_rows(
        code,
        f"SpatialDimType eq 'COUNTRY' and TimeDim ge {year_from} "
        f"and TimeDim le {year_to}",
    )
    path = _save_rows(
        output_dir or _DEFAULT_RAW_DIR, f"{code}_{year_from}-{year_to}.json", rows, url
    )
    return path, url


def download_who_indicator_for_year(
    code: str,
    year: int,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one indicator for every country, for a single year."""
    rows, url = _download_rows(code, f"SpatialDimType eq 'COUNTRY' and TimeDim eq {year}")
    path = _save_rows(output_dir or _DEFAULT_RAW_DIR, f"{code}_{year}.json", rows, url)
    return path, url
