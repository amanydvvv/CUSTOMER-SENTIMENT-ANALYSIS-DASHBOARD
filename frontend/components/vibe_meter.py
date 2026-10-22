"""
vibe_meter.py
─────────────
Moctale-inspired visual analytics components for consumer intelligence dashboards.

Provides two premium Plotly chart functions:
  - render_purchase_meter(): 180-degree semicircular gauge showing purchase confidence
    with four colored tiers (Avoid / Mixed / Buy / Top Tier) and center annotation.
  - render_aspect_donut(): Dark-mode hollow donut chart showing aspect discussion
    distribution with dominant-aspect center annotation.
"""

import streamlit as st
import plotly.graph_objects as go

# Colour palette (Moctale-inspired)
_AVOID_COLOR   = "#ff385c"
_MIXED_COLOR   = "#fca311"
_BUY_COLOR     = "#00e599"
_TOPTIER_COLOR = "#b5179e"
_HIDDEN_COLOR  = "rgba(0,0,0,0)"

_ASPECT_PALETTE = [
    "#7C5CFF", "#22D3EE", "#00e599", "#fca311",
    "#ff385c", "#b5179e", "#38BDF8", "#F59E0B",
]


def _score_to_tier(score_pct):
    """Map a 0-100 confidence score to (tier_label, tier_color)."""
    if score_pct < 35:
        return "AVOID", _AVOID_COLOR
    elif score_pct < 55:
        return "MIXED", _MIXED_COLOR
    elif score_pct < 80:
        return "BUY", _BUY_COLOR
    else:
        return "TOP TIER", _TOPTIER_COLOR


def render_purchase_meter(
    score_pct,
    total_reviews,
    positive_count,
    distribution=None,
    height=300,
):
    """
    Render a semicircular Purchase Confidence Meter gauge.

    Parameters
    ----------
    score_pct       : 0-100 overall purchase confidence (e.g., positive %).
    total_reviews   : Total number of reviews in the current scope.
    positive_count  : Number of positive reviews.
    distribution    : Optional dict with keys 'avoid', 'mixed', 'buy', 'toptier'
                      and float values. If None, auto-derived from score_pct.
    height          : Chart height in pixels (default 300).
    """
    score_pct = max(0.0, min(100.0, float(score_pct)))
    tier_label, tier_color = _score_to_tier(score_pct)

    if not distribution:
        distribution = {
            "avoid":   round(100.0 - score_pct, 1),
            "mixed":   round(max(0.0, min(score_pct, 20.0)), 1),
            "buy":     round(max(0.0, min(score_pct - 20.0, 45.0)), 1),
            "toptier": round(max(0.0, score_pct - 65.0), 1),
        }
        total_d = sum(distribution.values())
        if total_d > 0:
            distribution = {k: round(v / total_d * 100, 1) for k, v in distribution.items()}

    avoid_v   = float(distribution.get("avoid", 25))
    mixed_v   = float(distribution.get("mixed", 20))
    buy_v     = float(distribution.get("buy", 40))
    toptier_v = float(distribution.get("toptier", 15))
    hidden_v  = avoid_v + mixed_v + buy_v + toptier_v

    labels = ["Avoid", "Mixed", "Buy", "Top Tier", ""]
    values = [avoid_v, mixed_v, buy_v, toptier_v, hidden_v]
    colors = [_AVOID_COLOR, _MIXED_COLOR, _BUY_COLOR, _TOPTIER_COLOR, _HIDDEN_COLOR]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.75,
                rotation=270,
                direction="clockwise",
                marker=dict(
                    colors=colors,
                    line=dict(color="#0D1017", width=3),
                ),
                textinfo="none",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                sort=False,
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        height=height,
        margin=dict(l=20, r=20, t=20, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=(
                    f"<b><span style='font-size:26px;color:{tier_color};'>"
                    f"{score_pct:.0f}%</span></b><br>"
                    f"<span style='font-size:11px;color:#98A2B3;'>"
                    f"{positive_count:,} / {total_reviews:,} Verified Reviews</span>"
                ),
                x=0.5, y=0.28,
                font=dict(family="Inter, sans-serif", size=14, color="#F5F7FA"),
                showarrow=False,
                align="center",
                xanchor="center",
            ),
        ],
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    pills_html = (
        "<div style='display:flex;justify-content:center;gap:0.75rem;flex-wrap:wrap;"
        "margin-top:-0.5rem;margin-bottom:0.75rem;'>"
        f"<span style='background:{_AVOID_COLOR}22;border:1px solid {_AVOID_COLOR}66;"
        f"color:{_AVOID_COLOR};font-size:0.72rem;font-weight:700;"
        f"padding:3px 12px;border-radius:20px;'>&#x2717; Avoid&nbsp;{avoid_v:.0f}%</span>"
        f"<span style='background:{_MIXED_COLOR}22;border:1px solid {_MIXED_COLOR}66;"
        f"color:{_MIXED_COLOR};font-size:0.72rem;font-weight:700;"
        f"padding:3px 12px;border-radius:20px;'>~ Mixed&nbsp;{mixed_v:.0f}%</span>"
        f"<span style='background:{_BUY_COLOR}22;border:1px solid {_BUY_COLOR}66;"
        f"color:{_BUY_COLOR};font-size:0.72rem;font-weight:700;"
        f"padding:3px 12px;border-radius:20px;'>&#x2713; Buy&nbsp;{buy_v:.0f}%</span>"
        f"<span style='background:{_TOPTIER_COLOR}22;border:1px solid {_TOPTIER_COLOR}66;"
        f"color:{_TOPTIER_COLOR};font-size:0.72rem;font-weight:700;"
        f"padding:3px 12px;border-radius:20px;'>&#9733; Top Tier&nbsp;{toptier_v:.0f}%</span>"
        "</div>"
        f"<div style='text-align:center;margin-bottom:0.5rem;'>"
        f"<span style='background:{tier_color}22;border:1px solid {tier_color}55;"
        f"color:{tier_color};font-size:0.8rem;font-weight:800;"
        f"padding:4px 18px;border-radius:20px;letter-spacing:0.06em;'>"
        f"VERDICT: {tier_label}</span></div>"
    )
    st.markdown(pills_html, unsafe_allow_html=True)


def render_aspect_donut(
    aspect_data,
    dominant_aspect,
    dominant_pct,
    height=280,
):
    """
    Render a dark-mode hollow donut showing aspect discussion distribution.

    Parameters
    ----------
    aspect_data     : dict mapping aspect name to percentage (0-100).
                      E.g. {"Quality": 38.2, "Value": 21.5, "Delivery": 18.0}
    dominant_aspect : Label for the most-discussed aspect (shown in center).
    dominant_pct    : Percentage of the dominant aspect (0-100).
    height          : Chart height in pixels (default 280).
    """
    if not aspect_data:
        aspect_data = {
            "Quality": 38.0,
            "Value": 22.0,
            "Delivery": 18.0,
            "Support": 12.0,
            "Packaging": 10.0,
        }
        dominant_aspect = "Quality"
        dominant_pct = 38.0

    labels = list(aspect_data.keys())
    values = list(aspect_data.values())
    colors = list(_ASPECT_PALETTE[: len(labels)])
    while len(colors) < len(labels):
        colors.append("#667085")

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.68,
                marker=dict(
                    colors=colors,
                    line=dict(color="#0D1017", width=2),
                ),
                textinfo="none",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
            )
        ]
    )

    dominant_color = colors[labels.index(dominant_aspect)] if dominant_aspect in labels else "#7C5CFF"

    fig.update_layout(
        showlegend=True,
        legend=dict(
            font=dict(color="#98A2B3", size=11, family="Inter"),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            orientation="v",
            x=1.02, y=0.5,
        ),
        height=height,
        margin=dict(l=10, r=120, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=(
                    "<span style='font-size:9px;color:#667085;'>TOP ASPECT</span><br>"
                    f"<b><span style='font-size:15px;color:{dominant_color};'>"
                    f"{dominant_aspect}</span></b><br>"
                    f"<span style='font-size:12px;color:#F5F7FA;font-weight:700;'>"
                    f"{dominant_pct:.1f}%</span>"
                ),
                x=0.38, y=0.5,
                font=dict(family="Inter, sans-serif", size=12, color="#F5F7FA"),
                showarrow=False,
                align="center",
                xanchor="center",
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
