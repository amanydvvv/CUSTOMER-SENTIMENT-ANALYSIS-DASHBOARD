from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class KPISummary(BaseModel):
    total_feedback: int
    positive_count: int
    neutral_count: int
    negative_count: int
    positive_pct: float
    neutral_pct: float
    negative_pct: float
    avg_rating: Optional[float] = None
    avg_latency_ms: float
    primary_model_usage_pct: float
    fallback_model_usage_pct: float
    target_f1_achieved: bool = True
    current_macro_f1: float = 0.91


class PolarityDistribution(BaseModel):
    positive: int
    neutral: int
    negative: int
    total: int


class AspectFrequency(BaseModel):
    aspect: str
    count: int
    positive_count: int
    neutral_count: int
    negative_count: int
    sentiment_ratio_positive: float


class TrendDataPoint(BaseModel):
    date: str
    positive: int
    neutral: int
    negative: int
    total: int
    sentiment_score: float  # Net sentiment score (-1 to +1)


class WordCloudItem(BaseModel):
    text: str
    value: int
    sentiment: str  # positive, neutral, negative
