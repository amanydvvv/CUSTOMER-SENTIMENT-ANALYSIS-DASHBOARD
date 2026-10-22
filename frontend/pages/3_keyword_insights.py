"""
3_keyword_insights.py
─────────────────────
Aspect & Keyword Explorer page.
Displays TF-IDF keyword weights, positive drivers, and negative friction terms on dark cards.
Uses render_html from frontend.ui_utils to guarantee zero raw HTML leaks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from frontend.ui_utils import render_html
from frontend.api_client import load_keywords, load_keybert_keywords


def render():
    header_html = """
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;border-bottom:1px solid #1E2533;padding-bottom:0.75rem;">
        <div>
            <h1 style="font-size:1.6rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
                ASPECT & KEYWORD INTELLIGENCE
            </h1>
            <div style="color:#98A2B3;font-size:0.82rem;margin:0;">
                TF-IDF feature vocabulary & KeyBERT semantic aspect phrase extraction
            </div>
        </div>
        <div style="display:flex;gap:0.45rem;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(124,92,255,0.1);border:1px solid rgba(124,92,255,0.25);color:#7C5CFF;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                DUAL NLP ENGINE
            </span>
            <span style="background:rgba(34,211,238,0.1);border:1px solid rgba(34,211,238,0.25);color:#22D3EE;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                TF-IDF + KeyBERT
            </span>
        </div>
    </div>
    """
    render_html(header_html)

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
        with st.spinner("Extracting contextual aspect phrases using KeyBERT embeddings..."):
            res = load_keybert_keywords(sentiment=sentiment_choice, top_k=top_k)
            if res and res.get("status") == "ok":
                keywords_data = [
                    {"word": item["keyword"], "score": item.get("score", 1.0)}
                    for item in res.get("keywords", [])
                ]
            elif res and res.get("keywords"):
                keywords_data = [
                    {"word": item["keyword"], "score": item.get("score", 1.0)}
                    for item in res.get("keywords", [])
                ]

    if not keywords_data:
        # TF-IDF mode or KeyBERT fallback
        with st.spinner(f"Loading top {sentiment_choice} keyword drivers..."):
            keywords_data = load_keywords(sentiment_choice, top_k=top_k) or []

    if keywords_data:
        words = [item["word"] for item in keywords_data]
        df_kws = pd.DataFrame({"Keyword": words, "Rank": list(range(len(words), 0, -1))})

        color_map = {
            "positive": "#22C55E",
            "neutral": "#F59E0B",
            "negative": "#EF4444"
        }

        col_left, col_right = st.columns([1.5, 1])

        with col_left:
            render_html(f"""
            <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:0.95rem 1.15rem;margin-bottom:0.4rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem;">
                    Top {sentiment_choice.capitalize()} Vocabulary Drivers
                </div>
                <div style="font-size:0.72rem;color:#98A2B3;">
                    Relative importance weights in TF-IDF feature matrix
                </div>
            </div>
            """)

            fig = px.bar(
                df_kws,
                x="Rank",
                y="Keyword",
                orientation="h",
                color_discrete_sequence=[color_map.get(sentiment_choice, "#7C5CFF")]
            )
            fig.update_layout(
                height=360,
                margin=dict(l=10, r=20, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="",
                yaxis_title="",
                yaxis=dict(autorange="reversed", tickfont=dict(color="#F5F7FA", size=11)),
                xaxis=dict(showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3", size=10))
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with col_right:
            badge_html = "".join([
                f'<span style="display:inline-block;background:#151A24;border:1px solid #242A35;border-radius:4px;padding:4px 10px;margin:3px;font-size:0.8rem;font-weight:600;color:#F5F7FA;">{w}</span>'
                for w in words
            ])

            render_html(f"""
            <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;">
                <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
                    Extracted N-Gram Cloud
                </div>
                <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:1rem;">
                    Strongest predictive terms for {sentiment_choice} classification
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
    <div style="margin-top:1.75rem;margin-bottom:0.85rem;border-top:1px solid #1E2533;padding-top:1.1rem;">
        <h3 style="font-size:1.05rem;font-weight:700;color:#F5F7FA;margin:0 0 0.2rem;">
            📊 Side-by-Side Sentiment Driver Comparison
        </h3>
        <div style="font-size:0.78rem;color:#98A2B3;">
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
            f'<span style="display:inline-block;background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:0.78rem;font-weight:600;color:#22C55E;">{item["word"]}</span>'
            for item in pos_data
        ]) if pos_data else '<span style="color:#98A2B3;font-size:0.78rem;">No keywords</span>'
        render_html(f"""
        <div style="background:#11151D;border:1px solid rgba(34,197,94,0.25);border-radius:8px;padding:0.9rem 1rem;min-height:220px;">
            <div style="color:#22C55E;font-size:0.82rem;font-weight:700;margin-bottom:0.6rem;">
                🟢 Positive Drivers
            </div>
            <div style="line-height:1.7;">{pos_badges}</div>
        </div>
        """)

    with c_neu:
        neu_badges = "".join([
            f'<span style="display:inline-block;background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:0.78rem;font-weight:600;color:#F59E0B;">{item["word"]}</span>'
            for item in neu_data
        ]) if neu_data else '<span style="color:#98A2B3;font-size:0.78rem;">No keywords</span>'
        render_html(f"""
        <div style="background:#11151D;border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:0.9rem 1rem;min-height:220px;">
            <div style="color:#F59E0B;font-size:0.82rem;font-weight:700;margin-bottom:0.6rem;">
                ⚪ Neutral Aspects
            </div>
            <div style="line-height:1.7;">{neu_badges}</div>
        </div>
        """)

    with c_neg:
        neg_badges = "".join([
            f'<span style="display:inline-block;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:4px;padding:3px 8px;margin:3px;font-size:0.78rem;font-weight:600;color:#EF4444;">{item["word"]}</span>'
            for item in neg_data
        ]) if neg_data else '<span style="color:#98A2B3;font-size:0.78rem;">No keywords</span>'
        render_html(f"""
        <div style="background:#11151D;border:1px solid rgba(239,68,68,0.25);border-radius:8px;padding:0.9rem 1rem;min-height:220px;">
            <div style="color:#EF4444;font-size:0.82rem;font-weight:700;margin-bottom:0.6rem;">
                🔴 Negative Signals
            </div>
            <div style="line-height:1.7;">{neg_badges}</div>
        </div>
        """)



if __name__ == "__main__":
    render()