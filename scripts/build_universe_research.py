"""Build a research shortlist from 20 explicitly listed official NSE archives."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import yaml
from src.eligibility import dhan_mapping
from src.universe_reference import attach_references
from src.universe_research import build_research, validate_dates

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dates-file", required=True)
    parser.add_argument("--raw-dir", required=True)
    parser.add_argument("--target-date", required=True)
    parser.add_argument("--config", default="config/universe.yaml")
    parser.add_argument("--dhan-master")
    parser.add_argument("--equity-master")
    parser.add_argument("--price-bands")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    temporary = None
    try:
        if bool(args.equity_master) != bool(args.price_bands) or (args.equity_master and not args.dhan_master):
            raise ValueError("Reference review requires equity master, price bands and Dhan master together")
        config_bytes = Path(args.config).read_bytes()
        cfg = yaml.safe_load(config_bytes)
        days = [line.strip() for line in Path(args.dates_file).read_text().splitlines()
                if line.strip() and not line.lstrip().startswith("#")]
        validate_dates(days, args.target_date, cfg["universe"]["required_history_sessions"])
        paths = [(day, Path(args.raw_dir) /
                 ("BhavCopy_NSE_CM_0_0_0_" + day.replace("-", "") + "_F_0000.csv.zip"))
                 for day in days]
        mapping = dhan_mapping(args.dhan_master) if args.dhan_master else None
        report = build_research(paths, args.target_date, cfg, mapping)
        if args.equity_master:
            report = attach_references(report, args.equity_master, args.price_bands, args.dhan_master)
        report["config_sha256"] = hashlib.sha256(config_bytes).hexdigest()
        if args.dhan_master:
            report["dhan_master"] = {
                "filename": Path(args.dhan_master).name,
                "sha256": hashlib.sha256(Path(args.dhan_master).read_bytes()).hexdigest(),
                "effective_date_verified": False}
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         delete=False, suffix=".tmp") as handle:
            temporary = handle.name
            json.dump(report, handle, indent=2)
            handle.write("\n")
        os.replace(temporary, output)
        temporary = None
        print(json.dumps({"status": "RESEARCH_ONLY", **report["summary"],
                          "tradable_count": 0, "execution_enabled": False}))
    except Exception as exc:
        # No partial output replaces an earlier report on failure.
        parser.exit(2, f"NOT_READY: {type(exc).__name__}: {exc}\n")
    finally:
        if temporary:
            Path(temporary).unlink(missing_ok=True)

if __name__ == "__main__":
    main()
