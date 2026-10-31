"""Finite scheduled Dhan research; no broker order capabilities."""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from src.market_schedule import research_window
from src.dhan_scheduled_pipeline import process_once
from src.scan_store import ScanStore

def main():
    now=datetime.now(ZoneInfo("Asia/Kolkata"))
    active,reason=research_window(now)
    if not active:
        print(json.dumps({"status":reason,"execution_enabled":False}),flush=True)
        return 0
    url=os.getenv("SCAN_DATABASE_URL")
    token=os.getenv("DHAN_ACCESS_TOKEN")
    if not url or not token or not url.startswith(("postgres://","postgresql://")):
        print(json.dumps({"status":"DATA_PUBLISHER_NOT_CONFIGURED",
                          "execution_enabled":False}),flush=True)
        return 0
    try:
        outcome=process_once(token,"2885","RELIANCE",now,ScanStore(url))
        # No raw prices, credentials or broker response bodies in scheduled logs.
        print(json.dumps({"status":outcome["status"],
                          "execution_enabled":False}),flush=True)
    except Exception as exc:
        print(json.dumps({"status":"DATA_PIPELINE_FAILED",
                          "error_type":type(exc).__name__,
                          "execution_enabled":False}),flush=True)
        return 1
    return 0

if __name__=="__main__":
    raise SystemExit(main())
