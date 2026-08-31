import os
import pandas as pd
from sqlalchemy.orm import Session
from backend.app.core.config import settings, DATA_DIR
from backend.app.core.security import get_password_hash
from backend.app.db.base import Base
from backend.app.db.session import engine, SessionLocal
from backend.app.models.user import User, UserRole
from backend.app.models.feedback import FeedbackRecord, AspectTag
from backend.app.models.benchmark import BenchmarkRun
from backend.app.services.fast_model import fast_classifier
from backend.app.services.aspect_extractor import aspect_extractor


def init_db(db: Session = None):
    """Create all database tables and seed initial administrator accounts & benchmark data."""
    Base.metadata.create_all(bind=engine)

    if db is None:
        db = SessionLocal()
        should_close = True
    else:
        should_close = False

    try:
        # 1. Seed Users
        seed_users = [
            {
                "email": "admin@sentiment.io",
                "username": "admin",
                "full_name": "System Administrator",
                "password": "admin123",
                "role": UserRole.ADMIN.value,
            },
            {
                "email": "analyst@sentiment.io",
                "username": "analyst",
                "full_name": "Senior Data Analyst",
                "password": "analyst123",
                "role": UserRole.ANALYST.value,
            },
            {
                "email": "viewer@sentiment.io",
                "username": "viewer",
                "full_name": "Product Viewer",
                "password": "viewer123",
                "role": UserRole.VIEWER.value,
            },
        ]

        for u in seed_users:
            existing = db.query(User).filter(
                (User.email == u["email"]) | (User.username == u["username"])
            ).first()
            if not existing:
                user = User(
                    email=u["email"],
                    username=u["username"],
                    full_name=u["full_name"],
                    hashed_password=get_password_hash(u["password"]),
                    role=u["role"],
                    is_active=True,
                )
                db.add(user)

        db.commit()

        # 2. Seed initial feedback records if empty
        record_count = db.query(FeedbackRecord).count()
        if record_count == 0:
            for dataset_file, source_name in [
                ("amazon_reviews_sample.csv", "Amazon Reviews"),
                ("yelp_reviews_sample.csv", "Yelp Reviews"),
            ]:
                file_path = DATA_DIR / dataset_file
                if os.path.exists(file_path):
                    df = pd.read_csv(file_path)
                    for _, row in df.iterrows():
                        cat_col = "product_category" if "product_category" in row else "business_category"
                        category = row.get(cat_col, "General")
                        text = str(row.get("review_text", ""))
                        rating = float(row.get("rating", 4.0))
                        sentiment = str(row.get("sentiment", "positive")).lower()
                        aspects_str = str(row.get("aspects", ""))

                        record = FeedbackRecord(
                            external_id=str(row.get("review_id", "")),
                            source=source_name,
                            category=category,
                            review_text=text,
                            cleaned_text=text,
                            rating=rating,
                            sentiment=sentiment,
                            confidence=0.95,
                            model_used="distilbert",
                            latency_ms=18.4,
                            aspects_raw=aspects_str,
                        )
                        db.add(record)
                        db.flush()

                        # Parse aspect tags
                        if aspects_str and aspects_str != "nan":
                            aspect_list = [a.strip() for a in aspects_str.split(",") if a.strip()]
                            for asp in aspect_list:
                                tag = AspectTag(
                                    feedback_id=record.id,
                                    aspect_phrase=asp.lower(),
                                    sentiment_polarity=sentiment,
                                    relevance_score=0.90,
                                )
                                db.add(tag)

            db.commit()

    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    print("Initializing Database...")
    init_db()
    print("Database Initialized with Seed Users and Benchmark Samples!")
