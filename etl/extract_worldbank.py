"""Download the country list and indicators from the World Bank API."""

import json
from pathlib import Path

import requests

from etl.config import SOURCES, YEAR_FROM, YEAR_TO
from etl.json_types import JsonRecord
from etl.raw_files import RAW_DIR, save_raw

BASE_URL = SOURCES["world_bank"]["api_url"]
HTTP_TIMEOUT_S = 120
_DEFAULT_RAW_DIR = RAW_DIR / "worldbank"

Params = dict[str, str | int]


class WorldBankApiError(RuntimeError):
    """The World Bank API returned an error or an unexpected response."""


def _get_all_pages(url: str, params: Params) -> list[JsonRecord]:
    """Download every page of ``url``.

    Each response is a pair [paging metadata, records]. Errors such as an
    unknown indicator come back with HTTP 200 and a different shape, so the
    shape is checked before the records are used.
    """
    page = 1
    records: list[JsonRecord] = []
    while True:
        response = requests.get(
            url, params={**params, "format": "json", "page": page}, timeout=HTTP_TIMEOUT_S
        )
        response.raise_for_status()
        body: object = response.json()
        if not (isinstance(body, list) and len(body) == 2):
            raise WorldBankApiError(f"{url}: unexpected response {body!r}")
        meta, data = body
        if not isinstance(meta, dict) or "pages" not in meta:
            raise WorldBankApiError(f"{url}: missing page metadata in {meta!r}")
        if data is not None and not isinstance(data, list):
            raise WorldBankApiError(f"{url}: records are not a list: {data!r}")
        records.extend(data or [])
        if page >= int(meta["pages"]):
            return records
        page += 1


def _source_url(url: str, params: Params) -> str:
    """The request URL with its query string, without the page number."""
    return requests.Request("GET", url, params={**params, "format": "json"}).prepare().url or url


def _download(url: str, params: Params, output_dir: Path, filename: str) -> tuple[Path, str]:
    records = _get_all_pages(url, params)
    source_url = _source_url(url, params)
    path = save_raw(output_dir, filename, json.dumps(records).encode("utf-8"), source_url)
    return path, source_url


def download_worldbank_countries(*, output_dir: Path | None = None) -> tuple[Path, str]:
    """Download the list of economies (countries and aggregates)."""
    return _download(
        f"{BASE_URL}/country",
        {"per_page": 400},
        output_dir or _DEFAULT_RAW_DIR,
        "countries.json",
    )


def download_worldbank_indicator(
    code: str,
    year_from: int = YEAR_FROM,
    year_to: int = YEAR_TO,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one indicator for every economy in the year window."""
    return _download(
        f"{BASE_URL}/country/all/indicator/{code}",
        {"date": f"{year_from}:{year_to}", "per_page": 10000},
        output_dir or _DEFAULT_RAW_DIR,
        f"{code}_{year_from}-{year_to}.json",
    )


def download_worldbank_indicator_for_year(
    code: str,
    year: int,
    *,
    output_dir: Path | None = None,
) -> tuple[Path, str]:
    """Download one indicator for every economy, for a single year."""
    return _download(
        f"{BASE_URL}/country/all/indicator/{code}",
        {"date": str(year), "per_page": 10000},
        output_dir or _DEFAULT_RAW_DIR,
        f"{code}_{year}.json",
    )
