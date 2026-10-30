from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from src.run_cloud_worker import cycle,read_batch,main

class Collector:
    def __init__(self):self.calls=0
    def scan(self,now,batch):
        self.calls+=1
        return {"status":"SCANNED","execution_enabled":False}

def test_closed_market_skips_dataset_loading(tmp_path):
    collector=Collector()
    result=cycle(datetime(2026,11,2,16,0,tzinfo=ZoneInfo("Asia/Kolkata")),
                 tmp_path/"missing.json",collector)
    assert result["status"]=="OUTSIDE_SESSION"
    assert collector.calls==0

def test_missing_data_fails_closed(tmp_path):
    collector=Collector()
    result=cycle(datetime(2026,11,2,9,45,15,tzinfo=ZoneInfo("Asia/Kolkata")),
                 tmp_path/"missing.json",collector)
    assert result["status"]=="DATA_UNAVAILABLE"
    assert collector.calls==0
    invalid=tmp_path/"bad.json"
    invalid.write_text("invalid json")
    assert cycle(datetime(2026,11,2,9,45,15,tzinfo=ZoneInfo("Asia/Kolkata")),invalid,collector)["status"]=="DATA_UNAVAILABLE"
    assert collector.calls==0

def test_no_database_prevents_cloud_start(monkeypatch):
    monkeypatch.delenv("SCAN_DATABASE_URL",raising=False)
    monkeypatch.delenv("SCAN_DATASET_PATH",raising=False)
    with pytest.raises(SystemExit):
        main()

def test_ephemeral_sqlite_refused(monkeypatch):
    monkeypatch.setenv("SCAN_DATABASE_URL","sqlite:///tmp/foo.db")
    monkeypatch.setenv("SCAN_DATASET_PATH","/tmp/data.json")
    with pytest.raises(SystemExit,match="persistent Postgres"):
        main()
