from sqlalchemy.orm import Session
from . import models

def create_review(db: Session, text: str, product: str = None):
    db_review = models.Review(text=text, product=product)
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def get_reviews(db: Session, product: str = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Review)
    if product:
        query = query.filter(models.Review.product == product)
    return query.offset(skip).limit(limit).all()

def create_prediction(db: Session, review_id: int, sentiment: str, confidence: float, model_used: str):
    db_prediction = models.Prediction(
        review_id=review_id,
        sentiment=sentiment,
        confidence=confidence,
        model_used=model_used
    )
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_stats(db: Session):
    total_reviews = db.query(models.Review).count()
    total_predictions = db.query(models.Prediction).count()
    return {
        "total_reviews": total_reviews,
        "total_predictions": total_predictions
    }
