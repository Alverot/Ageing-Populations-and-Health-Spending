"""Download every source and indicator listed in etl/config.py.

Usage, from the project root with the virtual environment active:

    python -m etl.extract

A new source is added by writing its extractor and adding one line to
_DOWNLOADERS below.
"""

from collections.abc import Callable
from pathlib import Path

from etl.config import INDICATORS
from etl.extract_owid import download_owid_chart
from etl.extract_who import download_who_indicator
from etl.extract_worldbank import download_worldbank_countries, download_worldbank_indicator

# Source key in config.SOURCES -> function that downloads one indicator.
_DOWNLOADERS: dict[str, Callable[[str], tuple[Path, str]]] = {
    "who": download_who_indicator,
    "world_bank": download_worldbank_indicator,
    "owid": download_owid_chart,
}


def download_all() -> list[Path]:
    """Download the World Bank country list and every indicator in the config."""
    path, _ = download_worldbank_countries()
    print(f"{'countries':<24} -> {path}")
    paths = [path]
    for indicator in INDICATORS:
        download = _DOWNLOADERS[indicator["source"]]
        path, _ = download(indicator["code"])
        print(f"{indicator['code']:<24} -> {path}")
        paths.append(path)
    return paths


if __name__ == "__main__":
    download_all()
