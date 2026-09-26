import pandas as pd
import joblib
import os
import json
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from .preprocessing import preprocess_df
from .features import get_vectorizer


def train_all(raw_data_path, models_dir):
    print("Loading data...")
    df = pd.read_csv(raw_data_path)

    # ── Normalise column names ──────────────────────────────────────────────
    # Support both legacy (Review/Summary/Sentiment) and new standardized schema.
    if 'Review' in df.columns and 'Summary' in df.columns:
        df['Review'] = df['Review'].fillna("")
        df['Summary'] = df['Summary'].fillna("")
        df['text'] = df['Review'] + " " + df['Summary']
    elif 'text' in df.columns:
        pass  # already combined
    else:
        raise ValueError("Dataset must have either (Review + Summary) or a 'text' column.")

    if 'Sentiment' in df.columns and 'sentiment' not in df.columns:
        df['sentiment'] = df['Sentiment']
    if 'sentiment' not in df.columns:
        raise ValueError("Dataset must have a 'sentiment' (or 'Sentiment') column.")

    print(f"  Raw rows: {len(df):,}")

    # ── Preprocess (includes clean_text dedup) ──────────────────────────────
    df = preprocess_df(df)
    print(f"  After preprocessing + dedup: {len(df):,} unique rows")
    print("  Class distribution:")
    print(df['sentiment'].value_counts().to_string())

    X = df['clean_text']
    y = df['sentiment']

    # ── Split AFTER dedup ───────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n  Train: {len(X_train):,}  |  Test: {len(X_test):,}")

    # Verify zero clean_text overlap between train and test
    overlap = set(X_train) & set(X_test)
    print(f"  Train/test text overlap: {len(overlap)} (must be 0)")
    assert len(overlap) == 0, "FATAL: train/test text overlap detected!"

    # ── TF-IDF (fit on train only) ──────────────────────────────────────────
    print("\nFitting TF-IDF on training data only...")
    tfidf = get_vectorizer()
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf  = tfidf.transform(X_test)

    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(tfidf, os.path.join(models_dir, 'tfidf_vectorizer.joblib'))

    # Save label list for reference
    labels = sorted(y.unique().tolist())
    with open(os.path.join(models_dir, 'label_info.json'), 'w') as f:
        json.dump({
            "labels": labels,
            "labeling_rule": {
                "1-2": "negative",
                "3":   "neutral",
                "4-5": "positive"
            },
            "source": "amazon_reviews_2023_all_beauty",
            "total_unique_reviews": len(df),
            "class_distribution": df['sentiment'].value_counts().to_dict(),
            "train_size": len(X_train),
            "test_size":  len(X_test),
        }, f, indent=2)

    # ── Models ──────────────────────────────────────────────────────────────
    models = {
        'logistic_regression':          LogisticRegression(max_iter=1000, random_state=42),
        'balanced_logistic_regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        'linearsvc':                    LinearSVC(random_state=42, max_iter=2000),
    }

    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_tfidf, y_train)
        joblib.dump(model, os.path.join(models_dir, f'{name}.joblib'))
        print(f"  Saved {name}.joblib")

    # Save test split for evaluation
    joblib.dump((X_test_tfidf, y_test), os.path.join(models_dir, 'test_data.joblib'))
    print("\nTraining complete. All artifacts saved.")


if __name__ == "__main__":
    train_all(
        os.path.join("backend", "data", "processed", "amazon_all_beauty_reviews.csv"),
        os.path.join("backend", "models")
    )
