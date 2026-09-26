import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


def clean_text(text):
    """
    Stateless text cleaner. Safe to apply before or after splitting.
    Expands common negation contractions before stripping punctuation
    so that 'don't' → 'do not' is preserved as a meaningful signal.
    """
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Strip URLs
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text, flags=re.MULTILINE)

    negation_map = {
        "don't": "do not", "doesn't": "does not", "didn't": "did not",
        "can't": "cannot", "couldn't": "could not", "won't": "will not",
        "wouldn't": "would not", "aren't": "are not", "isn't": "is not",
        "wasn't": "was not", "weren't": "were not", "hasn't": "has not",
        "haven't": "have not", "hadn't": "had not", "shouldn't": "should not",
        "mightn't": "might not", "mustn't": "must not"
    }
    for word, replacement in negation_map.items():
        text = text.replace(word, replacement)

    # Keep only letters and spaces
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    stop_words = set(stopwords.words('english'))
    # Retain negation-related words
    neg_words = {
        'no', 'not', 'nor', 'against', 'but',
        'do', 'does', 'did', 'is', 'are', 'was', 'were',
        'has', 'have', 'had', 'should', 'could', 'would',
        'might', 'must', 'can', 'will'
    }
    custom_stop_words = stop_words - neg_words

    words = text.split()
    filtered = [w for w in words if w not in custom_stop_words]
    return " ".join(filtered)


def preprocess_df(df):
    """
    Accepts a DataFrame with at minimum columns: text (raw combined text),
    sentiment (label). Optionally accepts any of the standardized schema
    columns (review_id, title, rating, product, category, price, date,
    helpful_votes, source) which are preserved but not used for modelling.

    Key guarantee: deduplication is performed on clean_text BEFORE this
    function returns, so callers can safely split immediately after.
    """
    # Build combined raw text if separate Review/Summary columns exist
    # (legacy path — kept for backward compatibility)
    if 'Review' in df.columns and 'Summary' in df.columns:
        df = df.copy()
        df['Review'] = df['Review'].fillna("")
        df['Summary'] = df['Summary'].fillna("")
        if 'text' not in df.columns:
            df['text'] = df['Review'] + " " + df['Summary']

    # Drop rows with empty raw text
    if 'text' in df.columns:
        df = df[df['text'].str.strip() != ""]

    # Drop rows with missing sentiment label
    if 'Sentiment' in df.columns and 'sentiment' not in df.columns:
        df = df.rename(columns={'Sentiment': 'sentiment'})
    if 'sentiment' in df.columns:
        df = df.dropna(subset=['sentiment'])

    # Apply text cleaning
    df = df.copy()
    df['clean_text'] = df['text'].apply(clean_text)
    df = df[df['clean_text'].str.strip() != ""]

    # ── CRITICAL FIX ──────────────────────────────────────────────────────────
    # Deduplicate on clean_text BEFORE any split.
    # The old pipeline used drop_duplicates() on full rows, which left
    # thousands of near-identical clean_text strings crossing train/test.
    df = df.drop_duplicates(subset=['clean_text'])
    # ─────────────────────────────────────────────────────────────────────────

    df = df.reset_index(drop=True)
    return df
