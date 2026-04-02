"""API endpoint tests."""
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint."""
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
