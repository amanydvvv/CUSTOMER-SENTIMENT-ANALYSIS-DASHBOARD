import os
import re
import html
import joblib
import numpy as np

_CACHE = {}

def _get_artifacts(model_dir, model_name="balanced_logistic_regression"):
    cache_key = f"{model_dir}_{model_name}"
    if cache_key not in _CACHE:
        vec_path = os.path.join(model_dir, "tfidf_vectorizer.joblib")
        mod_path = os.path.join(model_dir, f"{model_name}.joblib")
        if not os.path.exists(vec_path) or not os.path.exists(mod_path):
            return None, None
        vectorizer = joblib.load(vec_path)
        model = joblib.load(mod_path)
        feature_names = np.array(vectorizer.get_feature_names_out())
        feat_to_idx = {f: i for i, f in enumerate(feature_names)}
        _CACHE[cache_key] = (vectorizer, model, feature_names, feat_to_idx)
    return _CACHE[cache_key]


def extract_keywords(model_dir, top_n=10):
    """Extract top predictive N-grams per sentiment class."""
    vec_path = os.path.join(model_dir, "tfidf_vectorizer.joblib")
    mod_path = os.path.join(model_dir, "logistic_regression.joblib")
    if not os.path.exists(vec_path) or not os.path.exists(mod_path):
        return {}

    vectorizer = joblib.load(vec_path)
    model = joblib.load(mod_path)
    feature_names = np.array(vectorizer.get_feature_names_out())

    keywords = {}
    for i, class_label in enumerate(model.classes_):
        top_indices = np.argsort(model.coef_[i])[-top_n:]
        keywords[class_label] = feature_names[top_indices].tolist()

    return keywords


def explain_text(text: str, model_dir: str, model_name: str = "balanced_logistic_regression"):
    """
    Computes token-level sentiment contribution and returns:
      - highlighted_html: HTML string with green/red word highlights
      - top_positive: list of (word, score)
      - top_negative: list of (word, score)
    """
    vectorizer, model, feature_names, feat_to_idx = _get_artifacts(model_dir, model_name)
    if not model or not hasattr(model, "coef_"):
        return {"highlighted_html": html.escape(text), "top_positive": [], "top_negative": []}

    classes = list(model.classes_)
    pos_idx = classes.index("positive") if "positive" in classes else 2
    neg_idx = classes.index("negative") if "negative" in classes else 0

    tokens = re.findall(r'\b\w+\b|[^\w\s]|\s+', text)
    highlighted_parts = []
    word_scores = []

    for tok in tokens:
        clean_tok = tok.lower().strip()
        if clean_tok in feat_to_idx:
            idx = feat_to_idx[clean_tok]
            p_score = float(model.coef_[pos_idx][idx])
            n_score = float(model.coef_[neg_idx][idx])
            diff = p_score - n_score

            word_scores.append((tok, diff, p_score, n_score))

            if diff > 0.8:
                # Strong Positive
                highlighted_parts.append(
                    f'<span style="background:rgba(34,197,94,0.18);color:#22C55E;padding:2px 5px;border-radius:4px;font-weight:600;" title="Positive (+{diff:.2f})">{html.escape(tok)}</span>'
                )
            elif diff < -0.8:
                # Strong Negative
                highlighted_parts.append(
                    f'<span style="background:rgba(239,68,68,0.18);color:#EF4444;padding:2px 5px;border-radius:4px;font-weight:600;" title="Negative ({diff:.2f})">{html.escape(tok)}</span>'
                )
            else:
                highlighted_parts.append(html.escape(tok))
        else:
            highlighted_parts.append(html.escape(tok))

    # Aggregate top positive & negative words
    unique_words = {}
    for tok, diff, p_score, n_score in word_scores:
        k = tok.lower()
        if k not in unique_words:
            unique_words[k] = diff

    sorted_words = sorted(unique_words.items(), key=lambda x: x[1], reverse=True)
    top_pos = [(w, score) for w, score in sorted_words if score > 0.5][:5]
    top_neg = [(w, abs(score)) for w, score in sorted_words if score < -0.5][-5:]

    return {
        "highlighted_html": "".join(highlighted_parts),
        "top_positive": top_pos,
        "top_negative": top_neg,
    }
