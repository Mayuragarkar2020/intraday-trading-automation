from datetime import datetime
from zoneinfo import ZoneInfo
from src.cloud_collector import PersistentScanCollector
from src.scan_store import ScanStore
from src.candle_input import BatchInput

def batch():
    bar=lambda t:{"time":t,"open":"100","high":"101","low":"99","close":"100","volume":1000}
    current=[bar("2026-11-02T09:%02d:00+05:30"%m) for m in (20,25,30)]
    from datetime import date,timedelta
    d=date(2026,10,30)
    prior=[]
    while len(prior)<20:
        if d.weekday()<5:
            prior.append([bar(d.isoformat()+"T09:%02d:00+05:30"%m) for m in (20,25,30)])
        d-=timedelta(days=1)
    htf=[bar("2026-10-30T09:30:00+05:30") for _ in range(21)]
    return BatchInput.model_validate({"candidates":[{"symbol":"RELIANCE",
        "completed_5m":current,"previous_sessions":prior,
        "completed_15m":htf,"ema_warmup_closes":["99"]*20}]})

def test_persistent_collector_saves_and_deduplicates(tmp_path):
    store=ScanStore("sqlite:///"+str(tmp_path/"persistent.db"))
    worker=PersistentScanCollector(store)
    now=datetime(2026,11,2,9,30,15,tzinfo=ZoneInfo("Asia/Kolkata"))
    first=worker.scan(now,batch())
    assert first["status"]=="SCANNED"
    assert store.latest()["setups"][0]["symbol"]=="RELIANCE"
    second=PersistentScanCollector(store).scan(now,batch())
    assert second["status"]=="ALREADY_SCANNED"
    assert len(store.latest()["setups"])==1
