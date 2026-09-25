from fastapi import FastAPI
from app.api import predict, reviews, stats
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Sentiment API")

app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])

@app.get("/")
def root():
    return {"message": "Welcome to the Customer Sentiment API"}
