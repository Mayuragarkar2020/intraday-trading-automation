from datetime import datetime
from zoneinfo import ZoneInfo
from src.candle_inbox import CandleInbox
from src.run_cloud_worker import database_cycle
from src.cloud_collector import PersistentScanCollector
from src.scan_store import ScanStore
from src.candle_input import BatchInput

def sample_batch():
    bar=lambda t:{"time":t,"open":"100","high":"101","low":"99","close":"100","volume":1000}
    latest=[bar(f"2026-11-02T09:{m:02d}:00+05:30") for m in (20,25,30)]
    from datetime import date,timedelta
    d=date(2026,10,30);previous=[]
    while len(previous)<20:
        if d.weekday()<5:
            previous.append([bar(f"{d.isoformat()}T09:{m:02d}:00+05:30") for m in (20,25,30)])
        d-=timedelta(days=1)
    htf=[bar("2026-10-30T09:30:00+05:30") for _ in range(21)]
    return BatchInput.model_validate({"candidates":[{"symbol":"RELIANCE","completed_5m":latest,
            "previous_sessions":previous,"completed_15m":htf,"ema_warmup_closes":["99"]*20}]})

def test_candle_inbox_publish_fetch_duplicate(tmp_path):
    inbox=CandleInbox("sqlite:///"+str(tmp_path/"data.db"));inbox.initialize()
    batch=sample_batch()
    assert inbox.publish(batch)["status"]=="PUBLISHED"
    assert inbox.publish(batch)["status"]=="ALREADY_EXISTS"
    assert inbox.fetch("2026-11-02T09:30:00+05:30").candidates[0].symbol=="RELIANCE"
    assert inbox.fetch("2026-11-02T09:35:00+05:30") is None

def test_worker_reads_shared_store_and_commits_one_snapshot(tmp_path):
    uri="sqlite:///"+str(tmp_path/"shared.db")
    inbox=CandleInbox(uri);inbox.initialize()
    store=ScanStore(uri)
    worker=PersistentScanCollector(store)
    now=datetime(2026,11,2,9,30,15,tzinfo=ZoneInfo("Asia/Kolkata"))
    assert database_cycle(now,inbox,worker)["status"]=="WAIT_FOR_COMPLETE_CANDLES"
    inbox.publish(sample_batch())
    assert database_cycle(now,inbox,worker)["status"]=="SCANNED"
    assert database_cycle(now,inbox,worker)["status"]=="ALREADY_SCANNED"
    assert store.latest()["setups"][0]["symbol"]=="RELIANCE"
