"""
places.py
─────────
FastAPI router for Google Places live review search, normalization, and inference.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import hashlib
import os
import joblib
from app.services import google_places
from app.ml.preprocessing import clean_text

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Load model artifacts
vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib'))
loaded_models = {
    'logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'logistic_regression.joblib')),
    'balanced_logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'balanced_logistic_regression.joblib')),
    'linearsvc': joblib.load(os.path.join(MODELS_DIR, 'linearsvc.joblib'))
}


@router.get("/search")
def search_places(query: str = Query(..., min_length=1), api_key: Optional[str] = None):
    """Search for places / businesses by query."""
    result = google_places.search_places_text(query, api_key=api_key)
    return result


@router.get("/{place_id}/analyze")
def analyze_place_reviews(
    place_id: str,
    model_name: Optional[str] = "balanced_logistic_regression",
    api_key: Optional[str] = None
):
    """
    Fetches live reviews for a place from Google Places API,
    normalizes them into the unified review schema, and applies
    OUR trained ML model for sentiment and aspect intelligence.
    """
    place_res = google_places.get_place_details(place_id, api_key=api_key)
    if not place_res.get("success"):
        return place_res

    place_data = place_res.get("place", {})
    raw_reviews = place_data.get("reviews", [])

    model_to_use = model_name if model_name in loaded_models else "balanced_logistic_regression"
    model = loaded_models[model_to_use]

    analyzed_reviews = []
    pos_count = 0
    neu_count = 0
    neg_count = 0
    mismatch_count = 0

    for r in raw_reviews:
        # Extract text from Google Place review object
        text_obj = r.get("text", {}) or r.get("originalText", {})
        review_text = text_obj.get("text", "").strip() if isinstance(text_obj, dict) else str(text_obj).strip()

        if not review_text:
            continue

        raw_rating = r.get("rating", 5.0)
        try:
            rating_val = float(raw_rating)
        except Exception:
            rating_val = 5.0

        author_info = r.get("authorAttribution", {})
        author_name = author_info.get("displayName", "Anonymous Google Reviewer")
        author_uri = author_info.get("uri", "")
        author_photo = author_info.get("photoUri", "")
        publish_time = r.get("relativePublishTimeDescription", "") or r.get("publishTime", "")

        # 1. Run OUR ML model inference on review text (never using rating as feature)
        cleaned = clean_text(review_text)
        if not cleaned.strip():
            pred = "neutral"
            conf = None
        else:
            feat = vectorizer.transform([cleaned])
            pred = model.predict(feat)[0]
            conf = None
            if hasattr(model, 'predict_proba'):
                conf = round(float(max(model.predict_proba(feat)[0])), 4)

        if pred == "positive":
            pos_count += 1
        elif pred == "negative":
            neg_count += 1
        else:
            neu_count += 1

        # 2. Rating - Sentiment Mismatch check
        is_mismatch = (
            (rating_val >= 4.0 and pred == "negative") or
            (rating_val <= 2.0 and pred == "positive")
        )
        if is_mismatch:
            mismatch_count += 1

        # Generate deterministic review ID
        rev_hash = hashlib.sha256(f"{place_id}_{author_name}_{review_text}".encode("utf-8")).hexdigest()[:16]

        analyzed_reviews.append({
            "review_id": f"g_{rev_hash}",
            "text": review_text,
            "title": "",
            "rating": rating_val,
            "product": place_data.get("name", "Unknown Place"),
            "category": "Local Business / Places",
            "price": "",
            "date": publish_time,
            "helpful_votes": 0,
            "verified_purchase": False,
            "sentiment": pred,
            "confidence": conf,
            "source": "google_places_api",
            "author_name": author_name,
            "author_uri": author_uri,
            "author_photo_uri": author_photo,
            "google_maps_uri": place_data.get("maps_uri", ""),
            "is_mismatch": is_mismatch,
            "clean_text": cleaned
        })

    total_analyzed = len(analyzed_reviews)
    pos_pct = round((pos_count / total_analyzed) * 100, 1) if total_analyzed > 0 else 0.0
    neu_pct = round((neu_count / total_analyzed) * 100, 1) if total_analyzed > 0 else 0.0
    neg_pct = round((neg_count / total_analyzed) * 100, 1) if total_analyzed > 0 else 0.0

    return {
        "success": True,
        "place_info": {
            "place_id": place_data.get("place_id"),
            "name": place_data.get("name"),
            "address": place_data.get("address"),
            "overall_rating": place_data.get("rating"),
            "user_rating_count": place_data.get("user_rating_count"),
            "maps_uri": place_data.get("maps_uri")
        },
        "model_used": model_to_use,
        "sentiment_pulse": {
            "total_reviews": total_analyzed,
            "positive_count": pos_count,
            "neutral_count": neu_count,
            "negative_count": neg_count,
            "positive_pct": pos_pct,
            "neutral_pct": neu_pct,
            "negative_pct": neg_pct,
            "mismatch_count": mismatch_count,
            "mismatch_pct": round((mismatch_count / total_analyzed) * 100, 1) if total_analyzed > 0 else 0.0
        },
        "reviews": analyzed_reviews,
        "attribution_note": "Reviews provided by Google Places API. Sentiment and aspect intelligence generated by our custom ML pipeline.",
        "limitation_note": "Live review availability and ordering are provided by Google Places API. Only the reviews returned by the API are analyzed by this application."
    }
