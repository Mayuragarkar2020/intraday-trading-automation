from fastapi.testclient import TestClient
from src.cloud_app import app

def test_ui_has_read_only_dhan_probe():
    response=TestClient(app).get("/")
    assert response.status_code==200
    assert 'id="dhanStatus"' in response.text
    assert 'id="dhanProbe"' in response.text
    assert '/api/dhan-history-probe' in response.text
    assert 'No orders are submitted' in response.text
    assert 'id="dhanProbe" disabled' in response.text
