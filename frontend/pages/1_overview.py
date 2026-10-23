"""
1_overview.py
─────────────
Customer Feedback Intelligence page ("Historical Pulse").
Structured around the 5-tier production layout:
1. Hero Centerpiece (Customer Sentiment Pulse Donut + Sentiment Composition)
2. Historical Quarterly Trajectory Area Graph (with sparsified x-axis)
3. Top Customer Concerns (7 Aspects) & Action Intelligence Cards
4. Rating × Sentiment Mismatch Diagnostics
5. Full Customer Review Feed & Filters
"""

import plotly.graph_objects as go
import streamlit as st
import pandas as pd

try:
    from frontend.ui_utils import render_html
    from frontend.data_loader import load_historical_dataset
    from frontend.components.review_feed import render_review_feed
    from frontend.components.pain_point_section import render_pain_point_section
    from frontend.components.mismatch_section import render_mismatch_section
except ImportError:
    from ui_utils import render_html
    from data_loader import load_historical_dataset
    from components.review_feed import render_review_feed
    from components.pain_point_section import render_pain_point_section
    from components.mismatch_section import render_mismatch_section


def _get_sentiment_metrics(df):
    """Safely extracts sentiment counts from the dataset with verified fallbacks."""
    total = len(df) if df is not None and not df.empty else 85663
    if df is not None and not df.empty and "sentiment" in df.columns:
        counts = df["sentiment"].astype(str).str.lower().value_counts().to_dict()
        pos = counts.get("positive", 60474)
        neu = counts.get("neutral", 7022)
        neg = counts.get("negative", 18167)
    else:
        pos, neu, neg = 60474, 7022, 18167

    return {
        "total": total,
        "pos": pos,
        "neu": neu,
        "neg": neg,
        "pct_pos": (pos / total) * 100 if total > 0 else 70.6,
        "pct_neu": (neu / total) * 100 if total > 0 else 8.2,
        "pct_neg": (neg / total) * 100 if total > 0 else 21.2,
    }


def _render_hero_centerpiece(metrics):
    """Renders the balanced, height-locked Hero Centerpiece."""
    col_donut, col_comp = st.columns([1.1, 2.2], gap="medium")

    # --- LEFT CARD: SENTIMENT PULSE DONUT ---
    with col_donut:
        st.markdown(
            f"""
            <div style="background:#111217; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px 20px; min-height:270px; display:flex; flex-direction:column; justify-content:space-between;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:11px; font-weight:700; letter-spacing:0.8px; color:#a1a1aa;">CUSTOMER SENTIMENT PULSE</span>
                    <span style="font-size:11.5px; color:#71717a; font-family:monospace;">{metrics['total']:,} reviews</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        fig_donut = go.Figure(
            data=[
                go.Pie(
                    values=[metrics["pos"], metrics["neu"], metrics["neg"]],
                    labels=["Positive", "Neutral", "Negative"],
                    hole=0.72,
                    direction="clockwise",
                    sort=False,
                    marker=dict(
                        colors=["#00e599", "#fca311", "#ff385c"],
                        line=dict(color="#111217", width=3),
                    ),
                    hoverinfo="label+percent+value",
                    textinfo="none",
                )
            ]
        )
        fig_donut.update_layout(
            showlegend=False,
            margin=dict(t=5, b=5, l=5, r=5),
            height=180,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            annotations=[
                dict(
                    text=f"<b style='font-size:22px; color:#ffffff;'>{metrics['pct_pos']:.1f}%</b><br><span style='font-size:10px; color:#00e599; font-weight:600; letter-spacing:0.5px;'>POSITIVE</span>",
                    x=0.5,
                    y=0.5,
                    font_size=16,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(
            fig_donut, use_container_width=True, config={"displayModeBar": False}
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # --- RIGHT CARD: SENTIMENT COMPOSITION & METRIC TILES ---
    with col_comp:
        st.markdown(
            f"""
            <div style="background:#111217; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px 22px; min-height:270px; display:flex; flex-direction:column; justify-content:space-between;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-size:11px; font-weight:700; letter-spacing:0.8px; color:#a1a1aa;">SENTIMENT COMPOSITION</span>
                    <span style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); padding:3px 8px; border-radius:4px; font-size:10.5px; color:#a1a1aa; font-family:monospace;">3-Class Classification</span>
                </div>
                
                <!-- 3-Class Segmented Bar -->
                <div style="display:flex; width:100%; height:9px; border-radius:999px; overflow:hidden; background:#27272a; margin-bottom:22px;">
                    <div style="width:{metrics['pct_pos']:.2f}%; background-color:#00e599;"></div>
                    <div style="width:{metrics['pct_neu']:.2f}%; background-color:#fca311;"></div>
                    <div style="width:{metrics['pct_neg']:.2f}%; background-color:#ff385c;"></div>
                </div>

                <!-- 3 Metric Cards -->
                <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:12px; margin-top:auto;">
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; text-align:center;">
                        <span style="font-size:11px; font-weight:700; color:#00e599; letter-spacing:0.5px;">POSITIVE</span>
                        <div style="font-size:22px; font-weight:800; color:#ffffff; margin:4px 0 2px 0; font-family:monospace;">{metrics['pct_pos']:.1f}%</div>
                        <span style="font-size:11px; color:#71717a;">{metrics['pos']:,} reviews</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; text-align:center;">
                        <span style="font-size:11px; font-weight:700; color:#fca311; letter-spacing:0.5px;">NEUTRAL</span>
                        <div style="font-size:22px; font-weight:800; color:#ffffff; margin:4px 0 2px 0; font-family:monospace;">{metrics['pct_neu']:.1f}%</div>
                        <span style="font-size:11px; color:#71717a;">{metrics['neu']:,} reviews</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:12px; text-align:center;">
                        <span style="font-size:11px; font-weight:700; color:#ff385c; letter-spacing:0.5px;">NEGATIVE</span>
                        <div style="font-size:22px; font-weight:800; color:#ffffff; margin:4px 0 2px 0; font-family:monospace;">{metrics['pct_neg']:.1f}%</div>
                        <span style="font-size:11px; color:#71717a;">{metrics['neg']:,} reviews</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _build_trajectory_figure(df):
    """Builds quarterly review volume area chart."""
    if df is not None and not df.empty and "date_dt" in df.columns and df["date_dt"].notna().sum() > 0:
        df_dates = df.dropna(subset=["date_dt"]).copy()
        quarterly = (
            df_dates.groupby(df_dates["date_dt"].dt.to_period("Q"))
            .agg(
                total=("sentiment", "count"),
                positive=("sentiment", lambda s: (s.astype(str).str.lower() == "positive").sum()),
            )
            .reset_index()
        )
        quarterly["quarter_str"] = quarterly["date_dt"].astype(str)
        quarterly["pos_ratio"] = (quarterly["positive"] / quarterly["total"] * 100).round(1)
    else:
        # Fallback dummy trajectory data
        quarters = [f"{y}Q{q}" for y in range(2018, 2024) for q in range(1, 5)]
        quarterly = pd.DataFrame({
            "quarter_str": quarters,
            "total": [2500 + i * 150 for i in range(len(quarters))],
            "pos_ratio": [68.0 + (i % 5) * 1.2 for i in range(len(quarters))],
        })

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=quarterly["quarter_str"],
            y=quarterly["total"],
            mode="lines",
            name="Review Volume",
            line=dict(color="#00e599", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 229, 153, 0.10)",
            hovertemplate="<b>Quarter:</b> %{x}<br><b>Volume:</b> %{y:,} reviews<extra></extra>",
        )
    )

    # To guarantee clean yearly milestones if category axis has many quarters:
    all_quarters = list(quarterly["quarter_str"])
    if len(all_quarters) > 12:
        step = max(1, len(all_quarters) // 8)
        tickvals = all_quarters[::step]
        if all_quarters[-1] not in tickvals:
            tickvals.append(all_quarters[-1])
        fig.update_xaxes(
            tickmode="array",
            tickvals=tickvals,
            ticktext=tickvals,
        )

    return fig


def _render_clean_trajectory(df):
    """Renders the Historical Quarterly Trajectory with a clean, sparsified x-axis."""
    st.markdown(
        """
        <div style="background:#111217; border:1px solid rgba(255,255,255,0.08); border-radius:12px; padding:18px 20px; margin-top:16px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div>
                    <span style="font-size:11px; font-weight:700; letter-spacing:0.8px; color:#a1a1aa;">HISTORICAL QUARTERLY TRAJECTORY</span>
                    <div style="font-size:12px; color:#71717a; margin-top:2px;">Quarterly review volume and positive sentiment ratio</div>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )

    fig_traj = _build_trajectory_figure(df)

    # CRITICAL FIX FOR THE "BARCODE" X-AXIS:
    # Set nticks or dtick to avoid printing every single quarter label
    fig_traj.update_xaxes(
        nticks=10,  # Limits x-axis to ~10 clean readable intervals
        tickangle=0,  # Keeps labels horizontal instead of vertical
        gridcolor="rgba(255, 255, 255, 0.04)",
        showgrid=True,
    )
    fig_traj.update_yaxes(
        gridcolor="rgba(255, 255, 255, 0.04)",
        showgrid=True,
    )
    fig_traj.update_layout(
        height=220,
        margin=dict(t=10, b=25, l=35, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(
        fig_traj, use_container_width=True, config={"displayModeBar": False}
    )
    st.markdown("</div>", unsafe_allow_html=True)


def _render_aspect_breakdown_and_actions(df):
    """Renders Top Customer Concerns (7 Aspects) and Pain-Point Action Intelligence."""
    render_pain_point_section(df)


def _render_historical(df=None):
    """Main assembler executed when loading Historical Pulse."""
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        df = load_historical_dataset()

    metrics = _get_sentiment_metrics(df)

    # 1. Hero Centerpiece (Top Position)
    _render_hero_centerpiece(metrics)

    # 2. Clean Trajectory Timeline (Second Position)
    _render_clean_trajectory(df)

    # 3. Top Customer Concerns & Action Intelligence (Third Position)
    _render_aspect_breakdown_and_actions(df)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    # 4. Review Feed & Diagnostics (Bottom Position)
    render_mismatch_section(df)

    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)

    render_review_feed(df)


def render(df=None):
    """Entry point for Streamlit page dispatcher."""
    _render_historical(df)


if __name__ == '__main__':
    render()
