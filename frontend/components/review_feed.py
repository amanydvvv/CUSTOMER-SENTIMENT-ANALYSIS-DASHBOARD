"""
review_feed.py
──────────────
Analytically rich Customer Review Feed component.
Directly connects genuine customer feedback to:
Aspect Extraction → Issue Detection → Priority → Action Recommendation.
Uses render_html from frontend.ui_utils to guarantee zero raw HTML leaks.
"""

import streamlit as st
import pandas as pd
from frontend.ui_utils import render_html
from frontend.components.aspect_analyzer import extract_aspects_and_issues


def _star_icons(rating: float) -> str:
    try:
        r = int(round(float(rating)))
    except Exception:
        r = 5
    r = max(1, min(5, r))
    return "★" * r + "☆" * (5 - r)


def render_review_feed(df: pd.DataFrame):
    """Renders the analytical Customer Review Feed."""
    if len(df) == 0:
        st.info("No reviews match the selected filter criteria.")
        return

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:0.75rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                    CUSTOMER REVIEW FEED & ANALYTICS
                </div>
                <div style="font-size:0.78rem;color:#98A2B3;margin-top:2px;">
                    Connecting raw customer feedback to automated aspect classification & action items
                </div>
            </div>
        </div>
    </div>
    """)

    # Controls Header
    col_sort, col_aspect, col_size = st.columns([1.5, 1.5, 1])

    with col_sort:
        sort_by = st.selectbox(
            "Sort Reviews",
            ["Most Recent", "Highest Rating", "Lowest Rating", "Most Helpful", "Mismatch Cases Only"],
            key="feed_sort",
        )

    with col_aspect:
        aspect_filter = st.selectbox(
            "Filter Aspect",
            ["All Aspects", "Product Quality", "Delivery", "Packaging",
             "Customer Service", "Price & Value", "Performance", "Usability & Application"],
            key="feed_aspect_filter",
        )

    with col_size:
        page_size = st.selectbox("Reviews per page", [10, 25, 50], index=0, key="feed_page_size")

    # Data prep
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
            badge_bg = "rgba(34, 197, 94, 0.15)"
            badge_color = "#22C55E"
            badge_border = "rgba(34, 197, 94, 0.3)"
        elif sentiment_str == "NEGATIVE":
            badge_bg = "rgba(239, 68, 68, 0.15)"
            badge_color = "#EF4444"
            badge_border = "rgba(239, 68, 68, 0.3)"
        else:
            badge_bg = "rgba(245, 158, 11, 0.15)"
            badge_color = "#F59E0B"
            badge_border = "rgba(245, 158, 11, 0.3)"

        p_color = {
            "HIGH": "#EF4444",
            "MEDIUM": "#F59E0B",
            "LOW": "#22C55E",
        }.get(intel["priority"], "#98A2B3")

        mismatch_html = ""
        if row.get("is_mismatch"):
            mismatch_html = (
                f'<span style="background:rgba(239,68,68,0.15);color:#EF4444;border:1px solid rgba(239,68,68,0.35);'
                f'padding:2px 8px;border-radius:4px;font-size:0.7rem;font-weight:700;">'
                f'⚠️ MISMATCH: {row["rating"]:.0f}★ vs {sentiment_str}</span>'
            )

        title_text = str(row.get("title", "")).strip()
        title_html = (
            f'<div style="font-weight:700;font-size:0.92rem;color:#F5F7FA;margin-bottom:0.25rem;">{title_text}</div>'
            if title_text else ""
        )

        verified_html = (
            '<span style="color:#22C55E;font-size:0.72rem;font-weight:600;">✓ Verified Purchase</span>'
            if row.get("verified_purchase") else ""
        )

        helpful = row.get("helpful_votes", 0)
        helpful_html = f'<span style="color:#98A2B3;font-size:0.72rem;">👍 {helpful} helpful</span>' if helpful > 0 else ""

        full_text = str(row["text"])
        snippet = full_text[:280] + ("…" if len(full_text) > 280 else "")

        card_html = f"""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.75rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;">
                    <span style="color:#F59E0B;font-size:0.95rem;letter-spacing:1px;">{_star_icons(row['rating'])}</span>
                    <span style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">{row['rating']:.0f}/5</span>
                    <span style="background:{badge_bg};color:{badge_color};border:1px solid {badge_border};padding:2px 8px;border-radius:4px;font-size:0.72rem;font-weight:800;letter-spacing:0.04em;">
                        {sentiment_str}
                    </span>
                    {mismatch_html}
                </div>
                <div style="font-size:0.75rem;color:#667085;">{str(row.get('date', ''))[:10]}</div>
            </div>

            {title_html}
            <div style="color:#D0D5DD;font-size:0.88rem;line-height:1.5;margin-bottom:0.65rem;">
                "{snippet}"
            </div>

            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;border-top:1px solid #1E2533;padding-top:0.6rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;font-size:0.75rem;">
                    <span style="background:#151A24;border:1px solid #242A35;color:#98A2B3;padding:2px 8px;border-radius:4px;">
                        <b>Aspect:</b> {intel['primary_aspect']}
                    </span>
                    <span style="background:#151A24;border:1px solid #242A35;color:#98A2B3;padding:2px 8px;border-radius:4px;">
                        <b>Issue:</b> {intel['issue']}
                    </span>
                    <span style="background:#151A24;border:1px solid #242A35;color:{p_color};font-weight:700;padding:2px 8px;border-radius:4px;">
                        Priority: {intel['priority']}
                    </span>
                </div>
                <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.75rem;">
                    <span style="color:#667085;">ASIN: <code style="color:#22D3EE;font-size:0.7rem;">{row.get('product', 'N/A')}</code></span>
                    {verified_html}
                    {helpful_html}
                </div>
            </div>

            <div style="background:#151A24;border-left:3px solid #7C5CFF;padding:0.4rem 0.65rem;margin-top:0.6rem;border-radius:0 4px 4px 0;font-size:0.76rem;color:#98A2B3;">
                <b style="color:#F5F7FA;">Action:</b> {intel['suggested_action']}
            </div>
        </div>
        """

        render_html(card_html)

        if len(full_text) > 280:
            with st.expander("🔍 View Complete Review Text & AI Extraction Details", expanded=False):
                st.write(full_text)
                st.caption(f"Primary Aspect: {intel['primary_aspect']} | Detected Sub-Issue: {intel['issue']} | Recommended Intervention: {intel['suggested_action']}")
