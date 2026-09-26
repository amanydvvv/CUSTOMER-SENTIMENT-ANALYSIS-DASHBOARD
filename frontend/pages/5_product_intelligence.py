"""
5_product_intelligence.py
─────────────────────────
Product-Based Customer Feedback Intelligence Module.
Provides granular, actionable product-level analytics following the decision flow:
SELECT PRODUCT → HOW CUSTOMERS FEEL → WHAT THEY ARE COMPLAINING ABOUT → HOW BIG THE PROBLEM IS → WHAT REVIEWS SUPPORT IT → WHAT SHOULD BE INVESTIGATED

Story & Structure:
1. Header & Context: Product Feedback Intelligence
2. SELECT PRODUCT: Searchable ASIN selector + Info row (ASIN, Review Volume, Date Coverage)
3. PRODUCT OVERVIEW: 5 Compact KPI cards + Factual Dynamic Summary
4. CUSTOMER SENTIMENT & CONCERNS: Side-by-side Donut Chart + Top Concerns Horizontal Bar Chart
5. PRODUCT PAIN-POINT INTELLIGENCE: Aspect Table + Priority Rule + Why This Matters
6. SUPPORTING CUSTOMER EVIDENCE: Evidence Inspector with aspect filter & real customer reviews
7. DIAGNOSTICS & TRENDS: Rating x Sentiment Mismatch + Product Feedback Over Time
8. COMPARE PRODUCTS: Objective Cross-Product Sentiment & Concerns Heatmap
9. PRODUCT REVIEW FEED: Filterable product review feed with responsive wrapped cards
"""

import html
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from frontend.ui_utils import render_html
from frontend.data_loader import load_historical_dataset
from frontend.components.aspect_analyzer import extract_aspects_and_issues, ASPECT_KEYWORDS


def _star_icons(rating: float) -> str:
    try:
        r = int(round(float(rating)))
    except Exception:
        r = 5
    r = max(1, min(5, r))
    return "★" * r + "☆" * (5 - r)


@st.cache_data(show_spinner=False)
def _get_product_catalog(df_raw: pd.DataFrame):
    """
    Extracts product counts and prepares formatted selector list.
    Sorted by review volume descending.
    """
    if df_raw.empty or "product" not in df_raw.columns:
        return [], {}

    counts = df_raw["product"].value_counts()
    product_options = [f"{asin} ({count:,} reviews)" for asin, count in counts.items()]
    asin_lookup = {f"{asin} ({count:,} reviews)": asin for asin, count in counts.items()}
    return product_options, asin_lookup


def _analyze_product_aspects(neg_reviews: pd.DataFrame):
    """
    Computes aspect breakdown, specific detected issues, priorities, and actions for negative reviews of a single product.
    """
    total_neg = len(neg_reviews)
    if total_neg == 0:
        return [], {}, 0

    aspect_counts = {}
    aspect_issues = {}
    aspect_actions = {}
    high_priority_count = 0
    aspect_sample_reviews = {}

    for _, row in neg_reviews.iterrows():
        text = str(row.get("text", ""))
        rating = float(row.get("rating", 1.0))
        intel = extract_aspects_and_issues(text, sentiment="negative", rating=rating)
        p_aspect = intel["primary_aspect"]
        issue = intel["issue"]
        priority = intel["priority"]
        action = intel["suggested_action"]

        aspect_counts[p_aspect] = aspect_counts.get(p_aspect, 0) + 1

        if p_aspect not in aspect_issues:
            aspect_issues[p_aspect] = {}
        if issue != "General Feedback":
            aspect_issues[p_aspect][issue] = aspect_issues[p_aspect].get(issue, 0) + 1

        if p_aspect not in aspect_actions:
            aspect_actions[p_aspect] = action

        if priority == "HIGH":
            high_priority_count += 1

        if p_aspect not in aspect_sample_reviews:
            aspect_sample_reviews[p_aspect] = []
        if len(aspect_sample_reviews[p_aspect]) < 6:
            aspect_sample_reviews[p_aspect].append(row)

    aspect_summary = []
    for aspect, count in sorted(aspect_counts.items(), key=lambda x: x[1], reverse=True):
        share_pct = (count / total_neg) * 100

        top_issue = "General Complaints"
        if aspect in aspect_issues and aspect_issues[aspect]:
            top_issue = max(aspect_issues[aspect].items(), key=lambda x: x[1])[0]

        # Transparent data-driven priority assignment matching rule:
        # HIGH: >= 25% share of negative reviews OR critical issue term with >= 3 complaints
        # MEDIUM: >= 12% share OR >= 2 complaints
        # LOW: < 12% share
        has_critical_issue = any(term in top_issue.lower() for term in ["reaction", "rash", "burn", "delay", "broken", "leaked", "damage"])
        if share_pct >= 25.0 or (has_critical_issue and count >= 3):
            pri = "HIGH"
        elif share_pct >= 12.0 or count >= 2:
            pri = "MEDIUM"
        else:
            pri = "LOW"

        aspect_summary.append({
            "aspect": aspect,
            "count": count,
            "share_pct": share_pct,
            "issue": top_issue,
            "priority": pri,
            "action": aspect_actions.get(aspect, "Review customer feedback and inspect quality standards.")
        })

    return aspect_summary, aspect_sample_reviews, high_priority_count


def _generate_dynamic_summary(pos_pct: float, neu_pct: float, neg_pct: float, total: int, neg_count: int, aspect_summary: list) -> str:
    """
    Generates a factual, data-driven narrative interpretation based strictly on calculated product metrics.
    Avoids dramatic buzzwords and presents clean objective interpretation.
    """
    if total == 0:
        return "No review records available for the selected product."

    if neg_count == 0:
        return f"Customer sentiment is exclusively favorable across <b>{total:,}</b> reviews (<b>{pos_pct:.1f}%</b> positive, <b>{neu_pct:.1f}%</b> neutral) with zero negative complaints recorded in the dataset."

    top_aspect = aspect_summary[0]["aspect"] if aspect_summary else "Product Quality"
    top_aspect_share = aspect_summary[0]["share_pct"] if aspect_summary else 0.0
    top_issue = aspect_summary[0]["issue"] if aspect_summary else "General Feedback"

    if len(aspect_summary) > 1 and aspect_summary[1]["share_pct"] >= 15.0:
        second_aspect = aspect_summary[1]["aspect"]
        second_aspect_share = aspect_summary[1]["share_pct"]
        aspect_phrase = f"<b>{top_aspect}</b> ({top_aspect_share:.1f}%) and <b>{second_aspect}</b> ({second_aspect_share:.1f}%)"
    else:
        aspect_phrase = f"<b>{top_aspect}</b>, accounting for <b>{top_aspect_share:.1f}%</b> of negative reviews (primarily <i>{top_issue}</i>)"

    if pos_pct >= 70.0:
        return (
            f"Customer sentiment is predominantly positive (<b>{pos_pct:.1f}%</b>). Negative feedback "
            f"(<b>{neg_pct:.1f}%</b>, {neg_count:,} reviews) is most concentrated around {aspect_phrase}."
        )
    elif neg_pct >= 30.0:
        return (
            f"Negative feedback represents a substantial share (<b>{neg_pct:.1f}%</b>, {neg_count:,} reviews) for this product. "
            f"Friction is primarily concentrated in {aspect_phrase}."
        )
    else:
        return (
            f"Customer feedback reflects a balanced distribution across <b>{total:,}</b> reviews (<b>{pos_pct:.1f}%</b> positive, "
            f"<b>{neu_pct:.1f}%</b> neutral, <b>{neg_pct:.1f}%</b> negative). "
            f"Negative feedback is most concentrated in {aspect_phrase}."
        )


def render():
    """Renders the presentation-ready Product Intelligence page."""
    df_raw = load_historical_dataset()

    if df_raw.empty:
        st.error("Cannot load dataset. Please ensure backend/data/processed/amazon_all_beauty_reviews.csv exists.")
        return

    # Top Product Catalog preparation
    product_options, asin_lookup = _get_product_catalog(df_raw)

    if not product_options:
        st.warning("No products found in the active dataset.")
        return

    # Page Header (Compact & Professional)
    render_html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;border-bottom:1px solid #1E2533;padding-bottom:0.75rem;">
        <div>
            <h1 style="font-size:1.55rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
                PRODUCT FEEDBACK INTELLIGENCE
            </h1>
            <div style="color:#98A2B3;font-size:0.82rem;margin:0;">
                AI-powered product-level customer feedback analysis
            </div>
        </div>
        <div style="display:flex;gap:0.45rem;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(124,92,255,0.1);border:1px solid rgba(124,92,255,0.25);color:#7C5CFF;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                ASIN ANALYTICS
            </span>
            <span style="background:#11151D;border:1px solid #242A35;color:#22C55E;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;display:flex;align-items:center;gap:4px;">
                <span style="display:inline-block;width:5px;height:5px;border-radius:50%;background:#22C55E;"></span>
                LOCAL INFERENCE
            </span>
        </div>
    </div>
    """)

    # ── 1. SELECT PRODUCT ───────────────────────────────────────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.35rem;">
        SELECT PRODUCT
    </div>
    """)

    selected_option = st.selectbox(
        "Search or select product ASIN",
        options=product_options,
        index=0,
        help="Select any product ASIN from the Amazon 2023 dataset. Ranked by review volume.",
        label_visibility="collapsed"
    )

    selected_asin = asin_lookup.get(selected_option, product_options[0].split()[0])

    # Filter strictly for the selected product
    product_df = df_raw[df_raw["product"] == selected_asin].copy()
    total_reviews = len(product_df)

    if total_reviews == 0:
        st.warning(f"No reviews found for product {selected_asin}.")
        return

    # Calculate real product metrics
    pos_count = int((product_df["sentiment"] == "positive").sum())
    neg_count = int((product_df["sentiment"] == "negative").sum())
    neu_count = int((product_df["sentiment"] == "neutral").sum())

    pos_pct = (pos_count / total_reviews) * 100
    neg_pct = (neg_count / total_reviews) * 100
    neu_pct = (neu_count / total_reviews) * 100
    avg_rating = float(product_df["rating"].mean())
    verified_pct = (product_df["verified_purchase"].sum() / total_reviews) * 100 if "verified_purchase" in product_df.columns else 0.0

    # Determine date coverage
    date_coverage_str = "All Available"
    if "date_dt" in product_df.columns and product_df["date_dt"].notna().sum() > 0:
        valid_dates = product_df["date_dt"].dropna()
        min_d = valid_dates.min()
        max_d = valid_dates.max()
        if pd.notna(min_d) and pd.notna(max_d):
            date_coverage_str = f"{min_d.strftime('%b %Y')} – {max_d.strftime('%b %Y')}"

    # Compact product metadata row
    render_html(f"""
    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:0.65rem;background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.65rem 0.95rem;margin:0.4rem 0 1rem 0;">
        <div>
            <div style="font-size:0.62rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;">ASIN</div>
            <div style="font-size:0.92rem;font-weight:800;color:#7C5CFF;font-family:'JetBrains Mono',monospace;">{selected_asin}</div>
        </div>
        <div>
            <div style="font-size:0.62rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;">REVIEW VOLUME</div>
            <div style="font-size:0.92rem;font-weight:800;color:#22D3EE;">{total_reviews:,} reviews</div>
        </div>
        <div>
            <div style="font-size:0.62rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;">DATE COVERAGE</div>
            <div style="font-size:0.85rem;font-weight:600;color:#F5F7FA;">{date_coverage_str}</div>
        </div>
    </div>
    """)

    neg_df = product_df[product_df["sentiment"] == "negative"]
    aspect_summary, aspect_samples, high_pri_cnt = _analyze_product_aspects(neg_df)

    summary_narrative = _generate_dynamic_summary(pos_pct, neu_pct, neg_pct, total_reviews, neg_count, aspect_summary)

    # ── 2. PRODUCT OVERVIEW & KPI CARDS (5 EQUAL-HEIGHT CARDS) ──────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.45rem;">
        PRODUCT OVERVIEW
    </div>
    """)

    render_html(f"""
    <div style="display:grid;grid-template-columns:repeat(5, 1fr);gap:0.6rem;margin-bottom:0.75rem;">
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.75rem 0.85rem;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.62rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;">REVIEWS</div>
            <div style="font-size:1.35rem;font-weight:800;color:#F5F7FA;margin:0.15rem 0;">{total_reviews:,}</div>
            <div style="font-size:0.65rem;color:#667085;">100% sample</div>
        </div>
        <div style="background:#11151D;border:1px solid rgba(245,158,11,0.25);border-radius:8px;padding:0.75rem 0.85rem;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.62rem;font-weight:700;color:#F59E0B;text-transform:uppercase;letter-spacing:0.05em;">AVG RATING</div>
            <div style="font-size:1.35rem;font-weight:800;color:#F59E0B;margin:0.15rem 0;">{avg_rating:.2f} ★</div>
            <div style="font-size:0.65rem;color:#F59E0B;">{_star_icons(avg_rating)}</div>
        </div>
        <div style="background:#11151D;border:1px solid rgba(34,197,94,0.25);border-radius:8px;padding:0.75rem 0.85rem;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.62rem;font-weight:700;color:#22C55E;text-transform:uppercase;letter-spacing:0.05em;">POSITIVE</div>
            <div style="font-size:1.35rem;font-weight:800;color:#22C55E;margin:0.15rem 0;">{pos_pct:.1f}%</div>
            <div style="font-size:0.65rem;color:#667085;">{pos_count:,} reviews</div>
        </div>
        <div style="background:#11151D;border:1px solid rgba(239,68,68,0.25);border-radius:8px;padding:0.75rem 0.85rem;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.62rem;font-weight:700;color:#EF4444;text-transform:uppercase;letter-spacing:0.05em;">NEGATIVE</div>
            <div style="font-size:1.35rem;font-weight:800;color:#EF4444;margin:0.15rem 0;">{neg_pct:.1f}%</div>
            <div style="font-size:0.65rem;color:#667085;">{neg_count:,} reviews</div>
        </div>
        <div style="background:#11151D;border:1px solid rgba(34,211,238,0.25);border-radius:8px;padding:0.75rem 0.85rem;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:0.62rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:0.05em;">VERIFIED</div>
            <div style="font-size:1.35rem;font-weight:800;color:#22D3EE;margin:0.15rem 0;">{verified_pct:.1f}%</div>
            <div style="font-size:0.65rem;color:#667085;">verified buyers</div>
        </div>
    </div>
    """)

    # ── 3. PRODUCT FEEDBACK SUMMARY ─────────────────────────────────────────────
    render_html(f"""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.85rem 1.1rem;margin-bottom:1.15rem;">
        <div style="font-size:0.65rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
            PRODUCT FEEDBACK SUMMARY
        </div>
        <div style="font-size:0.84rem;color:#F5F7FA;line-height:1.5;">
            {summary_narrative}
        </div>
    </div>
    """)

    # ── 4. CUSTOMER SENTIMENT & TOP CUSTOMER CONCERNS (SIDE-BY-SIDE) ────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.45rem;">
        CUSTOMER SENTIMENT & CONCERNS
    </div>
    """)

    col_sentiment, col_concerns = st.columns([1.1, 1.9])

    with col_sentiment:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.85rem 1rem 0.4rem 1rem;margin-bottom:0.4rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.15rem;">
                PRODUCT SENTIMENT
            </div>
            <div style="font-size:0.7rem;color:#98A2B3;">
                Distribution across sentiment classes
            </div>
        </div>
        """)

        # Donut Chart
        sent_labels = ["Positive", "Neutral", "Negative"]
        sent_values = [pos_count, neu_count, neg_count]
        sent_colors = ["#22C55E", "#F59E0B", "#EF4444"]

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=sent_labels,
                    values=sent_values,
                    hole=0.62,
                    marker=dict(colors=sent_colors, line=dict(color="#11151D", width=2)),
                    textinfo="percent",
                    textfont=dict(color="#F5F7FA", size=11, family="Inter"),
                    hoverinfo="label+value+percent",
                )
            ]
        )
        fig_donut.update_layout(
            showlegend=False,
            height=190,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b>{total_reviews:,}</b><br><span style='font-size:9px;color:#98A2B3;'>REVIEWS</span>",
                    x=0.5,
                    y=0.5,
                    font=dict(size=13, color="#F5F7FA", family="Inter"),
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

        # Side-by-side Sentiment Breakdown Box
        render_html(f"""
        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.55rem 0.8rem;margin-bottom:0.85rem;">
            <div style="font-size:0.65rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.35rem;border-bottom:1px solid #1E2533;padding-bottom:0.25rem;">
                SENTIMENT BREAKDOWN
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.2rem 0;border-bottom:1px solid #1E2533;font-size:0.76rem;">
                <span style="color:#22C55E;font-weight:600;display:flex;align-items:center;gap:5px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#22C55E;display:inline-block;"></span>
                    Positive
                </span>
                <span style="color:#22C55E;font-weight:700;">{pos_pct:.1f}%</span>
                <span style="color:#98A2B3;font-family:'JetBrains Mono',monospace;">{pos_count:,} reviews</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.2rem 0;border-bottom:1px solid #1E2533;font-size:0.76rem;">
                <span style="color:#F59E0B;font-weight:600;display:flex;align-items:center;gap:5px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#F59E0B;display:inline-block;"></span>
                    Neutral
                </span>
                <span style="color:#F59E0B;font-weight:700;">{neu_pct:.1f}%</span>
                <span style="color:#98A2B3;font-family:'JetBrains Mono',monospace;">{neu_count:,} reviews</span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.2rem 0;font-size:0.76rem;">
                <span style="color:#EF4444;font-weight:600;display:flex;align-items:center;gap:5px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#EF4444;display:inline-block;"></span>
                    Negative
                </span>
                <span style="color:#EF4444;font-weight:700;">{neg_pct:.1f}%</span>
                <span style="color:#98A2B3;font-family:'JetBrains Mono',monospace;">{neg_count:,} reviews</span>
            </div>
        </div>
        """)

    with col_concerns:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.85rem 1rem 0.4rem 1rem;margin-bottom:0.4rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.15rem;">
                <span style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                    TOP CUSTOMER CONCERNS
                </span>
                <span style="font-size:0.68rem;color:#98A2B3;">
                    Negative feedback breakdown
                </span>
            </div>
            <div style="font-size:0.7rem;color:#98A2B3;">
                Where negative feedback is concentrated across product dimensions
            </div>
        </div>
        """)

        if aspect_summary:
            df_chart = pd.DataFrame(aspect_summary)
            fig_bar = px.bar(
                df_chart,
                x="share_pct",
                y="aspect",
                orientation="h",
                text=df_chart.apply(lambda r: f"{r['count']:,} ({r['share_pct']:.1f}%)", axis=1),
                color="share_pct",
                color_continuous_scale=[[0, "#3B82F6"], [0.5, "#F59E0B"], [1, "#EF4444"]],
            )
            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(color="#F5F7FA", size=10, family="Inter"),
                marker=dict(line=dict(width=0))
            )
            fig_bar.update_layout(
                height=max(200, len(aspect_summary) * 32),
                margin=dict(l=10, r=70, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed", tickfont=dict(color="#F5F7FA", size=10), title=""),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="#1E2533",
                    tickfont=dict(color="#98A2B3", size=9),
                    range=[0, max(df_chart['share_pct'].max() * 1.35, 15)],
                    title="% of Negative Feedback"
                )
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
        else:
            render_html("""
            <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:1.5rem;text-align:center;color:#22C55E;font-size:0.82rem;margin-top:0.75rem;">
                ✓ Zero negative customer concerns recorded for this product.
            </div>
            """)

    # ── 5. PRODUCT PAIN-POINT INTELLIGENCE ──────────────────────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-top:1.25rem;margin-bottom:0.45rem;">
        CUSTOMER CONCERNS & PAIN POINTS
    </div>
    """)

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.6rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                PRODUCT PAIN-POINT INTELLIGENCE
            </span>
            <span style="font-size:0.7rem;color:#98A2B3;">
                Measurable priority & suggested actions
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;">
            Aspect-level root cause mapping and concrete operational remediation recommendations.
        </div>
    </div>
    """)

    with st.expander("ℹ️ How Priority is Calculated (Transparent Rule)", expanded=False):
        render_html("""
        <div style="font-size:0.8rem;color:#98A2B3;line-height:1.6;">
            <div style="margin-bottom:0.4rem;"><b style="color:#EF4444;">HIGH:</b> High concentration of negative feedback (≥ 25% share) or defined critical issue pattern (e.g., adverse reaction, rash, burn, broken seal, shipping delay) with ≥ 3 complaints.</div>
            <div style="margin-bottom:0.4rem;"><b style="color:#F59E0B;">MEDIUM:</b> Meaningful recurring negative feedback (≥ 12% share or ≥ 2 complaints).</div>
            <div><b style="color:#3B82F6;">LOW:</b> Lower-volume concern (< 12% share).</div>
        </div>
        """)

    if aspect_summary:
        # Table Header
        render_html("""
        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px 6px 0 0;padding:0.55rem 0.85rem;display:grid;grid-template-columns:1.8fr 1.1fr 1fr 1fr 2.5fr 3.6fr;gap:0.5rem;font-size:0.68rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.05em;margin-top:0.4rem;">
            <div>ASPECT</div>
            <div>NEG REVIEWS</div>
            <div>SHARE</div>
            <div>PRIORITY</div>
            <div>CUSTOMER ISSUE</div>
            <div>SUGGESTED ACTION</div>
        </div>
        """)

        # Table Rows
        for item in aspect_summary:
            pri = item["priority"]
            if pri == "HIGH":
                pri_color = "#EF4444"
                pri_bg = "rgba(239,68,68,0.15)"
            elif pri == "MEDIUM":
                pri_color = "#F59E0B"
                pri_bg = "rgba(245,158,11,0.15)"
            else:
                pri_color = "#3B82F6"
                pri_bg = "rgba(59,130,246,0.15)"

            render_html(f"""
            <div style="background:#11151D;border:1px solid #242A35;border-top:none;padding:0.7rem 0.85rem;display:grid;grid-template-columns:1.8fr 1.1fr 1fr 1fr 2.5fr 3.6fr;gap:0.5rem;align-items:center;font-size:0.8rem;">
                <div style="font-weight:700;color:#F5F7FA;">{item['aspect']}</div>
                <div style="color:#F5F7FA;font-family:'JetBrains Mono',monospace;">{item['count']:,}</div>
                <div style="color:#98A2B3;font-family:'JetBrains Mono',monospace;">{item['share_pct']:.1f}%</div>
                <div>
                    <span style="background:{pri_bg};color:{pri_color};border:1px solid {pri_color};border-radius:4px;padding:2px 7px;font-size:0.68rem;font-weight:800;">
                        {pri}
                    </span>
                </div>
                <div style="color:#F5F7FA;font-size:0.78rem;">{item['issue']}</div>
                <div style="color:#98A2B3;font-size:0.78rem;line-height:1.4;">{item['action']}</div>
            </div>
            """)

        # Why this matters box
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-left:3px solid #7C5CFF;border-radius:0 6px 6px 0;padding:0.65rem 0.95rem;margin-top:0.65rem;">
            <div style="font-size:0.65rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.15rem;">WHY THIS MATTERS</div>
            <div style="font-size:0.78rem;color:#98A2B3;line-height:1.45;">
                Product-level analysis helps separate overall customer sentiment from issues specific to an individual product.
            </div>
        </div>
        """)
    else:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:6px;padding:1.25rem;color:#22C55E;font-size:0.85rem;">
            ✓ No pain points extracted for this product.
        </div>
        """)

    # ── 6. SUPPORTING CUSTOMER EVIDENCE ─────────────────────────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-top:1.5rem;margin-bottom:0.45rem;">
        EVIDENCE
    </div>
    """)

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.6rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                SUPPORTING CUSTOMER EVIDENCE
            </span>
            <span style="font-size:0.7rem;color:#98A2B3;">
                Insight → Actual Customer Evidence
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;">
            Inspect genuine customer reviews behind the identified concern dimensions.
        </div>
    </div>
    """)

    if aspect_summary:
        available_aspects = [item["aspect"] for item in aspect_summary]
        selected_evidence_aspect = st.selectbox(
            "Select Concern Dimension to View Evidence",
            options=available_aspects,
            index=0,
            key="evidence_aspect_sel"
        )

        sample_evidence = aspect_samples.get(selected_evidence_aspect, [])
        if sample_evidence:
            for s_row in sample_evidence:
                r_rating = float(s_row.get("rating", 1.0))
                r_text = str(s_row.get("text", "")).strip()
                r_title = str(s_row.get("title", "")).strip()
                r_date = str(s_row.get("date", "N/A"))
                r_verified = bool(s_row.get("verified_purchase", False))
                r_helpful = int(s_row.get("helpful_votes", 0))

                intel = extract_aspects_and_issues(r_text, sentiment="negative", rating=r_rating)

                verified_badge = (
                    '<span style="background:rgba(34,211,238,0.12);color:#22D3EE;border:1px solid #22D3EE;border-radius:3px;padding:1px 6px;font-size:0.65rem;font-weight:700;">VERIFIED PURCHASE</span>'
                    if r_verified else ''
                )

                safe_title = html.escape(r_title)
                safe_text = html.escape(r_text)

                render_html(f"""
                <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
                        <div style="display:flex;align-items:center;gap:0.55rem;">
                            <span style="color:#F59E0B;font-size:0.95rem;letter-spacing:1px;">{_star_icons(r_rating)}</span>
                            <span style="color:#98A2B3;font-size:0.75rem;font-family:'JetBrains Mono',monospace;">{r_rating:.1f} ★</span>
                            <span style="background:rgba(239,68,68,0.15);color:#EF4444;border:1px solid #EF4444;border-radius:4px;padding:1px 6px;font-size:0.65rem;font-weight:800;">NEGATIVE</span>
                            {verified_badge}
                        </div>
                        <div style="font-size:0.72rem;color:#667085;font-family:'JetBrains Mono',monospace;">{r_date}</div>
                    </div>
                    {f'<div style="font-size:0.85rem;font-weight:700;color:#F5F7FA;margin-bottom:0.25rem;">{safe_title}</div>' if safe_title else ''}
                    <div style="font-size:0.82rem;color:#D1D5DB;line-height:1.5;margin-bottom:0.45rem;">
                        "{safe_text}"
                    </div>
                    <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;border-top:1px solid #1E2533;padding-top:0.4rem;color:#98A2B3;">
                        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;">
                            <span><b>Aspect:</b> <span style="color:#F5F7FA;">{selected_evidence_aspect}</span></span>
                            <span><b>Detected Issue:</b> <span style="color:#F5F7FA;">{intel['issue']}</span></span>
                            <span><b>Priority:</b> <span style="color:#EF4444;font-weight:700;">{intel['priority']}</span></span>
                        </div>
                        {f'<div>Helpful votes: {r_helpful}</div>' if r_helpful > 0 else ''}
                    </div>
                </div>
                """)
        else:
            st.info(f"No specific review samples for {selected_evidence_aspect}.")
    else:
        st.info("No negative concerns recorded for this product.")

    # ── 7. DIAGNOSTICS & TRENDS (MISMATCH & TIME TRAJECTORY) ────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-top:1.5rem;margin-bottom:0.45rem;">
        DIAGNOSTICS & TRENDS
    </div>
    """)

    col_diag_mismatch, col_diag_time = st.columns([1, 1])

    with col_diag_mismatch:
        # High Rating (4-5) + Negative Sentiment
        high_neg_df = product_df[(product_df["rating"] >= 4.0) & (product_df["sentiment"] == "negative")]
        # Low Rating (1-2) + Positive Sentiment
        low_pos_df = product_df[(product_df["rating"] <= 2.0) & (product_df["sentiment"] == "positive")]

        render_html(f"""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.55rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem;">
                RATING × SENTIMENT MISMATCH
            </div>
            <div style="font-size:0.75rem;color:#98A2B3;margin-bottom:0.65rem;">
                These reviews contain disagreement between the explicit star rating and the sentiment expressed in the review text.
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-bottom:0.4rem;">
                <div style="background:#151A24;border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:0.65rem 0.75rem;">
                    <div style="font-size:0.62rem;font-weight:700;color:#EF4444;text-transform:uppercase;">4–5★ + Negative Text</div>
                    <div style="font-size:1.15rem;font-weight:800;color:#F5F7FA;margin:2px 0;">{len(high_neg_df):,} reviews</div>
                </div>
                <div style="background:#151A24;border:1px solid rgba(34,197,94,0.3);border-radius:6px;padding:0.65rem 0.75rem;">
                    <div style="font-size:0.62rem;font-weight:700;color:#22C55E;text-transform:uppercase;">1–2★ + Positive Text</div>
                    <div style="font-size:1.15rem;font-weight:800;color:#F5F7FA;margin:2px 0;">{len(low_pos_df):,} reviews</div>
                </div>
            </div>
        </div>
        """)

        with st.expander("🔍 Inspect Mismatch Reviews", expanded=False):
            if len(high_neg_df) > 0 or len(low_pos_df) > 0:
                mismatch_type = st.radio(
                    "Mismatch Type",
                    options=["4–5★ Rating + Negative Text", "1–2★ Rating + Positive Text"],
                    horizontal=True,
                    key="p_mismatch_radio"
                )
                target_df = high_neg_df if "4–5★" in mismatch_type else low_pos_df

                if target_df.empty:
                    st.info("No reviews match this specific mismatch criteria.")
                else:
                    for _, r in target_df.head(4).iterrows():
                        safe_r_text = html.escape(str(r.get('text', '')))
                        render_html(f"""
                        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.65rem 0.85rem;margin-bottom:0.45rem;font-size:0.78rem;">
                            <div style="display:flex;justify-content:space-between;margin-bottom:0.25rem;">
                                <span style="color:#F59E0B;font-weight:600;">{_star_icons(r['rating'])} ({r['rating']:.1f}★)</span>
                                <span style="color:#98A2B3;font-family:'JetBrains Mono',monospace;">{r.get('date', 'N/A')}</span>
                            </div>
                            <div style="color:#F5F7FA;line-height:1.4;">"{safe_r_text}"</div>
                        </div>
                        """)
            else:
                st.info("No rating-sentiment mismatch cases detected for this product.")

    with col_diag_time:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.55rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.2rem;">
                PRODUCT FEEDBACK OVER TIME
            </div>
            <div style="font-size:0.75rem;color:#98A2B3;">
                Monthly review volume and sentiment trajectory
            </div>
        </div>
        """)

        # Check date column
        has_dates = "date_dt" in product_df.columns and product_df["date_dt"].notna().sum() >= 15
        if has_dates:
            p_dates = product_df.dropna(subset=["date_dt"]).copy()
            p_dates["month_year"] = p_dates["date_dt"].dt.to_period("M").dt.to_timestamp()
            unique_months = p_dates["month_year"].nunique()

            if unique_months >= 3:
                time_grp = p_dates.groupby(["month_year", "sentiment"]).size().unstack(fill_value=0).reset_index()
                for s in ["positive", "neutral", "negative"]:
                    if s not in time_grp.columns:
                        time_grp[s] = 0

                fig_time = go.Figure()
                fig_time.add_trace(go.Bar(x=time_grp["month_year"], y=time_grp["positive"], name="Positive", marker_color="#22C55E"))
                fig_time.add_trace(go.Bar(x=time_grp["month_year"], y=time_grp["neutral"], name="Neutral", marker_color="#F59E0B"))
                fig_time.add_trace(go.Bar(x=time_grp["month_year"], y=time_grp["negative"], name="Negative", marker_color="#EF4444"))

                fig_time.update_layout(
                    barmode="stack",
                    height=200,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#98A2B3", size=9)),
                    xaxis=dict(showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3", size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3", size=9), title="Volume")
                )
                st.plotly_chart(fig_time, use_container_width=True, config={"displayModeBar": False})
            else:
                render_html("""
                <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:1.5rem;text-align:center;">
                    <div style="font-size:0.75rem;font-weight:700;color:#98A2B3;text-transform:uppercase;margin-bottom:0.25rem;">INSUFFICIENT DATA</div>
                    <div style="font-size:0.78rem;color:#667085;">Not enough dated reviews to display a meaningful time trend.</div>
                </div>
                """)
        else:
            render_html("""
            <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:1.5rem;text-align:center;">
                <div style="font-size:0.75rem;font-weight:700;color:#98A2B3;text-transform:uppercase;margin-bottom:0.25rem;">INSUFFICIENT DATA</div>
                <div style="font-size:0.78rem;color:#667085;">Not enough dated reviews to display a meaningful time trend.</div>
            </div>
            """)

    # ── 8. COMPARE PRODUCTS ─────────────────────────────────────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-top:1.5rem;margin-bottom:0.45rem;">
        COMPARISON
    </div>
    """)

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.6rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                COMPARE PRODUCTS
            </span>
            <span style="font-size:0.7rem;color:#98A2B3;">
                Objective cross-product benchmarking
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;">
            Select up to 5 products to compare sentiment distributions and customer complaint concentrations side-by-side.
        </div>
    </div>
    """)

    top_comparison_options = product_options[:15]
    default_selected = top_comparison_options[:3]

    selected_compare_options = st.multiselect(
        "Select Products to Compare (Max 5)",
        options=product_options,
        default=default_selected,
        max_selections=5,
        key="compare_multiselect"
    )

    if selected_compare_options:
        compare_asins = [asin_lookup.get(opt, opt.split()[0]) for opt in selected_compare_options]
        compare_df = df_raw[df_raw["product"].isin(compare_asins)].copy()

        col_comp_sent, col_comp_heat = st.columns([1.1, 1.1])

        # 1. Product Sentiment Comparison (Stacked Bar)
        with col_comp_sent:
            render_html("""
            <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.65rem 0.85rem;margin-bottom:0.4rem;">
                <div style="font-size:0.7rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;">PRODUCT SENTIMENT COMPARISON</div>
                <div style="font-size:0.7rem;color:#98A2B3;">Measured share of positive, neutral, and negative sentiment</div>
            </div>
            """)

            comp_stats = []
            for c_asin in compare_asins:
                c_sub = compare_df[compare_df["product"] == c_asin]
                c_tot = len(c_sub)
                if c_tot > 0:
                    c_pos = (c_sub["sentiment"] == "positive").sum() / c_tot * 100
                    c_neu = (c_sub["sentiment"] == "neutral").sum() / c_tot * 100
                    c_neg = (c_sub["sentiment"] == "negative").sum() / c_tot * 100
                    comp_stats.append({"product": c_asin, "Positive": c_pos, "Neutral": c_neu, "Negative": c_neg, "total": c_tot})

            if comp_stats:
                df_comp_stats = pd.DataFrame(comp_stats)
                fig_comp = go.Figure()
                fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Positive"], name="Positive", orientation="h", marker_color="#22C55E"))
                fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Neutral"], name="Neutral", orientation="h", marker_color="#F59E0B"))
                fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Negative"], name="Negative", orientation="h", marker_color="#EF4444"))

                fig_comp.update_layout(
                    barmode="stack",
                    height=max(190, len(comp_stats) * 42),
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#98A2B3", size=9)),
                    xaxis=dict(showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3", size=9), title="Sentiment Share %", range=[0, 100]),
                    yaxis=dict(autorange="reversed", tickfont=dict(color="#F5F7FA", size=9))
                )
                st.plotly_chart(fig_comp, use_container_width=True, config={"displayModeBar": False})

        # 2. Product × Customer Concerns Heatmap
        with col_comp_heat:
            render_html("""
            <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.65rem 0.85rem;margin-bottom:0.4rem;">
                <div style="font-size:0.7rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;">PRODUCT × CUSTOMER CONCERNS</div>
                <div style="font-size:0.7rem;color:#98A2B3;">Negative feedback distribution (% share) across aspects</div>
            </div>
            """)

            heat_aspects = ["Product Quality", "Delivery", "Packaging", "Customer Service", "Price & Value", "Usability & Application"]
            matrix_data = []

            for c_asin in compare_asins:
                c_neg = compare_df[(compare_df["product"] == c_asin) & (compare_df["sentiment"] == "negative")]
                c_neg_tot = len(c_neg)
                row_shares = []

                if c_neg_tot > 0:
                    c_summary, _, _ = _analyze_product_aspects(c_neg)
                    summary_dict = {item["aspect"]: item["share_pct"] for item in c_summary}
                    for asp in heat_aspects:
                        row_shares.append(round(summary_dict.get(asp, 0.0), 1))
                else:
                    row_shares = [0.0] * len(heat_aspects)

                matrix_data.append(row_shares)

            fig_heat = px.imshow(
                matrix_data,
                labels=dict(x="Aspect", y="Product", color="Share %"),
                x=heat_aspects,
                y=compare_asins,
                color_continuous_scale=[[0, "#11151D"], [0.3, "#3B82F6"], [0.6, "#F59E0B"], [1.0, "#EF4444"]],
                text_auto=True
            )
            fig_heat.update_traces(textfont=dict(color="#F5F7FA", size=9))
            fig_heat.update_layout(
                height=max(190, len(compare_asins) * 42),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                xaxis=dict(tickfont=dict(color="#98A2B3", size=9), side="bottom"),
                yaxis=dict(tickfont=dict(color="#F5F7FA", size=9))
            )
            st.plotly_chart(fig_heat, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Select at least one product to display cross-product comparisons.")

    # ── 9. PRODUCT REVIEW FEED ──────────────────────────────────────────────────
    render_html("""
    <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.1em;margin-top:1.5rem;margin-bottom:0.45rem;">
        REVIEWS
    </div>
    """)

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.95rem 1.15rem;margin-bottom:0.6rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.2rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                PRODUCT REVIEW FEED
            </span>
            <span style="font-size:0.7rem;color:#98A2B3;">
                Interactive review log for selected product
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;">
            Filter and inspect all customer submissions specifically associated with this ASIN.
        </div>
    </div>
    """)

    # Sub-filters for product feed
    f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1.2, 1])
    with f_col1:
        f_sent = st.selectbox("Sentiment", options=["All", "Positive", "Neutral", "Negative"], index=0, key="pfeed_sent")
    with f_col2:
        f_rating = st.selectbox("Rating", options=["All", "5.0", "4.0", "3.0", "2.0", "1.0"], index=0, key="pfeed_rating")
    with f_col3:
        aspect_filter_opts = ["All"] + list(ASPECT_KEYWORDS.keys())
        f_aspect = st.selectbox("Aspect Filter", options=aspect_filter_opts, index=0, key="pfeed_aspect")
    with f_col4:
        f_verified = st.checkbox("Verified Only", value=False, key="pfeed_ver")

    # Apply product review filters
    feed_df = product_df.copy()
    if f_sent != "All":
        feed_df = feed_df[feed_df["sentiment"] == f_sent.lower()]
    if f_rating != "All":
        feed_df = feed_df[feed_df["rating"] == float(f_rating)]
    if f_verified:
        feed_df = feed_df[feed_df["verified_purchase"] == True]
    if f_aspect != "All":
        kws = ASPECT_KEYWORDS.get(f_aspect, [])
        feed_df = feed_df[feed_df["text"].str.lower().apply(lambda t: any(k in str(t) for k in kws))]

    feed_count = len(feed_df)
    st.caption(f"Showing **{min(15, feed_count)}** of **{feed_count:,}** matching reviews for Product `{selected_asin}`")

    if feed_count == 0:
        st.info("No reviews match the selected feed filters.")
    else:
        for _, row in feed_df.head(15).iterrows():
            r_rating = float(row.get("rating", 5.0))
            r_sent = str(row.get("sentiment", "neutral")).upper()
            r_text = str(row.get("text", "")).strip()
            r_title = str(row.get("title", "")).strip()
            r_date = str(row.get("date", "N/A"))
            r_verified = bool(row.get("verified_purchase", False))

            intel = extract_aspects_and_issues(r_text, sentiment=r_sent.lower(), rating=r_rating)

            if r_sent == "POSITIVE":
                sent_color = "#22C55E"
                sent_bg = "rgba(34,197,94,0.12)"
            elif r_sent == "NEGATIVE":
                sent_color = "#EF4444"
                sent_bg = "rgba(239,68,68,0.12)"
            else:
                sent_color = "#F59E0B"
                sent_bg = "rgba(245,158,11,0.12)"

            ver_badge = (
                '<span style="background:rgba(34,211,238,0.1);color:#22D3EE;border:1px solid #22D3EE;border-radius:3px;padding:1px 5px;font-size:0.62rem;font-weight:700;">VERIFIED</span>'
                if r_verified else ''
            )

            safe_feed_title = html.escape(r_title)
            safe_feed_text = html.escape(r_text)

            render_html(f"""
            <div style="background:#11151D;border:1px solid #242A35;border-radius:6px;padding:0.85rem 1.1rem;margin-bottom:0.55rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
                    <div style="display:flex;align-items:center;gap:0.5rem;">
                        <span style="color:#F59E0B;font-size:0.9rem;">{_star_icons(r_rating)}</span>
                        <span style="color:#98A2B3;font-size:0.75rem;font-family:'JetBrains Mono',monospace;">{r_rating:.1f}/5</span>
                        <span style="background:{sent_bg};color:{sent_color};border:1px solid {sent_color};border-radius:4px;padding:1px 6px;font-size:0.65rem;font-weight:800;">{r_sent}</span>
                        {ver_badge}
                    </div>
                    <div style="font-size:0.7rem;color:#667085;font-family:'JetBrains Mono',monospace;">{r_date}</div>
                </div>
                {f'<div style="font-size:0.82rem;font-weight:700;color:#F5F7FA;margin-bottom:0.25rem;">{safe_feed_title}</div>' if safe_feed_title else ''}
                <div style="font-size:0.8rem;color:#D1D5DB;line-height:1.45;margin-bottom:0.45rem;">
                    "{safe_feed_text}"
                </div>
                <div style="display:flex;gap:0.85rem;font-size:0.7rem;color:#98A2B3;border-top:1px solid #1E2533;padding-top:0.35rem;flex-wrap:wrap;">
                    <span>Aspect: <b style="color:#F5F7FA;">{intel['primary_aspect']}</b></span>
                    <span>Issue: <b style="color:#F5F7FA;">{intel['issue']}</b></span>
                    <span>Priority: <b style="color:{'#EF4444' if intel['priority']=='HIGH' else '#F59E0B' if intel['priority']=='MEDIUM' else '#3B82F6'};">{intel['priority']}</b></span>
                </div>
            </div>
            """)
