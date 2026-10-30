from fastapi.testclient import TestClient
from src.cloud_app import app
client=TestClient(app)

def test_scan_requires_auth(monkeypatch):
    monkeypatch.delenv("COCKPIT_ACCESS_TOKEN",raising=False)
    assert client.post("/api/scan-candles",json={"candidates":[]}).status_code==401

def test_scan_rejects_missing_dataset(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test")
    r=client.post("/api/scan-candles",headers={"X-Access-Token":"test"},
                  json={"candidates":[{"symbol":"RELIANCE"}]})
    assert r.status_code==422

def test_scan_rejects_unknown_fields(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test")
    r=client.post("/api/scan-candles",headers={"X-Access-Token":"test"},
                  json={"candidates":[],"execute_orders":True})
    assert r.status_code==422

def test_no_live_order_endpoint():
    assert client.post("/api/orders",json={}).status_code==404
