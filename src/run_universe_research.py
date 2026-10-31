"""Opt-in replacement path in the EXISTING research cron. Research only."""
from datetime import datetime,time
import json
import os

from src.forward_capture import ForwardCaptureStore,IST
from src.market_schedule import research_window
from src.research_cycle import run_cycle
from src.run_forward_capture import capture_once
from src.scan_store import ScanStore
from src.universe_scanner import UniverseScanStore,run_universe_scan,warm_universe_references
from src.universe_store import UniverseStore


def execute_cycle(now,url,token,*,capture_enabled=False):
    """Existing daily publication, cached full-pool scan, existing RELIANCE capture."""
    universe = UniverseStore(url)
    if now.astimezone(IST).time() < time(9,15):
        # Retain the existing same-day pre-market publication and no-late-rebuild policy.
        refresh = run_cycle(now,universe,ScanStore(url),None)
        if refresh["status"] not in {"UNIVERSE_READY","UNIVERSE_REFRESHED"}:
            return refresh
    local = now.astimezone(IST)
    if local.time() < time(9,40):
        outcome = warm_universe_references(now,universe,UniverseScanStore(url),token)
    else:
        outcome = run_universe_scan(now,universe,UniverseScanStore(url),token)
    if capture_enabled:
        captured = capture_once(now,universe,ForwardCaptureStore(url),token)
        outcome["forward_capture"] = captured.get("report",{}).get("status",captured["status"])
    return outcome


def main():
    if os.getenv("UNIVERSE_SCAN_ENABLED") != "true":
        print(json.dumps({"status":"UNIVERSE_SCAN_DISABLED","execution_enabled":False}))
        return 0
    now = datetime.now(IST)
    capture_enabled = os.getenv("FORWARD_CAPTURE_ENABLED") == "true"
    active,reason = research_window(now,start=time(8,30),end=time(15,25) if capture_enabled else time(11,40))
    if not active:
        print(json.dumps({"status":reason,"execution_enabled":False}))
        return 0
    url = os.getenv("SCAN_DATABASE_URL","")
    if not url.startswith(("postgresql://","postgres://")):
        print(json.dumps({"status":"UNIVERSE_SCAN_STORE_REQUIRED","execution_enabled":False}))
        return 1
    try:
        result = execute_cycle(now,url,os.getenv("DHAN_ACCESS_TOKEN"),capture_enabled=capture_enabled)
        report = result.get("report",{})
        print(json.dumps({"status":result["status"],"mode":report.get("mode"),
            "selected_count":report.get("selected_count"),"summary":report.get("summary"),
            "coverage_complete":report.get("coverage_complete"),"broker_requests":report.get("broker_requests"),
            "forward_capture":result.get("forward_capture"),"execution_enabled":False,"forward_paper_ready":False}))
        return 0
    except Exception as exc:
        print(json.dumps({"status":"UNIVERSE_SCAN_FAILED","error_type":type(exc).__name__,"execution_enabled":False}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

