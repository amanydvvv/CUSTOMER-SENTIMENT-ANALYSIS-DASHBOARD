import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_auth_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@sentiment.io", "password": "admin123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


def test_predict_endpoint():
    response = client.post(
        "/api/v1/predict",
        json={
            "text": "The espresso machine is fast and makes great frothy coffee!",
            "model_preference": "auto",
            "extract_aspects": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert "confidence" in data
    assert "aspects" in data


def test_analytics_summary_endpoint():
    response = client.get("/api/v1/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_feedback" in data
    assert "positive_pct" in data
    assert "negative_pct" in data


def test_feedback_listing_endpoint():
    response = client.get("/api/v1/feedback?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
