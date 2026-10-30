from fastapi.testclient import TestClient
from src.cloud_app import app

client=TestClient(app)

def test_health_is_read_only():
    r=client.get("/health")
    assert r.status_code==200
    assert r.json()["execution_enabled"] is False

def test_dashboard_private_by_default(monkeypatch):
    monkeypatch.delenv("COCKPIT_ACCESS_TOKEN",raising=False)
    assert client.get("/api/status").status_code==401
    assert client.post("/api/preview",json={}).status_code==401

def test_preview_is_auth_only_and_never_trades(monkeypatch):
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","test-only-secret")
    data={"symbol":"RELIANCE","entry":"1000","initial_stop":"990",
          "estimated_round_trip_cost_per_share":"2"}
    result=client.post("/api/preview",json=data,headers={"X-Access-Token":"test-only-secret"})
    assert result.status_code==200
    assert result.json()["quantity"]==816
    assert result.json()["execution_enabled"] is False
    assert client.post("/api/orders",json=data,headers={"X-Access-Token":"test-only-secret"}).status_code==404
