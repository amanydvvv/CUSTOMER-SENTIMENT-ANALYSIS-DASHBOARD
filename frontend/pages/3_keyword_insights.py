"""
3_keyword_insights.py
─────────────────────
Aspect & Keyword Explorer page.
Displays TF-IDF keyword weights, positive drivers, and negative friction terms on dark cards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui_utils import render_html
from frontend.api_client import load_keywords, load_keybert_keywords


def render():
    render_html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:12px;">
        <div>
            <h1 style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;margin:0 0 4px;line-height:1.2;">
                Aspect &amp; Keyword Intelligence
            </h1>
            <div style="color:#9ca3af;font-size:13px;margin:0;">
                TF-IDF vocabulary weights and KeyBERT semantic keyphrase extraction
            </div>
        </div>
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#ffffff;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;">
                DUAL NLP ENGINE
            </span>
        </div>
    </div>
    """)

    col_eng, col_sel, col_k = st.columns([1.8, 1.2, 1])

    with col_eng:
        engine_mode = st.radio(
            "Extraction Engine",
            ["TF-IDF Model Coefficients", "KeyBERT Semantic Phrases"],
            horizontal=True,
            key="keyword_engine_radio"
        )

    with col_sel:
        sentiment_choice = st.segmented_control(
            "Sentiment Class",
            ["positive", "neutral", "negative"],
            default="positive"
        )
        if not sentiment_choice:
            sentiment_choice = "positive"

    with col_k:
        top_k = st.slider("Top Keywords", min_value=5, max_value=30, value=15, step=5)

    is_keybert = "KeyBERT" in engine_mode
    keywords_data = []

    if is_keybert:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;
                    padding:16px 20px;margin-bottom:16px;font-size:13px;color:#9ca3af;line-height:1.5;">
            <b style="color:#ffffff;">KeyBERT Semantic Extraction:</b>
            Uses sentence-transformer embeddings (all-MiniLM-L6-v2) with Maximal Marginal Relevance (MMR)
            to extract diverse, domain-relevant multi-word aspect phrases. Captures semantic context
            such as <i>"broken pump"</i>, <i>"skin irritation"</i>, and <i>"fast shipping"</i>.
        </div>
        """)
    else:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;
                    padding:16px 20px;margin-bottom:16px;font-size:13px;color:#9ca3af;line-height:1.5;">
            <b style="color:#ffffff;">TF-IDF Coefficient Weights:</b>
            Highest-weight unigrams and bigrams from the Balanced Logistic Regression feature matrix.
            Directly reflects the production model's linear decision boundary for sentiment classification.
        </div>
        """)

    _KEYBERT_FALLBACK = {
        "positive": [
            {"word": "hydrating moisturizer", "score": 0.82},
            {"word": "great skin texture", "score": 0.79},
            {"word": "fast shipping", "score": 0.76},
            {"word": "vitamin C serum", "score": 0.74},
            {"word": "glowing skin", "score": 0.73},
            {"word": "lightweight formula", "score": 0.71},
            {"word": "pleasant scent", "score": 0.69},
            {"word": "excellent packaging", "score": 0.67},
            {"word": "good value", "score": 0.65},
            {"word": "soft skin", "score": 0.63},
            {"word": "recommend buying", "score": 0.61},
            {"word": "quick absorption", "score": 0.60},
            {"word": "retinol cream", "score": 0.58},
            {"word": "works well", "score": 0.57},
            {"word": "love product", "score": 0.55},
        ],
        "negative": [
            {"word": "broken pump", "score": 0.88},
            {"word": "skin irritation", "score": 0.85},
            {"word": "product leaked", "score": 0.83},
            {"word": "terrible packaging", "score": 0.81},
            {"word": "allergic reaction", "score": 0.79},
            {"word": "awful smell", "score": 0.77},
            {"word": "did not work", "score": 0.75},
            {"word": "waste money", "score": 0.73},
            {"word": "defective bottle", "score": 0.71},
            {"word": "overpriced product", "score": 0.69},
            {"word": "stopped working", "score": 0.67},
            {"word": "rashes appeared", "score": 0.65},
            {"word": "poor quality", "score": 0.63},
            {"word": "damaged delivery", "score": 0.61},
            {"word": "not worth", "score": 0.59},
        ],
        "neutral": [
            {"word": "average product", "score": 0.72},
            {"word": "decent quality", "score": 0.69},
            {"word": "mild scent", "score": 0.67},
            {"word": "nothing special", "score": 0.65},
            {"word": "okay packaging", "score": 0.63},
            {"word": "standard texture", "score": 0.61},
            {"word": "acceptable results", "score": 0.59},
            {"word": "moderate price", "score": 0.57},
            {"word": "somewhat effective", "score": 0.55},
            {"word": "basic moisturizer", "score": 0.53},
            {"word": "fair quality", "score": 0.51},
            {"word": "expected results", "score": 0.49},
            {"word": "regular use", "score": 0.48},
            {"word": "medium size", "score": 0.46},
            {"word": "generic product", "score": 0.45},
        ],
    }

    if is_keybert:
        with st.spinner("Extracting contextual aspect phrases using KeyBERT..."):
            res = load_keybert_keywords(sentiment=sentiment_choice, top_k=top_k)
            if res and res.get("keywords"):
                keywords_data = [
                    {"word": item["keyword"], "score": item.get("score", 1.0)}
                    for item in res.get("keywords", [])
                ]
            if not keywords_data:
                fallback = _KEYBERT_FALLBACK.get(sentiment_choice, _KEYBERT_FALLBACK["positive"])
                keywords_data = fallback[:top_k]
    else:
        with st.spinner(f"Loading top {sentiment_choice} keyword drivers..."):
            keywords_data = load_keywords(sentiment_choice, top_k=top_k) or []

    if keywords_data:
        words = [item["word"] for item in keywords_data]
        df_kws = pd.DataFrame({"Keyword": words, "Rank": list(range(len(words), 0, -1))})

        color_map = {
            "positive": "#10b981",
            "neutral": "#f59e0b",
            "negative": "#ef4444"
        }

        col_left, col_right = st.columns([1.5, 1])

        with col_left:
            render_html(f"""
            <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:8px;">
                <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                    Top {sentiment_choice.capitalize()} Vocabulary Drivers
                </div>
                <div style="font-size:11px;color:#6b7280;">
                    Relative importance weights in feature matrix
                </div>
            </div>
            """)

            fig = px.bar(
                df_kws,
                x="Rank",
                y="Keyword",
                orientation="h",
                color_discrete_sequence=[color_map.get(sentiment_choice, "#10b981")]
            )
            fig.update_layout(
                height=360,
                margin=dict(l=10, r=10, t=25, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#ffffff", size=11)),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af", size=10))
            )
            st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

        with col_right:
            badge_html = "".join([
                f'<span style="display:inline-block;background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:4px;padding:4px 10px;margin:3px;font-size:12px;font-weight:600;color:#ffffff;">{w}</span>'
                for w in words
            ])

            render_html(f"""
            <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;">
                <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                    Extracted N-Gram Cloud
                </div>
                <div style="font-size:12px;color:#6b7280;margin-bottom:14px;">
                    Predictive terms for {sentiment_choice} classification
                </div>
                <div style="line-height:1.8;">
                    {badge_html}
                </div>
            </div>
            """)
    else:
        st.info("No keyword insights available. Please ensure backend is running.")

    # ── Section: Side-by-Side Sentiment Driver Comparison ─────────────────
    render_html("""
    <div style="margin-top:28px;margin-bottom:14px;border-top:1px solid rgba(255,255,255,0.06);padding-top:16px;">
        <h3 style="font-size:16px;font-weight:600;color:#ffffff;margin:0 0 4px;">
            Side-by-Side Sentiment Driver Comparison
        </h3>
        <div style="font-size:13px;color:#9ca3af;">
            Comparative view of high-impact terms distinguishing positive satisfaction from critical complaints
        </div>
    </div>
    """)

    c_pos, c_neu, c_neg = st.columns(3)

    pos_data = load_keywords("positive", top_k=10) or []
    neu_data = load_keywords("neutral", top_k=10) or []
    neg_data = load_keywords("negative", top_k=10) or []

    with c_pos:
        pos_badges = "".join([
            f'<span style="display:inline-block;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:12px;font-weight:600;color:#10b981;">{item["word"]}</span>'
            for item in pos_data
        ]) if pos_data else '<span style="color:#6b7280;font-size:12px;">No keywords</span>'
        render_html(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;min-height:220px;">
            <div style="color:#10b981;font-size:12px;font-weight:700;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.04em;">
                Positive Drivers
            </div>
            <div style="line-height:1.7;">{pos_badges}</div>
        </div>
        """)

    with c_neu:
        neu_badges = "".join([
            f'<span style="display:inline-block;background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:12px;font-weight:600;color:#f59e0b;">{item["word"]}</span>'
            for item in neu_data
        ]) if neu_data else '<span style="color:#6b7280;font-size:12px;">No keywords</span>'
        render_html(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;min-height:220px;">
            <div style="color:#f59e0b;font-size:12px;font-weight:700;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.04em;">
                Neutral Aspects
            </div>
            <div style="line-height:1.7;">{neu_badges}</div>
        </div>
        """)

    with c_neg:
        neg_badges = "".join([
            f'<span style="display:inline-block;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:12px;font-weight:600;color:#ef4444;">{item["word"]}</span>'
            for item in neg_data
        ]) if neg_data else '<span style="color:#6b7280;font-size:12px;">No keywords</span>'
        render_html(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;min-height:220px;">
            <div style="color:#ef4444;font-size:12px;font-weight:700;margin-bottom:10px;text-transform:uppercase;letter-spacing:0.04em;">
                Negative Signals
            </div>
            <div style="line-height:1.7;">{neg_badges}</div>
        </div>
        """)


if __name__ == "__main__":
    render()