"""
sentiment_pulse.py
──────────────────
Customer Sentiment Pulse & Sentiment Composition component.
Visualizes aggregate sentiment with dynamic data-driven business interpretation.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend.ui_utils import render_html


def render_sentiment_pulse(df_filtered: pd.DataFrame, df_total: pd.DataFrame = None):
    """
    Renders Customer Sentiment Pulse (Left) and Sentiment Composition (Right)
    in a clean, coherent card layout with transparent Plotly charts.
    """
    total_active = len(df_filtered)
    if total_active == 0:
        st.warning("No reviews match the current filter selection.")
        return

    pos_count = int((df_filtered["sentiment"] == "positive").sum())
    neu_count = int((df_filtered["sentiment"] == "neutral").sum())
    neg_count = int((df_filtered["sentiment"] == "negative").sum())

    pos_pct = (pos_count / total_active) * 100
    neu_pct = (neu_count / total_active) * 100
    neg_pct = (neg_count / total_active) * 100

    col_left, col_right = st.columns([1.1, 1.9])

    # ── LEFT: CUSTOMER SENTIMENT PULSE ──────────────────────────────────────────
    with col_left:
        render_html(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                    CUSTOMER SENTIMENT PULSE
                </span>
                <span style="font-size:11px;color:#6b7280;font-family:monospace;">
                    {total_active:,} reviews
                </span>
            </div>
        </div>
        """)

        fig_donut = go.Figure(data=[go.Pie(
            labels=["Positive", "Neutral", "Negative"],
            values=[pos_count, neu_count, neg_count],
            hole=0.68,
            marker=dict(colors=["#10b981", "#f59e0b", "#ef4444"], line=dict(color="#111317", width=2)),
            textinfo="none",
            hoverinfo="label+percent+value",
            sort=False,
        )])
        fig_donut.update_layout(
            showlegend=False,
            height=160,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b style='font-size:22px;color:#ffffff;'>{pos_pct:.1f}%</b><br><span style='font-size:10px;color:#10b981;font-weight:700;'>POSITIVE</span>",
                    x=0.5, y=0.5,
                    font=dict(family="Inter, sans-serif"),
                    showarrow=False,
                )
            ]
        )
        st.plotly_chart(fig_donut, width='stretch', config={"displayModeBar": False})

    # ── RIGHT: SENTIMENT COMPOSITION ────────────────────────────────────────────
    with col_right:
        render_html(f"""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                <span style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
                    SENTIMENT COMPOSITION
                </span>
                <span style="font-size:11px;color:#9ca3af;background:rgba(255,255,255,0.05);padding:2px 8px;border-radius:4px;border:1px solid rgba(255,255,255,0.07);">
                    3-Class Classification
                </span>
            </div>

            <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;background:#1e2533;margin-bottom:14px;">
                <div style="width:{pos_pct}%;background:#10b981;"></div>
                <div style="width:{neu_pct}%;background:#f59e0b;"></div>
                <div style="width:{neg_pct}%;background:#ef4444;"></div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;">
                <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;text-align:center;">
                    <div style="font-size:11px;font-weight:600;color:#10b981;text-transform:uppercase;">Positive</div>
                    <div style="font-size:22px;font-weight:700;color:#ffffff;margin:2px 0;">{pos_pct:.1f}%</div>
                    <div style="font-size:11px;color:#6b7280;">{pos_count:,} reviews</div>
                </div>

                <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;text-align:center;">
                    <div style="font-size:11px;font-weight:600;color:#f59e0b;text-transform:uppercase;">Neutral</div>
                    <div style="font-size:22px;font-weight:700;color:#ffffff;margin:2px 0;">{neu_pct:.1f}%</div>
                    <div style="font-size:11px;color:#6b7280;">{neu_count:,} reviews</div>
                </div>

                <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;text-align:center;">
                    <div style="font-size:11px;font-weight:600;color:#ef4444;text-transform:uppercase;">Negative</div>
                    <div style="font-size:22px;font-weight:700;color:#ffffff;margin:2px 0;">{neg_pct:.1f}%</div>
                    <div style="font-size:11px;color:#6b7280;">{neg_count:,} reviews</div>
                </div>
            </div>
        </div>
        """)
