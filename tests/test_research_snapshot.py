import json
import pytest
from src.research_snapshot import load_research_snapshot

def test_committed_live_download_snapshot_is_read_only():
    result = load_research_snapshot()
    snapshot = result["snapshot"]
    assert result["live"] is False and result["execution_enabled"] is False
    assert snapshot["summary"]["liquidity_candidate_count"] == 109
    assert snapshot["summary"]["reference_research_candidate_count"] == 106
    assert len(snapshot["sources"]) == 20
    assert snapshot["tradable_count"] == 0

@pytest.mark.parametrize("field,value", [
    ("execution_enabled", True), ("tradable_count", 1),
    ("mode", "LIVE"), ("restrictions_verified", True),
])
def test_unexpected_snapshot_mode_rejected(tmp_path, field, value):
    snapshot = load_research_snapshot()["snapshot"]
    snapshot[field] = value
    path = tmp_path/"unsafe.json"
    path.write_text(json.dumps(snapshot))
    with pytest.raises(ValueError):
        load_research_snapshot(path)

def test_authenticated_endpoint(monkeypatch):
    from fastapi.testclient import TestClient
    from src.cloud_app import app
    monkeypatch.setenv("COCKPIT_ACCESS_TOKEN", "research-test-token")
    client = TestClient(app)
    assert client.get("/api/universe-research").status_code == 401
    response = client.get("/api/universe-research", headers={"X-Access-Token": "research-test-token"})
    assert response.status_code == 200
    assert response.json()["snapshot"]["tradable_count"] == 0
