from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud
from app.schemas import ReviewCreate, PredictionResponse
from app.ml.preprocessing import clean_text
import joblib
import os

router = APIRouter()

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "models")
vectorizer = joblib.load(os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib'))
loaded_models = {
    'logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'logistic_regression.joblib')),
    'balanced_logistic_regression': joblib.load(os.path.join(MODELS_DIR, 'balanced_logistic_regression.joblib')),
    'linearsvc': joblib.load(os.path.join(MODELS_DIR, 'linearsvc.joblib'))
}

@router.post("/", response_model=PredictionResponse)
def predict_sentiment(review_req: ReviewCreate, db: Session = Depends(get_db)):
    if not review_req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    cleaned = clean_text(review_req.text)
    if not cleaned.strip():
        pred, conf = "neutral", 0.0
    else:
        features = vectorizer.transform([cleaned])
        model = loaded_models.get(review_req.model_name, loaded_models['linearsvc'])
        pred = model.predict(features)[0]
        
        conf = None
        if hasattr(model, 'predict_proba'):
            conf = float(max(model.predict_proba(features)[0]))
        
    db_review = crud.create_review(db, text=review_req.text, product=review_req.product)
    db_pred = crud.create_prediction(
        db,
        review_id=db_review.id,
        sentiment=pred,
        confidence=conf,
        model_used=review_req.model_name
    )
    
    return {
        "review_id": db_review.id,
        "sentiment": pred,
        "confidence": conf,
        "model_used": review_req.model_name
    }
