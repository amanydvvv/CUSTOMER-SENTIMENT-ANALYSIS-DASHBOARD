"""
1_overview.py
─────────────
Customer Feedback Intelligence page.
Structured around customer intelligence decision-support:
REVIEWS → SENTIMENT → ASPECT → PROBLEM → PRIORITY → ACTION

Tabs:
 1. Historical Reviews  — Amazon Reviews 2023 dataset, fully local
 2. Held-Out Validation — Held-out test split (Model Validation)
 3. New Review Analysis — Single review inference & batch testing
 4. Store Ingestion     — Preloaded verified venue feedback
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import importlib

from frontend.ui_utils import render_html
from frontend.data_loader import load_historical_dataset, filter_dataset
from frontend.components.sentiment_pulse import render_sentiment_pulse
from frontend.components.review_feed import render_review_feed
from frontend.components.pain_point_section import render_pain_point_section, analyze_negative_aspects
from frontend.components.mismatch_section import render_mismatch_section
from frontend.components.aspect_analyzer import extract_aspects_and_issues
from frontend.unseen_review_loader import load_unseen_reviews


def _rating_label(rating: float) -> str:
    try:
        r = float(rating)
    except Exception:
        r = 5.0
    return f"{r:.1f} / 5.0"


def _render_historical():
    df_raw = load_historical_dataset()

    if df_raw.empty:
        st.error("Cannot load dataset. Ensure backend/data/processed/amazon_all_beauty_reviews.csv exists.")
        return

    # Compact sidebar filters
    with st.sidebar:
        render_html('<div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:12px;">FILTER REVIEWS</div>')

        if st.button("Reset Filters", width='stretch'):
            for k in ["filter_products", "filter_ratings", "filter_sentiments",
                      "filter_verified", "filter_search", "filter_date_from", "filter_date_to"]:
                st.session_state.pop(k, None)
            st.rerun()

        st.markdown("<div style='font-size:12px;color:#9ca3af;font-weight:600;margin-top:12px;'>Date Range</div>", unsafe_allow_html=True)
        _dcol1, _dcol2 = st.columns(2)
        with _dcol1:
            date_from = st.date_input("From", value=None, key="filter_date_from")
        with _dcol2:
            date_to = st.date_input("To", value=None, key="filter_date_to")

        top_products = ["All"] + sorted(df_raw["product"].value_counts().head(20).index.tolist())
        selected_prods = st.multiselect(
            "Product ASIN", options=top_products,
            default=st.session_state.get("filter_products", ["All"]),
            key="filter_products"
        )
        selected_ratings = st.multiselect(
            "Star Rating", options=["All", "5.0", "4.0", "3.0", "2.0", "1.0"],
            default=st.session_state.get("filter_ratings", ["All"]),
            key="filter_ratings"
        )
        selected_sentiments = st.multiselect(
            "Sentiment Class", options=["All", "Positive", "Neutral", "Negative"],
            default=st.session_state.get("filter_sentiments", ["All"]),
            key="filter_sentiments"
        )
        verified_only = st.checkbox(
            "Verified Purchases Only",
            value=st.session_state.get("filter_verified", False),
            key="filter_verified"
        )
        search_query = st.text_input(
            "Keyword search",
            value=st.session_state.get("filter_search", ""),
            placeholder="e.g. rash, broken, delivery...",
            key="filter_search"
        )

    df = filter_dataset(
        df_raw,
        selected_products=selected_prods,
        selected_ratings=selected_ratings,
        selected_sentiments=selected_sentiments,
        verified_only=verified_only,
        search_query=search_query,
    )

    _date_from = st.session_state.get("filter_date_from")
    _date_to = st.session_state.get("filter_date_to")
    if _date_from and _date_to and _date_from > _date_to:
        st.warning("Start date must be before end date. Date filter skipped.")
    else:
        if "date_dt" in df.columns:
            import pandas as _pd
            if _date_from:
                df = df[df["date_dt"] >= _pd.Timestamp(_date_from)]
            if _date_to:
                df = df[df["date_dt"] <= _pd.Timestamp(_date_to)]

    total = len(df)
    if total == 0:
        st.warning("No reviews match the current filters. Please adjust or reset filters.")
        return

    pos_count = (df["sentiment"] == "positive").sum()
    neg_count = (df["sentiment"] == "negative").sum()
    neu_count = (df["sentiment"] == "neutral").sum()

    pos_pct = (pos_count / total) * 100
    neg_pct = (neg_count / total) * 100
    neu_pct = (neu_count / total) * 100
    avg_rating = df["rating"].mean()
    verified_pct = (df["verified_purchase"].sum() / total) * 100 if "verified_purchase" in df.columns else 0.0

    neg_df = df[df["sentiment"] == "negative"]
    aspect_summary, _, _ = analyze_negative_aspects(neg_df)
    top_aspect = aspect_summary[0]["aspect"] if aspect_summary else "General Quality"
    top_aspect_share = aspect_summary[0]["share_pct"] if aspect_summary else 0.0

    exec_summary_text = (
        f"<b>{pos_pct:.1f}%</b> of filtered reviews are classified as positive and <b>{neg_pct:.1f}%</b> as negative. "
        f"<b>{top_aspect}</b> ({top_aspect_share:.1f}% of complaints) is currently the most frequent friction area."
    )

    summary_card_html = f"""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                MACRO CUSTOMER FEEDBACK SUMMARY
            </div>
            <div style="font-size:11px;color:#6b7280;">
                Verified Buyers: <b style="color:#ffffff;">{verified_pct:.1f}%</b>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:12px;margin-bottom:14px;">
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px 16px;">
                <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;">REVIEWS</div>
                <div style="font-size:22px;font-weight:700;color:#ffffff;margin:4px 0 2px;">{total:,}</div>
                <div style="font-size:11px;color:#6b7280;">Filtered sample</div>
            </div>
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px 16px;">
                <div style="font-size:11px;font-weight:600;color:#10b981;text-transform:uppercase;">POSITIVE</div>
                <div style="font-size:22px;font-weight:700;color:#10b981;margin:4px 0 2px;">{pos_pct:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">{pos_count:,} reviews</div>
            </div>
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px 16px;">
                <div style="font-size:11px;font-weight:600;color:#ef4444;text-transform:uppercase;">NEGATIVE</div>
                <div style="font-size:22px;font-weight:700;color:#ef4444;margin:4px 0 2px;">{neg_pct:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">{neg_count:,} reviews</div>
            </div>
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px 16px;">
                <div style="font-size:11px;font-weight:600;color:#f59e0b;text-transform:uppercase;">AVG RATING</div>
                <div style="font-size:22px;font-weight:700;color:#f59e0b;margin:4px 0 2px;">{avg_rating:.2f}</div>
                <div style="font-size:11px;color:#6b7280;">out of 5.0</div>
            </div>
        </div>

        <div style="background:#181b21;border-left:3px solid #10b981;border-radius:0 6px 6px 0;padding:10px 14px;font-size:13px;color:#d1d5db;line-height:1.45;">
            {exec_summary_text}
        </div>
    </div>
    """
    render_html(summary_card_html)

    # ── HISTORICAL TREND OVER TIME (Rule 5) ──────────────────────────────────
    if "date_dt" in df.columns and df["date_dt"].notna().sum() > 0:
        df_dates = df.dropna(subset=["date_dt"]).copy()
        quarterly = (
            df_dates.groupby(df_dates["date_dt"].dt.to_period("Q"))
            .agg(
                total=("sentiment", "count"),
                positive=("sentiment", lambda s: (s == "positive").sum()),
            )
            .reset_index()
        )
        quarterly["quarter_str"] = quarterly["date_dt"].astype(str)
        quarterly["pos_ratio"] = (quarterly["positive"] / quarterly["total"] * 100).round(1)

        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                        HISTORICAL QUARTERLY TRAJECTORY
                    </span>
                    <div style="font-size:13px;color:#d1d5db;margin-top:2px;">
                        Quarterly review volume and positive sentiment ratio
                    </div>
                </div>
            </div>
        </div>
        """)

        trend_metric = st.segmented_control(
            "Trend View",
            options=["Review Volume", "Positive Ratio (%)"],
            default="Review Volume",
            key="hist_trend_view_toggle",
            label_visibility="collapsed"
        )

        fig_trend = go.Figure()
        if trend_metric == "Positive Ratio (%)":
            fig_trend.add_trace(go.Scatter(
                x=quarterly["quarter_str"],
                y=quarterly["pos_ratio"],
                mode="lines",
                name="Positive Ratio",
                line=dict(color="#10b981", width=2),
                fill="tozeroy",
                fillcolor="rgba(16, 185, 129, 0.10)",
                hovertemplate="Quarter: %{x}<br>Positive Ratio: %{y:.1f}%<extra></extra>"
            ))
            y_title = "Positive %"
        else:
            fig_trend.add_trace(go.Scatter(
                x=quarterly["quarter_str"],
                y=quarterly["total"],
                mode="lines",
                name="Review Volume",
                line=dict(color="#10b981", width=2),
                fill="tozeroy",
                fillcolor="rgba(16, 185, 129, 0.10)",
                hovertemplate="Quarter: %{x}<br>Volume: %{y:,} reviews<extra></extra>"
            ))
            y_title = "Review Count"

        fig_trend.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=220,
            margin=dict(l=10, r=10, t=25, b=10),
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af", size=10)),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af", size=10), title=y_title),
            showlegend=False
        )
        st.plotly_chart(fig_trend, width='stretch', config={"displayModeBar": False})

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── SENTIMENT PULSE ───────────────────────────────────────────────────────
    render_sentiment_pulse(df, df_raw)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── TOP CUSTOMER CONCERNS & PAIN POINTS ──────────────────────────────────
    render_pain_point_section(df)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── RATING × SENTIMENT MISMATCH ──────────────────────────────────────────
    render_mismatch_section(df)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # ── CUSTOMER REVIEW FEED ─────────────────────────────────────────────────
    render_review_feed(df)



def render():
    # Directly execute the complete, unmodified historical reviews view
    _render_historical()


if __name__ == '__main__':
    render()
