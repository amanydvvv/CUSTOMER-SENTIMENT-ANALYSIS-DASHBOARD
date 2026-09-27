from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import crud
from app.schemas import ReviewResponse

router = APIRouter()

@router.get("/", response_model=List[ReviewResponse])
def read_reviews(
    product: Optional[str] = None,
    sentiment: Optional[str] = Query(default=None, description="Filter by sentiment: positive, negative, neutral"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    reviews = crud.get_reviews(db, product=product, sentiment=sentiment, skip=skip, limit=limit)
    return reviews
