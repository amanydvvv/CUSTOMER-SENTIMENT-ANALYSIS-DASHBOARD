"""
1_overview.py
─────────────
Main Customer Feedback Intelligence page.
Structured around customer intelligence decision-support:
REVIEWS → SENTIMENT → ASPECT → PROBLEM → PRIORITY → ACTION

Tabs:
 1. 📊 Historical Customer Reviews — Amazon Reviews 2023 dataset, fully local
 2. 🔬 Unseen Review Analysis     — Held-out test split (Model Validation)
 3. 📝 Manual Review Analyzer     — Single review inference & batch testing
 4. 🌐 Live Google Reviews        — OPTIONAL / future feature (requires API key)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import importlib

from frontend.ui_utils import render_html
from frontend.data_loader import load_historical_dataset, filter_dataset
from frontend.components.sentiment_pulse import render_sentiment_pulse
from frontend.components.review_feed import render_review_feed
from frontend.components.pain_point_section import render_pain_point_section, analyze_negative_aspects
from frontend.components.mismatch_section import render_mismatch_section
from frontend.components.aspect_analyzer import extract_aspects_and_issues
from frontend.unseen_review_loader import load_unseen_reviews


def _star_icons(rating: float) -> str:
    try:
        r = int(round(float(rating)))
    except Exception:
        r = 5
    r = max(1, min(5, r))
    return "★" * r + "☆" * (5 - r)


def _render_historical():
    df_raw = load_historical_dataset()

    if df_raw.empty:
        st.error("Cannot load dataset. Ensure backend/data/processed/amazon_all_beauty_reviews.csv exists.")
        return

    # Compact sidebar filters
    with st.sidebar:
        render_html('<div class="nav-label">FILTER REVIEWS</div>')

        if st.button("🔄 Reset Filters", use_container_width=True):
            for k in ["filter_products", "filter_ratings", "filter_sentiments", "filter_verified", "filter_search"]:
                st.session_state.pop(k, None)
            st.rerun()

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

    # Extract top complaint aspect dynamically for the executive summary
    neg_df = df[df["sentiment"] == "negative"]
    aspect_summary, _, _ = analyze_negative_aspects(neg_df)
    top_aspect = aspect_summary[0]["aspect"] if aspect_summary else "General"
    top_aspect_share = aspect_summary[0]["share_pct"] if aspect_summary else 0.0
    top_aspect_issue = aspect_summary[0]["issue"] if aspect_summary else "General Feedback"

    # Dynamic interpretation generation based STRICTLY on filtered reviews (Objective & concise)
    exec_summary_text = (
        f"<b>{pos_pct:.1f}%</b> of filtered reviews are classified as positive and <b>{neg_pct:.1f}%</b> as negative. "
        f"<b>{top_aspect}</b> ({top_aspect_share:.1f}% of complaints) is currently the most frequently associated concern among negative reviews."
    )

    # ── 1. EXECUTIVE SUMMARY (4 COMPACT KPI CARDS) ──────────────────────────────
    summary_card_html = f"""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1rem 1.15rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.65rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                CUSTOMER FEEDBACK SUMMARY
            </div>
            <div style="font-size:0.7rem;color:#98A2B3;">
                Verified Buyers: <b style="color:#22D3EE;">{verified_pct:.1f}%</b>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(4, 1fr);gap:0.65rem;margin-bottom:0.75rem;">
            <div style="background:#151A24;border:1px solid #242A35;border-radius:8px;padding:0.85rem 0.95rem;">
                <div style="font-size:0.65rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;">REVIEWS</div>
                <div style="font-size:1.4rem;font-weight:800;color:#F5F7FA;margin:0.15rem 0;">{total:,}</div>
                <div style="font-size:0.68rem;color:#667085;">Filtered sample</div>
            </div>
            <div style="background:#151A24;border:1px solid rgba(34,197,94,0.25);border-radius:8px;padding:0.85rem 0.95rem;">
                <div style="font-size:0.65rem;font-weight:700;color:#22C55E;text-transform:uppercase;letter-spacing:0.05em;">POSITIVE</div>
                <div style="font-size:1.4rem;font-weight:800;color:#22C55E;margin:0.15rem 0;">{pos_pct:.1f}%</div>
                <div style="font-size:0.68rem;color:#667085;">{pos_count:,} reviews</div>
            </div>
            <div style="background:#151A24;border:1px solid rgba(239,68,68,0.25);border-radius:8px;padding:0.85rem 0.95rem;">
                <div style="font-size:0.65rem;font-weight:700;color:#EF4444;text-transform:uppercase;letter-spacing:0.05em;">NEGATIVE</div>
                <div style="font-size:1.4rem;font-weight:800;color:#EF4444;margin:0.15rem 0;">{neg_pct:.1f}%</div>
                <div style="font-size:0.68rem;color:#667085;">{neg_count:,} reviews</div>
            </div>
            <div style="background:#151A24;border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:0.85rem 0.95rem;">
                <div style="font-size:0.65rem;font-weight:700;color:#F59E0B;text-transform:uppercase;letter-spacing:0.05em;">AVG RATING</div>
                <div style="font-size:1.4rem;font-weight:800;color:#F59E0B;margin:0.15rem 0;">{avg_rating:.2f} ★</div>
                <div style="font-size:0.68rem;color:#F59E0B;">{_star_icons(avg_rating)}</div>
            </div>
        </div>

        <div style="background:#151A24;border-left:3px solid #7C5CFF;border-radius:0 6px 6px 0;padding:0.55rem 0.8rem;font-size:0.78rem;color:#D0D5DD;line-height:1.45;">
            {exec_summary_text}
        </div>
    </div>
    """
    render_html(summary_card_html)

    # ── 2. SENTIMENT PULSE | SENTIMENT COMPOSITION ─────────────────────────────
    render_sentiment_pulse(df, df_raw)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    # ── 3. TOP CUSTOMER CONCERNS & PAIN-POINT INTELLIGENCE ─────────────────────
    render_pain_point_section(df)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    # ── 4. RATING × SENTIMENT MISMATCH ─────────────────────────────────────────
    render_mismatch_section(df)

    st.markdown("<div style='height:0.75rem;'></div>", unsafe_allow_html=True)

    # ── 5. CUSTOMER REVIEW FEED ────────────────────────────────────────────────
    render_review_feed(df)


def _render_unseen():
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1.25rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.35rem;">
            <span style="background:rgba(124,92,255,0.15);color:#7C5CFF;border:1px solid rgba(124,92,255,0.3);padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:700;">
                HELD-OUT TEST SET
            </span>
            <span style="font-size:1.1rem;font-weight:700;color:#F5F7FA;">
                MODEL VALIDATION — HELD-OUT REVIEWS
            </span>
        </div>
        <div style="color:#98A2B3;font-size:0.82rem;line-height:1.45;">
            <b>16,336 unseen test reviews</b> (stratified 80/20 train-test partition, <code>random_state=42</code>).
            These reviews were <b>not used during model training</b>. Predictions displayed below are generated in real time by our saved ML model on genuinely unseen customer reviews.
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
    pos_u   = (df_unseen["sentiment"] == "positive").sum()
    neu_u   = (df_unseen["sentiment"] == "neutral").sum()
    neg_u   = (df_unseen["sentiment"] == "negative").sum()
    mism_u  = int(df_unseen["is_mismatch"].sum())
    accuracy_eval = (df_unseen["sentiment"] == df_unseen["label_sentiment"]).sum() / total_u * 100

    metrics_card = f"""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.9rem 1.25rem;margin-bottom:1rem;">
        <div style="display:flex;gap:2rem;flex-wrap:wrap;align-items:center;">
            <div>
                <div style="font-size:0.68rem;color:#98A2B3;font-weight:700;text-transform:uppercase;">EVALUATED</div>
                <div style="font-size:1.45rem;font-weight:800;color:#F5F7FA;">{total_u:,}</div>
                <div style="font-size:0.7rem;color:#667085;">Held-out reviews</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#22D3EE;font-weight:700;text-transform:uppercase;">AGREEMENT RATE</div>
                <div style="font-size:1.45rem;font-weight:800;color:#22D3EE;">{accuracy_eval:.1f}%</div>
                <div style="font-size:0.7rem;color:#667085;">vs Star Rule</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#22C55E;font-weight:700;text-transform:uppercase;">POSITIVE</div>
                <div style="font-size:1.45rem;font-weight:800;color:#22C55E;">{pos_u / total_u * 100:.1f}%</div>
                <div style="font-size:0.7rem;color:#667085;">{pos_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#F59E0B;font-weight:700;text-transform:uppercase;">NEUTRAL</div>
                <div style="font-size:1.45rem;font-weight:800;color:#F59E0B;">{neu_u / total_u * 100:.1f}%</div>
                <div style="font-size:0.7rem;color:#667085;">{neu_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#EF4444;font-weight:700;text-transform:uppercase;">NEGATIVE</div>
                <div style="font-size:1.45rem;font-weight:800;color:#EF4444;">{neg_u / total_u * 100:.1f}%</div>
                <div style="font-size:0.7rem;color:#667085;">{neg_u:,} reviews</div>
            </div>
            <div>
                <div style="font-size:0.68rem;color:#7C5CFF;font-weight:700;text-transform:uppercase;">MISMATCHES</div>
                <div style="font-size:1.45rem;font-weight:800;color:#7C5CFF;">{mism_u:,}</div>
                <div style="font-size:0.7rem;color:#667085;">Rating vs NLP</div>
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

    render_html(f"<div style='font-size:0.75rem;color:#98A2B3;margin-bottom:0.75rem;'>Displaying {min(40, len(df_show))} of {len(df_show):,} evaluated reviews</div>")

    for _, row in df_show.head(40).iterrows():
        intel = extract_aspects_and_issues(
            str(row["text"]),
            sentiment=str(row["sentiment"]),
            rating=float(row.get("rating", 3.0))
        )

        sent = str(row["sentiment"]).upper()
        if sent == "POSITIVE":
            badge_bg, badge_col, badge_bdr = "rgba(34,197,94,0.12)", "#22C55E", "rgba(34,197,94,0.28)"
        elif sent == "NEGATIVE":
            badge_bg, badge_col, badge_bdr = "rgba(239,68,68,0.12)", "#EF4444", "rgba(239,68,68,0.28)"
        else:
            badge_bg, badge_col, badge_bdr = "rgba(245,158,11,0.12)", "#F59E0B", "rgba(245,158,11,0.28)"

        pcol = {"HIGH": "#EF4444", "MEDIUM": "#F59E0B", "LOW": "#22C55E"}.get(intel["priority"], "#98A2B3")

        conf = row.get("confidence")
        conf_str = f"{conf * 100:.1f}%" if conf is not None else "N/A (LinearSVC)"

        mismatch_badge = ""
        if row.get("is_mismatch"):
            mismatch_badge = (
                f'<span style="background:rgba(239,68,68,0.15);color:#EF4444;border:1px solid rgba(239,68,68,0.35);'
                f'padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:700;">'
                f'⚠️ Mismatch ({row["rating"]:.0f}★ vs {sent})</span>'
            )

        title_html = f'<div style="font-weight:700;font-size:0.92rem;color:#F5F7FA;margin-bottom:0.25rem;">{row["title"]}</div>' if str(row.get("title", "")).strip() else ""

        u_card = f"""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.75rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
                    <span style="color:#F59E0B;font-size:0.95rem;">{_star_icons(row['rating'])}</span>
                    <span style="background:{badge_bg};color:{badge_col};border:1px solid {badge_bdr};padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:700;">
                        AI Prediction: {sent}
                    </span>
                    <span style="background:#151A24;color:#98A2B3;border:1px solid #242A35;padding:2px 6px;border-radius:4px;font-size:0.7rem;">
                        Confidence: {conf_str}
                    </span>
                    {mismatch_badge}
                </div>
                <span style="font-size:0.75rem;color:#667085;">{str(row.get('date',''))[:10]}</span>
            </div>

            {title_html}
            <div style="color:#D0D5DD;font-size:0.88rem;line-height:1.5;margin-bottom:0.6rem;">
                "{str(row['text'])[:350]}{'…' if len(str(row['text'])) > 350 else ''}"
            </div>

            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;border-top:1px solid #1E2533;padding-top:0.6rem;font-size:0.75rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;">
                    <span style="background:#151A24;border:1px solid #242A35;color:#98A2B3;padding:2px 6px;border-radius:4px;">
                        🏷️ <b>Aspect:</b> {intel['primary_aspect']}
                    </span>
                    <span style="background:#151A24;border:1px solid #242A35;color:#98A2B3;padding:2px 6px;border-radius:4px;">
                        🔍 <b>Issue:</b> {intel['issue']}
                    </span>
                    <span style="background:#151A24;border:1px solid #242A35;color:{pcol};font-weight:700;padding:2px 6px;border-radius:4px;">
                        Priority: {intel['priority']}
                    </span>
                </div>
                <span style="color:#667085;">ASIN: <code style="color:#22D3EE;font-size:0.7rem;">{row.get('product','N/A')}</code></span>
            </div>
            <div style="background:#151A24;border-left:3px solid #7C5CFF;padding:0.4rem 0.65rem;margin-top:0.6rem;border-radius:0 4px 4px 0;font-size:0.76rem;color:#98A2B3;">
                <b style="color:#F5F7FA;">Actionable Recommendation:</b> {intel['suggested_action']}
            </div>
        </div>
        """
        render_html(u_card)


def _render_manual():
    live_pred = importlib.import_module("frontend.pages.2_live_prediction")
    live_pred.render()


def _render_google_dormant():
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:2rem;text-align:center;margin-top:1rem;">
        <div style="font-size:2rem;margin-bottom:0.6rem;">🌐</div>
        <div style="font-size:1.15rem;font-weight:700;color:#F5F7FA;margin-bottom:0.35rem;">
            Live External Review Integration
        </div>
        <div style="color:#98A2B3;font-size:0.85rem;max-width:520px;margin:0 auto 1.25rem;line-height:1.5;">
            Connects to the <b>Google Places API (New)</b> to fetch and analyze real business reviews in real time.
        </div>
        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:1rem;max-width:440px;margin:0 auto;text-align:left;font-size:0.8rem;color:#D0D5DD;line-height:1.7;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;margin-bottom:0.35rem;text-transform:uppercase;">
                CONFIGURATION REQUIRED:
            </div>
            1. Create a Google Cloud API Key<br>
            2. Enable <b>Places API (New)</b><br>
            3. Set in <code>.streamlit/secrets.toml</code>:<br>
            &nbsp;&nbsp;<code style="color:#22D3EE;">GOOGLE_PLACES_API_KEY = "AIza..."</code><br>
            4. Restart the dashboard
        </div>
        <div style="color:#667085;font-size:0.75rem;margin-top:1rem;">
            The primary dashboard runs 100% locally on genuine Amazon feedback without requiring external APIs.
        </div>
    </div>
    """)


def render():
    header_html = """
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;border-bottom:1px solid #1E2533;padding-bottom:0.75rem;">
        <div>
            <h1 style="font-size:1.6rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
                CUSTOMER FEEDBACK INTELLIGENCE
            </h1>
            <div style="color:#98A2B3;font-size:0.82rem;margin:0;">
                AI-powered review analytics
            </div>
        </div>
        <div style="display:flex;gap:0.45rem;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);color:#22C55E;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;display:flex;align-items:center;gap:4px;">
                <span style="width:5px;height:5px;border-radius:50%;background:#22C55E;"></span>
                LOCAL ANALYTICS
            </span>
            <span style="background:#11151D;border:1px solid #242A35;color:#22D3EE;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                81.7K REVIEWS
            </span>
            <span style="background:#11151D;border:1px solid #242A35;color:#98A2B3;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                LOCAL INFERENCE
            </span>
        </div>
    </div>
    """
    render_html(header_html)

    tab_hist, tab_unseen, tab_manual, tab_google = st.tabs([
        "Historical Reviews",
        "Held-Out Validation",
        "New Review",
        "Google Reviews",
    ])

    with tab_hist:
        _render_historical()

    with tab_unseen:
        _render_unseen()

    with tab_manual:
        _render_manual()

    with tab_google:
        import os
        has_key = bool(os.environ.get("GOOGLE_PLACES_API_KEY", "").strip())
        if not has_key:
            try:
                has_key = bool(st.secrets.get("GOOGLE_PLACES_API_KEY", "").strip())
            except Exception:
                pass

        if has_key:
            from frontend.components.live_places_section import render_live_places_section
            render_live_places_section()
        else:
            _render_google_dormant()


if __name__ == "__main__":
    render()