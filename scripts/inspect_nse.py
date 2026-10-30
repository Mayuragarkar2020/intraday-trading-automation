"""Inspect local official NSE CM UDiFF files; no network calls.

Usage: python -m scripts.inspect_nse 2026-10-30 data/raw/BhavCopy_....csv.zip
"""
import json
import sys
from src.ingestion import DataQualityError, load_bhavcopy

def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python -m scripts.inspect_nse YYYY-MM-DD file.csv[.zip]", file=sys.stderr)
        return 2
    try:
        rows, manifest = load_bhavcopy(sys.argv[2], sys.argv[1])
    except (DataQualityError, OSError, ValueError) as exc:
        print(f"NOT_READY: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"manifest": manifest,
                      "first_eq": {k: str(v) for k, v in rows[0].items()}}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
