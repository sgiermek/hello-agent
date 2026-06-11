from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_index_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Hello, Agent's World!" in response.text
