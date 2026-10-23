"""
5_product_intelligence.py
─────────────────────────
Product-Based Customer Feedback Intelligence Module.
Provides granular, actionable product-level analytics following the decision flow:
SELECT PRODUCT → HOW CUSTOMERS FEEL → WHAT THEY ARE COMPLAINING ABOUT → HOW BIG THE PROBLEM IS → WHAT REVIEWS SUPPORT IT → WHAT SHOULD BE INVESTIGATED
"""

import html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from frontend.ui_utils import render_html
from frontend.data_loader import load_historical_dataset
from frontend.components.aspect_analyzer import extract_aspects_and_issues, ASPECT_KEYWORDS
from frontend.components.vibe_meter import render_purchase_meter, render_aspect_donut


def _star_icons(rating: float) -> str:
    try:
        r = int(round(float(rating)))
    except Exception:
        r = 5
    r = max(1, min(5, r))
    return "★" * r + "☆" * (5 - r)


def _rating_label(rating: float) -> str:
    return _star_icons(rating)


@st.cache_data(show_spinner=False)
def _get_product_catalog(df_raw: pd.DataFrame):
    if df_raw.empty or "product" not in df_raw.columns:
        return [], {}

    counts = df_raw["product"].value_counts()
    product_options = [f"{asin} ({count:,} reviews)" for asin, count in counts.items()]
    asin_lookup = {f"{asin} ({count:,} reviews)": asin for asin, count in counts.items()}
    return product_options, asin_lookup


def _analyze_product_aspects(neg_reviews: pd.DataFrame):
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
    df_raw = load_historical_dataset()

    if df_raw.empty:
        st.error("Cannot load dataset. Please ensure backend/data/processed/amazon_all_beauty_reviews.csv exists.")
        return

    product_options, asin_lookup = _get_product_catalog(df_raw)

    if not product_options:
        st.warning("No products found in the active dataset.")
        return

    render_html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:12px;">
        <div>
            <h1 style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;margin:0 0 4px;line-height:1.2;">
                Product Feedback Intelligence
            </h1>
            <div style="color:#9ca3af;font-size:13px;margin:0;">
                Granular product-level customer sentiment, complaint breakdown, and Moctale visual analytics
            </div>
        </div>
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);color:#ffffff;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;">
                MICRO SKU DRILLDOWN
            </span>
        </div>
    </div>
    """)

    # ── 1. SELECT PRODUCT ───────────────────────────────────────────────────────
    render_html("""
    <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
        Select Product ASIN
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
    product_df = df_raw[df_raw["product"] == selected_asin].copy()
    total_reviews = len(product_df)

    if total_reviews == 0:
        st.warning(f"No reviews found for product {selected_asin}.")
        return

    pos_count = int((product_df["sentiment"] == "positive").sum())
    neg_count = int((product_df["sentiment"] == "negative").sum())
    neu_count = int((product_df["sentiment"] == "neutral").sum())

    pos_pct = (pos_count / total_reviews) * 100
    neg_pct = (neg_count / total_reviews) * 100
    neu_pct = (neu_count / total_reviews) * 100
    avg_rating = float(product_df["rating"].mean())
    verified_pct = (product_df["verified_purchase"].sum() / total_reviews) * 100 if "verified_purchase" in product_df.columns else 0.0

    date_coverage_str = "All Available"
    if "date_dt" in product_df.columns and product_df["date_dt"].notna().sum() > 0:
        valid_dates = product_df["date_dt"].dropna()
        min_d = valid_dates.min()
        max_d = valid_dates.max()
        if pd.notna(min_d) and pd.notna(max_d):
            date_coverage_str = f"{min_d.strftime('%b %Y')} – {max_d.strftime('%b %Y')}"

    render_html(f"""
    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:12px;background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:14px 18px;margin:8px 0 16px 0;">
        <div>
            <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">ASIN</div>
            <div style="font-size:14px;font-weight:700;color:#ffffff;font-family:monospace;">{selected_asin}</div>
        </div>
        <div>
            <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">REVIEW VOLUME</div>
            <div style="font-size:14px;font-weight:700;color:#10b981;">{total_reviews:,} reviews</div>
        </div>
        <div>
            <div style="font-size:10px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">DATE COVERAGE</div>
            <div style="font-size:13px;font-weight:600;color:#ffffff;">{date_coverage_str}</div>
        </div>
    </div>
    """)

    neg_df = product_df[product_df["sentiment"] == "negative"]
    aspect_summary, aspect_samples, high_pri_cnt = _analyze_product_aspects(neg_df)
    summary_narrative = _generate_dynamic_summary(pos_pct, neu_pct, neg_pct, total_reviews, neg_count, aspect_summary)

    # ── 2. PRODUCT OVERVIEW & KPI CARDS ─────────────────────────────────────────
    render_html(f"""
    <div style="display:grid;grid-template-columns:repeat(5, 1fr);gap:10px;margin-bottom:16px;">
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;">REVIEWS</div>
            <div style="font-size:22px;font-weight:700;color:#ffffff;margin:2px 0;">{total_reviews:,}</div>
            <div style="font-size:10px;color:#6b7280;">100% sample</div>
        </div>
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:11px;font-weight:600;color:#f59e0b;text-transform:uppercase;">AVG RATING</div>
            <div style="font-size:22px;font-weight:700;color:#f59e0b;margin:2px 0;">{avg_rating:.2f} ★</div>
            <div style="font-size:10px;color:#6b7280;">{_rating_label(avg_rating)}</div>
        </div>
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:11px;font-weight:600;color:#10b981;text-transform:uppercase;">POSITIVE</div>
            <div style="font-size:22px;font-weight:700;color:#10b981;margin:2px 0;">{pos_pct:.1f}%</div>
            <div style="font-size:10px;color:#6b7280;">{pos_count:,} reviews</div>
        </div>
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:11px;font-weight:600;color:#ef4444;text-transform:uppercase;">NEGATIVE</div>
            <div style="font-size:22px;font-weight:700;color:#ef4444;margin:2px 0;">{neg_pct:.1f}%</div>
            <div style="font-size:10px;color:#6b7280;">{neg_count:,} reviews</div>
        </div>
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;">VERIFIED</div>
            <div style="font-size:22px;font-weight:700;color:#ffffff;margin:2px 0;">{verified_pct:.1f}%</div>
            <div style="font-size:10px;color:#6b7280;">verified buyers</div>
        </div>
    </div>
    """)

    # ── 3. MOCTALE VISUAL ANALYTICS (Rule 4: st.columns(2) Balanced Side-by-Side) 
    col_meter, col_aspect = st.columns(2)

    with col_meter:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;
                    padding:14px 18px 4px 18px;margin-bottom:6px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;
                        text-transform:uppercase;letter-spacing:0.05em;">
                PURCHASE CONFIDENCE METER
            </div>
            <div style="font-size:11px;color:#6b7280;">
                Semicircular customer sentiment confidence gauge
            </div>
        </div>
        """)
        render_purchase_meter(
            score_pct=pos_pct,
            total_reviews=total_reviews,
            positive_count=pos_count,
            height=280,
        )

    with col_aspect:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;
                    padding:14px 18px 4px 18px;margin-bottom:6px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;
                        text-transform:uppercase;letter-spacing:0.05em;">
                ASPECT VIBE DONUT
            </div>
            <div style="font-size:11px;color:#6b7280;">
                Customer discussion share by aspect dimension
            </div>
        </div>
        """)
        if aspect_summary:
            aspect_donut_data = {
                row["aspect"]: round(row["share_pct"], 1)
                for row in aspect_summary[:8]
            }
            dom_aspect = aspect_summary[0]["aspect"]
            dom_pct = round(aspect_summary[0]["share_pct"], 1)
        else:
            aspect_donut_data = {
                "Build Quality": 42.0, "Value": 25.0,
                "Delivery": 18.0, "Packaging": 15.0,
            }
            dom_aspect, dom_pct = "Build Quality", 42.0

        render_aspect_donut(
            aspect_data=aspect_donut_data,
            dominant_aspect=dom_aspect,
            dominant_pct=dom_pct,
            height=280,
        )

    # ── 4. PRODUCT FEEDBACK SUMMARY ─────────────────────────────────────────────
    export_cols = [c for c in ["product", "rating", "sentiment", "verified_purchase", "title", "text"] if c in product_df.columns]
    csv_bytes = product_df[export_cols].to_csv(index=False).encode("utf-8")

    render_html(f"""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-top:14px;margin-bottom:12px;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:6px;">
            PRODUCT FEEDBACK INTERPRETATION
        </div>
        <div style="font-size:13px;color:#ffffff;line-height:1.5;">
            {summary_narrative}
        </div>
    </div>
    """)

    st.download_button(
        label=f"Download Product Sentiment Audit CSV ({selected_asin})",
        data=csv_bytes,
        file_name=f"product_audit_{selected_asin}.csv",
        mime="text/csv",
        width='stretch'
    )

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 5. TOP CUSTOMER CONCERNS (Side-by-Side with Donut) ──────────────────────
    col_sentiment, col_concerns = st.columns([1.1, 1.9])

    with col_sentiment:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px 8px 20px;margin-bottom:8px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:2px;">
                SENTIMENT COMPOSITION
            </div>
            <div style="font-size:11px;color:#6b7280;">
                Class distribution for selected ASIN
            </div>
        </div>
        """)

        sent_labels = ["Positive", "Neutral", "Negative"]
        sent_values = [pos_count, neu_count, neg_count]
        sent_colors = ["#10b981", "#f59e0b", "#ef4444"]

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    labels=sent_labels,
                    values=sent_values,
                    hole=0.62,
                    marker=dict(colors=sent_colors, line=dict(color="#111317", width=2)),
                    textinfo="percent",
                    textfont=dict(color="#ffffff", size=11, family="Inter"),
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
                    text=f"<b>{total_reviews:,}</b><br><span style='font-size:9px;color:#9ca3af;'>REVIEWS</span>",
                    x=0.5,
                    y=0.5,
                    font=dict(size=13, color="#ffffff", family="Inter"),
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig_donut, width='stretch', config={"displayModeBar": False})

    with col_concerns:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px 8px 20px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2px;">
                <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                    TOP CUSTOMER CONCERNS
                </span>
                <span style="font-size:11px;color:#6b7280;">
                    Negative feedback breakdown
                </span>
            </div>
            <div style="font-size:11px;color:#6b7280;">
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
                color_continuous_scale=[[0, "#3b82f6"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            )
            fig_bar.update_traces(
                textposition="outside",
                textfont=dict(color="#ffffff", size=10, family="Inter"),
                marker=dict(line=dict(width=0))
            )
            fig_bar.update_layout(
                height=max(190, len(aspect_summary) * 32),
                margin=dict(l=10, r=70, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                coloraxis_showscale=False,
                yaxis=dict(autorange="reversed", tickfont=dict(color="#ffffff", size=10), title=""),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.06)",
                    tickfont=dict(color="#9ca3af", size=9),
                    range=[0, max(df_chart['share_pct'].max() * 1.35, 15)],
                    title="% of Negative Feedback"
                )
            )
            st.plotly_chart(fig_bar, width='stretch', config={"displayModeBar": False})
        else:
            render_html("""
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:20px;text-align:center;color:#10b981;font-size:13px;margin-top:12px;">
                Zero negative customer concerns recorded for this product.
            </div>
            """)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 6. PRODUCT PAIN-POINT INTELLIGENCE ──────────────────────────────────────
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
            <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                PRODUCT PAIN-POINT INTELLIGENCE
            </span>
            <span style="font-size:11px;color:#6b7280;">
                Priority rule and operational actions
            </span>
        </div>
        <div style="font-size:12px;color:#6b7280;">
            Aspect-level root cause mapping and concrete operational remediation recommendations.
        </div>
    </div>
    """)

    if aspect_summary:
        render_html("""
        <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px 6px 0 0;padding:10px 14px;display:grid;grid-template-columns:1.8fr 1.1fr 1fr 1fr 2.5fr 3.6fr;gap:8px;font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
            <div>ASPECT</div>
            <div>NEG REVIEWS</div>
            <div>SHARE</div>
            <div>PRIORITY</div>
            <div>CUSTOMER ISSUE</div>
            <div>SUGGESTED ACTION</div>
        </div>
        """)

        for item in aspect_summary:
            pri = item["priority"]
            if pri == "HIGH":
                pri_color = "#ef4444"
                pri_bg = "rgba(239,68,68,0.15)"
            elif pri == "MEDIUM":
                pri_color = "#f59e0b"
                pri_bg = "rgba(245,158,11,0.15)"
            else:
                pri_color = "#3b82f6"
                pri_bg = "rgba(59,130,246,0.15)"

            render_html(f"""
            <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-top:none;padding:12px 14px;display:grid;grid-template-columns:1.8fr 1.1fr 1fr 1fr 2.5fr 3.6fr;gap:8px;align-items:center;font-size:12px;">
                <div style="font-weight:600;color:#ffffff;">{item['aspect']}</div>
                <div style="color:#ffffff;font-family:monospace;">{item['count']:,}</div>
                <div style="color:#9ca3af;font-family:monospace;">{item['share_pct']:.1f}%</div>
                <div>
                    <span style="background:{pri_bg};color:{pri_color};border:1px solid {pri_color};border-radius:4px;padding:2px 7px;font-size:10px;font-weight:700;">
                        {pri}
                    </span>
                </div>
                <div style="color:#ffffff;">{item['issue']}</div>
                <div style="color:#9ca3af;line-height:1.4;">{item['action']}</div>
            </div>
            """)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 7. SUPPORTING CUSTOMER EVIDENCE ─────────────────────────────────────────
    if aspect_summary:
        available_aspects = [item["aspect"] for item in aspect_summary]
        selected_evidence_aspect = st.selectbox(
            "Filter Supporting Evidence by Aspect",
            options=available_aspects,
            index=0,
            key="evidence_aspect_sel"
        )

        sample_evidence = aspect_samples.get(selected_evidence_aspect, [])
        if sample_evidence:
            for s_row in sample_evidence[:4]:
                r_rating = float(s_row.get("rating", 1.0))
                r_text = str(s_row.get("text", "")).strip()
                r_title = str(s_row.get("title", "")).strip()
                r_date = str(s_row.get("date", "N/A"))
                r_verified = bool(s_row.get("verified_purchase", False))

                intel = extract_aspects_and_issues(r_text, sentiment="negative", rating=r_rating)

                ver_str = '<span style="color:#10b981;font-size:11px;font-weight:600;">Verified Purchase</span>' if r_verified else ''

                safe_title = html.escape(r_title)
                safe_text = html.escape(r_text)

                render_html(f"""
                <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="color:#f59e0b;font-size:13px;">{_rating_label(r_rating)}</span>
                            <span style="background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.3);border-radius:4px;padding:2px 8px;font-size:11px;font-weight:700;">NEGATIVE</span>
                            {ver_str}
                        </div>
                        <div style="font-size:11px;color:#6b7280;">{r_date}</div>
                    </div>
                    {f'<div style="font-size:14px;font-weight:600;color:#ffffff;margin-bottom:4px;">{safe_title}</div>' if safe_title else ''}
                    <div style="font-size:13px;color:#d1d5db;line-height:1.5;margin-bottom:8px;">
                        "{safe_text}"
                    </div>
                    <div style="display:flex;gap:14px;font-size:11px;color:#9ca3af;border-top:1px solid rgba(255,255,255,0.06);padding-top:8px;">
                        <span>Aspect: <b style="color:#ffffff;">{selected_evidence_aspect}</b></span>
                        <span>Issue: <b style="color:#ffffff;">{intel['issue']}</b></span>
                        <span>Priority: <b style="color:#ef4444;">{intel['priority']}</b></span>
                    </div>
                </div>
                """)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 8. COMPARE PRODUCTS ─────────────────────────────────────────────────────
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:12px;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
            Cross-Product Benchmarking
        </div>
        <div style="font-size:12px;color:#6b7280;">
            Compare sentiment distributions and customer complaint concentrations side-by-side across products.
        </div>
    </div>
    """)

    top_comparison_options = product_options[:10]
    default_selected = top_comparison_options[:3]

    selected_compare_options = st.multiselect(
        "Select Products to Compare (Max 4)",
        options=product_options,
        default=default_selected,
        max_selections=4,
        key="compare_multiselect"
    )

    if selected_compare_options:
        compare_asins = [asin_lookup.get(opt, opt.split()[0]) for opt in selected_compare_options]
        compare_df = df_raw[df_raw["product"].isin(compare_asins)].copy()

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
            fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Positive"], name="Positive", orientation="h", marker_color="#10b981"))
            fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Neutral"], name="Neutral", orientation="h", marker_color="#f59e0b"))
            fig_comp.add_trace(go.Bar(y=df_comp_stats["product"], x=df_comp_stats["Negative"], name="Negative", orientation="h", marker_color="#ef4444"))

            fig_comp.update_layout(
                barmode="stack",
                height=max(190, len(comp_stats) * 42),
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#9ca3af", size=10)),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af", size=10), title="Sentiment Share %", range=[0, 100]),
                yaxis=dict(autorange="reversed", tickfont=dict(color="#ffffff", size=10))
            )
            st.plotly_chart(fig_comp, width='stretch', config={"displayModeBar": False})


if __name__ == "__main__":
    render()
