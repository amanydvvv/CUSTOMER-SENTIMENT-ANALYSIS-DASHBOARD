from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    product = Column(String, index=True)
    timestamp = Column(DateTime, server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, index=True)
    sentiment = Column(String, index=True)
    confidence = Column(Float)
    model_used = Column(String)
    timestamp = Column(DateTime, server_default=func.now())

class ModelMetric(Base):
    __tablename__ = "model_metrics"
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, index=True)
    accuracy = Column(Float)
    precision = Column(Float)           # Macro Precision
    recall = Column(Float)              # Macro Recall
    macro_precision = Column(Float)
    macro_recall = Column(Float)
    f1 = Column(Float)                  # macro F1 — kept as 'f1' for backward compat
    macro_f1 = Column(Float)
    weighted_precision = Column(Float)
    weighted_recall = Column(Float)
    weighted_f1 = Column(Float)
    latency = Column(Float)
    evaluated_at = Column(DateTime, server_default=func.now())
