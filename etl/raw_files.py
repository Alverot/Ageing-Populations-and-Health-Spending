"""Saving raw downloads together with where they came from.

Each raw file gets a ``<name>.source.json`` file next to it with the download
URL and time, so the import can write the real URL to import_log instead of a
local path.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
_SIDECAR_SUFFIX = ".source.json"


def _sidecar_path(path: Path) -> Path:
    return path.with_name(path.name + _SIDECAR_SUFFIX)


def save_raw(output_dir: Path, filename: str, content: bytes, source_url: str) -> Path:
    """Write ``content`` unchanged and record ``source_url`` next to it."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    path.write_bytes(content)
    _sidecar_path(path).write_text(
        json.dumps(
            {
                "url": source_url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
            }
        ),
        encoding="utf-8",
    )
    return path


def read_source_url(path: Path) -> str:
    """Return the URL a raw file was downloaded from.

    Falls back to the local path if the file has no sidecar.
    """
    sidecar = _sidecar_path(path)
    try:
        meta: object = json.loads(sidecar.read_text(encoding="utf-8"))
    except FileNotFoundError:
        logger.warning("%s has no %s; run the extraction again", path.name, sidecar.name)
        return str(path)
    if not isinstance(meta, dict) or not isinstance(meta.get("url"), str):
        raise ValueError(f"{sidecar}: expected an object with a 'url' string")
    return meta["url"]
