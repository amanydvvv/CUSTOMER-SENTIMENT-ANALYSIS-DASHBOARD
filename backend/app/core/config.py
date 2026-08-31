import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project Root paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
SAVED_MODELS_DIR = BASE_DIR / "backend" / "saved_models"

SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Customer Sentiment Analysis Dashboard (PRJ_382)"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "secret-jwt-key-prj382-sentiment-super-secure-token-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'sentiment_analytics.db'}"
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:8501",
        "http://localhost:3000",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:8000",
        "*",
    ]

    # NLP & Model Settings
    DISTILBERT_MODEL_NAME: str = "distilbert-base-uncased-finetuned-sst-2-english"
    FALLBACK_MODEL_PATH: str = str(SAVED_MODELS_DIR / "tfidf_lr_model.joblib")
    TRANSFORMER_TIMEOUT_MS: float = 250.0
    FALLBACK_TIMEOUT_MS: float = 30.0
    TARGET_MACRO_F1: float = 0.88

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
