import os
import json
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from app.db.database import get_db
from app.db import crud
from app.db.models import ModelMetric, Prediction, Review
from app.schemas import StatsResponse, ModelMetricResponse
from app.ml.keywords import extract_keywords

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, "models")
DATASET_INFO_PATH = os.path.join(BASE_DIR, "data", "processed", "dataset_info.json")


def _get_dataset_info():
    if os.path.exists(DATASET_INFO_PATH):
        try:
            with open(DATASET_INFO_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


@router.get("/", response_model=StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    stats = crud.get_stats(db)
    metrics_db = db.query(ModelMetric).all()
    metrics = [
        ModelMetricResponse(
            model_name=m.model_name,
            accuracy=m.accuracy,
            precision=m.precision,
            recall=m.recall,
            macro_precision=getattr(m, 'macro_precision', m.precision),
            macro_recall=getattr(m, 'macro_recall', m.recall),
            f1=m.f1,
            macro_f1=getattr(m, 'macro_f1', m.f1),
            weighted_precision=getattr(m, 'weighted_precision', None),
            weighted_recall=getattr(m, 'weighted_recall', None),
            weighted_f1=m.weighted_f1,
            latency=m.latency
        )
        for m in metrics_db
    ]

    keywords = extract_keywords(MODELS_DIR, top_n=10)
    dataset_info = _get_dataset_info()

    return {
        "total_reviews": stats["total_reviews"],
        "total_predictions": stats["total_predictions"],
        "model_metrics": metrics,
        "top_keywords": keywords,
        "sentiment_distribution": dataset_info.get("class_distribution"),
        "rating_distribution": dataset_info.get("rating_distribution")
    }


@router.get("/sentiment-distribution")
def get_sentiment_distribution(db: Session = Depends(get_db)):
    dataset_info = _get_dataset_info()
    if "class_distribution" in dataset_info:
        return dataset_info["class_distribution"]

    # Fallback to database predictions
    counts = {}
    for row in db.query(Prediction.sentiment).all():
        s = row[0]
        counts[s] = counts.get(s, 0) + 1
    return counts


@router.get("/rating-distribution")
def get_rating_distribution():
    dataset_info = _get_dataset_info()
    return dataset_info.get("rating_distribution", {})


@router.get("/products")
def get_product_stats(db: Session = Depends(get_db)):
    products = db.query(Review.product).distinct().all()
    res = []
    for p in products:
        p_name = p[0] or "General"
        count = db.query(Review).filter(Review.product == p[0]).count()
        res.append({"product": p_name, "review_count": count})
    return res


@router.get("/keywords/{sentiment}")
def get_keywords_by_sentiment(sentiment: str, top_k: int = Query(default=20)):
    keywords_dict = extract_keywords(MODELS_DIR, top_n=top_k)
    s_clean = sentiment.lower().strip()
    words = keywords_dict.get(s_clean, [])
    # Return formatted list of dicts for frontend compatibility
    return [{"word": w, "score": 1.0} for w in words]


@router.get("/keywords/keybert")
def get_keybert_keywords(
    sentiment: Optional[str] = Query(default=None),
    top_k: int = Query(default=10),
    db: Session = Depends(get_db)
):
    """Extract semantic keyphrases using KeyBERT transformer embeddings."""
    try:
        from app.ml.keybert_extractor import extract_keybert_keywords, is_keybert_available
        if not is_keybert_available():
            return {"status": "unavailable", "keywords": []}

        query = db.query(Review.text)
        if sentiment:
            query = query.join(Prediction, Prediction.review_id == Review.id)\
                         .filter(Prediction.sentiment == sentiment.lower())
        texts = [r[0] for r in query.limit(100).all() if r[0]]
        if len(texts) < 5:
            csv_path = os.path.join(BASE_DIR, "data", "processed", "amazon_all_beauty_reviews.csv")
            if os.path.exists(csv_path):
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_path, nrows=3000)
                    if sentiment and "sentiment" in df.columns:
                        sub = df[df["sentiment"].str.lower() == sentiment.lower()]
                    else:
                        sub = df
                    if not sub.empty:
                        texts = sub["text"].dropna().sample(min(len(sub), 50), random_state=42).tolist()
                except Exception:
                    pass
        if not texts:
            texts = [
                "Great hydrating serum for glowing sensitive skin",
                "Pump broke after two uses and product leaked in packaging",
                "Average moisturizer, nothing special, mild scent"
            ]
        kws = extract_keybert_keywords(texts, top_n=top_k)
        return {"status": "ok", "sentiment": sentiment or "all", "keywords": kws}
    except Exception as e:
        return {"status": "error", "message": str(e), "keywords": []}

