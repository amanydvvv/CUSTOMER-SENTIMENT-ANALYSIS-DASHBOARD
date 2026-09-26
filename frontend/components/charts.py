import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from typing import Dict, List, Any


def render_sentiment_donut(dist: Dict[str, Any]):
    """Render high-contrast, glowing donut chart for sentiment polarity."""
    pos = dist.get("positive", 0)
    neu = dist.get("neutral", 0)
    neg = dist.get("negative", 0)
    total = pos + neu + neg

    if total == 0:
        st.info("No sentiment data available for this filter.")
        return

    labels = ["Positive", "Neutral", "Negative"]
    values = [pos, neu, neg]
    colors = ["#10B981", "#38BDF8", "#F43F5E"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.65,
                marker=dict(colors=colors, line=dict(color="#0B0F19", width=2)),
                textinfo="label+percent",
                hoverinfo="label+value+percent",
                textfont=dict(size=14, family="Outfit, sans-serif", color="#FFFFFF"),
            )
        ]
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(family="Outfit", color="#94A3B8", size=12),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=40),
        height=320,
        annotations=[
            dict(
                text=f"<b>{total:,}</b><br><span style='font-size:12px;color:#94A3B8;'>Reviews</span>",
                x=0.5,
                y=0.5,
                font_size=20,
                font_family="Outfit",
                font_color="#F1F5F9",
                showarrow=False,
            )
        ],
    )

    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_trends(trend_data: List[Dict[str, Any]]):
    """Render time-series trendline of positive, neutral, and negative sentiment."""
    if not trend_data:
        st.info("No trend data available.")
        return

    dates = [d["date"] for d in trend_data]
    pos = [d["positive"] for d in trend_data]
    neu = [d["neutral"] for d in trend_data]
    neg = [d["negative"] for d in trend_data]
    net_scores = [d.get("sentiment_score", 0.0) for d in trend_data]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=pos,
            name="Positive",
            mode="lines+markers",
            line=dict(color="#10B981", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(16, 185, 129, 0.08)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=neu,
            name="Neutral",
            mode="lines+markers",
            line=dict(color="#38BDF8", width=2),
            marker=dict(size=5),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=neg,
            name="Negative",
            mode="lines+markers",
            line=dict(color="#F43F5E", width=3),
            marker=dict(size=6),
            fill="tozeroy",
            fillcolor="rgba(244, 63, 94, 0.08)",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94A3B8", size=12),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            color="#94A3B8",
            tickfont=dict(family="Outfit"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            color="#94A3B8",
            tickfont=dict(family="Outfit"),
            title="Volume",
        ),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_aspect_breakdown(aspects_data: List[Dict[str, Any]]):
    """Render stacked horizontal bar chart showing positive vs negative sentiment per aspect."""
    if not aspects_data:
        st.info("No aspect data found.")
        return

    # Sort aspects by count descending
    aspects = [a["aspect"].title() for a in aspects_data][::-1]
    pos_counts = [a["positive_count"] for a in aspects_data][::-1]
    neu_counts = [a["neutral_count"] for a in aspects_data][::-1]
    neg_counts = [a["negative_count"] for a in aspects_data][::-1]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=aspects,
            x=pos_counts,
            name="Positive Mentions",
            orientation="h",
            marker=dict(color="#10B981", line=dict(color="rgba(0,0,0,0.2)", width=1)),
        )
    )

    fig.add_trace(
        go.Bar(
            y=aspects,
            x=neu_counts,
            name="Neutral Mentions",
            orientation="h",
            marker=dict(color="#38BDF8", line=dict(color="rgba(0,0,0,0.2)", width=1)),
        )
    )

    fig.add_trace(
        go.Bar(
            y=aspects,
            x=neg_counts,
            name="Negative Mentions",
            orientation="h",
            marker=dict(color="#F43F5E", line=dict(color="rgba(0,0,0,0.2)", width=1)),
        )
    )

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=30, b=20),
        height=380,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#94A3B8", size=12),
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            color="#94A3B8",
            title="Total Mentions",
        ),
        yaxis=dict(
            showgrid=False,
            color="#F1F5F9",
            tickfont=dict(family="Outfit", size=12),
        ),
    )

    st.plotly_chart(fig, use_container_width=True)
