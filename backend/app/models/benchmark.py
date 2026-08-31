from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from backend.app.db.base import Base


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(Integer, primary_key=True, index=True)
    dataset_name = Column(String(100), nullable=False)  # Amazon, Yelp, Combined
    sample_size = Column(Integer, nullable=False)
    
    # Model comparison metrics
    transformer_latency_avg_ms = Column(Float, nullable=False)
    transformer_latency_p95_ms = Column(Float, nullable=False)
    transformer_macro_f1 = Column(Float, nullable=False)
    transformer_accuracy = Column(Float, nullable=False)

    fallback_latency_avg_ms = Column(Float, nullable=False)
    fallback_latency_p95_ms = Column(Float, nullable=False)
    fallback_macro_f1 = Column(Float, nullable=False)
    fallback_accuracy = Column(Float, nullable=False)

    speedup_factor = Column(Float, nullable=False)
    status = Column(String(50), default="PASSED")  # PASSED, FAILED
    details_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
