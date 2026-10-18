from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
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

# ── Review-3: JWT Auth ────────────────────────────────────────────────────────
class User(Base):
    """Registered users for JWT authentication and RBAC."""
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role            = Column(String, default="viewer")   # viewer | analyst | admin
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, server_default=func.now())

# ── Review-3: Query History (Storage Layer) ───────────────────────────────────
class QueryHistory(Base):
    """Persistent log of every prediction run — survives session restart."""
    __tablename__ = "query_history"
    id          = Column(Integer, primary_key=True, index=True)
    username    = Column(String, index=True, nullable=True)   # null = anonymous
    query_text  = Column(String, nullable=False)
    sentiment   = Column(String)
    confidence  = Column(Float)
    model_used  = Column(String)
    timestamp   = Column(DateTime, server_default=func.now())

