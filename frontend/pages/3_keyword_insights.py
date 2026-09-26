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
from frontend.api_client import load_keywords


def render():
    header_html = """
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;border-bottom:1px solid #1E2533;padding-bottom:0.75rem;">
        <div>
            <h1 style="font-size:1.6rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
                ASPECT & KEYWORD INTELLIGENCE
            </h1>
            <div style="color:#98A2B3;font-size:0.82rem;margin:0;">
                TF-IDF feature vocabulary and sentiment coefficient drivers from customer feedback
            </div>
        </div>
        <div style="display:flex;gap:0.45rem;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(124,92,255,0.1);border:1px solid rgba(124,92,255,0.25);color:#7C5CFF;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                TF-IDF VOCABULARY
            </span>
        </div>
    </div>
    """
    render_html(header_html)

    col_sel, col_k = st.columns([2, 1])

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

    with st.spinner(f"Loading top {sentiment_choice} keyword drivers..."):
        keywords_data = load_keywords(sentiment_choice, top_k=top_k)

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


if __name__ == "__main__":
    render()