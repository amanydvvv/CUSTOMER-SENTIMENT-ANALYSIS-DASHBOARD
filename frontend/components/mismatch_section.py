"""
mismatch_section.py
───────────────────
Rating vs. AI Sentiment Mismatch Analytics component.
Detects discrepancies where numerical star ratings diverge from textual sentiment.
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


def render_mismatch_section(df: pd.DataFrame):
    """Renders the Rating–Sentiment Mismatch diagnostic analysis."""
    if len(df) == 0:
        return

    # High star (4-5) but negative text
    over_rated = df[(df["rating"] >= 4.0) & (df["sentiment"] == "negative")]
    # Low star (1-2) but positive text
    under_rated = df[(df["rating"] <= 2.0) & (df["sentiment"] == "positive")]

    total_mismatches = len(over_rated) + len(under_rated)
    mismatch_rate = (total_mismatches / len(df)) * 100 if len(df) > 0 else 0.0

    render_html(f"""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
            <span style="font-size:0.75rem;font-weight:700;color:#22D3EE;text-transform:uppercase;letter-spacing:0.08em;">
                RATING × SENTIMENT MISMATCH
            </span>
            <span style="font-size:0.72rem;color:#7C5CFF;background:rgba(124,92,255,0.12);padding:2px 8px;border-radius:4px;border:1px solid rgba(124,92,255,0.3);font-weight:600;">
                {total_mismatches:,} Discrepancies ({mismatch_rate:.2f}%)
            </span>
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.9rem;">
            Reviews where star rating and review text tell different stories.
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;margin-bottom:0.9rem;">
            <div style="background:#151A24;border:1px solid rgba(239,68,68,0.25);border-radius:6px;padding:0.75rem;">
                <div style="font-size:0.68rem;color:#EF4444;text-transform:uppercase;font-weight:700;">4–5 ★ + Negative Text</div>
                <div style="font-size:1.35rem;font-weight:800;color:#F5F7FA;margin:2px 0;">{len(over_rated):,} reviews</div>
                <div style="font-size:0.72rem;color:#98A2B3;line-height:1.35;">
                    Customers gave a high rating but expressed negative feedback in the text.
                </div>
            </div>
            <div style="background:#151A24;border:1px solid rgba(34,197,94,0.25);border-radius:6px;padding:0.75rem;">
                <div style="font-size:0.68rem;color:#22C55E;text-transform:uppercase;font-weight:700;">1–2 ★ + Positive Text</div>
                <div style="font-size:1.35rem;font-weight:800;color:#F5F7FA;margin:2px 0;">{len(under_rated):,} reviews</div>
                <div style="font-size:0.72rem;color:#98A2B3;line-height:1.35;">
                    Customers gave a low rating but used positive language in the review.
                </div>
            </div>
        </div>

        <div style="background:#151A24;border-left:3px solid #7C5CFF;border-radius:0 4px 4px 0;padding:0.6rem 0.85rem;font-size:0.75rem;color:#98A2B3;line-height:1.45;">
            <b style="color:#F5F7FA;">NOTE:</b> These cases indicate disagreement between explicit star rating and textual sentiment.
        </div>
    </div>
    """)

    # Expandable Inspection
    if total_mismatches > 0:
        with st.expander(f"🔍 Inspect Rating–Sentiment Mismatch Sample Reviews ({total_mismatches:,})", expanded=False):
            tab_over, tab_under = st.tabs([
                f"4–5★ + Negative Text ({len(over_rated):,})",
                f"1–2★ + Positive Text ({len(under_rated):,})"
            ])

            with tab_over:
                if len(over_rated) > 0:
                    for _, row in over_rated.head(4).iterrows():
                        intel = extract_aspects_and_issues(str(row["text"]), sentiment="negative", rating=row["rating"])
                        render_html(f"""
                        <div style="background:#151A24;border:1px solid rgba(239,68,68,0.2);border-radius:6px;padding:0.75rem;margin-bottom:0.5rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                                <div>
                                    <span style="color:#F59E0B;font-size:0.85rem;">{_star_icons(row['rating'])}</span>
                                    <b style="color:#F5F7FA;margin-left:0.3rem;">{row['rating']:.0f}★</b>
                                    <span style="background:rgba(239,68,68,0.15);color:#EF4444;border:1px solid rgba(239,68,68,0.3);padding:1px 6px;border-radius:3px;font-size:0.68rem;font-weight:700;margin-left:0.4rem;">NLP: NEGATIVE</span>
                                </div>
                                <span style="font-size:0.72rem;color:#667085;">{str(row.get('date', ''))[:10]}</span>
                            </div>
                            <div style="color:#D0D5DD;font-size:0.82rem;line-height:1.4;margin:0.25rem 0;">"{str(row['text'])[:280]}…"</div>
                            <div style="font-size:0.72rem;color:#98A2B3;">
                                <b>Detected Friction:</b> {intel['primary_aspect']} ({intel['issue']}) · <b>Action:</b> {intel['suggested_action']}
                            </div>
                        </div>
                        """)
                else:
                    st.caption("No records in this category.")

            with tab_under:
                if len(under_rated) > 0:
                    for _, row in under_rated.head(4).iterrows():
                        intel = extract_aspects_and_issues(str(row["text"]), sentiment="positive", rating=row["rating"])
                        render_html(f"""
                        <div style="background:#151A24;border:1px solid rgba(34,197,94,0.2);border-radius:6px;padding:0.75rem;margin-bottom:0.5rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
                                <div>
                                    <span style="color:#F59E0B;font-size:0.85rem;">{_star_icons(row['rating'])}</span>
                                    <b style="color:#F5F7FA;margin-left:0.3rem;">{row['rating']:.0f}★</b>
                                    <span style="background:rgba(34,197,94,0.15);color:#22C55E;border:1px solid rgba(34,197,94,0.3);padding:1px 6px;border-radius:3px;font-size:0.68rem;font-weight:700;margin-left:0.4rem;">NLP: POSITIVE</span>
                                </div>
                                <span style="font-size:0.72rem;color:#667085;">{str(row.get('date', ''))[:10]}</span>
                            </div>
                            <div style="color:#D0D5DD;font-size:0.82rem;line-height:1.4;margin:0.25rem 0;">"{str(row['text'])[:280]}…"</div>
                            <div style="font-size:0.72rem;color:#98A2B3;">
                                <b>Praised Aspect:</b> {intel['primary_aspect']} · <b>Observation:</b> Positive experience despite low star score (possible user error or shipping issue).
                            </div>
                        </div>
                        """)
                else:
                    st.caption("No records in this category.")
