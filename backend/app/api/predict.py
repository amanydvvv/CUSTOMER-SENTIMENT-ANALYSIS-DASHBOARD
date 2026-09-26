from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud
from app.schemas import ReviewCreate, PredictionResponse, BatchPredictRequest, BatchPredictionItem
from app.ml.preprocessing import clean_text
import joblib
import os

router = APIRouter()

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")

# Load model artifacts safely
vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib'))
loaded_models = {
    'logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'logistic_regression.joblib')),
    'balanced_logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'balanced_logistic_regression.joblib')),
    'linearsvc': joblib.load(os.path.join(MODELS_DIR, 'linearsvc.joblib'))
}


def _predict_single(text: str, model_name: str):
    """Internal helper to clean text, vectorize, and run inference with valid confidence."""
    model = loaded_models.get(model_name, loaded_models['balanced_logistic_regression'])
    cleaned = clean_text(text)

    if not cleaned.strip():
        return "neutral", None, cleaned

    features = vectorizer.transform([cleaned])
    pred = model.predict(features)[0]

    conf = None
    # Calculate genuine probability only when supported by the model
    if hasattr(model, 'predict_proba'):
        conf = round(float(max(model.predict_proba(features)[0])), 4)
    # LinearSVC does not provide calibrated probabilities; leave conf as None

    return pred, conf, cleaned


@router.post("/", response_model=PredictionResponse)
def predict_sentiment(review_req: ReviewCreate, db: Session = Depends(get_db)):
    if not review_req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    model_to_use = review_req.get_model()
    if model_to_use not in loaded_models:
        model_to_use = 'balanced_logistic_regression'

    pred, conf, cleaned = _predict_single(review_req.text, model_to_use)

    db_review = crud.create_review(db, text=review_req.text, product=review_req.product)
    db_pred = crud.create_prediction(
        db,
        review_id=db_review.id,
        sentiment=pred,
        confidence=conf,
        model_used=model_to_use
    )

    return {
        "review_id": db_review.id,
        "sentiment": pred,
        "confidence": conf,
        "model_used": model_to_use,
        "clean_text": cleaned
    }


@router.post("/batch", response_model=List[BatchPredictionItem])
def predict_sentiment_batch(batch_req: BatchPredictRequest, db: Session = Depends(get_db)):
    if not batch_req.texts:
        raise HTTPException(status_code=400, detail="Texts list cannot be empty.")

    model_to_use = batch_req.get_model()
    if model_to_use not in loaded_models:
        model_to_use = 'balanced_logistic_regression'

    results = []
    for text in batch_req.texts:
        if not str(text).strip():
            results.append({
                "review_id": None,
                "text": text,
                "sentiment": "neutral",
                "confidence": None,
                "model_used": model_to_use
            })
            continue

        pred, conf, cleaned = _predict_single(text, model_to_use)

        db_review = crud.create_review(db, text=text, product=batch_req.product)
        crud.create_prediction(
            db,
            review_id=db_review.id,
            sentiment=pred,
            confidence=conf,
            model_used=model_to_use
        )

        results.append({
            "review_id": db_review.id,
            "text": text,
            "sentiment": pred,
            "confidence": conf,
            "model_used": model_to_use
        })

    return results
