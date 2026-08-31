from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AspectItem(BaseModel):
    aspect: str
    sentiment: str = "neutral"
    relevance: float = 1.0


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Customer review text to analyze")
    model_preference: Optional[str] = Field("auto", description="auto, primary (distilbert), or fallback (tfidf_lr)")
    extract_aspects: bool = True
    category: Optional[str] = None
    source: Optional[str] = "Live Tester"


class PredictResponse(BaseModel):
    review_text: str
    cleaned_text: str
    sentiment: str  # positive, neutral, negative
    confidence: float
    probabilities: Dict[str, float]
    model_used: str  # distilbert or tfidf_lr
    latency_ms: float
    aspects: List[AspectItem]
    fallback_triggered: bool = False


class BatchPredictRequest(BaseModel):
    items: List[PredictRequest]


class BatchPredictResponse(BaseModel):
    total_processed: int
    avg_latency_ms: float
    results: List[PredictResponse]


class FeedbackCreate(BaseModel):
    review_text: str
    source: Optional[str] = "Manual"
    category: Optional[str] = None
    rating: Optional[float] = None
    sentiment: Optional[str] = None
    aspects: Optional[List[str]] = None


class FeedbackResponse(BaseModel):
    id: int
    external_id: Optional[str] = None
    source: str
    category: Optional[str] = None
    review_text: str
    cleaned_text: Optional[str] = None
    rating: Optional[float] = None
    sentiment: str
    confidence: float
    model_used: str
    latency_ms: float
    aspects_raw: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BatchUploadResponse(BaseModel):
    total_rows: int
    inserted_records: int
    failed_records: int
    message: str
    summary_stats: Dict[str, Any]
