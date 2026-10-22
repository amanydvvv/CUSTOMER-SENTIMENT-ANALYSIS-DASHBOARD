"""
mismatch_section.py
───────────────────
Rating vs. AI Sentiment Mismatch Analytics component.
Detects discrepancies where numerical star ratings diverge from textual sentiment.
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
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
            <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                RATING × SENTIMENT MISMATCH
            </span>
            <span style="font-size:11px;color:#f59e0b;background:rgba(245,158,11,0.12);padding:2px 8px;border-radius:4px;border:1px solid rgba(245,158,11,0.3);font-weight:600;">
                {total_mismatches:,} Discrepancies ({mismatch_rate:.2f}%)
            </span>
        </div>
        <div style="font-size:13px;color:#d1d5db;margin-bottom:14px;">
            Reviews where customer star rating and review text express conflicting signals.
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px;">
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px;">
                <div style="font-size:11px;color:#ef4444;text-transform:uppercase;font-weight:600;">4–5 ★ + Negative Text</div>
                <div style="font-size:22px;font-weight:700;color:#ffffff;margin:4px 0 2px;">{len(over_rated):,} reviews</div>
                <div style="font-size:11px;color:#9ca3af;line-height:1.4;">
                    Customers gave high star ratings but reported critical complaints in text.
                </div>
            </div>
            <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px;">
                <div style="font-size:11px;color:#10b981;text-transform:uppercase;font-weight:600;">1–2 ★ + Positive Text</div>
                <div style="font-size:22px;font-weight:700;color:#ffffff;margin:4px 0 2px;">{len(under_rated):,} reviews</div>
                <div style="font-size:11px;color:#9ca3af;line-height:1.4;">
                    Customers gave low star ratings but used favorable language in review body.
                </div>
            </div>
        </div>

        <div style="background:#181b21;border-left:3px solid #f59e0b;border-radius:0 4px 4px 0;padding:10px 14px;font-size:12px;color:#9ca3af;line-height:1.45;">
            <b style="color:#ffffff;">Diagnostic Value:</b> Highlights silent friction where customers leave positive star ratings despite reporting severe product flaws.
        </div>
    </div>
    """)

    if total_mismatches > 0:
        with st.expander(f"Inspect Mismatch Samples ({total_mismatches:,} reviews)", expanded=False):
            tab_over, tab_under = st.tabs([
                f"High Star + Negative Text ({len(over_rated):,})",
                f"Low Star + Positive Text ({len(under_rated):,})"
            ])

            with tab_over:
                if len(over_rated) > 0:
                    for _, row in over_rated.head(4).iterrows():
                        intel = extract_aspects_and_issues(str(row["text"]), sentiment="negative", rating=row["rating"])
                        render_html(f"""
                        <div style="background:#181b21;border:1px solid rgba(239,68,68,0.2);border-radius:6px;padding:12px;margin-bottom:8px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                                <div>
                                    <span style="color:#f59e0b;font-size:12px;">{row['rating']:.1f} / 5.0</span>
                                    <b style="color:#ffffff;margin-left:6px;">{row['rating']:.0f}★</b>
                                    <span style="background:rgba(239,68,68,0.15);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;margin-left:8px;">NLP: NEGATIVE</span>
                                </div>
                                <span style="font-size:11px;color:#6b7280;">{str(row.get('date', ''))[:10]}</span>
                            </div>
                            <div style="color:#d1d5db;font-size:12px;line-height:1.45;margin:4px 0;">"{str(row['text'])[:280]}…"</div>
                            <div style="font-size:11px;color:#9ca3af;">
                                <b>Detected Friction:</b> {intel['primary_aspect']} ({intel['issue']}) · <b>Action:</b> {intel['suggested_action']}
                            </div>
                        </div>
                        """)
                else:
                    st.info("No matching reviews in this category.")

            with tab_under:
                if len(under_rated) > 0:
                    for _, row in under_rated.head(4).iterrows():
                        intel = extract_aspects_and_issues(str(row["text"]), sentiment="positive", rating=row["rating"])
                        render_html(f"""
                        <div style="background:#181b21;border:1px solid rgba(16,185,129,0.2);border-radius:6px;padding:12px;margin-bottom:8px;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                                <div>
                                    <span style="color:#f59e0b;font-size:12px;">{row['rating']:.1f} / 5.0</span>
                                    <b style="color:#ffffff;margin-left:6px;">{row['rating']:.0f}★</b>
                                    <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:1px 6px;border-radius:3px;font-size:10px;font-weight:700;margin-left:8px;">NLP: POSITIVE</span>
                                </div>
                                <span style="font-size:11px;color:#6b7280;">{str(row.get('date', ''))[:10]}</span>
                            </div>
                            <div style="color:#d1d5db;font-size:12px;line-height:1.45;margin:4px 0;">"{str(row['text'])[:280]}…"</div>
                            <div style="font-size:11px;color:#9ca3af;">
                                <b>Identified Sentiment:</b> Favorable customer review text despite 1-2 star rating.
                            </div>
                        </div>
                        """)
                else:
                    st.info("No matching reviews in this category.")
