from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.api import predict, reviews, stats, places
from app.db.database import engine, Base, get_db
from app.db.models import ModelMetric
from app.schemas import ModelMetricResponse

# Ensure tables are created
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Feedback Intelligence API",
    description="FastAPI backend for real-time customer feedback intelligence, sentiment analysis, and model metrics.",
    version="2.0.0"
)

# Core feature routers
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])
app.include_router(places.router, prefix="/places", tags=["places"])


@app.get("/")
def root():
    return {"message": "Welcome to the Customer Feedback Intelligence API"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    import os
    from sqlalchemy import text

    # --- Check 1: Live database connectivity ---
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # --- Check 2: ML model artifact files ---
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
    expected = [
        "logistic_regression.joblib",
        "balanced_logistic_regression.joblib",
        "linearsvc.joblib",
        "tfidf_vectorizer.joblib"
    ]
    found   = [m for m in expected if os.path.exists(os.path.join(models_dir, m))]
    missing = [m for m in expected if m not in found]

    overall = "ok" if (db_status == "connected" and len(missing) == 0) else "degraded"

    return {
        "status": overall,
        "database": db_status,
        "models_dir": models_dir,
        "models_found": found,
        "models_missing": missing,
        "all_models_loaded": len(missing) == 0,
        "api_version": "2.0.0"
    }


@app.get("/models", response_model=List[str])
def list_available_models():
    return ["logistic_regression", "balanced_logistic_regression", "linearsvc"]


@app.get("/models/metrics", response_model=List[ModelMetricResponse])
def get_all_model_metrics(db: Session = Depends(get_db)):
    metrics_db = db.query(ModelMetric).all()
    return [
        ModelMetricResponse(
            model_name=m.model_name,
            accuracy=m.accuracy,
            precision=m.precision,
            recall=m.recall,
            f1=m.f1,
            macro_f1=getattr(m, 'macro_f1', m.f1),
            weighted_f1=m.weighted_f1,
            latency=m.latency
        )
        for m in metrics_db
    ]
