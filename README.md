# Customer Feedback Intelligence & Sentiment Analysis Dashboard

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.59+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![DistilBERT](https://img.shields.io/badge/DistilBERT-Multilingual-FFD700.svg?logo=huggingface)](https://huggingface.co/lxyuan/distilbert-base-multilingual-cased-sentiments-student)
[![Tests](https://img.shields.io/badge/Tests-60%20Passed-22C55E.svg)](./pytest.ini)

A production-grade, 3-tier NLP intelligence system for customer sentiment analysis, aspect-based pain-point extraction, and automated decision support. Built on **FastAPI**, **SQLite**, **Scikit-Learn**, **DistilBERT Transformer**, and **Streamlit** — trained and evaluated on real **Amazon All Beauty Reviews 2023** data (81,700 reviews) with live **Google Places API** review ingestion.

---

## 🏛️ System Architecture

```
mini/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint (all routers registered)
│   │   ├── api/
│   │   │   ├── predict.py              # POST /predict, POST /predict/batch (DistilBERT + TF-IDF)
│   │   │   ├── reviews.py              # GET /reviews (sentiment + product filter + pagination)
│   │   │   ├── stats.py                # GET /stats, /stats/keywords/{sentiment}, /stats/keywords/keybert
│   │   │   ├── places.py               # GET /places/search, GET /places/{id}/analyze
│   │   │   └── auth.py                 # POST /auth/register, /auth/login, GET /auth/me (JWT HS256 RBAC)
│   │   ├── ml/
│   │   │   ├── preprocessing.py        # clean_text() — negation-aware, deduplicated (21-token whitelist)
│   │   │   ├── features.py             # TF-IDF (unigrams + bigrams, top 10,000 features, L2-normalized)
│   │   │   ├── train.py                # LR, Balanced LR, LinearSVC training pipeline
│   │   │   ├── evaluate.py             # Empirical evaluation (Macro F1, Macro Recall, Confusion Matrix)
│   │   │   ├── keywords.py             # Linear coefficient word attribution & surrogate explainability
│   │   │   ├── keybert_extractor.py    # KeyBERT semantic aspect extractor (all-MiniLM-L6-v2 + MMR)
│   │   │   └── distilbert_model.py     # DistilBERT multilingual transformer inference pipeline
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy session & SQLite engine
│   │   │   ├── models.py               # DB tables: reviews, predictions, model_metrics, users, query_history
│   │   │   └── crud.py                 # DB read/write helpers (sentiment-joined queries)
│   │   ├── services/
│   │   │   └── google_places.py        # Google Places API (Text Search + Place Details + mock fallback)
│   │   └── schemas.py                  # Pydantic request/response validation schemas
│   ├── data/
│   │   └── processed/
│   │       ├── amazon_all_beauty_reviews.csv   # 81.7K preprocessed genuine customer reviews
│   │       └── dataset_info.json               # Class distribution & metadata
│   ├── data/raw/                        # Raw downloaded files — gitignored
│   ├── models/                         # Serialized ML artifacts (.joblib)
│   │   ├── tfidf_vectorizer.joblib
│   │   ├── logistic_regression.joblib
│   │   ├── balanced_logistic_regression.joblib
│   │   ├── linearsvc.joblib
│   │   ├── evaluation_results.json
│   │   └── label_info.json
│   ├── init_db.py                      # Database schema creator & metric seeder
│   ├── migrate_db.py                   # Safe, non-destructive schema migration
│   ├── prepare_dataset.py              # Raw review extractor & preprocessor
│   ├── requirements.txt                # Backend dependencies
│   └── tests/                          # Automated backend test suites (60 tests)
│       ├── test_api.py                 # Core API endpoint tests (14 tests)
│       ├── test_auth_and_models.py     # Auth, JWT, and Model Registry tests (5 tests)
│       ├── test_phase5_google_places.py# Google Places integration & resilience tests (36 tests)
│       └── test_preprocessing.py       # NLP cleaning unit tests (5 tests)
├── frontend/
│   ├── streamlit_app.py                # App shell, dark design system, sidebar navigation
│   ├── api_client.py                   # Unified HTTP client communicating with backend
│   ├── data_loader.py                  # Cached review dataset loader
│   ├── unseen_review_loader.py         # Held-out validation review sampler (16,336 split)
│   ├── ui_utils.py                     # Safe HTML rendering utilities
│   ├── components/                     # Modular dashboard components
│   │   ├── sentiment_pulse.py          # Interactive Sentiment Pulse gauge
│   │   ├── review_feed.py              # Filterable review feed with attribution badges
│   │   ├── pain_point_section.py       # Aspect & complaint breakdown engine
│   │   ├── mismatch_section.py         # Star rating vs. AI sentiment mismatch detector
│   │   ├── aspect_analyzer.py          # 7-dimension aspect & issue priority extractor
│   │   ├── vibe_meter.py               # Moctale 180° Semicircular Purchase Confidence Meter & Donut
│   │   └── live_places_section.py      # Google Places live analysis component
│   └── pages/                          # Multi-page dashboard modules
│       ├── 0_about.py                  # Executive Overview & system architecture
│       ├── 1_overview.py               # Historical Pulse & overall analysis
│       ├── 2_live_prediction.py        # Live single & batch review inference
│       ├── 4_model_comparison.py       # Model benchmark & evaluation matrices
│       └── 5_product_intelligence.py   # ASIN-level product intelligence
├── .streamlit/
│   ├── config.toml                     # Theme & server configuration
│   └── secrets.toml.example            # Safe template for API keys
├── run_project.bat                     # Windows 1-click launcher (Python 3.10 pinned)
├── smoke_test_unseen.py                # Latency & held-out review split smoke test
├── verify_final_audit.py               # Full 6-tier system integrity audit
├── pytest.ini                          # Test configuration & path setup
└── README.md
```

---

## 📦 Dataset

- **Source:** Amazon Reviews 2023 — All Beauty category
- **Size:** 81,700 preprocessed genuine customer reviews
- **Split:** 80% train / 20% held-out test (stratified) — **16,336 test reviews**
- **Class Distribution:** ~70% Positive · ~21.6% Negative · ~8.4% Neutral
- **Preprocessing:** Negation-aware cleaning, contraction expansion, 21-token stopword whitelist, deduplication

---

## 📊 Model Evaluation & Empirical Benchmark

Evaluated on the **held-out 20% stratified test set (16,336 genuine Amazon customer reviews)**:

| Model Architecture | Test Accuracy | Macro Recall *(Decisive)* | Macro Precision | Macro F1 | Weighted F1 | Per-Sample Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Balanced Logistic Regression** 🏆 | 79.70% | **70.84%** *(+8.95%)* | 65.57% | **0.6677** *(+0.042)* | 0.8179 | **0.000186 ms** (186 ns) |
| **LinearSVC** | 84.67% | 62.48% | 67.12% | 0.6311 | 0.8285 | 0.000122 ms |
| **Standard Logistic Regression** | **85.02%** | 61.89% | **68.15%** | 0.6253 | **0.8282** | 0.000122 ms |
| **DistilBERT Multilingual** | SOTA Contextual | Robust Semantic | Contextual | Contextual | High Semantic | ~250.0 ms |

> ### 💡 Why Macro Recall & Macro F1 are the Decisive Metrics:
> Customer review datasets suffer from severe class imbalance (**~70% positive, 21.6% negative, 8.4% neutral**). A standard classifier achieves high raw accuracy by almost always predicting positive (achieving only **11.27% recall on neutral reviews**).  
> **Balanced Logistic Regression** applies inverse class frequency weighting ($w_c = \frac{N}{|C| \cdot N_c}$), boosting **Neutral Recall from 11.27% to 52.65% (+41.38 percentage points)** and preserving **75.66% Negative Recall**, ensuring critical customer dissatisfaction is never ignored.
>
> **Catastrophic Error Reduction:** Misclassifying an angry customer review as Positive collapses from **644 instances** in Standard LR down to **187 instances** in Balanced LR—a **70.96% relative reduction** in catastrophic dissatisfaction leakage.

---

## ⚡ Quick Start

### Option A: 1-Click Launch (Windows)
Double-click the **`run_project.bat`** file in the root folder. It will:
1. Initialize the SQLite database schema and seed model benchmarks.
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

#### 3. Train the ML models
```bash
python backend/app/ml/train.py
```
> **Note:** `.joblib` model files are **not included** in the repo (gitignored due to size). You must run this step before starting the backend.

#### 4. Initialize the database
```bash
python backend/init_db.py
```

#### 5. Run the Backend API (Terminal 1)
```bash
cd backend
python -m uvicorn app.main:app --port 8000
```
* Interactive Swagger Docs → **[http://localhost:8000/docs](http://localhost:8000/docs)**
* Alternative ReDoc → **[http://localhost:8000/redoc](http://localhost:8000/redoc)**

#### 6. Run the Frontend Dashboard (Terminal 2)
```bash
streamlit run frontend/streamlit_app.py
```
* Dashboard UI → **[http://localhost:8501](http://localhost:8501)**

---

## 🧪 Automated Testing & QA

Run the full automated test suite (60 tests covering NLP cleaning, API endpoints, auth security, and Google Places integration):

```bash
python -m pytest backend/tests -v
```

Run independent smoke and integrity checks:
```bash
python smoke_test_unseen.py
python verify_final_audit.py
```

---

## 🗂️ Dashboard Pages

| Page | Description |
| :--- | :--- |
| **About / Overview** (`0_about.py`) | Executive summary, system architecture, tech stack |
| **Historical Pulse** (`1_overview.py`) | Aggregate sentiment trends, rating distributions, time-series explorer |
| **Live Prediction** (`2_live_prediction.py`) | Real-time single & batch review inference with confidence scores |
| **Model Comparison** (`4_model_comparison.py`) | Side-by-side benchmark metrics, confusion matrices, classification reports |
| **Product Intelligence** (`5_product_intelligence.py`) | ASIN-level deep dives — aspect breakdown, pain points, vibe meter |

---

## 🛠️ API Reference

| Method | Endpoint | Request Schema | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/predict/` | `ReviewCreate` | Real-time sentiment prediction with calibrated confidence score |
| `POST` | `/predict/batch` | `BatchPredictRequest` | High-throughput batch inference over arrays of review texts |
| `GET` | `/reviews/` | Query Params | Fetch paginated historical reviews with sentiment and product filters |
| `GET` | `/stats/` | None | Dashboard summary metrics, top keywords, and class distributions |
| `GET` | `/stats/keywords/{sentiment}` | Path Param | Linear model coefficient-derived keywords per sentiment class |
| `GET` | `/stats/keywords/keybert` | Query Params | Dense transformer keyphrase extraction using KeyBERT (MMR) |
| `GET` | `/places/search` | Query Params | Search businesses via Google Places API (with resilient fallback) |
| `GET` | `/places/{id}/analyze` | Path Param | Ingest and analyze live Google reviews with custom ML model |
| `POST` | `/auth/register` | `UserRegister` | Register user account with bcrypt password hashing |
| `POST` | `/auth/login` | `UserLogin` | Authenticate user and issue signed HS256 JWT access token |
| `GET` | `/auth/me` | Bearer Token | Retrieve currently authenticated user context and role |
| `GET` | `/models/metrics` | None | Retrieve live empirical evaluation metrics from SQLite DB |
| `GET` | `/models` | None | List available models in the active model zoo |
| `GET` | `/health` | None | Backend service health, DB connectivity, and ML artifact check |

---

## 📦 Key Dependencies

| Package | Version | Purpose |
| :--- | :--- | :--- |
| `fastapi` | 0.115.12 | Async REST API framework |
| `uvicorn` | 0.34.3 | ASGI server |
| `streamlit` | 1.59.2 | Dashboard frontend |
| `scikit-learn` | 1.7.2 | ML models (LR, LinearSVC, TF-IDF) |
| `transformers` | ≥4.30.0 | DistilBERT multilingual inference |
| `torch` | ≥2.0.0 | PyTorch backend for transformer |
| `keybert` | ≥0.7.0 | Semantic keyphrase extraction |
| `sentence-transformers` | ≥2.2.2 | all-MiniLM-L6-v2 embeddings |
| `sqlalchemy` | 2.0.41 | ORM & SQLite integration |
| `python-jose` | 3.3.0 | JWT token generation & validation |
| `bcrypt` | 4.0.1 | Password hashing |
| `plotly` | 5.24.1 | Interactive charts |
| `nltk` | 3.10.3 | NLP preprocessing |

---

## 🔒 Security & Configuration

- **JWT Authentication:** HS256 signed tokens, bcrypt password hashing, RBAC-ready
- **Secrets:** Never commit `.env` or `secrets.toml`. Use `.env.example` and `secrets.toml.example` as templates
- **Gitignored:** `.env`, `secrets.toml`, `*.joblib` model files, `app.db`, `backend/data/raw/`

