from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_models():
    response = client.get("/models")
    assert response.status_code == 200
    models = response.json()
    assert isinstance(models, list)
    assert "logistic_regression" in models
    assert "balanced_logistic_regression" in models
    assert "linearsvc" in models


def test_model_metrics():
    response = client.get("/models/metrics")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    for m in data:
        assert "model_name" in m
        assert "accuracy" in m
        assert "f1" in m
        assert "latency" in m


def test_predict_sentiment_linearsvc():
    response = client.post("/predict/", json={"text": "This serum is absolute magic for glowing skin!", "model_name": "linearsvc"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "positive"
    assert "review_id" in data
    assert data["model_used"] == "linearsvc"
    # LinearSVC should not return artificial probability
    assert data["confidence"] is None


def test_predict_sentiment_balanced_lr():
    response = client.post("/predict/", json={"text": "Terrible rash, smelled like burning plastic and arrived broken.", "model": "balanced_logistic_regression"})
    assert response.status_code == 200
    data = response.json()
    assert data["sentiment"] == "negative"
    assert "review_id" in data
    assert data["confidence"] is not None
    assert 0.0 <= data["confidence"] <= 1.0


def test_predict_batch():
    texts = [
        "Love this lotion, highly recommended!",
        "Defective pump and ruined my clothes.",
        "Average product, neither great nor bad."
    ]
    response = client.post("/predict/batch", json={"texts": texts, "model": "logistic_regression"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["sentiment"] == "positive"
    assert data[1]["sentiment"] == "negative"


def test_predict_empty_text():
    response = client.post("/predict/", json={"text": "   "})
    assert response.status_code == 400


def test_get_stats():
    response = client.get("/stats/")
    assert response.status_code == 200
    data = response.json()
    assert "total_reviews" in data
    assert "total_predictions" in data
    assert "model_metrics" in data
    assert "top_keywords" in data


def test_get_sentiment_distribution():
    response = client.get("/stats/sentiment-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "positive" in data
    assert "negative" in data


def test_get_keywords():
    response = client.get("/stats/keywords/positive?top_k=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_places_search_missing_key():
    response = client.get("/places/search?query=Coffee+Shop")
    assert response.status_code == 200
    data = response.json()
    # Missing key must return graceful structured response without crashing
    assert data["success"] is False
    assert data["error"] == "API_KEY_MISSING"


def test_places_analyze_missing_key():
    response = client.get("/places/ChIJ12345/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "API_KEY_MISSING"


def test_places_analyze_mock_reviews():
    """Verify live review normalization and ML model sentiment analysis with mocked Places API."""
    mock_place_data = {
        "success": True,
        "place": {
            "place_id": "ChIJ_mock_123",
            "name": "Artisan Coffee Roasters",
            "address": "123 Indiranagar, Bangalore",
            "rating": 4.5,
            "user_rating_count": 250,
            "maps_uri": "https://maps.google.com/?cid=123",
            "reviews": [
                {
                    "text": {"text": "Best cappuccino in Bangalore, wonderful ambiance and quick service!"},
                    "rating": 5.0,
                    "relativePublishTimeDescription": "2 days ago",
                    "authorAttribution": {"displayName": "John Doe", "uri": "https://maps.google.com/user/1"}
                },
                {
                    "text": {"text": "Extremely rude staff and our order took 45 minutes to arrive."},
                    "rating": 1.0,
                    "relativePublishTimeDescription": "a week ago",
                    "authorAttribution": {"displayName": "Jane Smith", "uri": "https://maps.google.com/user/2"}
                }
            ]
        }
    }

    with patch("app.services.google_places.get_place_details", return_value=mock_place_data):
        response = client.get("/places/ChIJ_mock_123/analyze?model_name=balanced_logistic_regression&api_key=mock_key")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["place_info"]["name"] == "Artisan Coffee Roasters"
        assert len(data["reviews"]) == 2
        
        # Check first review analyzed with our model
        r1 = data["reviews"][0]
        assert r1["sentiment"] == "positive"
        assert r1["source"] == "google_places_api"
        assert r1["author_name"] == "John Doe"

        # Check second review analyzed with our model
        r2 = data["reviews"][1]
        assert r2["sentiment"] == "negative"
        assert r2["source"] == "google_places_api"

        # Check pulse metrics
        pulse = data["sentiment_pulse"]
        assert pulse["total_reviews"] == 2
        assert pulse["positive_count"] == 1
        assert pulse["negative_count"] == 1
        assert pulse["positive_pct"] == 50.0
        assert pulse["negative_pct"] == 50.0
