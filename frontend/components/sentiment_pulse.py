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
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1rem 1.15rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
                    CUSTOMER SENTIMENT PULSE
                </span>
                <span style="font-size:0.7rem;color:#98A2B3;font-family:'JetBrains Mono',monospace;">
                    {total_active:,} reviews
                </span>
            </div>
        </div>
        """)

        fig_donut = go.Figure(data=[go.Pie(
            labels=["Positive", "Neutral", "Negative"],
            values=[pos_count, neu_count, neg_count],
            hole=0.68,
            marker=dict(colors=["#22C55E", "#F59E0B", "#EF4444"], line=dict(color="#11151D", width=2)),
            textinfo="none",
            hoverinfo="label+percent+value",
            sort=False,
        )])
        fig_donut.update_layout(
            showlegend=False,
            height=160,
            margin=dict(l=10, r=10, t=5, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b style='font-size:22px;color:#F5F7FA;'>{pos_pct:.1f}%</b><br><span style='font-size:10px;color:#22C55E;font-weight:700;'>POSITIVE</span>",
                    x=0.5, y=0.5,
                    font=dict(family="Inter, sans-serif"),
                    showarrow=False,
                )
            ]
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})

    # ── RIGHT: SENTIMENT COMPOSITION ────────────────────────────────────────────
    with col_right:
        render_html(f"""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1rem 1.25rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.65rem;">
                <span style="font-size:0.72rem;font-weight:700;color:#98A2B3;text-transform:uppercase;letter-spacing:0.08em;">
                    SENTIMENT COMPOSITION
                </span>
                <span style="font-size:0.7rem;color:#22D3EE;background:rgba(34,211,238,0.1);padding:2px 7px;border-radius:4px;border:1px solid rgba(34,211,238,0.25);">
                    3-Class Classification
                </span>
            </div>

            <div style="display:flex;height:8px;border-radius:4px;overflow:hidden;background:#1E2533;margin-bottom:0.85rem;">
                <div style="width:{pos_pct}%;background:#22C55E;"></div>
                <div style="width:{neu_pct}%;background:#F59E0B;"></div>
                <div style="width:{neg_pct}%;background:#EF4444;"></div>
            </div>

            <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:0.65rem;">
                <div style="background:#151A24;border:1px solid rgba(34,197,94,0.25);border-radius:6px;padding:0.65rem 0.75rem;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:#22C55E;text-transform:uppercase;">Positive</div>
                    <div style="font-size:1.3rem;font-weight:800;color:#F5F7FA;margin:0.1rem 0;">{pos_pct:.1f}%</div>
                    <div style="font-size:0.7rem;color:#98A2B3;">{pos_count:,} reviews</div>
                </div>

                <div style="background:#151A24;border:1px solid rgba(245,158,11,0.25);border-radius:6px;padding:0.65rem 0.75rem;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:#F59E0B;text-transform:uppercase;">Neutral</div>
                    <div style="font-size:1.3rem;font-weight:800;color:#F5F7FA;margin:0.1rem 0;">{neu_pct:.1f}%</div>
                    <div style="font-size:0.7rem;color:#98A2B3;">{neu_count:,} reviews</div>
                </div>

                <div style="background:#151A24;border:1px solid rgba(239,68,68,0.25);border-radius:6px;padding:0.65rem 0.75rem;text-align:center;">
                    <div style="font-size:0.68rem;font-weight:700;color:#EF4444;text-transform:uppercase;">Negative</div>
                    <div style="font-size:1.3rem;font-weight:800;color:#F5F7FA;margin:0.1rem 0;">{neg_pct:.1f}%</div>
                    <div style="font-size:0.7rem;color:#98A2B3;">{neg_count:,} reviews</div>
                </div>
            </div>
        </div>
        """)
