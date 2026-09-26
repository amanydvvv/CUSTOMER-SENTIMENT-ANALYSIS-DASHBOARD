"""
data_loader.py
──────────────
High-performance cached data loader for the processed Amazon Reviews dataset.
"""

import os
import pandas as pd
import streamlit as st
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "data", "processed", "amazon_all_beauty_reviews.csv")


@st.cache_data(show_spinner=False)
def load_historical_dataset(sample_limit: int = None) -> pd.DataFrame:
    """
    Loads processed real Amazon Reviews dataset with caching.
    Loads the full dataset by default.
    """
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    read_kwargs = {
        "dtype": {
            "review_id": str,
            "text": str,
            "title": str,
            "rating": float,
            "product": str,
            "category": str,
            "price": str,
            "date": str,
            "helpful_votes": int,
            "verified_purchase": bool,
            "sentiment": str,
            "clean_text": str,
            "source": str,
        }
    }
    if sample_limit is not None:
        read_kwargs["nrows"] = sample_limit

    df = pd.read_csv(DATA_PATH, **read_kwargs)

    # Fill NaNs
    df["text"] = df["text"].fillna("")
    df["title"] = df["title"].fillna("")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(5.0)
    df["helpful_votes"] = pd.to_numeric(df["helpful_votes"], errors="coerce").fillna(0).astype(int)
    df["verified_purchase"] = df["verified_purchase"].fillna(False).astype(bool)
    df["product"] = df["product"].fillna("Unknown")
    df["sentiment"] = df["sentiment"].fillna("neutral").str.lower()
    df["date_dt"] = pd.to_datetime(df["date"], errors="coerce")

    return df


def filter_dataset(
    df: pd.DataFrame,
    selected_products=None,
    selected_ratings=None,
    selected_sentiments=None,
    verified_only=False,
    search_query: str = ""
) -> pd.DataFrame:
    """Apply interactive filters to the dataset."""
    filtered = df

    if selected_products and "All" not in selected_products:
        filtered = filtered[filtered["product"].isin(selected_products)]

    if selected_ratings and "All" not in selected_ratings:
        numeric_ratings = [float(r) for r in selected_ratings if str(r).replace('.', '', 1).isdigit()]
        if numeric_ratings:
            filtered = filtered[filtered["rating"].isin(numeric_ratings)]

    if selected_sentiments and "All" not in selected_sentiments:
        clean_sents = [s.lower() for s in selected_sentiments]
        filtered = filtered[filtered["sentiment"].isin(clean_sents)]

    if verified_only:
        filtered = filtered[filtered["verified_purchase"] == True]

    if search_query and search_query.strip():
        q = search_query.strip().lower()
        filtered = filtered[
            filtered["text"].str.lower().str.contains(q, na=False) |
            filtered["title"].str.lower().str.contains(q, na=False)
        ]

    return filtered
