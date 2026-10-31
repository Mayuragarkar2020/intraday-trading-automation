"""Show shared daily research, with an explicitly labeled dated-file fallback."""
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from src.universe_store import UniverseStore, validate_report

SNAPSHOT_PATH = Path(__file__).resolve().parent.parent / "research" / "2026-10-30" / "universe.json"

def load_research_snapshot(path=None):
    source = "DATED_NSE_RESEARCH_SNAPSHOT"
    availability = "Showing saved research snapshot; daily refresh is not configured."
    revision = None
    report = None
    if path is None and os.getenv("SCAN_DATABASE_URL"):
        try:
            stored = UniverseStore(os.environ["SCAN_DATABASE_URL"]).latest()
            if stored:
                report = stored["snapshot"]
                revision = stored["revision"]
                source = "PERSISTED_DAILY_RESEARCH_UNIVERSE"
                availability = "Showing a stored daily research universe."
            else:
                availability = "No daily refresh is stored yet; showing saved research snapshot."
        except Exception:
            # No initialization/DDL on a dashboard read; never expose database details.
            availability = "Daily refresh unavailable; showing saved research snapshot."
    if report is None:
        report = json.loads(Path(path or SNAPSHOT_PATH).read_text(encoding="utf-8"))
    validate_report(report)
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    target_matches = report["target_date"] == today
    if not target_matches:
        availability += " This snapshot is for a different trading date."
    return {"source": source, "live": False, "execution_enabled": False,
            "snapshot": report, "revision": revision, "availability": availability,
            "target_matches_today": target_matches}
