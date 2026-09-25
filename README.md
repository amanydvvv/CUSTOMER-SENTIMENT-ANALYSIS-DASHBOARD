# Customer Sentiment Analysis Dashboard
**CSE7102 Mini Project — Presidency University**

A fully decoupled 3-tier NLP system: FastAPI backend + SQLite database + Streamlit frontend.

---

## Architecture

```
mini/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── predict.py           # POST /predict
│   │   │   ├── reviews.py           # GET /reviews
│   │   │   └── stats.py             # GET /stats
│   │   ├── ml/
│   │   │   ├── preprocessing.py     # Text cleaning + negation handling
│   │   │   ├── features.py          # TF-IDF (unigram+bigram, max 10k)
│   │   │   ├── train.py             # LR, Balanced LR, LinearSVC
│   │   │   ├── evaluate.py          # accuracy, macro-F1, latency
│   │   │   └── keywords.py          # top-N keywords per class from coefficients
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy engine + session
│   │   │   ├── models.py            # reviews, predictions, model_metrics tables
│   │   │   └── crud.py              # DB read/write helpers
│   │   └── schemas.py               # Pydantic request/response schemas
│   ├── tests/
│   │   ├── test_api.py              # API endpoint tests (FastAPI TestClient)
│   │   └── test_preprocessing.py   # NLP cleaning unit tests
│   ├── data/
│   │   ├── raw/Dataset-SA.csv
│   │   └── processed/app.db        # SQLite database
│   ├── models/                      # joblib artifacts
│   ├── init_db.py                   # creates tables + seeds model_metrics
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py             # Home page
│   ├── pages/
│   │   ├── 1_overview.py            # KPIs
│   │   ├── 2_live_prediction.py     # Live inference
│   │   ├── 3_keyword_insights.py    # Per-class top keywords
│   │   └── 4_model_comparison.py   # Accuracy + latency charts
│   └── api_client.py               # All HTTP calls to backend (single place)
└── notebooks/EDA.ipynb
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Train models (only needed once, or if you delete backend/models/)
```bash
cd backend
python -m app.ml.train
```

### 3. Initialise the database
```bash
# still inside backend/
python init_db.py
```
This creates `data/processed/app.db` and populates `model_metrics` from the actual evaluation run — no hardcoded numbers.

### 4. Start the backend API
```bash
# still inside backend/
uvicorn app.main:app --reload --port 8000
```
Interactive docs → http://127.0.0.1:8000/docs

### 5. Start the frontend (new terminal)
```bash
cd frontend
streamlit run streamlit_app.py
```
Dashboard → http://localhost:8501

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/predict/` | Run sentiment inference + log to DB |
| `GET` | `/reviews/` | List logged reviews (filterable by `product`) |
| `GET` | `/stats/` | KPIs + model metrics + top keywords per class |

### Example — predict
```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Absolutely loved this product!", "model_name": "linearsvc"}'
```
```json
{"review_id": 1, "sentiment": "positive", "confidence": null, "model_used": "linearsvc"}
```

### Example — stats
```bash
curl http://127.0.0.1:8000/stats/
```

---

## ML Pipeline

| Step | Detail |
|------|--------|
| Split | 80:20 stratified, `random_state=42` |
| Vectoriser | TF-IDF, `ngram_range=(1,2)`, `max_features=10000` |
| Models | Logistic Regression, Balanced LR, LinearSVC |
| Serialisation | `joblib` — vectoriser + each model saved separately |
| Keywords | Top-N features per class from `model.coef_[i]` (LR) |

> **Note on 100% accuracy:** the synthetic dataset uses a small, fixed vocabulary per class, so separation is trivial for TF-IDF models. Real-world messy data will produce lower, more meaningful metrics.

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

```
tests/test_api.py::test_root                        PASSED
tests/test_api.py::test_predict_sentiment           PASSED
tests/test_api.py::test_predict_empty_text          PASSED
tests/test_api.py::test_get_stats                   PASSED
tests/test_preprocessing.py::test_clean_text_removes_html        PASSED
tests/test_preprocessing.py::test_clean_text_preserves_negation  PASSED
tests/test_preprocessing.py::test_clean_text_removes_stopwords   PASSED
tests/test_preprocessing.py::test_clean_text_empty_string        PASSED
tests/test_preprocessing.py::test_clean_text_removes_urls        PASSED

9 passed in 8.91s
```

---

## Viva Q&A Notes

**Q: Why three models?**
LR is interpretable (coefficients = keyword weights). Balanced LR handles class imbalance. LinearSVC is typically fastest at inference on sparse TF-IDF matrices.

**Q: Why TF-IDF and not word2vec/BERT?**
Scope is intentionally kept at classical ML. TF-IDF + bigrams is sufficient for this dataset and keeps the pipeline fully explainable to non-ML reviewers.

**Q: Where does the frontend get its data?**
Entirely over HTTP from the FastAPI backend. The frontend imports zero ML code — true tier separation.

**Q: How are model metrics in the database populated?**
`init_db.py` calls `evaluate_models()` at startup, which loads the saved test split (`test_data.joblib`) and runs actual inference. Nothing is hardcoded.

---

## Team Contributions

| Member | Responsibility |
|--------|----------------|
| Member 1 | Data pipeline: `preprocessing.py`, `features.py`, `train.py` |
| Member 2 | Backend API: `main.py`, `api/`, `db/`, `schemas.py`, `tests/` |
| Member 3 | Frontend: `streamlit_app.py`, `pages/`, `api_client.py` |
