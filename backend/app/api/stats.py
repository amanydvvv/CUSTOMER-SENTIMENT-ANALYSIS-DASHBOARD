from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.db.models import ModelMetric
from app.schemas import StatsResponse
from app.ml.keywords import extract_keywords
import os

router = APIRouter()
MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")

@router.get("/", response_model=StatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    stats = crud.get_stats(db)
    
    metrics_db = db.query(ModelMetric).all()
    metrics = [{"model_name": m.model_name, "accuracy": m.accuracy, "f1": m.f1, "latency": m.latency} for m in metrics_db]
    
    keywords = extract_keywords(MODELS_DIR, top_n=10)
    
    return {
        "total_reviews": stats["total_reviews"],
        "total_predictions": stats["total_predictions"],
        "model_metrics": metrics,
        "top_keywords": keywords
    }
