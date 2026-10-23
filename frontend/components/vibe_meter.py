"""
vibe_meter.py
─────────────
Moctale-inspired visual analytics components for consumer intelligence dashboards.

Provides two clean, production-grade Plotly chart functions:
  - render_purchase_meter(): 180-degree semicircular gauge showing purchase confidence
    with four colored tiers (Avoid / Mixed / Buy / Top Tier) and center annotation.
  - render_aspect_donut(): Dark-mode hollow donut chart showing aspect discussion
    distribution with dominant-aspect center annotation.
"""

import streamlit as st
import plotly.graph_objects as go

# Functional Color Palette (Moctale-inspired, strict semantic rules)
_AVOID_COLOR   = "#ff385c"  # Crimson
_MIXED_COLOR   = "#fca311"  # Amber
_BUY_COLOR     = "#00e599"  # Neon Emerald
_TOPTIER_COLOR = "#b5179e"  # Vivid Purple (reserved exclusively for Top Tier)
_HIDDEN_COLOR  = "rgba(0,0,0,0)"

_ASPECT_PALETTE = [
    "#00e599", "#38bdf8", "#fca311", "#9ca3af",
    "#ff385c", "#6b7280", "#4b5563", "#d1d5db"
]


def _score_to_tier(score_pct: float):
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
    score_pct: float,
    total_reviews: int,
    positive_count: int,
    distribution: dict = None,
    height: int = 280,
):
    """
    Render a semicircular Purchase Confidence Meter gauge.

    Parameters
    ----------
    score_pct       : 0-100 overall purchase confidence (e.g., positive %).
    total_reviews   : Total number of reviews in current scope.
    positive_count  : Number of positive reviews.
    distribution    : Optional dict with keys 'avoid', 'mixed', 'buy', 'toptier'
                      and float values. If None, auto-derived from score_pct.
    height          : Chart height in pixels (default 280).
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
                hole=0.76,
                rotation=270,
                direction="clockwise",
                marker=dict(
                    colors=colors,
                    line=dict(color="#111317", width=2),
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
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=(
                    f"<b><span style='font-size:30px;color:{tier_color};'>"
                    f"{score_pct:.0f}%</span></b><br>"
                    f"<span style='font-size:11px;color:#9ca3af;font-weight:400;'>"
                    f"{positive_count:,} / {total_reviews:,} Verified Reviews</span>"
                ),
                x=0.5, y=0.28,
                font=dict(family="Inter, -apple-system, sans-serif", size=13, color="#f3f4f6"),
                showarrow=False,
                align="center",
                xanchor="center",
            ),
        ],
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})

    pills_html = (
        "<div style='display:flex;justify-content:center;gap:0.5rem;flex-wrap:wrap;"
        "margin-top:-0.5rem;margin-bottom:0.6rem;'>"
        f"<span style='background:{_AVOID_COLOR}15;border:1px solid {_AVOID_COLOR}35;"
        f"color:{_AVOID_COLOR};font-size:0.72rem;font-weight:500;"
        f"padding:3px 10px;border-radius:4px;'>Avoid {avoid_v:.0f}%</span>"
        f"<span style='background:{_MIXED_COLOR}15;border:1px solid {_MIXED_COLOR}35;"
        f"color:{_MIXED_COLOR};font-size:0.72rem;font-weight:500;"
        f"padding:3px 10px;border-radius:4px;'>Mixed {mixed_v:.0f}%</span>"
        f"<span style='background:{_BUY_COLOR}15;border:1px solid {_BUY_COLOR}35;"
        f"color:{_BUY_COLOR};font-size:0.72rem;font-weight:500;"
        f"padding:3px 10px;border-radius:4px;'>Buy {buy_v:.0f}%</span>"
        f"<span style='background:{_TOPTIER_COLOR}15;border:1px solid {_TOPTIER_COLOR}35;"
        f"color:{_TOPTIER_COLOR};font-size:0.72rem;font-weight:500;"
        f"padding:3px 10px;border-radius:4px;'>Top Tier {toptier_v:.0f}%</span>"
        "</div>"
        f"<div style='text-align:center;margin-bottom:0.25rem;'>"
        f"<span style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);"
        f"color:{tier_color};font-size:0.75rem;font-weight:600;"
        f"padding:3px 14px;border-radius:4px;letter-spacing:0.06em;'>"
        f"VERDICT: {tier_label}</span></div>"
    )
    st.markdown(pills_html, unsafe_allow_html=True)


def render_aspect_donut(
    aspect_data: dict,
    dominant_aspect: str = None,
    dominant_pct: float = None,
    height: int = 280,
):
    """
    Render a clean dark-mode hollow donut showing aspect discussion distribution.

    Parameters
    ----------
    aspect_data     : dict mapping aspect name to percentage (0-100).
    dominant_aspect : Label for the most-discussed aspect (shown in center).
    dominant_pct    : Percentage of dominant aspect (0-100).
    height          : Chart height in pixels (default 280).
    """
    if not aspect_data:
        aspect_data = {
            "Build Quality": 42.0,
            "Price & Value": 24.0,
            "Delivery": 16.0,
            "Customer Support": 10.0,
            "Packaging": 8.0,
        }

    if dominant_aspect is None or dominant_pct is None:
        dominant_aspect = max(aspect_data.items(), key=lambda x: x[1])[0]
        dominant_pct = aspect_data[dominant_aspect]

    labels = list(aspect_data.keys())
    values = list(aspect_data.values())
    colors = list(_ASPECT_PALETTE[: len(labels)])
    while len(colors) < len(labels):
        colors.append("#6b7280")

    # Split multi-word aspects across lines if long to avoid donut text overflow
    if len(dominant_aspect) > 9 and " " in dominant_aspect:
        words = dominant_aspect.split(" ")
        mid = len(words) // 2
        formatted_aspect = " ".join(words[:mid]) + "<br>" + " ".join(words[mid:])
    else:
        formatted_aspect = dominant_aspect

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.72,
                domain=dict(x=[0.0, 0.84], y=[0.0, 1.0]),
                marker=dict(
                    colors=colors,
                    line=dict(color="#111317", width=2),
                ),
                textinfo="none",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
                sort=False,
            )
        ]
    )

    dominant_color = colors[labels.index(dominant_aspect)] if dominant_aspect in labels else "#00e599"

    fig.update_layout(
        showlegend=True,
        legend=dict(
            font=dict(color="#9ca3af", size=10, family="Inter, -apple-system, sans-serif"),
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            orientation="v",
            x=0.86, y=0.5,
            xanchor="left",
            yanchor="middle",
        ),
        height=height,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=(
                    "<span style='font-size:9px;color:#9ca3af;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;'>Top Aspect</span><br>"
                    f"<b><span style='font-size:13px;color:#ffffff;line-height:1.25;'>"
                    f"{formatted_aspect}</span></b><br>"
                    f"<span style='font-size:12px;color:{dominant_color};font-weight:600;font-family:JetBrains Mono,monospace;'>"
                    f"{dominant_pct:.1f}%</span>"
                ),
                x=0.42, y=0.5,
                font=dict(family="Inter, -apple-system, sans-serif", size=12, color="#f3f4f6"),
                showarrow=False,
                align="center",
                xanchor="center",
                yanchor="middle",
            )
        ],
    )

    st.plotly_chart(fig, width='stretch', config={"displayModeBar": False})
