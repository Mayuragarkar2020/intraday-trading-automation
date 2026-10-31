from fastapi.testclient import TestClient
from src.cloud_app import app

def test_cockpit_is_mobile_friendly_preview_only():
    response=TestClient(app).get("/")
    assert response.status_code==200
    assert "text/html" in response.headers["content-type"]
    assert 'name="viewport"' in response.text
    assert "Execution is disabled." in response.text
    assert "No orders can be placed." in response.text
    assert "https://tv.dhan.co/" in response.text
    assert "https://tv.dhan.co/chart/?symbol=" not in response.text
    assert "Copy symbol" in response.text
    assert 'id="calc"' in response.text
    assert 'id="universeCsv"' in response.text
    assert "Indicative" in response.text or "indicative" in response.text
    assert response.headers["cache-control"]=="no-store"

def test_ui_never_provides_order_endpoint():
    client=TestClient(app)
    assert client.post("/api/orders",json={}).status_code==404
