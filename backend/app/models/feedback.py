from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.db.base import Base


class FeedbackRecord(Base):
    __tablename__ = "feedback_records"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    source = Column(String(50), default="Manual", index=True)  # Amazon, Yelp, CSV, Live
    category = Column(String(100), nullable=True, index=True)
    review_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    
    # Sentiment predictions
    sentiment = Column(String(20), nullable=False, index=True)  # positive, neutral, negative
    confidence = Column(Float, default=1.0)
    
    # Model tracking
    model_used = Column(String(50), default="distilbert")  # distilbert, tfidf_lr
    latency_ms = Column(Float, default=0.0)
    
    # Aspect summary as comma-separated or json string
    aspects_raw = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    aspect_tags = relationship("AspectTag", back_populates="feedback", cascade="all, delete-orphan")


class AspectTag(Base):
    __tablename__ = "aspect_tags"

    id = Column(Integer, primary_key=True, index=True)
    feedback_id = Column(Integer, ForeignKey("feedback_records.id", ondelete="CASCADE"), nullable=False)
    aspect_phrase = Column(String(100), nullable=False, index=True)
    sentiment_polarity = Column(String(20), default="neutral")  # positive, neutral, negative
    relevance_score = Column(Float, default=1.0)

    feedback = relationship("FeedbackRecord", back_populates="aspect_tags")


# Composite indexes for fast analytics queries
Index("idx_feedback_sentiment_source", FeedbackRecord.sentiment, FeedbackRecord.source)
Index("idx_feedback_created_sentiment", FeedbackRecord.created_at, FeedbackRecord.sentiment)
