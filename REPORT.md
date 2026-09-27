# Customer Sentiment Intelligence Dashboard — Project Report

**Course:** Data Science / Machine Learning Project  
**Team:** Aman (Project Lead · ML Engineer) · Pasha (Frontend Developer) · Guru (Backend Developer)  
**Repository:** https://github.com/amanydvvv/CUSTOMER-SENTIMENT-ANALYSIS-DASHBOARD

---

## 1. Problem Statement

Customer reviews contain rich, unstructured signals about product quality, service failures, and user satisfaction. Businesses that rely solely on star ratings miss the nuance within review text — a 3-star review can contain both praise and serious complaints. Manual review analysis at scale is not feasible.

This project builds a production-grade **Customer Sentiment Intelligence System** that automatically classifies customer review text into Positive, Neutral, or Negative sentiment using machine learning, and surfaces actionable insights through an interactive real-time dashboard. The system answers business questions such as: *"Which products have the most negative feedback?"*, *"What are customers complaining about?"*, and *"Which reviews contradict their own star rating?"*

---

## 2. Dataset

| Property | Value |
|---|---|
| **Source** | Amazon Reviews 2023 — All Beauty category |
| **Total Reviews** | 81,700 (after deduplication and preprocessing) |
| **Held-out Test Set** | 16,336 reviews (20% stratified split) |
| **Features** | Review text + title (combined), star rating, product ASIN, verified purchase |
| **Labels** | Positive (rating ≥ 4), Negative (rating ≤ 2), Neutral (rating = 3) |

### Class Distribution (Imbalance)

| Class | Count | Proportion |
|---|---|---|
| Positive | ~57,100 | ~69.9% |
| Negative | ~17,900 | ~21.9% |
| Neutral | ~6,700 | ~8.2% |

**Key insight:** The dataset suffers from severe class imbalance (~70% positive). A naive classifier that always predicts "Positive" would achieve ~70% accuracy — making raw Accuracy a deceptive metric. Macro Recall, which gives equal weight to all 3 classes, is the decisive evaluation metric for this task.

### Preprocessing Pipeline

1. HTML tag removal
2. URL stripping
3. Lowercasing
4. Negation-aware tokenization (`not good` → `not_good` to preserve sentiment polarity)
5. Stopword removal with negation exception list
6. Text length filtering (remove empty reviews after cleaning)
7. Review + Title concatenation to maximize signal

---

## 3. Model Selection & Justification

Three models were evaluated, each representing a distinct design choice:

### Model 1 — Standard Logistic Regression (Baseline)
A linear classifier on TF-IDF features. Chosen as the baseline for interpretability and speed. No class weighting applied.

### Model 2 — Balanced Logistic Regression (Production Model)
Identical architecture to Model 1 but trained with `class_weight='balanced'` in scikit-learn. This automatically adjusts class weights inversely proportional to class frequency, forcing the model to pay more attention to minority classes (Neutral, Negative). This is the **recommended production model**.

### Model 3 — LinearSVC (Alternative)
A linear Support Vector Classifier — typically faster and often competitive with logistic regression on text tasks. Does not produce calibrated probabilities (confidence scores show as N/A in the dashboard).

### Feature Engineering
- TF-IDF vectorizer: unigrams + bigrams, top 10,000 features by term frequency
- All models share the same vectorizer artifact (`tfidf_vectorizer.joblib`)

---

## 4. Empirical Results

Evaluated on the 20% stratified held-out test set (16,336 reviews, never seen during training):

| Model | Accuracy | Macro Recall | Macro Precision | Macro F1 | Weighted F1 | Latency |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Standard Logistic Regression | 85.02% | 61.89% | 68.15% | 0.6253 | 0.8282 | 0.0001 ms |
| **Balanced Logistic Regression** ⭐ | **79.70%** | **70.84%** | 65.57% | **0.6677** | 0.8179 | 0.0002 ms |
| LinearSVC | 84.67% | 62.48% | 67.12% | 0.6311 | 0.8285 | 0.0001 ms |

### Why Balanced LR Wins Despite Lower Accuracy

Standard LR achieves 85% accuracy primarily by predicting "Positive" almost always — it achieves only **11% recall on Neutral reviews**. Balanced LR trades 5 percentage points of raw accuracy to:

- Boost **Neutral recall from 11% → 53%** (+42 points)
- Boost **Negative recall from 76% → 76%** (maintained)
- Overall **Macro Recall: 61.89% → 70.84%** (+8.95 points)

For a customer feedback system, missing a Negative or Neutral review is a business failure. Balanced LR is the correct choice.

---

## 5. System Architecture

The project follows a **3-tier architecture**:

```
┌──────────────────────────────┐
│  Streamlit Frontend (Port 8501) │  ← User-facing dashboard (5 pages)
│  frontend/                      │
└──────────────┬───────────────┘
               │ HTTP REST API
┌──────────────▼───────────────┐
│  FastAPI Backend (Port 8000)    │  ← Business logic, inference, DB
│  backend/app/                   │
└──────────────┬───────────────┘
               │ SQLAlchemy ORM
┌──────────────▼───────────────┐
│  SQLite Database + .joblib      │  ← Persistence + ML artifacts
│  backend/data/processed/        │
│  backend/models/                │
└─────────────────────────────┘
```

**Tier 1 — Frontend (Streamlit):** Five distinct dashboard pages rendered in a dark-themed UI. Communicates with the backend exclusively via HTTP through `api_client.py`. Data is loaded directly from the processed CSV for performance-critical views using `@st.cache_data`.

**Tier 2 — Backend (FastAPI):** Exposes a REST API with 12 endpoints covering prediction (single + batch), review retrieval, statistics, keyword extraction, model metrics, and Google Places live review ingestion. SQLAlchemy ORM manages all database interactions. ML model artifacts are loaded once at startup.

**Tier 3 — Data Layer (SQLite + joblib):** SQLite stores prediction history (Review and Prediction tables). Four `.joblib` files store the trained TF-IDF vectorizer and three model artifacts.

---

## 6. Key Dashboard Features

| Feature | Description |
|---|---|
| **Overview & Filters** | Filter 81,700 reviews by product, rating, sentiment, date range, and keyword. View sentiment KPI cards, pain point analysis, and star/sentiment mismatch detection. |
| **Live Prediction** | Type any review for real-time ML inference with word-level TF-IDF explainability highlights. Batch mode supports CSV upload. Session history tracks last 10 analyses. |
| **Keyword Insights** | Visualise the TF-IDF vocabulary for each sentiment class. Identify strongest predictive terms and n-gram patterns. |
| **Model Benchmark** | Side-by-side comparison of all 3 models with accuracy, macro recall, macro F1, and interactive confusion matrix heatmaps. |
| **Product Intelligence** | ASIN-level deep dive: sentiment donut chart, aspect pain-point table with priority scoring, supporting evidence inspector, rating/sentiment mismatch detector, feedback trend over time, cross-product heatmap. |
| **Google Places Integration** | Search any real business and ingest live Google Maps reviews for real-time sentiment analysis. |

---

## 7. Limitations & Future Work

1. **Rule-based aspect extraction:** Pain point aspect detection (packaging, scent, texture, etc.) uses keyword matching rather than learned aspect-based sentiment analysis (ABSA). A fine-tuned transformer (e.g. BERT-ABSA) would be more precise.

2. **Domain limitation:** Models were trained exclusively on Amazon Beauty reviews. Sentiment vocabulary in other domains (electronics, hospitality) will differ, reducing out-of-domain accuracy.

3. **No deep learning baseline:** Transformer-based models (DistilBERT, RoBERTa) were not evaluated due to computational constraints. A future comparison against fine-tuned transformers would be valuable.

4. **Static keyword scores:** TF-IDF keyword scores are fixed at training time. Live-ingested Google Places reviews are not incorporated into the keyword model.

5. **Google Places API dependency:** The live review ingestion feature requires a paid Google API key. Without it, only the historical Amazon dataset analysis is available.

---

## 8. Conclusion

This project delivers a complete, production-grade customer sentiment intelligence system. The core ML pipeline achieves 70.84% Macro Recall on a severely imbalanced 3-class problem using a deliberately chosen Balanced Logistic Regression model. The system is accessible through a real-time analytics dashboard that translates raw review text into structured, actionable business intelligence — from product-level pain points to live Google Maps review analysis. All components are tested (55 automated tests), version-controlled, and structured as a proper 3-tier application.
