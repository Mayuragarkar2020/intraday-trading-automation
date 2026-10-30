from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from src.cloud_app import app
from src.dhan_historical_diagnostics import historical_diagnostics
import src.cloud_app as module

IST=ZoneInfo("Asia/Kolkata")
def payload():
    stamps=[]
    for d in (28,29,30):
        for i in range(75):
            dt=datetime(2026,10,d,9,15,tzinfo=IST)+timedelta(minutes=i*5)
            stamps.append(int(dt.timestamp()))
    n=len(stamps)
    return {"timestamp":stamps,"open":[100]*n,"high":[101]*n,
      "low":[99]*n,"close":[100]*n,"volume":[1000]*n}

def test_historical_ema_vwap_diagnostics():
    r=historical_diagnostics(payload(),timestamps_are_open=True,
                             as_of=datetime(2026,10,30,16,0,tzinfo=IST))
    assert r["status"]=="HISTORICAL_INDICATORS_ONLY"
    assert r["candle_count"]==225
    assert r["ema10"]=="100" and r["session_vwap"]=="100"
    assert r["setup_qualified"] is False
    assert r["timestamp_convention_verified"] is False

def test_analysis_private_and_read_only(monkeypatch):
    client=TestClient(app)
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","private")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","opaque-secret")
    values={"security_id":"2885","from_date":"2026-10-28 09:15:00",
      "to_date":"2026-10-30 15:30:00","interval":5,"timestamps_are_open":True}
    assert client.post("/api/dhan-historical-analysis",json=values).status_code==401
    monkeypatch.setattr(module,"fetch_intraday",lambda *a,**k:payload())
    r=client.post("/api/dhan-historical-analysis",json=values,
      headers={"X-Access-Token":"private"})
    assert r.status_code==200
    assert r.json()["status"]=="HISTORICAL_INDICATORS_ONLY"
    assert "opaque-secret" not in r.text
    assert client.post("/api/orders",json={}).status_code==404

def test_cockpit_has_diagnostic_button():
    r=TestClient(app).get("/")
    assert 'id="dhanAnalyze"' in r.text
    assert "Timestamp convention unverified" in r.text
