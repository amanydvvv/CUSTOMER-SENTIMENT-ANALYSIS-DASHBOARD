"""
review_feed.py
──────────────
Analytically rich Customer Review Feed component.
Directly connects genuine customer feedback to:
Aspect Extraction → Issue Detection → Priority → Action Recommendation.
"""

import streamlit as st
import pandas as pd
from frontend.ui_utils import render_html
from frontend.components.aspect_analyzer import extract_aspects_and_issues


def _rating_label(rating) -> str:
    """Format numeric star rating into stars and fraction safely."""
    try:
        val = int(round(float(rating)))
        val = max(1, min(5, val))
    except (ValueError, TypeError):
        val = 5
    return f"{'★' * val}{'☆' * (5 - val)} {val}/5"


def _star_icons(rating: float) -> str:
    return _rating_label(rating)


def render_review_feed(df: pd.DataFrame, key_prefix: str = "feed"):
    """Renders the analytical Customer Review Feed."""
    if len(df) == 0:
        st.info("No reviews match the selected filter criteria.")
        return

    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                    CUSTOMER REVIEW FEED &amp; ANALYTICS
                </div>
                <div style="font-size:13px;color:#d1d5db;margin-top:4px;">
                    Connecting raw customer feedback to automated aspect classification and action items
                </div>
            </div>
        </div>
    </div>
    """)

    col_sort, col_aspect, col_size = st.columns([1.5, 1.5, 1])

    with col_sort:
        sort_by = st.selectbox(
            "Sort Reviews",
            ["Most Recent", "Highest Rating", "Lowest Rating", "Most Helpful", "Mismatch Cases Only"],
            key=f"{key_prefix}_sort",
        )

    with col_aspect:
        aspect_filter = st.selectbox(
            "Filter Aspect",
            ["All Aspects", "Product Quality", "Delivery", "Packaging",
             "Customer Service", "Price & Value", "Performance", "Usability & Application"],
            key=f"{key_prefix}_aspect_filter",
        )

    with col_size:
        page_size = st.selectbox("Reviews per page", [10, 25, 50], index=0, key=f"{key_prefix}_page_size")

    df_feed = df.copy()
    if "helpful_votes" not in df_feed.columns:
        df_feed["helpful_votes"] = 0
    df_feed["helpful_votes"] = pd.to_numeric(df_feed["helpful_votes"], errors="coerce").fillna(0).astype(int)

    if "rating" not in df_feed.columns:
        df_feed["rating"] = 5.0
    df_feed["rating"] = pd.to_numeric(df_feed["rating"], errors="coerce").fillna(5.0)

    df_feed["is_mismatch"] = (
        ((df_feed["rating"] >= 4.0) & (df_feed["sentiment"] == "negative")) |
        ((df_feed["rating"] <= 2.0) & (df_feed["sentiment"] == "positive"))
    )

    if sort_by == "Highest Rating":
        df_feed = df_feed.sort_values(by="rating", ascending=False)
    elif sort_by == "Lowest Rating":
        df_feed = df_feed.sort_values(by="rating", ascending=True)
    elif sort_by == "Most Helpful":
        df_feed = df_feed.sort_values(by="helpful_votes", ascending=False)
    elif sort_by == "Mismatch Cases Only":
        df_feed = df_feed[df_feed["is_mismatch"]]
    elif sort_by == "Most Recent" and "date_dt" in df_feed.columns:
        df_feed = df_feed.sort_values(by="date_dt", ascending=False)

    if aspect_filter != "All Aspects":
        df_feed["has_aspect"] = df_feed["text"].apply(
            lambda t: aspect_filter in extract_aspects_and_issues(str(t)).get("all_aspects", [])
        )
        df_feed = df_feed[df_feed["has_aspect"]]

    total_rows = len(df_feed)
    st.caption(f"Displaying {min(page_size, total_rows):,} of {total_rows:,} reviews")

    if total_rows == 0:
        st.info("No reviews match this specific feed filter.")
        return

    sample_df = df_feed.head(page_size)

    for idx, row in sample_df.iterrows():
        intel = extract_aspects_and_issues(
            str(row["text"]),
            sentiment=str(row.get("sentiment", "neutral")),
            rating=float(row.get("rating", 3.0)),
        )

        sentiment_str = str(row.get("sentiment", "neutral")).upper()
        if sentiment_str == "POSITIVE":
            badge_bg = "rgba(16, 185, 129, 0.12)"
            badge_color = "#10b981"
            badge_border = "rgba(16, 185, 129, 0.3)"
        elif sentiment_str == "NEGATIVE":
            badge_bg = "rgba(239, 68, 68, 0.12)"
            badge_color = "#ef4444"
            badge_border = "rgba(239, 68, 68, 0.3)"
        else:
            badge_bg = "rgba(245, 158, 11, 0.12)"
            badge_color = "#f59e0b"
            badge_border = "rgba(245, 158, 11, 0.3)"

        p_color = {
            "HIGH": "#ef4444",
            "MEDIUM": "#f59e0b",
            "LOW": "#10b981",
        }.get(intel["priority"], "#9ca3af")

        mismatch_html = ""
        if row.get("is_mismatch"):
            mismatch_html = (
                f'<span style="background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.3);'
                f'padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;">'
                f'MISMATCH: {row["rating"]:.0f}★ vs {sentiment_str}</span>'
            )

        title_text = str(row.get("title", "")).strip()
        title_html = (
            f'<div style="font-weight:600;font-size:14px;color:#ffffff;margin-bottom:4px;">{title_text}</div>'
            if title_text else ""
        )

        verified_html = (
            '<span style="color:#10b981;font-size:11px;font-weight:600;">Verified Purchase</span>'
            if row.get("verified_purchase") else ""
        )

        helpful = row.get("helpful_votes", 0)
        helpful_html = f'<span style="color:#6b7280;font-size:11px;">{helpful} helpful votes</span>' if helpful > 0 else ""

        full_text = str(row["text"])
        snippet = full_text[:280] + ("…" if len(full_text) > 280 else "")

        card_html = f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                    <span style="color:#f59e0b;font-size:13px;letter-spacing:1px;">{_rating_label(row['rating'])}</span>
                    <span style="background:{badge_bg};color:{badge_color};border:1px solid {badge_border};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;letter-spacing:0.04em;">
                        {sentiment_str}
                    </span>
                    {mismatch_html}
                </div>
                <div style="font-size:11px;color:#6b7280;">{str(row.get('date', ''))[:10]}</div>
            </div>

            {title_html}
            <div style="color:#d1d5db;font-size:13px;line-height:1.5;margin-bottom:10px;">
                "{snippet}"
            </div>

            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-top:1px solid rgba(255,255,255,0.06);padding-top:10px;">
                <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px;">
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:#9ca3af;padding:2px 8px;border-radius:4px;">
                        <b>Aspect:</b> {intel['primary_aspect']}
                    </span>
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:#9ca3af;padding:2px 8px;border-radius:4px;">
                        <b>Issue:</b> {intel['issue']}
                    </span>
                    <span style="background:#181b21;border:1px solid rgba(255,255,255,0.07);color:{p_color};font-weight:700;padding:2px 8px;border-radius:4px;">
                        Priority: {intel['priority']}
                    </span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;font-size:11px;">
                    <span style="color:#6b7280;">ASIN: <code style="color:#9ca3af;font-size:11px;">{row.get('product', 'N/A')}</code></span>
                    {verified_html}
                    {helpful_html}
                </div>
            </div>

            <div style="background:#181b21;border-left:3px solid #10b981;padding:8px 10px;margin-top:10px;border-radius:0 4px 4px 0;font-size:12px;color:#9ca3af;">
                <b style="color:#ffffff;">Action:</b> {intel['suggested_action']}
            </div>
        </div>
        """

        render_html(card_html)

        if len(full_text) > 280:
            with st.expander("View Full Review Text", expanded=False):
                st.write(full_text)
                st.caption(f"Primary Aspect: {intel['primary_aspect']} | Issue: {intel['issue']} | Recommended Action: {intel['suggested_action']}")
