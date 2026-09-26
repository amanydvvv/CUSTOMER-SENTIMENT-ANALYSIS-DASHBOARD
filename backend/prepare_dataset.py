"""
prepare_dataset.py
──────────────────
Extracts, standardizes, cleans, and deduplicates genuine reviews from the
Amazon Reviews 2023 (All_Beauty) dataset for the Customer Feedback Intelligence System.

Key guarantees:
1. Memory-efficient streaming from compressed raw JSONL.
2. Real data only — no synthesis, duplication, or templating.
3. Sentiment derived strictly from ratings:
     1–2 stars → negative
     3 stars   → neutral
     4–5 stars → positive
4. Deduplication on clean_text before export.
5. Standardized schema with rich metadata preserved.
"""

import gzip
import json
import os
import hashlib
import random
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from app.ml.preprocessing import clean_text

# ── Paths ─────────────────────────────────────────────────────────────────────
RAW_GZ = os.path.join("backend", "data", "raw", "All_Beauty.jsonl.gz")
PROCESSED_DIR = os.path.join("backend", "data", "processed")
OUT_CSV = os.path.join(PROCESSED_DIR, "amazon_all_beauty_reviews.csv")
INFO_JSON = os.path.join(PROCESSED_DIR, "dataset_info.json")

RANDOM_SEED = 42
TARGET_CANDIDATE_ROWS = 85000


def rating_to_sentiment(rating):
    """
    Project labeling rule:
        1–2 stars → negative
        3 stars   → neutral
        4–5 stars → positive
    """
    try:
        r = float(rating)
    except (TypeError, ValueError):
        return None
    if 1.0 <= r <= 2.0:
        return "negative"
    elif r == 3.0:
        return "neutral"
    elif 4.0 <= r <= 5.0:
        return "positive"
    return None


def generate_review_id(user_id, asin, timestamp, text):
    """Generate a deterministic, unique 16-char hex ID from primary record fields."""
    raw_key = f"{user_id}_{asin}_{timestamp}_{text}".encode("utf-8")
    return "rev_" + hashlib.sha256(raw_key).hexdigest()[:16]


def format_date(timestamp_ms):
    """Convert Unix timestamp (ms) to readable UTC string (YYYY-MM-DD HH:MM:SS)."""
    if not timestamp_ms:
        return ""
    try:
        ts_sec = float(timestamp_ms) / 1000.0
        return datetime.fromtimestamp(ts_sec, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""


def main():
    print("=" * 60)
    print("PHASE 1: REAL DATASET PREPARATION")
    print("=" * 60)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    rng = random.Random(RANDOM_SEED)

    # First pass: count total raw rows
    print(f"\n[1/5] Streaming raw dataset from {RAW_GZ} ...")
    total_raw_rows = 0
    with gzip.open(RAW_GZ, "rt", encoding="utf-8") as f:
        for _ in f:
            total_raw_rows += 1
    print(f"  Total raw rows in source: {total_raw_rows:,}")

    # Sampling probability to collect ~TARGET_CANDIDATE_ROWS preserving natural distribution
    sample_rate = min(1.0, (TARGET_CANDIDATE_ROWS * 1.05) / total_raw_rows)
    print(f"  Target candidate sample size: ~{TARGET_CANDIDATE_ROWS:,} (Sampling rate: {sample_rate:.4f}, Seed: {RANDOM_SEED})")

    # Second pass: stream, sample, and parse records
    print(f"\n[2/5] Parsing and normalizing standardized records ...")
    candidates = []
    skipped_empty = 0
    skipped_invalid_rating = 0

    with gzip.open(RAW_GZ, "rt", encoding="utf-8") as f:
        for line in f:
            # Deterministic pseudo-random sampling
            if rng.random() > sample_rate:
                continue

            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue

            rating = r.get("rating")
            sentiment = rating_to_sentiment(rating)
            if sentiment is None:
                skipped_invalid_rating += 1
                continue

            text = str(r.get("text") or "").strip()
            title = str(r.get("title") or "").strip()

            combined_raw = (text + " " + title).strip()
            if not combined_raw:
                skipped_empty += 1
                continue

            user_id = str(r.get("user_id") or "")
            asin = str(r.get("asin") or r.get("parent_asin") or "")
            ts = r.get("timestamp") or 0
            rev_id = generate_review_id(user_id, asin, ts, text)

            candidates.append({
                "review_id": rev_id,
                "text": text,
                "title": title,
                "rating": float(rating),
                "product": asin,
                "category": "All_Beauty",
                "price": "",  # Unavailable in raw source; no estimation/fabrication
                "date": format_date(ts),
                "helpful_votes": int(r.get("helpful_vote") or 0),
                "verified_purchase": bool(r.get("verified_purchase", False)),
                "sentiment": sentiment,
                "source": "amazon_reviews_2023",
                "_raw_combined": combined_raw
            })

    print(f"  Sampled candidate rows: {len(candidates):,}")
    print(f"  Skipped empty texts: {skipped_empty:,}")
    print(f"  Skipped invalid ratings: {skipped_invalid_rating:,}")

    df = pd.DataFrame(candidates)

    # 3. Clean text generation
    print(f"\n[3/5] Cleaning text using preprocessing pipeline ...")
    df["clean_text"] = df["_raw_combined"].apply(clean_text)
    df.drop(columns=["_raw_combined"], inplace=True)

    # Filter empty clean_text
    before_clean_filter = len(df)
    df = df[df["clean_text"].str.strip() != ""]
    empty_clean_removed = before_clean_filter - len(df)
    print(f"  Rows removed due to empty clean_text: {empty_clean_removed:,}")

    # 4. Exact deduplication on clean_text
    print(f"\n[4/5] Deduplicating on exact clean_text ...")
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["clean_text"]).reset_index(drop=True)
    duplicates_removed = before_dedup - len(df)
    print(f"  Duplicate clean_text rows removed: {duplicates_removed:,}")
    print(f"  Final unique dataset rows: {len(df):,}")

    # 5. Quality verification checks
    print(f"\n[5/5] Running quality verification checks ...")
    assert df["clean_text"].str.strip().ne("").all(), "Found empty clean_text!"
    assert df["clean_text"].duplicated().sum() == 0, "Found duplicate clean_text!"
    assert set(df["sentiment"].unique()).issubset({"positive", "neutral", "negative"}), "Invalid sentiment labels found!"
    assert df["rating"].between(1.0, 5.0).all(), "Ratings out of bounds!"
    assert df["review_id"].duplicated().sum() == 0, "Duplicate review IDs found!"
    assert (df["source"] == "amazon_reviews_2023").all(), "Incorrect source field!"
    print("  [OK] All assertions passed successfully.")

    # Distribution summaries
    sentiment_counts = df["sentiment"].value_counts()
    sentiment_pcts = df["sentiment"].value_counts(normalize=True) * 100
    rating_counts = df["rating"].value_counts().sort_index()

    print("\n" + "=" * 60)
    print("FINAL DATASET SUMMARY")
    print("=" * 60)
    print("\nClass Distribution:")
    for cls in ["positive", "neutral", "negative"]:
        count = sentiment_counts.get(cls, 0)
        pct = sentiment_pcts.get(cls, 0.0)
        print(f"  {cls.capitalize():<10}: {count:>7,} ({pct:6.2f}%)")

    print("\nRating Distribution:")
    for star, count in rating_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {star} stars : {count:>7,} ({pct:6.2f}%)")

    # Save to CSV
    df.to_csv(OUT_CSV, index=False)
    print(f"\nSaved CSV to: {OUT_CSV}")

    # Save metadata summary JSON
    summary_info = {
        "source": "Amazon Reviews 2023 (All_Beauty.jsonl.gz)",
        "source_category": "All_Beauty",
        "original_total_rows": total_raw_rows,
        "sampled_candidate_rows": len(candidates),
        "duplicate_clean_text_removed": duplicates_removed,
        "empty_clean_text_removed": empty_clean_removed,
        "final_usable_rows": len(df),
        "random_seed": RANDOM_SEED,
        "sampling_method": "Deterministic pseudo-random stratified stream sampling",
        "labeling_rule": "1.0-2.0 -> negative, 3.0 -> neutral, 4.0-5.0 -> positive",
        "class_distribution": {
            cls: {
                "count": int(sentiment_counts.get(cls, 0)),
                "percentage": round(float(sentiment_pcts.get(cls, 0.0)), 2)
            }
            for cls in ["positive", "neutral", "negative"]
        },
        "rating_distribution": {
            str(star): {
                "count": int(rating_counts.get(star, 0)),
                "percentage": round(float((rating_counts.get(star, 0) / len(df)) * 100), 2)
            }
            for star in rating_counts.index
        },
        "schema_columns": list(df.columns),
        "unavailable_fields": ["price"],
        "synthetic_data_used": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat()
    }

    with open(INFO_JSON, "w", encoding="utf-8") as f:
        json.dump(summary_info, f, indent=2)
    print(f"Saved metadata to: {INFO_JSON}")


if __name__ == "__main__":
    main()
