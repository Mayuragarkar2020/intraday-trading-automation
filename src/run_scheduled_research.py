"""Finite pre-market refresh and intraday research; never submits orders."""
import json
import os
from datetime import datetime, time
from zoneinfo import ZoneInfo
from src.market_schedule import research_window
from src.research_cycle import run_cycle
from src.scan_store import ScanStore
from src.universe_store import UniverseStore

def main():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    active, reason = research_window(now, start=time(8,30), end=time(11,40))
    if not active:
        print(json.dumps({"status": reason, "execution_enabled": False}), flush=True)
        return 0
    url = os.getenv("SCAN_DATABASE_URL")
    if not url or not url.startswith(("postgres://", "postgresql://")):
        print(json.dumps({"status": "UNIVERSE_STORE_NOT_CONFIGURED",
                          "execution_enabled": False}), flush=True)
        return 0
    try:
        outcome = run_cycle(now, UniverseStore(url), ScanStore(url), os.getenv("DHAN_ACCESS_TOKEN"))
        print(json.dumps({"status": outcome["status"],
                          "execution_enabled": False}), flush=True)
    except Exception as exc:
        # Do not print connection URLs, API bodies, credentials or exception text.
        print(json.dumps({"status": "RESEARCH_CYCLE_FAILED",
                          "error_type": type(exc).__name__,
                          "execution_enabled": False}), flush=True)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
