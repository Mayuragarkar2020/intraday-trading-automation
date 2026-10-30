from fastapi.testclient import TestClient
from src.cloud_app import app
import src.cloud_app as module

def test_probe_auth_required(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","secret")
    assert TestClient(app).get("/api/dhan-status").status_code==401
    assert TestClient(app).post("/api/dhan-history-probe",json={}).status_code==401

def test_probe_without_dhan_token(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","secret")
    monkeypatch.delenv("DHAN_ACCESS_TOKEN",raising=False)
    cli=TestClient(app)
    r=cli.post("/api/dhan-history-probe",headers={"X-Access-Token":"secret"},json={
      "security_id":"1333","from_date":"2026-10-20 09:15:00",
      "to_date":"2026-10-21 15:30:00","interval":5})
    assert r.status_code==200
    assert r.json()["status"]=="DHAN_TOKEN_NOT_CONFIGURED"
    assert r.json()["execution_enabled"] is False

def test_probe_sanitized_success(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","secret")
    monkeypatch.setenv("DHAN_ACCESS_TOKEN","never-return-this")
    def fake_fetch(token,security_id,interval,from_date,to_date):
        assert token=="never-return-this"
        return {"timestamp":[100,200],"open":[1,1],"high":[1,1],
                "low":[1,1],"close":[1,1],"volume":[10,10]}
    monkeypatch.setattr(module,"fetch_intraday",fake_fetch)
    r=TestClient(app).post("/api/dhan-history-probe",headers={"X-Access-Token":"secret"},json={
      "security_id":"1333","from_date":"2026-10-20 09:15:00",
      "to_date":"2026-10-21 15:30:00","interval":5})
    assert r.status_code==200
    assert r.json()["candle_count"]==2
    assert "never-return-this" not in r.text
    assert r.json()["timestamp_convention_verified"] is False
    assert TestClient(app).post("/api/orders",json={}).status_code==404
