from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_predict_ticket():
    response = client.post("/api/predict", json={
        "text": "I was charged twice and need a duplicate payment reversed today."
    })
    assert response.status_code == 200
    body = response.json()
    assert body["category"] in ["Account Access", "Billing", "Feature Request", "Security", "Service Outage", "Technical Issue"]
    assert body["priority"] in ["low", "medium", "high"]
    assert 0 <= body["category_confidence"] <= 1
    assert "keywords" in body

def test_short_ticket_rejected():
    response = client.post("/api/predict", json={"text": "help"})
    assert response.status_code == 422

def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "category_accuracy" in response.json()
