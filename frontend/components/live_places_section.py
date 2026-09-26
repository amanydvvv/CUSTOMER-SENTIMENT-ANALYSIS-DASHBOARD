"""
live_places_section.py
──────────────────────
Google Places API live review analysis component.
Handles place text search, review ingestion, normalization into unified schema,
sentiment & aspect inference with our saved ML models, and interactive dashboard rendering.
"""

import streamlit as st
import pandas as pd
from frontend.api_client import search_google_places, analyze_google_place_reviews
from frontend.components.sentiment_pulse import render_sentiment_pulse
from frontend.components.pain_point_section import render_pain_point_section
from frontend.components.mismatch_section import render_mismatch_section
from frontend.components.review_feed import render_review_feed
from frontend.components.aspect_analyzer import extract_aspects_and_issues


def render_live_places_section():
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="background: #2563eb; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">LIVE API</span>
            <h3 style="font-size: 1.25rem; font-weight: 700; color: #0f172a; margin: 0;">
                Google Places Live Feedback Intelligence
            </h3>
        </div>
        <p style="color: #64748b; font-size: 0.9rem; margin: 0 0 1rem;">
            Search any live business, restaurant, or store to fetch real customer reviews and run them through our trained ML intelligence pipeline.
        </p>
    """, unsafe_allow_html=True)

    # API Key Handling (supports env var, session state, or user input)
    with st.expander("🔑 Google Places API Key Configuration", expanded=False):
        custom_key = st.text_input(
            "API Key (Optional if GOOGLE_PLACES_API_KEY env var is set)",
            type="password",
            value=st.session_state.get("google_api_key", ""),
            placeholder="AIzaSy...",
            key="input_google_api_key"
        )
        if custom_key:
            st.session_state["google_api_key"] = custom_key.strip()
        st.caption("🔒 Keys are kept securely in runtime memory and are never committed or logged.")

    # Priority: session_state (user-entered) → st.secrets → env var (read by backend)
    active_key = st.session_state.get("google_api_key", None)
    if not active_key:
        try:
            active_key = st.secrets.get("GOOGLE_PLACES_API_KEY", None)
        except Exception:
            pass  # st.secrets not configured – backend will fall back to env var

    # Search Bar
    col_q, col_btn = st.columns([4, 1])
    with col_q:
        search_query = st.text_input(
            "Search Business or Place",
            placeholder="e.g., Starbucks Indiranagar Bangalore, Third Wave Coffee Koramangala",
            key="places_search_query"
        )
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search Places", type="primary", use_container_width=True)

    if search_clicked and search_query.strip():
        with st.spinner("Searching Google Places API..."):
            res = search_google_places(search_query.strip(), api_key=active_key)
            if res and res.get("success"):
                st.session_state["searched_places"] = res.get("places", [])
                st.session_state["selected_place_id"] = None
                st.session_state["live_analysis_result"] = None
            else:
                err_msg = res.get("message", "Failed to search places.") if res else "Backend unreachable."
                st.error(f"❌ {err_msg}")

    # Display Matching Places
    places_list = st.session_state.get("searched_places", [])
    if places_list:
        st.markdown("<h4 style='font-size: 1rem; font-weight: 600; margin: 1rem 0 0.5rem;'>Matching Places Found:</h4>", unsafe_allow_html=True)

        place_options = {p["place_id"]: f"{p['name']} — {p['address']} ({p.get('rating', 'N/A')}★, {p.get('user_rating_count', 0):,} ratings)" for p in places_list}
        selected_pid = st.selectbox(
            "Select Place to Analyze",
            options=list(place_options.keys()),
            format_func=lambda pid: place_options[pid],
            key="places_select_box"
        )

        col_model, col_analyze = st.columns([2, 1])
        with col_model:
            selected_model = st.selectbox(
                "Inference Model",
                ["balanced_logistic_regression", "logistic_regression", "linearsvc"],
                format_func=lambda x: {
                    "balanced_logistic_regression": "Balanced Logistic Regression (Minority Sensitive)",
                    "logistic_regression": "Standard Logistic Regression",
                    "linearsvc": "LinearSVC"
                }.get(x, x),
                key="places_model_select"
            )
        with col_analyze:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            analyze_clicked = st.button("⚡ Analyze Live Reviews", type="primary", use_container_width=True)

        if analyze_clicked and selected_pid:
            with st.spinner("Fetching genuine Google reviews and running ML intelligence pipeline..."):
                analysis_res = analyze_google_place_reviews(selected_pid, model=selected_model, api_key=active_key)
                if analysis_res and analysis_res.get("success"):
                    st.session_state["live_analysis_result"] = analysis_res
                else:
                    err_msg = analysis_res.get("message", "Failed to analyze reviews.") if analysis_res else "Backend unreachable."
                    st.error(f"❌ {err_msg}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Render Live Intelligence Dashboard if analysis exists
    analysis = st.session_state.get("live_analysis_result")
    if analysis and analysis.get("success"):
        place_info = analysis.get("place_info", {})
        pulse_data = analysis.get("sentiment_pulse", {})
        reviews_raw = analysis.get("reviews", [])

        # Place Header Card
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <span style="color: #64748b; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">Google Maps Verified Place</span>
                    <h2 style="font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 0.2rem 0;">{place_info.get('name')}</h2>
                    <p style="color: #475569; font-size: 0.95rem; margin: 0;">📍 {place_info.get('address')}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.8rem; font-weight: 800; color: #f59e0b;">
                        {place_info.get('overall_rating', 'N/A')} <span style="font-size: 1.2rem;">★</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #64748b;">
                        {place_info.get('user_rating_count', 0):,} Total Google Ratings
                    </div>
                    {f'<a href="{place_info.get("maps_uri")}" target="_blank" style="color: #2563eb; font-size: 0.85rem; text-decoration: none; font-weight: 600;">View on Google Maps ↗</a>' if place_info.get("maps_uri") else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not reviews_raw:
            st.info("No text reviews were returned by Google Places API for this business.")
            return

        # Convert to DataFrame for standard components
        df_live = pd.DataFrame(reviews_raw)

        # 1. LIVE CUSTOMER SENTIMENT PULSE
        render_sentiment_pulse(df_live)

        # 2. KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Live Reviews Analyzed", f"{len(df_live):,}")
        col2.metric("AI Positive %", f"{pulse_data.get('positive_pct', 0.0):.1f}%")
        col3.metric("AI Negative %", f"{pulse_data.get('negative_pct', 0.0):.1f}%")
        col4.metric("Mismatch Cases", f"{pulse_data.get('mismatch_count', 0)} ({pulse_data.get('mismatch_pct', 0.0):.1f}%)")

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Pain-Point Intelligence on Live Reviews
        render_pain_point_section(df_live)

        # 4. Rating vs Sentiment Mismatch
        render_mismatch_section(df_live)

        # 5. Review Feed for Live Google Reviews
        render_review_feed(df_live)

        # Google Attribution & Limitations Footer
        st.markdown("""
        <div style="background: #f1f5f9; border-radius: 8px; padding: 1rem; margin-top: 2rem; font-size: 0.8rem; color: #64748b; line-height: 1.5;">
            <b>Google Places Platform Attribution:</b> Reviews and place information provided by Google Places API.<br>
            <b>Limitation Note:</b> Live review availability and ordering are provided by Google Places API. Only the reviews returned by the API are analyzed by this application.
        </div>
        """, unsafe_allow_html=True)
