from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Customer Sentiment API"}

def test_predict_sentiment():
    response = client.post("/predict/", json={"text": "This is terrible!", "model_name": "linearsvc"})
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data
    assert "review_id" in data
    assert data["model_used"] == "linearsvc"

def test_predict_empty_text():
    response = client.post("/predict/", json={"text": "   "})
    assert response.status_code == 400

def test_get_stats():
    response = client.get("/stats/")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "model_metrics" in data
