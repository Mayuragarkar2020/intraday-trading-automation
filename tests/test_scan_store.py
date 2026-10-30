import pytest
from fastapi.testclient import TestClient
from src.cloud_app import app
from src.scan_store import ScanStore

def test_store_atomic_no_duplicate(tmp_path):
    s=ScanStore("sqlite:///"+str(tmp_path/"scans.db"))
    s.initialize()
    original=[{"symbol":"RELIANCE","status":"WAIT"}]
    assert s.commit_scan("2026-11-02T09:45:00+05:30",original)
    assert not s.commit_scan("2026-11-02T09:45:00+05:30",[{"symbol":"INFY"}])
    assert s.latest()["setups"]==original

def test_latest_scan_authenticated_and_read_only(tmp_path,monkeypatch):
    url="sqlite:///"+str(tmp_path/"cloud.db")
    s=ScanStore(url);s.initialize()
    s.commit_scan("2026-11-02T09:45:00+05:30",[{"symbol":"RELIANCE","status":"BLOCK"}])
    monkeypatch.setenv("SCAN_DATABASE_URL",url)
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test-token")
    client=TestClient(app)
    assert client.get("/api/latest-scan").status_code==401
    result=client.get("/api/latest-scan",headers={"X-Access-Token":"test-token"})
    assert result.status_code==200
    assert result.json()["execution_enabled"] is False
    assert result.json()["snapshot"]["setups"][0]["symbol"]=="RELIANCE"

def test_no_database_returns_clear_state(monkeypatch):
    monkeypatch.delenv("SCAN_DATABASE_URL",raising=False)
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test-token")
    res=TestClient(app).get("/api/latest-scan",headers={"X-Access-Token":"test-token"})
    assert res.json()["status"]=="STORE_NOT_CONFIGURED"
