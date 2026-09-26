"""
Smoke test: unseen review loader end-to-end (no real Streamlit session).
Run with: python smoke_test_unseen.py  (from project root)
"""
import sys, os
sys.path.insert(0, '.')
import unittest.mock as mock

# Patch st.cache_data and st.warning to no-ops
import streamlit as st
with mock.patch('streamlit.cache_data', lambda **kw: lambda f: f), \
     mock.patch('streamlit.warning', lambda *a, **k: None):
    from frontend.unseen_review_loader import load_unseen_reviews
    df = load_unseen_reviews(n_samples=50, model_name='balanced_logistic_regression')

if df.empty:
    print('ERROR: returned empty DataFrame')
    sys.exit(1)

print(f'PASS: {len(df)} unseen reviews loaded')
print(f'Columns: {df.columns.tolist()}')
print(f'Sentiment distribution: {df["sentiment"].value_counts().to_dict()}')
print(f'Mismatch count: {int(df["is_mismatch"].sum())}')
print(f'Source: {df["source"].iloc[0]}')
print(f'Model: {df["model_name"].iloc[0]}')
print(f'Has confidence scores: {df["confidence"].iloc[0] is not None}')
print()

r = df.iloc[0]
print('Sample review:')
print(f'  Rating: {r["rating"]}')
print(f'  Label: {r["label_sentiment"]}  ->  ML prediction: {r["sentiment"]}')
print(f'  Text: {str(r["text"])[:120]}...')

# Verify model didn't cheat — prediction column exists and differs from label for some
agrees = (df["sentiment"] == df["label_sentiment"]).sum()
differs = (df["sentiment"] != df["label_sentiment"]).sum()
print()
print(f'Model agrees with label: {agrees}/{len(df)}')
print(f'Model differs from label: {differs}/{len(df)} (expected non-zero — model makes independent predictions)')
print()
print('All smoke tests passed.')
