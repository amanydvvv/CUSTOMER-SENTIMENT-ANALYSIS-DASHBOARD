import time
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.feedback import PredictRequest, PredictResponse, BatchPredictRequest, BatchPredictResponse
from backend.app.services.nlp_pipeline import nlp_orchestrator

router = APIRouter()


@router.post("", response_model=PredictResponse)
def predict_sentiment(request: PredictRequest) -> Any:
    """
    Classify customer review sentiment and extract key aspects in real-time.
    Supports model preferences: 'auto' (default), 'primary' (DistilBERT), or 'fallback' (TF-IDF+LR).
    """
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review text cannot be empty.",
        )

    response = nlp_orchestrator.predict(
        text=request.text,
        model_preference=request.model_preference or "auto",
        extract_aspects=request.extract_aspects,
    )
    return response


@router.post("/batch", response_model=BatchPredictResponse)
def batch_predict(batch_request: BatchPredictRequest) -> Any:
    """
    Batch sentiment classification and aspect extraction.
    """
    if not batch_request.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch list cannot be empty.",
        )

    t0 = time.perf_counter()
    results = []
    for item in batch_request.items:
        res = nlp_orchestrator.predict(
            text=item.text,
            model_preference=item.model_preference or "auto",
            extract_aspects=item.extract_aspects,
        )
        results.append(res)

    total_time_ms = (time.perf_counter() - t0) * 1000.0
    avg_latency = total_time_ms / len(results)

    return BatchPredictResponse(
        total_processed=len(results),
        avg_latency_ms=round(avg_latency, 2),
        results=results,
    )
