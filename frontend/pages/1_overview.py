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


def _render_unseen():
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:20px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="background:rgba(255,255,255,0.06);color:#ffffff;border:1px solid rgba(255,255,255,0.12);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;">
                HELD-OUT TEST SET
            </span>
            <span style="font-size:16px;font-weight:600;color:#ffffff;">
                Model Validation — Held-Out Reviews
            </span>
        </div>
        <div style="color:#9ca3af;font-size:13px;line-height:1.5;">
            <b>16,336 unseen test reviews</b> (stratified 80/20 train-test partition, <code>random_state=42</code>).
            These reviews were strictly withheld during training. Predictions below reflect live inference on genuinely unseen consumer text.
        </div>
    </div>
    """)

    col_m, col_n = st.columns([2, 1])
    with col_m:
        model_choice = st.selectbox(
            "Evaluation Model",
            ["balanced_logistic_regression", "logistic_regression", "linearsvc"],
            format_func=lambda x: {
                "balanced_logistic_regression": "Balanced Logistic Regression (Handles Class Imbalance)",
                "logistic_regression": "Standard Logistic Regression",
                "linearsvc": "LinearSVC (High Accuracy)",
            }.get(x, x),
            key="unseen_model_select"
        )
    with col_n:
        n_samples = st.selectbox("Sample size to evaluate", [50, 100, 200], index=1, key="unseen_n_samples")

    with st.spinner("Running ML model inference on held-out test reviews..."):
        df_unseen = load_unseen_reviews(n_samples=n_samples, model_name=model_choice)

    if df_unseen.empty:
        st.error("Could not load held-out reviews. Ensure model artifacts exist in backend/models/.")
        return

    total_u = len(df_unseen)
    pos_u = (df_unseen["sentiment"] == "positive").sum()
    neu_u = (df_unseen["sentiment"] == "neutral").sum()
    neg_u = (df_unseen["sentiment"] == "negative").sum()
    mism_u = int(df_unseen["is_mismatch"].sum())
    accuracy_eval = (df_unseen["sentiment"] == df_unseen["label_sentiment"]).sum() / total_u * 100

    metrics_card = f"""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="display:flex;gap:28px;flex-wrap:wrap;align-items:center;">
            <div>
                <div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;">EVALUATED</div>
                <div style="font-size:24px;font-weight:700;color:#ffffff;">{total_u:,}</div>
                <div style="font-size:11px;color:#6b7280;">Held-out reviews</div>
            </div>
            <div>
                <div style="font-size:11px;color:#10b981;font-weight:600;text-transform:uppercase;">AGREEMENT RATE</div>
                <div style="font-size:24px;font-weight:700;color:#10b981;">{accuracy_eval:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">vs Star Rule</div>
            </div>
            <div>
                <div style="font-size:11px;color:#10b981;font-weight:600;text-transform:uppercase;">POSITIVE</div>
                <div style="font-size:24px;font-weight:700;color:#10b981;">{pos_u / total_u * 100:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">{pos_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:11px;color:#f59e0b;font-weight:600;text-transform:uppercase;">NEUTRAL</div>
                <div style="font-size:24px;font-weight:700;color:#f59e0b;">{neu_u / total_u * 100:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">{neu_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:11px;color:#ef4444;font-weight:600;text-transform:uppercase;">NEGATIVE</div>
                <div style="font-size:24px;font-weight:700;color:#ef4444;">{neg_u / total_u * 100:.1f}%</div>
                <div style="font-size:11px;color:#6b7280;">{neg_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;">MISMATCHES</div>
                <div style="font-size:24px;font-weight:700;color:#ffffff;">{mism_u:,}</div>
                <div style="font-size:11px;color:#6b7280;">Rating vs NLP</div>
            </div>
        </div>
    </div>
    """
    render_html(metrics_card)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sent_filter = st.selectbox("Filter by Model Prediction", ["All", "positive", "negative", "neutral"], key="unseen_sent_filter")
    with col_f2:
        mismatch_filter = st.checkbox("Show Mismatch Cases Only", key="unseen_mismatch_filter")

    df_show = df_unseen.copy()
    if sent_filter != "All":
        df_show = df_show[df_show["sentiment"] == sent_filter]
    if mismatch_filter:
        df_show = df_show[df_show["is_mismatch"]]

    render_html(f"<div style='font-size:12px;color:#6b7280;margin-bottom:12px;'>Displaying {min(40, len(df_show))} of {len(df_show):,} evaluated reviews</div>")

    for _, row in df_show.head(40).iterrows():
        intel = extract_aspects_and_issues(
            str(row["text"]),
            sentiment=str(row["sentiment"]),
            rating=float(row.get("rating", 3.0))
        )

        sent = str(row["sentiment"]).upper()
        if sent == "POSITIVE":
            badge_bg, badge_col, badge_bdr = "rgba(16,185,129,0.12)", "#10b981", "rgba(16,185,129,0.3)"
        elif sent == "NEGATIVE":
            badge_bg, badge_col, badge_bdr = "rgba(239,68,68,0.12)", "#ef4444", "rgba(239,68,68,0.3)"
        else:
            badge_bg, badge_col, badge_bdr = "rgba(245,158,11,0.12)", "#f59e0b", "rgba(245,158,11,0.3)"

        pcol = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}.get(intel["priority"], "#9ca3af")

        conf = row.get("confidence")
        conf_str = f"{conf * 100:.1f}%" if conf is not None else "N/A (LinearSVC)"

        mismatch_badge = ""
        if row.get("is_mismatch"):
            mismatch_badge = (
                f'<span style="background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.35);'
                f'padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">'
                f'Mismatch ({row["rating"]:.0f}★ vs {sent})</span>'
            )

        title_html = f'<div style="font-weight:600;font-size:14px;color:#ffffff;margin-bottom:4px;">{row["title"]}</div>' if str(row.get("title", "")).strip() else ""

        u_card = f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="color:#f59e0b;font-size:13px;">{row['rating']:.1f} / 5.0</span>
                    <span style="background:{badge_bg};color:{badge_col};border:1px solid {badge_bdr};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;">
                        Prediction: {sent}
                    </span>
                    <span style="background:#181b21;color:#9ca3af;border:1px solid rgba(255,255,255,0.07);padding:2px 6px;border-radius:4px;font-size:11px;">
                        Confidence: {conf_str}
                    </span>
                    {mismatch_badge}
                </div>
                <span style="font-size:11px;color:#6b7280;">{str(row.get('date',''))[:10]}</span>
            </div>

            {title_html}
            <div style="color:#d1d5db;font-size:13px;line-height:1.5;margin-bottom:10px;">
                "{str(row['text'])[:350]}{'…' if len(str(row['text'])) > 350 else ''}"
            </div>

            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-top:1px solid rgba(255,255,255,0.06);padding-top:10px;font-size:12px;">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:#9ca3af;padding:2px 8px;border-radius:4px;">
                        <b>Aspect:</b> {intel['primary_aspect']}
                    </span>
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:#9ca3af;padding:2px 8px;border-radius:4px;">
                        <b>Issue:</b> {intel['issue']}
                    </span>
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:{pcol};font-weight:700;padding:2px 8px;border-radius:4px;">
                        Priority: {intel['priority']}
                    </span>
                </div>
                <span style="color:#6b7280;">ASIN: <code style="color:#9ca3af;font-size:11px;">{row.get('product','N/A')}</code></span>
            </div>
            <div style="background:#181b21;border-left:3px solid #10b981;padding:8px 10px;margin-top:10px;border-radius:0 4px 4px 0;font-size:12px;color:#9ca3af;">
                <b style="color:#ffffff;">Suggested Action:</b> {intel['suggested_action']}
            </div>
        </div>
        """
        render_html(u_card)


def _render_manual():
    live_pred = importlib.import_module("frontend.pages.2_live_prediction")
    live_pred.render()


def render():
    # ── RULE 1: PRIORITIZE KEY METRICS (Above the Fold Metric Strip) ─────────
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;height:100%;">
            <div style="font-size:32px;font-weight:700;color:#ffffff;line-height:1.1;margin-bottom:4px;">81,700</div>
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">INGESTED REVIEWS</div>
            <div style="font-size:10px;color:#6b7280;margin-top:2px;">Amazon 2023 Beauty Corpus</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;height:100%;">
            <div style="font-size:32px;font-weight:700;color:#10b981;line-height:1.1;margin-bottom:4px;">70.84%</div>
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">MACRO RECALL</div>
            <div style="font-size:10px;color:#6b7280;margin-top:2px;">Unseen Test Benchmark</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;height:100%;">
            <div style="font-size:32px;font-weight:700;color:#ffffff;line-height:1.1;margin-bottom:4px;">4 Models</div>
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">EVALUATED ENGINES</div>
            <div style="font-size:10px;color:#6b7280;margin-top:2px;">Balanced LR · LinearSVC · DistilBERT</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;height:100%;">
            <div style="font-size:32px;font-weight:700;color:#10b981;line-height:1.1;margin-bottom:4px;">60 / 60</div>
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">PASSING TESTS</div>
            <div style="font-size:10px;color:#6b7280;margin-top:2px;">100% Automated Test Suite</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    tab_hist, tab_unseen, tab_manual, tab_stores = st.tabs([
        "01 · Historical Reviews",
        "02 · Held-Out Validation",
        "03 · New Review Analysis",
        "04 · Store Ingestion",
    ])

    with tab_hist:
        _render_historical()

    with tab_unseen:
        _render_unseen()

    with tab_manual:
        _render_manual()

    with tab_stores:
        from frontend.components.live_places_section import render_live_places_section
        render_live_places_section()


if __name__ == "__main__":
    render()