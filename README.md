# Customer Feedback Intelligence & Sentiment Analysis Dashboard

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Tests](https://img.shields.io/badge/Tests-66%20Passed-22C55E.svg)](file:///c:/Users/amanc/Desktop/mini/pytest.ini)

A production-grade, 3-tier NLP intelligence system for customer sentiment analysis, aspect-based pain-point extraction, and automated decision support. Built on **FastAPI**, **SQLite**, **Scikit-Learn**, and **Streamlit** using real **Amazon Reviews 2023** data and live **Google Places API** review ingestion.

---

## 🏛️ System Architecture

```
mini/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint (all routers registered)
│   │   ├── api/
│   │   │   ├── predict.py              # POST /predict, POST /predict/batch
│   │   │   ├── reviews.py              # GET /reviews
│   │   │   ├── stats.py                # GET /stats, /stats/sentiment-distribution
│   │   │   └── places.py               # GET /places/search, GET /places/{id}/analyze
│   │   ├── ml/
│   │   │   ├── preprocessing.py        # clean_text() — negation-aware, deduplicated
│   │   │   ├── features.py             # TF-IDF (unigrams + bigrams, top 10k features)
│   │   │   ├── train.py                # LR, Balanced LR, LinearSVC training pipeline
│   │   │   ├── evaluate.py             # Empirical evaluation (Macro F1, Macro Recall)
│   │   │   └── keywords.py             # Top-N class keywords from model coefficients
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy session & SQLite engine
│   │   │   ├── models.py               # Database schemas (reviews, predictions, model_metrics)
│   │   │   └── crud.py                 # DB read/write helpers
│   │   ├── services/
│   │   │   └── google_places.py        # Google Places API (Text Search + Place Details)
│   │   └── schemas.py                  # Pydantic request/response validation schemas
│   ├── data/
│   │   └── processed/
│   │       ├── amazon_all_beauty_reviews.csv   # 81.7K preprocessed genuine reviews
│   │       ├── dataset_info.json               # Class distribution & metadata
│   │       └── app.db                          # SQLite database
│   ├── models/                         # Serialized ML artifacts (.joblib)
│   │   ├── tfidf_vectorizer.joblib
│   │   ├── logistic_regression.joblib
│   │   ├── balanced_logistic_regression.joblib
│   │   ├── linearsvc.joblib
│   │   └── evaluation_results.json
│   ├── init_db.py                      # Database schema creator & metric seeder
│   ├── migrate_db.py                   # Safe, non-destructive schema migration
│   ├── prepare_dataset.py              # Raw review extractor & preprocessor
│   ├── requirements.txt                # Backend dependencies
│   └── tests/                          # Automated backend test suites
│       ├── test_api.py                 # Core API endpoint tests (14 tests)
│       ├── test_phase5_google_places.py# Google Places integration tests (36 tests)
│       └── test_preprocessing.py       # NLP cleaning unit tests (5 tests)
├── frontend/
│   ├── streamlit_app.py                # App shell, dark design system, sidebar navigation
│   ├── api_client.py                   # Unified HTTP client communicating with backend
│   ├── data_loader.py                  # Cached review dataset loader
│   ├── unseen_review_loader.py         # Held-out validation review sampler
│   ├── ui_utils.py                     # Safe HTML rendering utilities
│   ├── components/                     # Modular dashboard components
│   │   ├── sentiment_pulse.py          # Interactive Sentiment Pulse gauge
│   │   ├── review_feed.py              # Filterable review feed with attribution badges
│   │   ├── pain_point_section.py       # Aspect & complaint breakdown engine
│   │   ├── mismatch_section.py         # Star rating vs. AI sentiment mismatch detector
│   │   ├── aspect_analyzer.py          # Aspect & issue priority extractor
│   │   └── live_places_section.py      # Google Places live analysis component
│   └── pages/                          # Multi-page dashboard modules
│       ├── 1_overview.py               # Overall Analysis & historical explorer
│       ├── 2_live_prediction.py        # Live Single & batch review inference
│       ├── 3_keyword_insights.py       # Aspect & keyword vocabulary explorer
│       ├── 4_model_comparison.py       # Model benchmark & evaluation metrics
│       └── 5_product_intelligence.py   # ASIN-level product intelligence
├── .streamlit/
│   ├── config.toml                     # Theme & server configuration
│   └── secrets.toml.example            # Safe template for API keys
├── run_project.bat                     # Windows 1-click launcher (starts backend + frontend)
├── pytest.ini                          # Test configuration & path setup
└── README.md
```

---

## 📊 Model Evaluation & Empirical Benchmark

Evaluated on a **held-out 20% stratified test set (16,336 genuine Amazon reviews)**.

| Model | Accuracy | Macro Recall *(Unweighted)* | Macro Precision | Macro F1 | Weighted F1 | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Standard Logistic Regression** | **85.02%** | 61.89% | 68.15% | 0.6253 | 0.8282 | 0.0001 ms |
| **Balanced Logistic Regression** 🏆 | 79.70% | **70.84%** *(+8.95%)* | 65.57% | **0.6677** *(+0.042)* | 0.8179 | 0.0002 ms |
| **LinearSVC** | 84.67% | 62.48% | 67.12% | 0.6311 | 0.8285 | 0.0001 ms |

> ### 💡 Why Macro Recall & Macro F1 are the Decisive Metrics:
> Customer review datasets suffer from severe class imbalance (**~70% positive, 22% negative, 8% neutral**). A standard classifier achieves high raw accuracy by almost always guessing positive (achieving only **11% recall on neutral reviews**).  
> **Balanced Logistic Regression** trades a small fraction of overall accuracy to boost **Neutral Recall from 11% to 53%** and **Negative Recall to 76%**, ensuring critical customer dissatisfaction is never ignored.

---

## ⚡ Quick Start

### Option A: 1-Click Launch (Windows)
Simply double-click the **`run_project.bat`** file in the root folder. It will:
1. Initialize the SQLite database.
2. Launch the FastAPI backend on port `8000`.
3. Launch the Streamlit dashboard on port `8501`.

---

### Option B: Manual CLI Setup

#### 1. Clone the repository
```bash
git clone https://github.com/amanydvvv/CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD.git
cd CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD
```

#### 2. Install dependencies
```bash
pip install -r backend/requirements.txt
```

#### 3. Initialize the database
```bash
python backend/init_db.py
```

#### 4. Run the Backend API (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --port 8000
```
* Interactive Swagger Docs → **[http://localhost:8000/docs](http://localhost:8000/docs)**
* Alternative ReDoc → **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

#### 5. Run the Frontend Dashboard (Terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```
* Dashboard UI → **[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Automated Testing & QA

Run the full automated test suite (66 tests covering NLP cleaning, API endpoints, and Google Places integration):

```bash
python -m pytest
```

Run independent smoke and integrity checks:
```bash
python smoke_test_unseen.py
python verify_final_audit.py
```

---

## 🌐 Google Places API Configuration (Optional)

To enable live Google Maps review ingestion for businesses and restaurants:

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
2. Add your Google Places API Key:
   ```toml
   GOOGLE_PLACES_API_KEY = "AIzaSy..."
   ```

---

## 🛠️ API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/predict/` | Predict sentiment for a single review with confidence score |
| `POST` | `/predict/batch` | Batch sentiment inference over multiple reviews |
| `GET` | `/reviews/` | Fetch paginated historical reviews with optional filters |
| `GET` | `/stats/` | Dashboard summary metrics, top keywords, and class distributions |
| `GET` | `/places/search` | Search businesses via Google Places API |
| `GET` | `/places/{id}/analyze` | Ingest and analyze live Google reviews for a specific place |
| `GET` | `/models/metrics` | Retrieve live empirical evaluation metrics from SQLite DB |
| `GET` | `/health` | Backend service health and model status check |
