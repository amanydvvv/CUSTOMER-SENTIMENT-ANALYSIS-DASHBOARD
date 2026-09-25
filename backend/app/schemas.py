from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ReviewCreate(BaseModel):
    text: str
    product: Optional[str] = None
    model_name: Optional[str] = 'linearsvc'

class PredictionResponse(BaseModel):
    review_id: int
    sentiment: str
    confidence: Optional[float] = None
    model_used: str

class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    product: Optional[str]
    timestamp: datetime

class ModelMetricResponse(BaseModel):
    model_name: str
    accuracy: float
    f1: float
    latency: float

class StatsResponse(BaseModel):
    total_reviews: int
    total_predictions: int
    model_metrics: List[ModelMetricResponse]
    top_keywords: dict
