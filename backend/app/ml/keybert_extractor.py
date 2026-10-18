"""
keybert_extractor.py
────────────────────
KeyBERT-powered keyword and aspect extraction.
Replaces TF-IDF coefficient-based keyword extraction for richer,
semantically-grounded key phrase detection.

Architecture: Planned for Review-3 (as per project presentation slide).
"""

import os
from typing import List, Dict, Optional

# Lazy import — model loads only when first needed
_kb_model = None


def _get_keybert():
    """Lazy-load KeyBERT model (loads sentence-transformers once)."""
    global _kb_model
    if _kb_model is None:
        try:
            from keybert import KeyBERT
            # all-MiniLM-L6-v2 is fast, small (80MB), and works well on reviews
            _kb_model = KeyBERT(model="all-MiniLM-L6-v2")
        except Exception as e:
            raise RuntimeError(f"KeyBERT model failed to load: {e}")
    return _kb_model


def extract_keybert_keywords(
    texts: List[str],
    top_n: int = 10,
    keyphrase_ngram_range: tuple = (1, 2),
    stop_words: str = "english",
    diversity: float = 0.5,
) -> List[Dict]:
    """
    Extract top-N semantically representative keyphrases from a list of texts
    using KeyBERT (BERT embeddings + cosine similarity).

    Args:
        texts:                  List of raw review texts
        top_n:                  Number of keyphrases to extract
        keyphrase_ngram_range:  Min/max n-gram length (1,2) = unigrams + bigrams
        stop_words:             Language for stopword filtering
        diversity:              0.0 = no diversity, 1.0 = maximum diversity
                                (uses Maximal Marginal Relevance)

    Returns:
        List of dicts: [{"keyword": str, "score": float}, ...]
    """
    if not texts:
        return []

    kw_model = _get_keybert()

    # Combine all texts into one document for corpus-level extraction
    combined = " ".join([str(t) for t in texts if str(t).strip()])
    if not combined.strip():
        return []

    try:
        keywords = kw_model.extract_keywords(
            combined,
            keyphrase_ngram_range=keyphrase_ngram_range,
            stop_words=stop_words,
            top_n=top_n,
            use_mmr=True,        # Maximal Marginal Relevance for diversity
            diversity=diversity,
        )
        return [{"keyword": kw, "score": round(float(score), 4)} for kw, score in keywords]
    except Exception as e:
        return [{"keyword": f"[KeyBERT error: {e}]", "score": 0.0}]


def extract_keybert_by_sentiment(
    df,
    sentiment: str,
    text_col: str = "text",
    top_n: int = 15,
    sample_limit: int = 500,
) -> List[Dict]:
    """
    Extract keyphrases from reviews of a specific sentiment class.

    Args:
        df:           DataFrame with text_col and 'sentiment' column
        sentiment:    'positive', 'negative', or 'neutral'
        text_col:     Column name containing raw review text
        top_n:        Number of keyphrases to return
        sample_limit: Max reviews to sample (for speed on CPU)

    Returns:
        List of dicts: [{"keyword": str, "score": float}, ...]
    """
    subset = df[df["sentiment"] == sentiment.lower()][text_col]
    if subset.empty:
        return []

    # Sample for CPU performance
    if len(subset) > sample_limit:
        subset = subset.sample(sample_limit, random_state=42)

    texts = subset.dropna().tolist()
    return extract_keybert_keywords(texts, top_n=top_n)


def is_keybert_available() -> bool:
    """Check if KeyBERT can be loaded without actually loading it."""
    try:
        import keybert  # noqa
        import sentence_transformers  # noqa
        return True
    except ImportError:
        return False
