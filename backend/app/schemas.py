from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ReviewCreate(BaseModel):
    text: str
    product: Optional[str] = None
    model_name: Optional[str] = None
    model: Optional[str] = None

    def get_model(self) -> str:
        return self.model or self.model_name or "linearsvc"


class PredictionResponse(BaseModel):
    review_id: Optional[int] = None
    sentiment: str
    confidence: Optional[float] = None
    model_used: str
    clean_text: Optional[str] = None


class BatchPredictRequest(BaseModel):
    texts: List[str]
    model: Optional[str] = "balanced_logistic_regression"
    model_name: Optional[str] = None
    product: Optional[str] = None

    def get_model(self) -> str:
        return self.model_name or self.model or "balanced_logistic_regression"


class BatchPredictionItem(BaseModel):
    review_id: Optional[int] = None
    text: str
    sentiment: str
    confidence: Optional[float] = None
    model_used: str


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    text: str
    product: Optional[str] = None
    timestamp: datetime


class ModelMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    model_name: str
    accuracy: float
    precision: Optional[float] = None          # Macro Precision
    recall: Optional[float] = None             # Macro Recall
    macro_precision: Optional[float] = None
    macro_recall: Optional[float] = None
    f1: float                                  # Macro F1 (backward-compatible name)
    macro_f1: Optional[float] = None
    weighted_precision: Optional[float] = None
    weighted_recall: Optional[float] = None
    weighted_f1: Optional[float] = None
    latency: float


class StatsResponse(BaseModel):
    total_reviews: int
    total_predictions: int
    model_metrics: List[ModelMetricResponse]
    top_keywords: dict
    sentiment_distribution: Optional[Dict[str, Any]] = None
    rating_distribution: Optional[Dict[str, Any]] = None
