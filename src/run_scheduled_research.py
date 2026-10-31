"""One-shot scheduled research task. Does not persist tokens or place orders.

Fails closed until reviewed Dhan publisher and database wiring are complete.
"""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from src.market_schedule import research_window

def main():
    now=datetime.now(ZoneInfo("Asia/Kolkata"))
    active,reason=research_window(now)
    if not active:
        print(json.dumps({"status":reason,"execution_enabled":False}),flush=True)
        return 0
    if not os.getenv("SCAN_DATABASE_URL") or not os.getenv("DHAN_ACCESS_TOKEN"):
        print(json.dumps({"status":"DATA_PUBLISHER_NOT_CONFIGURED",
                          "execution_enabled":False}),flush=True)
        return 0
    # A future publisher must be verified and intentionally enabled before any
    # broker calls. Merely provisioning a cron must never imply trading.
    print(json.dumps({"status":"PUBLISHER_NOT_APPROVED",
                      "execution_enabled":False}),flush=True)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
