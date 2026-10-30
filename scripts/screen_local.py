"""Provisional screening: no stock can be approved until restrictions/Dhan mapping."""
import argparse
import json
import sys
from pathlib import Path
from src.ingestion import DataQualityError
from src.pipeline import run_directory

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof", required=True)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--config", default="config/universe.yaml")
    parser.add_argument("--output", default="output/provisional_universe.json")
    args = parser.parse_args()
    try:
        result = run_directory(args.input_dir, args.asof, args.config)
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, indent=2), encoding="utf8")
        print(f"PROVISIONAL_ONLY: {len(result['decisions'])} assessed, 0 approved; file={target}")
        return 0
    except (DataQualityError, ValueError, OSError, KeyError) as exc:
        print(f"NOT_READY: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
