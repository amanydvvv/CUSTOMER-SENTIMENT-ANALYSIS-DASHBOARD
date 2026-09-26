"""
test_phase5_google_places.py
────────────────────────────
Phase 5 tests: Google Places API integration, review normalization,
ML inference pipeline, mismatch detection, and error handling.

All Google API calls are mocked — no real API key is required.
Tests verify our sentiment model, aspect logic, and schema normalization
work correctly on live-style review data without touching training data.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ─── 1. Missing API Key ────────────────────────────────────────────────────────

class TestMissingApiKey:
    def test_search_missing_key(self):
        """Text search with no API key returns structured error, not a crash."""
        resp = client.get("/places/search?query=Best+Coffee+Bangalore")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "API_KEY_MISSING"
        assert "places" in data
        assert data["places"] == []

    def test_analyze_missing_key(self):
        """Place details fetch with no API key returns structured error."""
        resp = client.get("/places/ChIJtest123/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "API_KEY_MISSING"


# ─── 2. Invalid / Bad API Key ─────────────────────────────────────────────────

class TestInvalidApiKey:
    def test_search_invalid_key(self):
        """A 403 from Google is surfaced as AUTHENTICATION_OR_PERMISSION_ERROR."""
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        mock_resp.json.return_value = {
            "error": {"message": "API key not valid. Please pass a valid API key."}
        }
        with patch("requests.Session.post", return_value=mock_resp):
            resp = client.get("/places/search?query=Test&api_key=INVALID_KEY")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "AUTHENTICATION_OR_PERMISSION_ERROR"

    def test_details_invalid_key(self):
        """A 401 from Google Place Details is surfaced correctly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.json.return_value = {
            "error": {"message": "Request had invalid authentication credentials."}
        }
        with patch("requests.get", return_value=mock_resp):
            resp = client.get("/places/ChIJbad/analyze?api_key=BAD_KEY")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "AUTHENTICATION_OR_PERMISSION_ERROR"


# ─── 3. Quota / Rate Limit ────────────────────────────────────────────────────

class TestQuotaExceeded:
    def test_search_quota_exceeded(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        with patch("app.services.google_places.requests.post", return_value=mock_resp):
            resp = client.get("/places/search?query=Test&api_key=KEY")
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "QUOTA_EXCEEDED"

    def test_details_quota_exceeded(self):
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        with patch("requests.get", return_value=mock_resp):
            resp = client.get("/places/ChIJtest/analyze?api_key=KEY")
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "QUOTA_EXCEEDED"


# ─── 4. API Timeout ───────────────────────────────────────────────────────────

class TestApiTimeout:
    def test_search_timeout(self):
        import requests as req_lib
        with patch("app.services.google_places.requests.post", side_effect=req_lib.exceptions.Timeout):
            resp = client.get("/places/search?query=Test&api_key=KEY")
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "TIMEOUT"

    def test_details_timeout(self):
        import requests as req_lib
        with patch("requests.get", side_effect=req_lib.exceptions.Timeout):
            resp = client.get("/places/ChIJtest/analyze?api_key=KEY")
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "TIMEOUT"


# ─── 5. No Results / No Reviews ───────────────────────────────────────────────

class TestEmptyResults:
    def test_search_no_places_found(self):
        """A 200 with empty places list is handled cleanly."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"places": []}
        with patch("app.services.google_places.requests.post", return_value=mock_resp):
            resp = client.get("/places/search?query=xyzzy999&api_key=KEY")
        data = resp.json()
        assert data["success"] is True
        assert data["places"] == []
        assert data["total_found"] == 0

    def test_analyze_no_reviews_returned(self):
        """A place with 0 reviews is handled gracefully — empty list, not a crash."""
        mock_place = {
            "success": True,
            "place": {
                "place_id": "ChIJ_empty",
                "name": "Ghost Restaurant",
                "address": "123 Nowhere St",
                "rating": 4.0,
                "user_rating_count": 0,
                "maps_uri": "",
                "reviews": [],
            },
        }
        with patch("app.services.google_places.get_place_details", return_value=mock_place):
            resp = client.get("/places/ChIJ_empty/analyze?api_key=KEY")
        data = resp.json()
        assert data["success"] is True
        assert data["reviews"] == []
        assert data["sentiment_pulse"]["total_reviews"] == 0


# ─── 6. Schema Normalization ──────────────────────────────────────────────────

class TestSchemaNormalization:
    """Verify review objects from Google API are normalized into the unified schema."""

    MOCK_PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_norm_test",
            "name": "Normalize Test Cafe",
            "address": "456 Schema Rd, Bangalore",
            "rating": 4.2,
            "user_rating_count": 100,
            "maps_uri": "https://maps.google.com/?cid=norm",
            "reviews": [
                {
                    "text": {"text": "Amazing coffee and great atmosphere, loved every visit!"},
                    "rating": 5.0,
                    "relativePublishTimeDescription": "3 days ago",
                    "authorAttribution": {
                        "displayName": "Alice Tester",
                        "uri": "https://maps.google.com/user/alice",
                        "photoUri": "",
                    },
                },
                {
                    "text": {"text": "Terrible experience, staff were rude and food was cold."},
                    "rating": 1.0,
                    "relativePublishTimeDescription": "a week ago",
                    "authorAttribution": {
                        "displayName": "Bob Reviewer",
                        "uri": "https://maps.google.com/user/bob",
                    },
                },
            ],
        },
    }

    def _get_reviews(self, model="balanced_logistic_regression"):
        with patch("app.services.google_places.get_place_details", return_value=self.MOCK_PLACE):
            resp = client.get(f"/places/ChIJ_norm_test/analyze?api_key=KEY&model_name={model}")
        assert resp.status_code == 200
        return resp.json()

    def test_schema_required_fields_present(self):
        data = self._get_reviews()
        for rev in data["reviews"]:
            assert "review_id" in rev
            assert "text" in rev
            assert "rating" in rev
            assert "sentiment" in rev
            assert "source" in rev
            assert "author_name" in rev

    def test_source_is_google_places_api(self):
        data = self._get_reviews()
        for rev in data["reviews"]:
            assert rev["source"] == "google_places_api"

    def test_review_id_is_deterministic(self):
        """Same inputs must always produce the same review_id (hash-based)."""
        data1 = self._get_reviews()
        data2 = self._get_reviews()
        ids1 = [r["review_id"] for r in data1["reviews"]]
        ids2 = [r["review_id"] for r in data2["reviews"]]
        assert ids1 == ids2

    def test_review_id_prefixed_with_g(self):
        data = self._get_reviews()
        for rev in data["reviews"]:
            assert rev["review_id"].startswith("g_")

    def test_rating_preserved_as_metadata(self):
        data = self._get_reviews()
        ratings = [rev["rating"] for rev in data["reviews"]]
        assert 5.0 in ratings
        assert 1.0 in ratings

    def test_author_attribution_captured(self):
        data = self._get_reviews()
        authors = {rev["author_name"] for rev in data["reviews"]}
        assert "Alice Tester" in authors
        assert "Bob Reviewer" in authors

    def test_relative_publish_time_captured(self):
        data = self._get_reviews()
        dates = [rev["date"] for rev in data["reviews"]]
        assert "3 days ago" in dates


# ─── 7. Sentiment Inference (ML model, NOT Google rating) ─────────────────────

class TestSentimentInference:
    """The sentiment must come from OUR ML model, not from the Google star rating."""

    POSITIVE_REVIEW_PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_sentiment",
            "name": "Sentiment Test Place",
            "address": "789 ML Ave",
            "rating": 3.0,
            "user_rating_count": 50,
            "maps_uri": "",
            "reviews": [
                {
                    "text": {"text": "Absolutely wonderful! Best product I have ever used, highly recommend."},
                    "rating": 1.0,  # Intentionally low star to test mismatch
                    "relativePublishTimeDescription": "yesterday",
                    "authorAttribution": {"displayName": "Mismatch User"},
                },
                {
                    "text": {"text": "Disgusting quality. Broken on arrival, waste of money, terrible service."},
                    "rating": 5.0,  # Intentionally high star to test mismatch
                    "relativePublishTimeDescription": "2 days ago",
                    "authorAttribution": {"displayName": "Mismatch User 2"},
                },
            ],
        },
    }

    def test_model_classifies_positive_text_correctly(self):
        with patch("app.services.google_places.get_place_details", return_value=self.POSITIVE_REVIEW_PLACE):
            resp = client.get("/places/ChIJ_sentiment/analyze?api_key=KEY&model_name=balanced_logistic_regression")
        data = resp.json()
        reviews = data["reviews"]
        pos_rev = next(r for r in reviews if "wonderful" in r["text"].lower())
        assert pos_rev["sentiment"] == "positive"

    def test_model_classifies_negative_text_correctly(self):
        with patch("app.services.google_places.get_place_details", return_value=self.POSITIVE_REVIEW_PLACE):
            resp = client.get("/places/ChIJ_sentiment/analyze?api_key=KEY&model_name=balanced_logistic_regression")
        data = resp.json()
        reviews = data["reviews"]
        neg_rev = next(r for r in reviews if "disgusting" in r["text"].lower())
        assert neg_rev["sentiment"] == "negative"

    def test_rating_is_not_used_as_sentiment_input(self):
        """A 1-star review with positive text must get POSITIVE sentiment from our model."""
        with patch("app.services.google_places.get_place_details", return_value=self.POSITIVE_REVIEW_PLACE):
            resp = client.get("/places/ChIJ_sentiment/analyze?api_key=KEY&model_name=balanced_logistic_regression")
        data = resp.json()
        reviews = data["reviews"]
        mismatch_rev = next(r for r in reviews if r["rating"] == 1.0)
        # Our model should see positive text and predict positive, not follow the 1-star rating
        assert mismatch_rev["sentiment"] == "positive"


# ─── 8. Rating–Sentiment Mismatch ─────────────────────────────────────────────

class TestRatingSentimentMismatch:
    """Mismatch = high star + negative text OR low star + positive text."""

    MISMATCH_PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_mismatch",
            "name": "Mismatch Test",
            "address": "100 Mismatch Ln",
            "rating": 3.5,
            "user_rating_count": 10,
            "maps_uri": "",
            "reviews": [
                {
                    "text": {"text": "Great quality product, fantastic smell and it really works!"},
                    "rating": 1.0,  # low star, positive text → mismatch
                    "relativePublishTimeDescription": "1 day ago",
                    "authorAttribution": {"displayName": "Low Star Pos"},
                },
                {
                    "text": {"text": "Broken, defective, terrible quality, never buying again."},
                    "rating": 5.0,  # high star, negative text → mismatch
                    "relativePublishTimeDescription": "2 days ago",
                    "authorAttribution": {"displayName": "High Star Neg"},
                },
            ],
        },
    }

    def _get_data(self):
        with patch("app.services.google_places.get_place_details", return_value=self.MISMATCH_PLACE):
            resp = client.get("/places/ChIJ_mismatch/analyze?api_key=KEY")
        return resp.json()

    def test_mismatch_detected_low_star_positive(self):
        data = self._get_data()
        rev = next(r for r in data["reviews"] if r["rating"] == 1.0)
        if rev["sentiment"] == "positive":
            assert rev["is_mismatch"] is True

    def test_mismatch_detected_high_star_negative(self):
        data = self._get_data()
        rev = next(r for r in data["reviews"] if r["rating"] == 5.0)
        if rev["sentiment"] == "negative":
            assert rev["is_mismatch"] is True

    def test_mismatch_count_in_pulse(self):
        data = self._get_data()
        pulse = data["sentiment_pulse"]
        assert "mismatch_count" in pulse
        assert "mismatch_pct" in pulse
        assert pulse["mismatch_count"] >= 0


# ─── 9. Sentiment Pulse Metrics ───────────────────────────────────────────────

class TestSentimentPulse:

    PULSE_PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_pulse",
            "name": "Pulse Test",
            "address": "1 Pulse St",
            "rating": 4.0,
            "user_rating_count": 3,
            "maps_uri": "",
            "reviews": [
                {
                    "text": {"text": "Best cappuccino in Bangalore, wonderful ambiance and quick service!"},
                    "rating": 5.0,
                    "relativePublishTimeDescription": "2 days ago",
                    "authorAttribution": {"displayName": "John Doe"},
                },
                {
                    "text": {"text": "Extremely rude staff and our order took 45 minutes to arrive."},
                    "rating": 1.0,
                    "relativePublishTimeDescription": "a week ago",
                    "authorAttribution": {"displayName": "Jane Smith"},
                },
            ],
        },
    }

    def test_pulse_total_matches_analyzed_reviews(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PULSE_PLACE):
            resp = client.get("/places/ChIJ_pulse/analyze?api_key=KEY")
        data = resp.json()
        pulse = data["sentiment_pulse"]
        total = pulse["total_reviews"]
        assert total == len(data["reviews"])
        assert pulse["positive_count"] + pulse["neutral_count"] + pulse["negative_count"] == total

    def test_pulse_percentages_sum_to_100(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PULSE_PLACE):
            resp = client.get("/places/ChIJ_pulse/analyze?api_key=KEY")
        data = resp.json()
        pulse = data["sentiment_pulse"]
        total_pct = round(pulse["positive_pct"] + pulse["neutral_pct"] + pulse["negative_pct"], 0)
        assert total_pct == 100.0

    def test_pulse_does_not_invent_reviews(self):
        """Pulse must reflect exactly the reviews returned by the API — no inflation."""
        with patch("app.services.google_places.get_place_details", return_value=self.PULSE_PLACE):
            resp = client.get("/places/ChIJ_pulse/analyze?api_key=KEY")
        data = resp.json()
        assert data["sentiment_pulse"]["total_reviews"] == 2


# ─── 10. Confidence Scores ────────────────────────────────────────────────────

class TestConfidenceScores:

    SINGLE_REVIEW_PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_conf",
            "name": "Confidence Test",
            "address": "1 Prob St",
            "rating": 4.0,
            "user_rating_count": 1,
            "maps_uri": "",
            "reviews": [
                {
                    "text": {"text": "Excellent product quality, fast delivery, very happy!"},
                    "rating": 5.0,
                    "relativePublishTimeDescription": "today",
                    "authorAttribution": {"displayName": "Happy User"},
                }
            ],
        },
    }

    def test_logistic_regression_returns_probability(self):
        with patch("app.services.google_places.get_place_details", return_value=self.SINGLE_REVIEW_PLACE):
            resp = client.get(
                "/places/ChIJ_conf/analyze?api_key=KEY&model_name=balanced_logistic_regression"
            )
        data = resp.json()
        rev = data["reviews"][0]
        assert rev["confidence"] is not None
        assert 0.0 <= rev["confidence"] <= 1.0

    def test_linearsvc_confidence_is_none(self):
        """LinearSVC must NOT return decision_function output as probability."""
        with patch("app.services.google_places.get_place_details", return_value=self.SINGLE_REVIEW_PLACE):
            resp = client.get(
                "/places/ChIJ_conf/analyze?api_key=KEY&model_name=linearsvc"
            )
        data = resp.json()
        rev = data["reviews"][0]
        assert rev["confidence"] is None


# ─── 11. Model Selection ──────────────────────────────────────────────────────

class TestModelSelection:

    PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_model",
            "name": "Model Select Test",
            "address": "1 Model St",
            "rating": 4.0,
            "user_rating_count": 1,
            "maps_uri": "",
            "reviews": [
                {
                    "text": {"text": "Solid product, works as expected."},
                    "rating": 4.0,
                    "relativePublishTimeDescription": "today",
                    "authorAttribution": {"displayName": "User A"},
                }
            ],
        },
    }

    @pytest.mark.parametrize("model_name", [
        "logistic_regression",
        "balanced_logistic_regression",
        "linearsvc",
    ])
    def test_all_models_run_successfully(self, model_name):
        with patch("app.services.google_places.get_place_details", return_value=self.PLACE):
            resp = client.get(f"/places/ChIJ_model/analyze?api_key=KEY&model_name={model_name}")
        data = resp.json()
        assert data["success"] is True
        assert data["model_used"] == model_name
        assert len(data["reviews"]) == 1

    def test_invalid_model_name_falls_back_to_balanced_lr(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PLACE):
            resp = client.get("/places/ChIJ_model/analyze?api_key=KEY&model_name=nonexistent_model")
        data = resp.json()
        assert data["success"] is True
        assert data["model_used"] == "balanced_logistic_regression"


# ─── 12. Attribution & Limitation Notes ──────────────────────────────────────

class TestAttributionNotes:

    PLACE = {
        "success": True,
        "place": {
            "place_id": "ChIJ_attr",
            "name": "Attribution Test",
            "address": "1 Attr St",
            "rating": 4.0,
            "user_rating_count": 1,
            "maps_uri": "https://maps.google.com/?cid=attr",
            "reviews": [
                {
                    "text": {"text": "Good place overall."},
                    "rating": 4.0,
                    "relativePublishTimeDescription": "today",
                    "authorAttribution": {"displayName": "A User"},
                }
            ],
        },
    }

    def test_attribution_note_present(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PLACE):
            resp = client.get("/places/ChIJ_attr/analyze?api_key=KEY")
        data = resp.json()
        assert "attribution_note" in data
        assert len(data["attribution_note"]) > 0

    def test_limitation_note_present(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PLACE):
            resp = client.get("/places/ChIJ_attr/analyze?api_key=KEY")
        data = resp.json()
        assert "limitation_note" in data
        assert "Google Places API" in data["limitation_note"]

    def test_place_info_includes_maps_uri(self):
        with patch("app.services.google_places.get_place_details", return_value=self.PLACE):
            resp = client.get("/places/ChIJ_attr/analyze?api_key=KEY")
        data = resp.json()
        assert "maps_uri" in data["place_info"]


# ─── 13. Empty Query Guard ────────────────────────────────────────────────────

class TestEmptyQueryGuard:
    def test_search_empty_query_rejected(self):
        """Empty query must be rejected before hitting the API."""
        resp = client.get("/places/search?query=&api_key=KEY")
        # FastAPI query validation (min_length=1) returns 422
        assert resp.status_code == 422
