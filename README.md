# Customer Feedback Intelligence Dashboard
**CSE7102 Mini Project — Presidency University**

A fully decoupled 3-tier NLP system: FastAPI backend + SQLite database + Streamlit frontend,
with real Amazon Reviews 2023 training data and live Google Places API review ingestion.

---

## Architecture

```
mini/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint (all routers registered)
│   │   ├── api/
│   │   │   ├── predict.py              # POST /predict, POST /predict/batch
│   │   │   ├── reviews.py              # GET /reviews
│   │   │   ├── stats.py                # GET /stats, /stats/sentiment-distribution, etc.
│   │   │   └── places.py              # GET /places/search, GET /places/{id}/analyze
│   │   ├── ml/
│   │   │   ├── preprocessing.py        # clean_text() — negation-aware, stopword-filtered
│   │   │   ├── features.py             # TF-IDF (unigram+bigram, max 10k features)
│   │   │   ├── train.py                # LR, Balanced LR, LinearSVC — saves joblib artifacts
│   │   │   ├── evaluate.py             # accuracy, macro-F1, latency — no hardcoding
│   │   │   └── keywords.py             # top-N keywords per class from LR coefficients
│   │   ├── db/
│   │   │   ├── database.py             # SQLAlchemy engine + session
│   │   │   ├── models.py               # reviews, predictions, model_metrics tables
│   │   │   └── crud.py                 # DB read/write helpers
│   │   ├── services/
│   │   │   └── google_places.py        # Google Places API (New) — Text Search + Place Details
│   │   └── schemas.py                  # Pydantic request/response schemas
│   ├── tests/
│   │   ├── test_api.py                 # Core API endpoint tests (14 tests)
│   │   ├── test_phase5_google_places.py # Phase 5 Google Places integration (36 tests)
│   │   └── test_preprocessing.py       # NLP cleaning unit tests
│   ├── data/
│   │   ├── raw/                        # Amazon Reviews 2023 (All Beauty) source
│   │   └── processed/
│   │       ├── amazon_all_beauty_reviews.csv   # 50k preprocessed reviews
│   │       └── app.db                          # SQLite database (gitignored)
│   ├── models/                         # joblib artifacts (gitignored — large binaries)
│   │   ├── tfidf_vectorizer.joblib
│   │   ├── logistic_regression.joblib
│   │   ├── balanced_logistic_regression.joblib
│   │   └── linearsvc.joblib
│   ├── init_db.py                      # Creates tables + seeds model_metrics
│   ├── migrate_db.py                   # DB schema migrations
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py                # App shell + sidebar navigation
│   ├── api_client.py                   # All HTTP calls to backend (single place)
│   ├── data_loader.py                  # Cached dataset loading
│   ├── pages/
│   │   ├── 1_overview.py               # Main dashboard (Historical / Live / Manual)
│   │   ├── 2_live_prediction.py        # Single + batch manual inference
│   │   ├── 3_keyword_insights.py       # Per-class top keyword explorer
│   │   └── 4_model_comparison.py       # Accuracy + latency benchmark charts
│   └── components/
│       ├── sentiment_pulse.py          # Interactive Sentiment Pulse gauge
│       ├── review_feed.py              # Review cards (Amazon + Google attribution)
│       ├── pain_point_section.py       # Aspect/complaint breakdown charts
│       ├── mismatch_section.py         # Rating vs AI sentiment mismatch analysis
│       ├── aspect_analyzer.py          # Rule-based aspect + pain-point engine
│       └── live_places_section.py      # Google Places live review UI section
├── .streamlit/
│   ├── config.toml                     # Theme + server config
│   └── secrets.toml.example            # Safe-to-commit template (no real keys)
├── .env.example                        # Safe-to-commit env var template
├── .gitignore
└── README.md
```

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Train models
> Only needed once, or if you delete `backend/models/`. The Amazon Reviews 2023
> dataset must be prepared first.
```bash
cd backend
python prepare_dataset.py          # download + preprocess Amazon Reviews 2023
python -m app.ml.train             # train and save the three models
```

### 3. Initialise the database
```bash
# still inside backend/
python init_db.py
```
Creates `data/processed/app.db` and seeds `model_metrics` from actual evaluation — no hardcoded numbers.

### 4. Start the backend API
```bash
# still inside backend/
uvicorn app.main:app --reload --port 8000
```
Interactive docs → http://127.0.0.1:8000/docs

### 5. Start the frontend (new terminal)
```bash
# from the project root (mini/)
streamlit run frontend/streamlit_app.py
```
Dashboard → http://localhost:8501

---

## Google Places API — Live Review Analysis (Phase 5)

The dashboard can fetch real customer reviews from Google Maps and analyze them
with our trained ML models. **The training dataset is never modified.**

### How to configure

**Option A — Streamlit secrets (recommended for persistent sessions)**

Copy the example file and add your key:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml:
#   GOOGLE_PLACES_API_KEY = "AIzaSy..."
```

**Option B — Environment variable**
```bash
# Windows PowerShell
$env:GOOGLE_PLACES_API_KEY = "AIzaSy..."
uvicorn app.main:app --reload --port 8000

# Linux / macOS
export GOOGLE_PLACES_API_KEY="AIzaSy..."
uvicorn app.main:app --reload --port 8000
```

**Option C — UI (per session)**

Open the dashboard → **🌐 Live Google Reviews** tab →
expand **🔑 Google Places API Key Configuration** → paste key.
The key is stored in Streamlit session memory only and is never logged or committed.

### Getting an API key

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a project and enable **Places API (New)**
3. Create an API key and (recommended) restrict it to Places API

### Live review workflow

```
1. Select "🌐 Live Google Reviews" in the dashboard
2. Type a business name, e.g. "Starbucks Indiranagar Bangalore"
3. Click [🔍 Search Places]
4. Select a place from the dropdown
5. Choose inference model (Balanced LR recommended)
6. Click [⚡ Analyze Live Reviews]
```

The app then:
- Fetches reviews via Google Places API (New)
- Runs each review through `clean_text()` → saved TF-IDF → saved ML model
- Applies aspect/pain-point analysis
- Detects rating vs. AI sentiment mismatches
- Displays results with required Google attribution

### API limitations

| Limitation | Detail |
|---|---|
| Reviews per place | Google Places API returns **at most 5 reviews** per request |
| Language | Model trained on English; non-English reviews may have lower accuracy |
| Caching | Raw Google review text is **not** stored in SQLite (policy compliance) |
| Polling | No automatic polling — all API calls require explicit user action |
| Real-time count | Sentiment Pulse shows the actual returned count only — no inflation |

> **Disclaimer:** "Live review availability and ordering are provided by Google Places API.
> Only the reviews returned by the API are analyzed by this application."

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Root welcome message |
| `GET` | `/health` | Health check |
| `GET` | `/models` | List available model names |
| `GET` | `/models/metrics` | Model accuracy, F1, latency from DB |
| `POST` | `/predict/` | Single review sentiment inference + log to DB |
| `POST` | `/predict/batch` | Batch inference |
| `GET` | `/reviews/` | List logged reviews |
| `GET` | `/stats/` | KPIs + model metrics + top keywords |
| `GET` | `/stats/sentiment-distribution` | Sentiment breakdown |
| `GET` | `/stats/rating-distribution` | Rating histogram |
| `GET` | `/stats/products` | Per-product stats |
| `GET` | `/stats/keywords/{sentiment}` | Top keywords for a sentiment class |
| `GET` | `/places/search?query=…&api_key=…` | Google Places Text Search |
| `GET` | `/places/{place_id}/analyze?model_name=…&api_key=…` | Fetch + analyze live reviews |

### Example — predict
```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Absolutely loved this product!", "model": "balanced_logistic_regression"}'
```
```json
{"review_id": 1, "sentiment": "positive", "confidence": 0.9412, "model_used": "balanced_logistic_regression"}
```

### Example — live place search
```bash
curl "http://127.0.0.1:8000/places/search?query=Third+Wave+Coffee+Bangalore&api_key=YOUR_KEY"
```

---

## ML Pipeline

| Step | Detail |
|------|--------|
| Dataset | Amazon Reviews 2023 — All Beauty (real reviews) |
| Split | 80:20 stratified, `random_state=42` |
| Vectoriser | TF-IDF, `ngram_range=(1,2)`, `max_features=10000` |
| Models | Logistic Regression · Balanced LR · LinearSVC |
| Serialisation | `joblib` — vectoriser + each model saved separately |
| Keywords | Top-N features per class from `model.coef_[i]` (LR) |
| Confidence | LR/Balanced LR → `predict_proba()` · LinearSVC → `None` (no calibrated prob) |
| Aspect analysis | Transparent rule-based keyword matching — no black-box AI |

**Inference flow for live API reviews:**
```
raw review text
  → clean_text()                # negation expansion + stopword removal
  → tfidf_vectorizer.transform()  # saved vectorizer — NOT retrained
  → model.predict()            # saved model — NOT retrained
  → sentiment label
  → extract_aspects_and_issues()  # rule-based aspect + pain-point engine
  → mismatch check             # (Google rating metadata vs ML sentiment)
```

The Google star rating is **never passed as a model feature** — it is retained
only as metadata for display and mismatch detection.

---

## Tests

```bash
cd backend
python -m pytest tests/ -v
```

**50 tests / 50 passing** (as of Phase 5):

| Test file | Tests | Coverage |
|---|---|---|
| `test_api.py` | 14 | Core endpoints, models, predict, stats, Places missing-key |
| `test_phase5_google_places.py` | 36 | Missing key, invalid key, quota, timeout, empty results, schema normalization, ML inference, mismatch, pulse metrics, confidence scores, model selection, attribution notes |
| `test_preprocessing.py` | varies | Text cleaning, negation, stopword removal |

---

## Dashboard Pages

| Page | Key Features |
|---|---|
| **⚡ Intelligence Dashboard** | Source selector · Sentiment Pulse gauge · Pain-Point Intelligence · Mismatch Analysis · Review Feed · Live Google Reviews tab |
| **📝 Live Review Intelligence** | Single review analysis · Batch tester · Aspect/Issue/Priority/Action output |
| **🏷️ Aspect & Keyword Explorer** | Per-class TF-IDF keyword viewer |
| **📊 Model Benchmark & Evaluation** | Accuracy · Macro-F1 · Latency charts |

---

## Viva Q&A Notes

**Q: Why three models?**
LR is interpretable (coefficients = keyword weights). Balanced LR handles class imbalance without resampling the dataset. LinearSVC is fastest at inference on sparse TF-IDF matrices.

**Q: Why TF-IDF and not BERT?**
Scope is classical ML with full explainability. TF-IDF + bigrams on real Amazon data is sufficient to demonstrate meaningful sentiment classification to non-ML reviewers.

**Q: Where does the frontend get its data?**
Entirely over HTTP from the FastAPI backend. The frontend imports zero ML code — true 3-tier separation.

**Q: Does the Google Places integration retrain the model?**
No. The saved TF-IDF vectorizer and model artifacts are loaded once at startup. Google review text is passed through the existing inference pipeline — no retraining occurs.

**Q: How are model metrics populated in the database?**
`init_db.py` calls `evaluate_models()` which loads the saved test split (`test_data.joblib`) and runs actual inference. Nothing is hardcoded.

**Q: Why does LinearSVC return `None` for confidence?**
`LinearSVC.decision_function()` output is not a calibrated probability. Presenting it as a percentage would be misleading. Logistic Regression models use `predict_proba()` for genuine confidence scores.

---

## Team Contributions

| Member | Responsibility |
|--------|----------------|
| Member 1 | Data pipeline: `preprocessing.py`, `features.py`, `train.py`, `prepare_dataset.py` |
| Member 2 | Backend API: `main.py`, `api/`, `db/`, `schemas.py`, `services/google_places.py`, `tests/` |
| Member 3 | Frontend: `streamlit_app.py`, `pages/`, `components/`, `api_client.py` |
