from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from fastapi.testclient import TestClient
from src.dhan_candle_audit import audit_candles
from src.cloud_app import app
import src.cloud_app as cloud

IST=ZoneInfo("Asia/Kolkata")
def sample(missing=None):
    start=datetime(2026,10,29,9,15,tzinfo=IST)
    stamps=[int((start+timedelta(minutes=5*i)).timestamp()) for i in range(75) if i!=missing]
    n=len(stamps)
    return {"timestamp":stamps,"open":[100]*n,"high":[101]*n,
            "low":[99]*n,"close":[100]*n,"volume":[1000]*n}

def test_full_session():
    r=audit_candles(sample(),as_of=datetime(2026,10,30,16,0,tzinfo=IST),timestamps_are_open=True)
    assert r["all_sessions_complete"] is True
    assert r["sessions"][0]["received"]==75
    assert r["timestamp_convention_verified"] is False

def test_missing_midday_bar_reported():
    r=audit_candles(sample(20),as_of=datetime(2026,10,30,16,0,tzinfo=IST),timestamps_are_open=True)
    assert r["all_sessions_complete"] is False
    assert r["sessions"][0]["missing_count"]==1
    assert "11:00" in r["sessions"][0]["first_missing"]

def test_authenticated_endpoint_never_places_orders(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","cockpit-secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","dhan-secret")
    monkeypatch.setattr(cloud,"fetch_intraday",lambda *a,**k:sample())
    client=TestClient(app)
    args={"security_id":"2885","from_date":"2026-10-28 09:15:00",
          "to_date":"2026-10-30 15:30:00","interval":5,"timestamps_are_open":True}
    assert client.post("/api/dhan-candle-audit",json=args).status_code==401
    r=client.post("/api/dhan-candle-audit",json=args,headers={"X-Access-Token":"cockpit-secret"})
    assert r.json()["status"]=="AUDITED"
    assert r.json()["execution_enabled"] is False
    assert "dhan-secret" not in r.text
    assert client.post("/api/orders",json={}).status_code==404
