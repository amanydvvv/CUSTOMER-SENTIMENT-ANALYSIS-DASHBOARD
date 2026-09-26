from fastapi import APIRouter
from backend.app.api.endpoints import auth, predict, feedback, analytics, benchmark

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & RBAC"])
api_router.include_router(predict.router, prefix="/predict", tags=["Real-time Prediction"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback Management & Batch Ingestion"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & KPIs"])
api_router.include_router(benchmark.router, prefix="/benchmark", tags=["Model Benchmarking"])
