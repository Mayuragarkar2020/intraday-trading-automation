"""Reproducible, fail-closed 20-session screening from official local NSE reports."""
from __future__ import annotations
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
import yaml
from src.ingestion import DataQualityError, load_bhavcopy
from src.screening import evaluate, provisional_status

def screen_files(paths: list[str], asof: str, config: dict) -> dict:
    required = int(config["universe"]["required_history_sessions"])
    if len(paths) != required:
        raise DataQualityError(f"Expected {required} distinct NSE session files")
    sessions = {}
    manifest = []
    for path in paths:
        # NSE official names use YYYYMMDD; locally renamed files may use YYYY-MM-DD.
        name = Path(path).name
        import re
        matches = re.findall(r"(?<!\\d)(?:\\d{4}-\\d{2}-\\d{2}|\\d{8})(?!\\d)", name)
        if len(matches) != 1:
            raise DataQualityError(f"Filename must have exactly one session date: {name}")
        raw_date = matches[0]
        try:
            day = (date.fromisoformat(raw_date) if "-" in raw_date
                   else date.strptime(raw_date, "%Y%m%d")).isoformat()
        except (ValueError, AttributeError):
            from datetime import datetime
            try:
                day = datetime.strptime(raw_date, "%Y%m%d").date().isoformat()
            except ValueError as exc:
                raise DataQualityError(f"Invalid session date: {raw_date}") from exc
        if day in sessions:
            raise DataQualityError(f"Duplicate session: {day}")
        rows, info = load_bhavcopy(path, day)
        sessions[day] = rows
        manifest.append(info)
    ordered = sorted(sessions)
    if ordered[-1] != asof:
        raise DataQualityError(f"Most recent session {ordered[-1]} does not match {asof}")
    if any(day > asof for day in ordered):
        raise DataQualityError("Lookahead data detected")
    by_isin = defaultdict(list)
    for day in ordered:
        for row in sessions[day]:
            by_isin[row["isin"]].append(row)
    decisions = []
    for isin, history in sorted(by_isin.items()):
        if len(history) != required:
            decisions.append({"isin": isin, "symbol": history[-1]["symbol"],
                              "status": "EXCLUDED_INCOMPLETE_HISTORY",
                              "failed_rules": ["E05_HISTORY"], "sessions": len(history)})
            continue
        item = evaluate(history, config)
        item["status"] = provisional_status(item)
        decisions.append(item)
    return {"asof_date": asof, "session_dates": ordered, "source_manifest": manifest,
            "status": "PROVISIONAL_ONLY", "decisions": decisions,
            "eligible_count": 0, "hold_count": sum(d["status"].startswith("HOLD") for d in decisions)}

def run_directory(directory: str, asof: str, config_path: str) -> dict:
    with open(config_path, encoding="utf8") as f:
        config = yaml.safe_load(f)
    paths = sorted(str(p) for p in Path(directory).iterdir() if p.suffix.lower() in {".csv", ".zip"})
    return screen_files(paths, asof, config)
