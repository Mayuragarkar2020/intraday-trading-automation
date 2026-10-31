"""Fetch or replay official NSE eligibility evidence for a research snapshot."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from src.nse_eligibility_audit import audit_eligibility, fetch_sources

def _atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            json.dump(value, handle, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--evidence", required=True, help="JSON source bundle to save or replay")
    parser.add_argument("--output", required=True)
    parser.add_argument("--fetch", action="store_true", help="Download three official NSE sources")
    args = parser.parse_args()
    try:
        snapshot_path, evidence_path, output = map(Path, (args.snapshot, args.evidence, args.output))
        if evidence_path.resolve() in {snapshot_path.resolve(), output.resolve()}:
            raise ValueError("Evidence must be separate from snapshot and output")
        if args.fetch and evidence_path.exists():
            raise ValueError("Use a new evidence filename; existing evidence is preserved")
        report = json.loads(snapshot_path.read_text(encoding="utf-8"))
        sources = fetch_sources(report) if args.fetch else json.loads(evidence_path.read_text(encoding="utf-8"))
        audited = audit_eligibility(report, sources)
        if args.fetch:
            _atomic_json(evidence_path, sources)
        _atomic_json(output, audited)
        print(json.dumps({"status": "RESEARCH_ONLY", **audited["summary"],
                          "tradable_count": 0, "execution_enabled": False}))
    except Exception as exc:
        parser.exit(2, f"NOT_READY: {type(exc).__name__}: {exc}\n")

if __name__ == "__main__":
    main()
