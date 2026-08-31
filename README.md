# 🧠 Customer Sentiment Analysis Dashboard

> **Course / Project ID:** CSE7102 · PRJ_382 — Review-1 Technical Implementation
> **Institution:** Presidency University
> **Architecture:** 3-Tier Production Architecture (FastAPI + Streamlit + Dual-Model NLP)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 📌 Overview

A full-stack, production-grade **NLP sentiment analysis platform** that classifies customer reviews as **Positive / Neutral / Negative** using a dual-path ML engine. Built with a REST API backend, interactive Streamlit dashboard, JWT-secured role-based access control, and real-time benchmarking across Amazon & Yelp datasets.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Dual-Path NLP Engine** | DistilBERT (primary, <250ms) + TF-IDF/LR (fallback, <30ms) with smart auto-failover |
| 🔍 **Aspect-Based Extraction** | KeyBERT-powered keyword & aspect-level sentiment tagging |
| 🔐 **JWT + RBAC Security** | Admin / Analyst / Viewer roles with bcrypt password hashing |
| 📊 **Interactive Dashboard** | Live KPI cards, donut charts, trendlines, word clouds & confusion matrices |
| 📂 **Batch Ingestion** | CSV/Excel drag-and-drop uploader with column mapping |
| 🏁 **Live Benchmark Center** | Real-time F1, precision, recall & latency profiling on Amazon/Yelp datasets |

---

## 📂 Project Structure

```
miniproj/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                  # JWT Auth & DB dependencies
│   │   │   └── endpoints/
│   │   │       ├── auth.py              # /api/v1/auth  (login, register, me)
│   │   │       ├── predict.py           # /api/v1/predict  (single & batch)
│   │   │       ├── feedback.py          # /api/v1/feedback  (CRUD + CSV upload)
│   │   │       ├── analytics.py         # /api/v1/analytics (KPIs, trends, aspects)
│   │   │       └── benchmark.py         # /api/v1/benchmark (latency & F1 tests)
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic Settings (.env, JWT secrets)
│   │   │   └── security.py              # Password hashing & JWT generators
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py               # Engine & sessionmaker (SQLite/Postgres)
│   │   │   └── init_db.py               # Seeder (admin user & benchmark data)
│   │   ├── models/
│   │   │   ├── user.py                  # User & Role ORM models
│   │   │   ├── feedback.py              # FeedbackRecord & AspectTag models
│   │   │   └── benchmark.py             # BenchmarkRun metrics model
│   │   ├── schemas/
│   │   │   ├── user.py                  # UserCreate, UserLogin, Token schemas
│   │   │   ├── feedback.py              # FeedbackInput, BatchUpload schemas
│   │   │   └── analytics.py             # KPISummary, SentimentDistribution schemas
│   │   ├── services/
│   │   │   ├── nlp_pipeline.py          # DualPathClassifier orchestrator & failover
│   │   │   ├── preprocessor.py          # Text cleaner, contractions, lemmatizer
│   │   │   ├── transformer_model.py     # DistilBERT classifier implementation
│   │   │   ├── fast_model.py            # TF-IDF + Logistic Regression classifier
│   │   │   ├── aspect_extractor.py      # Aspect & keyword extraction (KeyBERT)
│   │   │   └── evaluator.py             # Macro F1, precision, recall & latency
│   │   └── main.py                      # FastAPI entrypoint with CORS
│   └── saved_models/                    # Auto-generated model artifacts (git-ignored)
├── frontend/
│   ├── app.py                           # Streamlit multi-page dashboard
│   ├── components/
│   │   ├── auth_view.py                 # Login / Register / Role selector UI
│   │   ├── kpi_cards.py                 # Metric cards (Volume, Sentiment %, F1)
│   │   ├── charts.py                    # Donut chart, trendlines, aspect bars
│   │   ├── wordcloud_view.py            # Word cloud & topic frequency generator
│   │   ├── batch_upload.py              # CSV/Excel drag-and-drop ingestion
│   │   ├── live_tester.py               # Single feedback tester with aspect tags
│   │   └── model_benchmark_view.py      # Dual-path comparator & metrics view
│   ├── utils/
│   │   └── api_client.py                # HTTP client calling FastAPI endpoints
│   └── styles/
│       └── custom.css                   # Dark glassmorphic UI styling
├── data/
│   ├── amazon_reviews_sample.csv        # Amazon Customer Reviews benchmark dataset
│   └── yelp_reviews_sample.csv          # Yelp Open Dataset benchmark sample
├── tests/
│   ├── test_nlp_pipeline.py             # Unit tests: preprocessing & dual-path models
│   ├── test_api_endpoints.py            # Integration tests: FastAPI endpoints
│   └── test_benchmarks.py              # Latency & Macro F1 automated assertions
├── scripts/
│   ├── train_fast_model.py              # Train & serialize TF-IDF + LR model
│   ├── seed_data.py                     # Seed database with benchmark reviews
│   └── run_all.py                       # One-click launcher (Backend + Frontend)
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**

### 1 · Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2 · Set Up Environment

```bash
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# Install all dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 3 · Configure Environment Variables

```bash
copy .env.example .env
# Edit .env and set your SECRET_KEY and DATABASE_URL
```

### 4 · Launch

**One-click launcher (recommended):**
```bash
python scripts/run_all.py
```

**Or run independently:**
```bash
# Terminal 1 — FastAPI Backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — Streamlit Dashboard
python -m streamlit run frontend/app.py --server.port 8501
```

| Service | URL |
|---|---|
| 📡 FastAPI REST API | http://127.0.0.1:8000 |
| 📖 Swagger Docs | http://127.0.0.1:8000/docs |
| 🖥️ Dashboard | http://localhost:8501 |

---

## 👤 Default User Accounts

| Role | Email | Password | Access |
|---|---|---|---|
| 🔴 **Admin** | admin@sentiment.io | admin123 | Full CRUD, Benchmark, Manage |
| 🟡 **Analyst** | analyst@sentiment.io | analyst123 | Analytics, Ingestion, Benchmarks |
| 🟢 **Viewer** | viewer@sentiment.io | viewer123 | Read-only Dashboard |

> ⚠️ Change all default passwords before deploying to production.

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

Covers: NLP pipeline unit tests · REST endpoint integration · Latency SLA & F1 assertions

---

## 🤖 NLP Engine

### Dual-Path Routing

| Path | Model | Latency | Use Case |
|---|---|---|---|
| **Primary** | DistilBERT (distilbert-base-uncased-finetuned-sst-2-english) | < 250 ms | High-accuracy contextual inference |
| **Fallback** | TF-IDF N-gram + Logistic Regression | < 30 ms | High-speed / compute-constrained |

Auto-failover kicks in if transformer exceeds the SLA threshold.

### Aspect Extraction
KeyBERT + spaCy noun-chunk mining for granular aspect-level sentiment:
```
"battery life: negative"  |  "sound quality: positive"  |  "build quality: neutral"
```

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|---|---|---|
| SECRET_KEY | — | JWT HMAC-SHA256 signing key |
| ACCESS_TOKEN_EXPIRE_MINUTES | 1440 | Token lifetime (minutes) |
| DATABASE_URL | sqlite:///sentiment_analytics.db | SQLite or PostgreSQL URL |
| DISTILBERT_MODEL_NAME | distilbert-base-uncased-finetuned-sst-2-english | HuggingFace model ID |
| TRANSFORMER_TIMEOUT_MS | 250.0 | Latency SLA threshold (ms) |
| TARGET_MACRO_F1 | 0.88 | Minimum acceptable Macro F1 |

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| **API Backend** | FastAPI, Uvicorn, Pydantic v2 |
| **Frontend** | Streamlit, Plotly, WordCloud, Matplotlib |
| **NLP / ML** | HuggingFace Transformers, scikit-learn, spaCy, KeyBERT |
| **Auth** | python-jose, passlib, bcrypt, PyJWT |
| **Database** | SQLAlchemy 2.0, SQLite (dev) / PostgreSQL (prod) |
| **Testing** | pytest, httpx |

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">Made with ❤️ for CSE7102 · Presidency University</div>
