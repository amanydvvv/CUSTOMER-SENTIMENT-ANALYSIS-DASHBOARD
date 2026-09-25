from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import crud
from app.schemas import ReviewResponse

router = APIRouter()

@router.get("/", response_model=List[ReviewResponse])
def read_reviews(product: Optional[str] = None, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    reviews = crud.get_reviews(db, product=product, skip=skip, limit=limit)
    return reviews
