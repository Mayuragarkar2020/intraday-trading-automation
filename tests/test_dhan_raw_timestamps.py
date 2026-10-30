from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from src.dhan_raw_timestamps import raw_timestamp_report
from fastapi.testclient import TestClient
from src.cloud_app import app
import src.cloud_app as cloud

def test_raw_report_no_shift():
    start=datetime(2026,10,29,9,15,tzinfo=ZoneInfo("Asia/Kolkata"))
    payload={"timestamp":[float((start+timedelta(minutes=5*i)).timestamp()) for i in range(3)]}
    r=raw_timestamp_report(payload)
    assert r["sessions"][0]["first_raw_ist"]==["09:15","09:20","09:25"]
    assert r["timestamp_convention_verified"] is False

def test_raw_endpoint_auth_and_no_orders(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","hidden")
    monkeypatch.setattr(cloud,"fetch_intraday",lambda *args,**kwargs:{"timestamp":[1793245500]})
    data={"security_id":"2885","from_date":"2026-10-28 09:15:00",
          "to_date":"2026-10-30 15:30:00","interval":5}
    client=TestClient(app)
    assert client.post("/api/dhan-raw-timestamps",json=data).status_code==401
    r=client.post("/api/dhan-raw-timestamps",json=data,headers={"X-Access-Token":"secret"})
    assert r.status_code==200
    assert "hidden" not in r.text
    assert client.post("/api/orders",json={}).status_code==404
