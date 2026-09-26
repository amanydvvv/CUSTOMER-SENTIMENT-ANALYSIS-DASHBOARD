import io
import pandas as pd
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.api.deps import get_db, get_current_user, require_analyst
from backend.app.models.user import User
from backend.app.models.feedback import FeedbackRecord, AspectTag
from backend.app.schemas.feedback import FeedbackCreate, FeedbackResponse, BatchUploadResponse
from backend.app.services.nlp_pipeline import nlp_orchestrator

router = APIRouter()


@router.get("", response_model=List[FeedbackResponse])
def list_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    sentiment: Optional[str] = Query(None, description="Filter by positive, neutral, negative"),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Search keyword in review text"),
    db: Session = Depends(get_db),
) -> Any:
    """List customer feedback records with pagination and multi-attribute filters."""
    query = db.query(FeedbackRecord)

    if sentiment:
        query = query.filter(FeedbackRecord.sentiment == sentiment.lower())
    if category:
        query = query.filter(FeedbackRecord.category == category)
    if source:
        query = query.filter(FeedbackRecord.source == source)
    if search:
        query = query.filter(FeedbackRecord.review_text.ilike(f"%{search}%"))

    records = query.order_by(desc(FeedbackRecord.created_at)).offset(skip).limit(limit).all()
    return records


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
) -> Any:
    """Create feedback entry and run dual-path sentiment & aspect pipeline."""
    pred = nlp_orchestrator.predict(text=feedback_in.review_text, model_preference="auto")

    aspect_str = ", ".join([a.aspect for a in pred.aspects])

    record = FeedbackRecord(
        source=feedback_in.source or "Manual",
        category=feedback_in.category,
        review_text=feedback_in.review_text,
        cleaned_text=pred.cleaned_text,
        rating=feedback_in.rating,
        sentiment=feedback_in.sentiment or pred.sentiment,
        confidence=pred.confidence,
        model_used=pred.model_used,
        latency_ms=pred.latency_ms,
        aspects_raw=aspect_str,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    # Add aspect tags
    for aspect_item in pred.aspects:
        aspect_tag = AspectTag(
            feedback_id=record.id,
            aspect_phrase=aspect_item.aspect,
            sentiment_polarity=aspect_item.sentiment,
            relevance_score=aspect_item.relevance,
        )
        db.add(aspect_tag)

    db.commit()
    return record


@router.delete("/{feedback_id}", status_code=status.HTTP_200_OK)
def delete_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst),
) -> Any:
    """Delete a feedback entry (analyst/admin only)."""
    record = db.query(FeedbackRecord).filter(FeedbackRecord.id == feedback_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    db.delete(record)
    db.commit()
    return {"status": "success", "message": f"Feedback {feedback_id} deleted"}


@router.post("/upload", response_model=BatchUploadResponse)
async def upload_feedback_file(
    file: UploadFile = File(...),
    source_name: str = Form("CSV Batch Upload"),
    text_column: str = Form("review_text"),
    rating_column: Optional[str] = Form("rating"),
    category_column: Optional[str] = Form("category"),
    sentiment_column: Optional[str] = Form("sentiment"),
    aspects_column: Optional[str] = Form("aspects"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Ingest CSV or Excel batch customer feedback dataset.
    Auto-classifies sentiment and extracts aspects for each row.
    """
    filename = file.filename.lower() if file.filename else "file.csv"
    contents = await file.read()

    try:
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse uploaded file: {str(e)}",
        )

    # Detect text column dynamically if default name not found
    candidate_text_cols = [text_column, "review_text", "review", "text", "comment", "feedback", "Review", "Text"]
    resolved_text_col = None
    for col in candidate_text_cols:
        if col in df.columns:
            resolved_text_col = col
            break

    if not resolved_text_col:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not locate text column. Available columns: {list(df.columns)}",
        )

    # Detect category column
    resolved_cat_col = None
    for col in [category_column, "category", "product_category", "business_category", "Category"]:
        if col and col in df.columns:
            resolved_cat_col = col
            break

    # Detect rating column
    resolved_rating_col = None
    for col in [rating_column, "rating", "stars", "score", "Rating"]:
        if col and col in df.columns:
            resolved_rating_col = col
            break

    # Detect sentiment column (if ground truth is supplied in dataset)
    resolved_sent_col = None
    for col in [sentiment_column, "sentiment", "label", "Sentiment"]:
        if col and col in df.columns:
            resolved_sent_col = col
            break

    # Detect aspects column
    resolved_aspects_col = None
    for col in [aspects_column, "aspects", "tags", "Aspects"]:
        if col and col in df.columns:
            resolved_aspects_col = col
            break

    inserted = 0
    failed = 0
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

    for _, row in df.iterrows():
        raw_text = str(row[resolved_text_col])
        if not raw_text or raw_text.strip() == "" or raw_text.lower() == "nan":
            failed += 1
            continue

        category_val = str(row[resolved_cat_col]) if resolved_cat_col and pd.notna(row[resolved_cat_col]) else None
        rating_val = float(row[resolved_rating_col]) if resolved_rating_col and pd.notna(row[resolved_rating_col]) else None

        # Run prediction
        pred = nlp_orchestrator.predict(text=raw_text, model_preference="auto")
        sentiment_val = (
            str(row[resolved_sent_col]).lower()
            if resolved_sent_col and pd.notna(row[resolved_sent_col]) and str(row[resolved_sent_col]).lower() in ["positive", "neutral", "negative"]
            else pred.sentiment
        )

        aspect_str = (
            str(row[resolved_aspects_col])
            if resolved_aspects_col and pd.notna(row[resolved_aspects_col])
            else ", ".join([a.aspect for a in pred.aspects])
        )

        record = FeedbackRecord(
            source=source_name,
            category=category_val,
            review_text=raw_text,
            cleaned_text=pred.cleaned_text,
            rating=rating_val,
            sentiment=sentiment_val,
            confidence=pred.confidence,
            model_used=pred.model_used,
            latency_ms=pred.latency_ms,
            aspects_raw=aspect_str,
        )
        db.add(record)
        db.flush()

        # Add aspect tags
        if pred.aspects:
            for aspect_item in pred.aspects:
                tag = AspectTag(
                    feedback_id=record.id,
                    aspect_phrase=aspect_item.aspect,
                    sentiment_polarity=aspect_item.sentiment,
                    relevance_score=aspect_item.relevance,
                )
                db.add(tag)

        inserted += 1
        sentiment_counts[sentiment_val] = sentiment_counts.get(sentiment_val, 0) + 1

    db.commit()

    return BatchUploadResponse(
        total_rows=len(df),
        inserted_records=inserted,
        failed_records=failed,
        message=f"Successfully processed {inserted} records from {filename}",
        summary_stats={
            "sentiment_distribution": sentiment_counts,
            "filename": filename,
            "source": source_name,
        },
    )
