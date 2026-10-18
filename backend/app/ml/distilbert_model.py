"""
distilbert_model.py
───────────────────
DistilBERT-based sentiment classifier.

Architecture Role: PRIMARY MODEL (as per project presentation slide).
Fallback: TF-IDF + Balanced Logistic Regression (when unavailable or low confidence).

Model used: lxyuan/distilbert-base-multilingual-cased-sentiments-student
- Pre-trained 3-class sentiment (positive / neutral / negative)
- No fine-tuning required
- ~268MB download, cached by HuggingFace after first load
- CPU inference: ~200-500ms per review
"""

import os
import time
from typing import Optional, Dict, Tuple

# Lazy globals — loaded once on first call
_pipeline = None
_load_error: Optional[str] = None

# Model identifier from HuggingFace Hub
DISTILBERT_MODEL_ID = "lxyuan/distilbert-base-multilingual-cased-sentiments-student"

# Label normalization — maps HuggingFace labels to our schema
LABEL_MAP = {
    "positive": "positive",
    "neutral":  "neutral",
    "negative": "negative",
    "LABEL_0":  "negative",   # fallback if model uses numeric labels
    "LABEL_1":  "neutral",
    "LABEL_2":  "positive",
}


def _load_pipeline():
    """
    Lazy-load the HuggingFace sentiment pipeline.
    First call downloads the model (~268MB, cached).
    Subsequent calls use the cache.
    """
    global _pipeline, _load_error
    if _pipeline is not None:
        return _pipeline
    if _load_error is not None:
        raise RuntimeError(_load_error)

    try:
        from transformers import pipeline
        _pipeline = pipeline(
            task="text-classification",
            model=DISTILBERT_MODEL_ID,
            return_all_scores=True,   # get probabilities for all 3 classes
            device=-1,                # -1 = CPU (no GPU required)
            truncation=True,
            max_length=512,
        )
        return _pipeline
    except Exception as e:
        _load_error = str(e)
        raise RuntimeError(f"DistilBERT failed to load: {e}")


def predict_distilbert(
    text: str,
    confidence_threshold: float = 0.50,
) -> Tuple[str, Optional[float], Optional[Dict[str, float]]]:
    """
    Run DistilBERT inference on a single review text.

    Returns:
        (sentiment, confidence, all_scores)
        - sentiment:   'positive' | 'neutral' | 'negative'
        - confidence:  float 0-1, winning class probability
        - all_scores:  dict with probabilities for all 3 classes
                       e.g. {"positive": 0.78, "neutral": 0.14, "negative": 0.08}

    If confidence < threshold, the caller should fall back to TF-IDF model.
    """
    if not text or not str(text).strip():
        return "neutral", None, None

    try:
        clf = _load_pipeline()
        start = time.time()
        raw = clf(str(text)[:512])   # truncate to model's max length
        elapsed_ms = (time.time() - start) * 1000

        # raw is a list of lists: [[{label, score}, ...]]
        scores_list = raw[0] if isinstance(raw[0], list) else raw

        # Build normalized scores dict
        all_scores = {}
        for item in scores_list:
            label_raw = item["label"].lower()
            label_norm = LABEL_MAP.get(label_raw, label_raw)
            all_scores[label_norm] = round(float(item["score"]), 4)

        # Pick winning class
        best_label = max(all_scores, key=all_scores.get)
        confidence  = all_scores[best_label]

        return best_label, confidence, all_scores

    except RuntimeError:
        raise
    except Exception as e:
        # Unexpected error — surface it
        raise RuntimeError(f"DistilBERT inference error: {e}")


def is_distilbert_available() -> bool:
    """
    Non-blocking check — returns True if pipeline is already loaded.
    Does NOT trigger a download. Use for health checks.
    """
    return _pipeline is not None


def get_distilbert_status() -> Dict:
    """Return status dict for /health endpoint."""
    return {
        "model_id": DISTILBERT_MODEL_ID,
        "loaded": _pipeline is not None,
        "load_error": _load_error,
    }
