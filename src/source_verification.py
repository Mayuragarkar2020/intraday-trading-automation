"""Source file preflight checks; downloading does not imply schema verification."""
from __future__ import annotations
import csv
import hashlib
import io
import urllib.request
from pathlib import Path

DHAN_DETAILED_URL = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
REQUIRED_DHAN = {"EXCH_ID", "SEGMENT", "ISIN", "SERIES", "SECURITY_ID"}

def fetch_dhan_master(destination: str, *, timeout: int = 30) -> dict:
    """Download with source hash; reject HTML/error content and schema surprises."""
    request = urllib.request.Request(DHAN_DETAILED_URL, headers={"User-Agent": "IntradayUniverseResearch/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"Dhan HTTP status: {response.status}")
        data = response.read(200_000_001)
    if len(data) > 200_000_000 or len(data) < 100:
        raise ValueError("Dhan master unexpectedly small or large")
    try:
        first_line = data.splitlines()[0].decode("utf-8-sig")
        header = next(csv.reader([first_line]))
    except (UnicodeError, StopIteration) as exc:
        raise ValueError("Dhan master is not readable CSV") from exc
    missing = REQUIRED_DHAN - set(header)
    if missing:
        raise ValueError(f"Dhan master changed columns: {sorted(missing)}")
    out = Path(destination)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Write only after full verification; no credentials or account APIs involved.
    out.write_bytes(data)
    return {"url": DHAN_DETAILED_URL, "filename": out.name,
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "schema_verified": True}
