import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from frontend.utils.api_client import api_client
from frontend.components.auth_view import render_auth_sidebar
from frontend.components.kpi_cards import render_kpi_cards
from frontend.components.charts import (
    render_sentiment_donut,
    render_sentiment_trends,
    render_aspect_breakdown,
)
from frontend.components.wordcloud_view import render_wordcloud_view
from frontend.components.live_tester import render_live_tester
from frontend.components.batch_upload import render_batch_upload
from frontend.components.model_benchmark_view import render_model_benchmark_view

# Page Config
st.set_page_config(
    page_title="Customer Sentiment Analytics (PRJ_382)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load Custom Glassmorphic CSS
css_path = BASE_DIR / "frontend" / "styles" / "custom.css"
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    # 1. Top Header Banner
    health_info = api_client.check_health()
    is_online = health_info.get("online", False)

    status_badge = (
        '<span style="background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">● FASTAPI BACKEND ONLINE</span>'
        if is_online
        else '<span style="background: rgba(244, 63, 94, 0.2); color: #FB7185; border: 1px solid #F43F5E; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600;">● OFFLINE (BOOTSTRAPPING)</span>'
    )

    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <h1 class="header-title">Customer Sentiment & Aspect Intelligence</h1>
                <div class="header-subtitle">
                    PRJ_382 Technical Specification • Dual-Path DistilBERT & Fast-Path Inference • KeyBERT Aspect Extraction
                </div>
            </div>
            <div>
                {status_badge}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Sidebar Filters & Authentication
    current_user = render_auth_sidebar()
    token = st.session_state.get("auth_token")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Global Filters")
    
    selected_category = st.sidebar.selectbox(
        "Filter Category",
        ["All", "Electronics", "Home & Kitchen", "Fashion", "Restaurants", "Hotels & Travel", "Automotive Services", "Beauty & Spas", "Sports & Fitness"],
        index=0,
    )
    
    selected_source = st.sidebar.selectbox(
        "Filter Data Source",
        ["All", "Amazon Reviews", "Yelp Reviews", "Manual", "CSV Upload"],
        index=0,
    )

    # 3. Main Multi-Tab Navigation
    tabs = st.tabs([
        "📊 Executive Overview",
        "🔍 Aspect & Topics",
        "⚡ Live Playground",
        "📥 Batch Ingestion",
        "🏆 Model Benchmarks",
        "📋 Feedback Explorer",
    ])

    # --- Cached API Wrappers (60s TTL to avoid re-fetch on every rerender) ---
    @st.cache_data(ttl=60, show_spinner=False)
    def _fetch_kpis(_category, _source):
        return api_client.get_kpis(category=_category, source=_source)

    @st.cache_data(ttl=60, show_spinner=False)
    def _fetch_distribution(_category, _source):
        return api_client.get_distribution(category=_category, source=_source)

    @st.cache_data(ttl=60, show_spinner=False)
    def _fetch_aspects(_limit, _category):
        return api_client.get_aspects(limit=_limit, category=_category)

    @st.cache_data(ttl=60, show_spinner=False)
    def _fetch_trends(_days):
        return api_client.get_trends(days=_days)

    # Fetch initial analytics (cached)
    kpis = _fetch_kpis(selected_category, selected_source)
    dist = _fetch_distribution(selected_category, selected_source)
    aspects = _fetch_aspects(15, selected_category)
    trends = _fetch_trends(30)
    feedbacks = api_client.get_feedback(
        limit=100,
        category=selected_category,
        source=selected_source,
        token=token,
    )

    # --- TAB 1: EXECUTIVE OVERVIEW ---
    with tabs[0]:
        st.markdown("### 📈 Executive Performance & KPI Metrics")
        render_kpi_cards(kpis)

        st.markdown("---")
        col_donut, col_trend = st.columns([1, 1.6])

        with col_donut:
            st.markdown("#### 🍩 Sentiment Polarity Share")
            render_sentiment_donut(dist)

        with col_trend:
            st.markdown("#### 📉 Sentiment Trajectory & Volume")
            render_sentiment_trends(trends)

        # Quick Highlights Bar
        st.markdown("#### 🌟 Top Extracted Product/Service Aspects")
        render_aspect_breakdown(aspects[:8])

    # --- TAB 2: ASPECT & TOPICS ---
    with tabs[1]:
        st.markdown("### 🔍 Aspect-Based Sentiment Analysis & Topics")
        col_asp, col_tab = st.columns([1.4, 1])

        with col_asp:
            st.markdown("#### 🏷️ Aspect Polarity Breakdown")
            render_aspect_breakdown(aspects)

        with col_tab:
            st.markdown("#### 📊 Aspect Frequency Table")
            if aspects:
                df_aspects = pd.DataFrame(aspects)
                st.dataframe(
                    df_aspects[["aspect", "count", "positive_count", "negative_count", "sentiment_ratio_positive"]],
                    column_config={
                        "aspect": "Aspect Name",
                        "count": "Mentions",
                        "positive_count": "Positive",
                        "negative_count": "Negative",
                        "sentiment_ratio_positive": st.column_config.ProgressColumn(
                            "Positive %", format="%f%%", min_value=0, max_value=100
                        ),
                    },
                    use_container_width=True,
                    height=360,
                )
            else:
                st.info("No aspects found for this filter.")

        st.markdown("---")
        render_wordcloud_view(feedbacks)

    # --- TAB 3: LIVE PLAYGROUND ---
    with tabs[2]:
        render_live_tester(token=token)

    # --- TAB 4: BATCH INGESTION ---
    with tabs[3]:
        render_batch_upload(token=token)

    # --- TAB 5: MODEL BENCHMARKS ---
    with tabs[4]:
        render_model_benchmark_view(token=token)

    # --- TAB 6: FEEDBACK EXPLORER ---
    with tabs[5]:
        st.markdown("### 📋 Customer Feedback Records Explorer")
        
        search_kw = st.text_input("🔍 Search Reviews by keyword:", placeholder="e.g. noise, battery, wait staff, crust...")
        
        filtered_records = api_client.get_feedback(
            skip=0,
            limit=200,
            category=selected_category,
            source=selected_source,
            search=search_kw if search_kw else None,
            token=token,
        )

        if filtered_records:
            df_feed = pd.DataFrame(filtered_records)
            st.dataframe(
                df_feed[[
                    "id", "source", "category", "review_text", "rating", "sentiment", "confidence", "model_used", "latency_ms", "aspects_raw", "created_at"
                ]],
                column_config={
                    "rating": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
                    "confidence": st.column_config.ProgressColumn("Confidence", format="%.2f", min_value=0.0, max_value=1.0),
                    "latency_ms": st.column_config.NumberColumn("Latency", format="%.1f ms"),
                    "created_at": "Timestamp",
                },
                use_container_width=True,
                height=450,
            )

            # Export to CSV option
            csv_data = df_feed.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Export Filtered Feedback as CSV",
                data=csv_data,
                file_name="sentiment_filtered_feedback.csv",
                mime="text/csv",
            )
        else:
            st.info("No feedback records matching the current query.")


if __name__ == "__main__":
    main()
