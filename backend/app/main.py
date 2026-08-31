import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.app.core.config import settings
from backend.app.api import api_router
from backend.app.db.init_db import init_db
from backend.app.services.fast_model import fast_classifier
from backend.app.services.transformer_model import transformer_classifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("sentiment_app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database and warm up fast model
    logger.info("Initializing Database Tables & Seed Data...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error during DB initialization: {e}")

    logger.info("Checking Fast-Path TF-IDF Model...")
    try:
        fast_classifier.predict("warmup test")
        logger.info("Fast model operational.")
    except Exception as e:
        logger.warning(f"Fast model warmup: {e}")

    # Asynchronously attempt transformer warmup in background
    logger.info("Checking Primary DistilBERT Model...")
    try:
        transformer_classifier.initialize()
        logger.info("Primary transformer classifier ready.")
    except Exception as e:
        logger.info(f"DistilBERT will initialize on first demand: {e}")

    yield

    logger.info("Shutting down Customer Sentiment Analysis API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
## PRJ_382 Customer Sentiment Analysis Dashboard API
A production-grade, 3-tier customer feedback sentiment analytics and aspect extraction system.

### Features
* **Dual-Path Classification**: DistilBERT Transformer (<250ms) + Fast-Path TF-IDF/Logistic Regression fallback (<30ms).
* **Aspect-Based Sentiment Extraction**: Keyphrase and attribute level polarity identification.
* **Role-Based Access Control (RBAC)**: Admin, Analyst, and Viewer authorization with JWT bearer tokens.
* **Batch Ingestion**: High-throughput CSV/Excel feedback processor.
* **Benchmarking & Evaluation**: Automated Macro F1 and latency profiling against Amazon & Yelp datasets.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Enable CORS for Streamlit and external frontend consumers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health & Status"])
def root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health & Status"])
def health_check():
    return {
        "status": "healthy",
        "primary_model_available": transformer_classifier.is_available,
        "fallback_model_available": fast_classifier.pipeline is not None,
    }
