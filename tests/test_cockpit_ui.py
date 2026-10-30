from fastapi.testclient import TestClient
from src.cloud_app import app

def test_cockpit_is_mobile_friendly_preview_only():
    response=TestClient(app).get("/")
    assert response.status_code==200
    assert "text/html" in response.headers["content-type"]
    assert 'name="viewport"' in response.text
    assert "PREVIEW ONLY — NO ORDERS" in response.text
    assert "https://tv.dhan.co/chart/?symbol=" in response.text
    assert "cannot draw overlays" in response.text
    assert 'id="calc" disabled' in response.text
    assert "Approve trade — unavailable" in response.text
    assert response.headers["cache-control"]=="no-store"

def test_ui_never_provides_order_endpoint():
    client=TestClient(app)
    assert client.post("/api/orders",json={}).status_code==404
