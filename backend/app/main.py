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
def health_check():
    return {"status": "ok", "message": "API server is healthy and models are loaded"}


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
            macro_f1=m.f1,
            weighted_f1=m.weighted_f1,
            latency=m.latency
        )
        for m in metrics_db
    ]
