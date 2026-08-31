# Customer Sentiment Analysis Dashboard

> **Project ID:** CSE7102 · PRJ_382
> **Institution:** Presidency University
> **Stack:** FastAPI + Streamlit + Dual-Model NLP

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

---

## Overview

A full-stack customer feedback sentiment analysis platform that classifies reviews as **Positive / Neutral / Negative** using a dual-path ML engine — DistilBERT as primary and TF-IDF + Logistic Regression as fast fallback.

---

## Features

| | Feature | Description |
|---|---|---|
| Dual-Path NLP | DistilBERT primary + TF-IDF/LR fallback | Auto-failover if transformer exceeds 250ms SLA |
| Aspect Extraction | KeyBERT + spaCy | Granular aspect-level sentiment tagging |
| JWT + RBAC | Admin / Analyst / Viewer roles | bcrypt password hashing |
| Interactive Dashboard | KPI cards, donut charts, trendlines, word clouds | Built with Streamlit + Plotly |
| Batch Ingestion | CSV/Excel upload | Column mapping + progress tracking |
| Benchmark Center | Amazon & Yelp datasets | Live F1, precision, recall & latency profiling |

---

## Project Structure

```
miniproj/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py                  # JWT auth & DB session dependencies
│   │   │   └── endpoints/
│   │   │       ├── auth.py              # /api/v1/auth  (login, register, me)
│   │   │       ├── predict.py           # /api/v1/predict
│   │   │       ├── feedback.py          # /api/v1/feedback  (CRUD + CSV upload)
│   │   │       ├── analytics.py         # /api/v1/analytics (KPIs, trends, aspects)
│   │   │       └── benchmark.py         # /api/v1/benchmark
│   │   ├── core/
│   │   │   ├── config.py                # Pydantic Settings (.env loader)
│   │   │   └── security.py              # bcrypt hashing & JWT token logic
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py               # SQLAlchemy engine & sessionmaker
│   │   │   └── init_db.py               # DB seeder (default users + sample data)
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── feedback.py
│   │   │   └── benchmark.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── feedback.py
│   │   │   └── analytics.py
│   │   ├── services/
│   │   │   ├── nlp_pipeline.py          # Dual-path orchestrator & failover logic
│   │   │   ├── preprocessor.py          # Text cleaner + lemmatizer
│   │   │   ├── transformer_model.py     # DistilBERT classifier
│   │   │   ├── fast_model.py            # TF-IDF + Logistic Regression classifier
│   │   │   ├── aspect_extractor.py      # KeyBERT aspect extraction
│   │   │   └── evaluator.py             # Macro F1, precision, recall & latency
│   │   └── main.py                      # FastAPI app entrypoint
│   └── saved_models/                    # Auto-generated on first run (git-ignored)
├── frontend/
│   ├── app.py                           # Streamlit multi-page app
│   ├── components/
│   │   ├── auth_view.py
│   │   ├── kpi_cards.py
│   │   ├── charts.py
│   │   ├── wordcloud_view.py
│   │   ├── batch_upload.py
│   │   ├── live_tester.py
│   │   └── model_benchmark_view.py
│   ├── utils/
│   │   └── api_client.py                # HTTP client for FastAPI calls
│   └── styles/
│       └── custom.css
├── data/
│   ├── amazon_reviews_sample.csv
│   └── yelp_reviews_sample.csv
├── tests/
│   ├── test_nlp_pipeline.py
│   ├── test_api_endpoints.py
│   └── test_benchmarks.py
├── scripts/
│   ├── train_fast_model.py              # Train & save TF-IDF + LR model
│   ├── seed_data.py                     # Seed DB with sample reviews
│   └── run_all.py                       # One-click launcher
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Quick Start

### Prerequisites
- Python **3.10+**

### 1. Clone

```bash
git clone https://github.com/amanydvvv/CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD.git
cd CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD
```

### 2. Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` and set your own `SECRET_KEY`.

### 4. Run

```bash
python scripts/run_all.py
```

Or run each service manually:

```bash
# Backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (separate terminal)
python -m streamlit run frontend/app.py --server.port 8501
```

| Service | URL |
|---|---|
| FastAPI Backend | http://127.0.0.1:8000 |
| Swagger API Docs | http://127.0.0.1:8000/docs |
| Streamlit Dashboard | http://localhost:8501 |

---

## Default Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@sentiment.io | admin123 |
| Analyst | analyst@sentiment.io | analyst123 |
| Viewer | viewer@sentiment.io | viewer123 |

---

## Running Tests

```bash
python -m pytest tests/ -v
```

---

## Environment Variables

See `.env.example` for all available options.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | — | JWT signing key |
| `DATABASE_URL` | `sqlite:///sentiment_analytics.db` | SQLite (default) |
| `DISTILBERT_MODEL_NAME` | `distilbert-base-uncased-finetuned-sst-2-english` | HuggingFace model |
| `TRANSFORMER_TIMEOUT_MS` | `250.0` | Latency SLA (ms) |
| `TARGET_MACRO_F1` | `0.88` | Minimum F1 threshold |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, Uvicorn, Pydantic v2 |
| Frontend | Streamlit, Plotly, Matplotlib, WordCloud |
| NLP / ML | HuggingFace Transformers, scikit-learn, spaCy, KeyBERT |
| Auth | python-jose, passlib, bcrypt |
| Database | SQLAlchemy 2.0 + SQLite |
| Testing | pytest, httpx |

---

<div align="center">Made for CSE7102 · Presidency University</div>
