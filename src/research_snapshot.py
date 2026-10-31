"""Serve a dated, non-executable research artifact without touching the database."""
import json
from pathlib import Path

SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "research" / "2026-10-30" / "universe.json"

def load_research_snapshot(path=None):
    report = json.loads(Path(path or SNAPSHOT_PATH).read_text(encoding="utf-8"))
    if (report.get("mode") != "LIQUIDITY_RESEARCH_ONLY"
            or report.get("execution_enabled") is not False
            or report.get("tradable_count") != 0
            or report.get("restrictions_verified") is not False
            or report.get("calendar_completeness_verified") is not False):
        raise ValueError("Unexpected research snapshot mode")
    return {"source": "DATED_NSE_RESEARCH_SNAPSHOT", "live": False,
            "execution_enabled": False, "snapshot": report}
