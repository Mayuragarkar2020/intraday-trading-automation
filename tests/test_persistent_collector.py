from datetime import datetime
from zoneinfo import ZoneInfo
from src.cloud_collector import PersistentScanCollector
from src.scan_store import ScanStore
from src.candle_input import BatchInput
from tests.test_cloud_collector import batch

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
