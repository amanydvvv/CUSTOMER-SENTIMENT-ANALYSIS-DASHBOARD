"""
smoke_test_unseen.py
────────────────────
Smoke and integrity test for the unseen/held-out customer review split.
Validates review sampling, ML model inference latency, and aspect extraction.
"""

import sys
import os
import time

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import joblib
from frontend.unseen_review_loader import load_unseen_reviews
from frontend.components.aspect_analyzer import extract_aspects_and_issues
from backend.app.ml.preprocessing import clean_text

def test_unseen_pipeline():
    print("=" * 60)
    print("[TEST] RUNNING SMOKE TEST: UNSEEN REVIEW DATASET & INFERENCE")
    print("=" * 60)

    # 1. Load Unseen Reviews
    t0 = time.time()
    df_unseen = load_unseen_reviews()
    load_time = (time.time() - t0) * 1000
    print(f"[OK] Loaded unseen test dataset in {load_time:.2f} ms")
    print(f"     Total held-out reviews: {len(df_unseen):,}")
    assert len(df_unseen) > 0, "Unseen dataset should not be empty!"

    required_cols = ["text", "rating", "sentiment", "product"]
    for col in required_cols:
        assert col in df_unseen.columns, f"Missing required column: {col}"
    print(f"[OK] Required schema verified: {required_cols}")

    # Class distribution check
    dist = df_unseen["sentiment"].value_counts().to_dict()
    print(f"     Sentiment distribution: {dist}")

    # 2. Test Model Artifacts
    models_dir = os.path.join(BACKEND_DIR, "models")
    vec_path = os.path.join(models_dir, "tfidf_vectorizer.joblib")
    lr_path = os.path.join(models_dir, "balanced_logistic_regression.joblib")

    assert os.path.exists(vec_path), f"Vectorizer missing at {vec_path}"
    assert os.path.exists(lr_path), f"Model missing at {lr_path}"

    vectorizer = joblib.load(vec_path)
    model = joblib.load(lr_path)
    print("[OK] Successfully loaded TF-IDF vectorizer and Balanced LR model")

    # 3. Test Inference on Sample of 50 Unseen Reviews
    sample_df = df_unseen.sample(min(50, len(df_unseen)), random_state=42)
    start_inf = time.time()
    cleaned_texts = [clean_text(str(t)) for t in sample_df["text"]]
    feats = vectorizer.transform(cleaned_texts)
    preds = model.predict(feats)
    total_inf_ms = (time.time() - start_inf) * 1000
    avg_latency = total_inf_ms / len(sample_df)

    print(f"[OK] Inferred {len(sample_df)} unseen reviews in {total_inf_ms:.2f} ms")
    print(f"     Average CPU latency: {avg_latency:.4f} ms/review (< 25.0 ms threshold)")
    assert avg_latency < 25.0, "Inference latency exceeded threshold!"

    # 4. Test Aspect & Issue Extraction
    sample_review = sample_df.iloc[0]["text"]
    sample_rating = float(sample_df.iloc[0]["rating"])
    intel = extract_aspects_and_issues(sample_review, sentiment=preds[0], rating=sample_rating)
    assert "primary_aspect" in intel
    assert "issue" in intel
    assert "priority" in intel
    assert "suggested_action" in intel
    print("[OK] Aspect extraction verified:")
    print(f"     Review snippet: {sample_review[:60]}...")
    print(f"     Aspect: {intel['primary_aspect']} | Issue: {intel['issue']} | Priority: {intel['priority']}")

    print("\n" + "=" * 60)
    print("[SUCCESS] ALL SMOKE TESTS PASSED (100% HEALTHY)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_unseen_pipeline()
    sys.exit(0 if success else 1)
