import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from frontend.api_client import (
    load_stats,
    load_sentiment_distribution,
    load_rating_distribution,
    load_product_stats,
)


def render_metric_card(icon_svg: str, value: str, label: str, trend: str = None, trend_class: str = None):
    trend_html = ""
    if trend and trend_class:
        trend_html = f'<div class="metric-trend {trend_class}">{trend}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon" style="background: var(--primary-light); color: var(--primary);">
            {icon_svg}
        </div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Overview</h1>
        <p class="page-subtitle">Dataset insights and sentiment distribution at a glance</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading dashboard data..."):
        stats = load_stats()
        sentiment_dist = load_sentiment_distribution()
        rating_dist = load_rating_distribution()
        product_stats = load_product_stats()

    if not stats:
        st.error("Unable to load data. Please ensure the backend is running.")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card(
            icon_svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
            value=f"{stats.get('total_reviews', 0):,}",
            label="Total Reviews",
            trend=f"+{stats.get('reviews_today', 0)} today",
            trend_class="trend-positive",
        )

    with col2:
        render_metric_card(
            icon_svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>',
            value=f"{stats.get('positive_pct', 0):.1f}%",
            label="Positive Sentiment",
            trend="Dominant class",
            trend_class="trend-positive",
        )

    with col3:
        render_metric_card(
            icon_svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>',
            value=f"{stats.get('avg_rating', 0):.1f}/5.0",
            label="Average Rating",
            trend="High satisfaction",
            trend_class="trend-positive",
        )

    with col4:
        render_metric_card(
            icon_svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>',
            value=f"{stats.get('unique_products', 0)}",
            label="Products Analyzed",
            trend=f"{stats.get('categories', 0)} categories",
            trend_class="trend-neutral",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Sentiment Distribution", "⭐ Rating Analysis", "🏷️ Top Products"])

    with tab1:
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Sentiment Distribution</h3>', unsafe_allow_html=True)

            if sentiment_dist:
                df_sentiment = pd.DataFrame(sentiment_dist)
                fig = px.pie(
                    df_sentiment,
                    values="count",
                    names="sentiment",
                    color="sentiment",
                    color_discrete_map={
                        "positive": "#22c55e",
                        "negative": "#ef4444",
                        "neutral": "#f59e0b",
                    },
                    hole=0.55,
                )
                fig.update_traces(
                    textposition="inside",
                    textinfo="percent+label",
                    textfont_size=13,
                    textfont_color="white",
                    textfont_family="Inter",
                    marker=dict(line=dict(color="white", width=2)),
                    pull=[0.05, 0, 0],
                )
                fig.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.15,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12, family="Inter"),
                    ),
                    margin=dict(t=10, b=10, l=10, r=10),
                    font=dict(family="Inter"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h3 class="chart-title">Sentiment Counts</h3>', unsafe_allow_html=True)

            if sentiment_dist:
                for item in sentiment_dist:
                    sentiment = item["sentiment"]
                    count = item["count"]
                    pct = item["percentage"]
                    color_class = {
                        "positive": "sentiment-positive",
                        "negative": "sentiment-negative",
                        "neutral": "sentiment-neutral",
                    }.get(sentiment, "sentiment-neutral")

                    st.markdown(f"""
                    <div style="padding: 0.75rem 0; border-bottom: 1px solid var(--border);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                            <span class="sentiment-badge {color_class}">{sentiment}</span>
                            <span style="font-weight: 600; color: var(--text-primary);">{count:,}</span>
                        </div>
                        <div style="height: 6px; background: var(--bg-tertiary); border-radius: 3px; overflow: hidden;">
                            <div style="width: {pct}%; height: 100%; background: {'#22c55e' if sentiment == 'positive' else '#ef4444' if sentiment == 'negative' else '#f59e0b'}; border-radius: 3px; transition: width 0.5s ease;"></div>
                        </div>
                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem; text-align: right;">{pct:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Rating Distribution by Sentiment</h3>', unsafe_allow_html=True)

        if rating_dist:
            df_rating = pd.DataFrame(rating_dist)
            fig = px.bar(
                df_rating,
                x="rating",
                y="count",
                color="sentiment",
                color_discrete_map={
                    "positive": "#22c55e",
                    "negative": "#ef4444",
                    "neutral": "#f59e0b",
                },
                barmode="group",
            )
            fig.update_layout(
                xaxis_title="Rating",
                yaxis_title="Number of Reviews",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12, family="Inter"),
                ),
                margin=dict(t=40, b=40, l=40, r=40),
                font=dict(family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor=var_border if (var_border := "var(--border)") else "#e2e8f0"),
                yaxis=dict(gridcolor=var_border if (var_border := "var(--border)") else "#e2e8f0"),
            )
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Top Products by Review Volume</h3>', unsafe_allow_html=True)

        if product_stats:
            df_products = pd.DataFrame(product_stats).head(15)
            fig = px.bar(
                df_products,
                x="review_count",
                y="product_name",
                orientation="h",
                color="avg_rating",
                color_continuous_scale=["#ef4444", "#f59e0b", "#22c55e"],
                range_color=[1, 5],
                text="review_count",
            )
            fig.update_traces(textposition="outside", textfont_size=11, textfont_family="Inter")
            fig.update_layout(
                xaxis_title="Number of Reviews",
                yaxis_title="",
                yaxis=dict(autorange="reversed"),
                coloraxis_colorbar=dict(title="Avg Rating", thickness=10, len=0.7),
                margin=dict(t=10, b=40, l=10, r=10),
                font=dict(family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown("### Product Details")
            display_df = df_products[["product_name", "review_count", "avg_rating", "sentiment_distribution"]].copy()
            display_df.columns = ["Product", "Reviews", "Avg Rating", "Sentiment Breakdown"]
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Product": st.column_config.TextColumn(width="medium"),
                    "Reviews": st.column_config.NumberColumn(format="%,d"),
                    "Avg Rating": st.column_config.NumberColumn(format="%.2f"),
                    "Sentiment Breakdown": st.column_config.TextColumn(width="large"),
                },
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📋 Dataset Summary", expanded=False):
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Data Quality**")
            st.write(f"• Total rows: {stats.get('total_reviews', 0):,}")
            st.write(f"• Missing reviews handled: {stats.get('missing_reviews', 0):,}")
            st.write(f"• Duplicates removed: {stats.get('duplicates_removed', 0):,}")
            st.write(f"• Unique products: {stats.get('unique_products', 0)}")

        with col_b:
            st.markdown("**Preprocessing**")
            st.write("• TF-IDF: n-grams (1,2), 10k features")
            st.write("• Stopwords: NLTK English (preserving negations)")
            st.write("• Text cleaning: HTML, URLs, special chars removed")
            st.write("• Negation handling: Expanded contractions")