"""Read-only scan-worker orchestration; intentionally no broker adapter.

An input publisher must atomically replace the dataset file with a complete
validated batch. This worker never fetches market data or submits orders.
"""
import json
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from src.candle_input import BatchInput
from src.cloud_collector import PersistentScanCollector,eligible_close
from src.scan_store import ScanStore
from src.candle_inbox import CandleInbox

IST=ZoneInfo("Asia/Kolkata")

def read_batch(path):
    source=Path(path)
    if not source.is_file():
        raise FileNotFoundError("No candle dataset available")
    if source.stat().st_size>2_000_000:
        raise ValueError("Dataset exceeds 2MB")
    return BatchInput.model_validate_json(source.read_text(encoding="utf-8"))

def cycle(now,dataset_path,collector):
    close=eligible_close(now)
    if close is None:
        return {"status":"OUTSIDE_SESSION","execution_enabled":False}
    try:
        batch=read_batch(dataset_path)
    except (FileNotFoundError,ValueError) as exc:
        return {"status":"DATA_UNAVAILABLE","execution_enabled":False}
    return collector.scan(now,batch)

def database_cycle(now,inbox,collector):
    close=eligible_close(now)
    if close is None:return {"status":"OUTSIDE_SESSION","execution_enabled":False}
    batch=inbox.fetch(close.isoformat())
    if batch is None:return {"status":"WAIT_FOR_COMPLETE_CANDLES","execution_enabled":False}
    return collector.scan(now,batch)

def main():
    url=os.getenv("SCAN_DATABASE_URL")
    if not url:
        raise SystemExit("SCAN_DATABASE_URL required; no market-data connector is bundled")
    if not url.startswith(("postgresql://","postgres://")):
        raise SystemExit("Cloud worker requires persistent Postgres; refuse ephemeral SQLite")
    collector=PersistentScanCollector(ScanStore(url))
    inbox=CandleInbox(url)
    inbox.initialize()
    while True:
        try:
            outcome=database_cycle(datetime.now(IST),inbox,collector)
            print(json.dumps({"status":outcome["status"],"execution_enabled":False}),flush=True)
        except Exception as exc:
            # Do not pretend this cycle succeeded; next loop retries. No trade execution is possible.
            print(json.dumps({"status":"ERROR","exception_type":type(exc).__name__,
                              "execution_enabled":False}),flush=True)
        time.sleep(15)

if __name__=="__main__":
    main()
