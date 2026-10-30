from fastapi.testclient import TestClient
from src.cloud_app import app
from src.candle_pipeline import scan_demo
def test_demo_scanner_computed_not_hardcoded_orders():
    items=scan_demo()
    assert len(items)==3
    assert all(x["mode"]=="SYNTHETIC_DEMO" for x in items)
    assert items[0]["status"]=="ARMED",items[0]
    assert float(items[0]["entry"])>float(items[0]["stop"])
    assert items[1]["status"]=="WAIT"
    assert items[2]["reason"]=="RELATIVE_VOLUME_INSUFFICIENT"
def test_demo_feed_auth_and_preview_only(monkeypatch):
    client=TestClient(app)
    assert client.get("/api/demo-setups").status_code==401
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN","synthetic-secret")
    data=client.get("/api/demo-setups",headers={"X-Access-Token":"synthetic-secret"})
    assert data.status_code==200
    assert data.json()["live"] is False
    assert data.json()["execution_enabled"] is False
