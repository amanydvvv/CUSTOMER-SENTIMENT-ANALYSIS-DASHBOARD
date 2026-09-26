import streamlit as st
from typing import Optional
from frontend.utils.api_client import api_client

SAMPLE_PROMPTS = [
    ("🎧 Great Sound", "The noise cancellation is phenomenal and bass is punchy, but the charging cable feels slightly flimsy."),
    ("☕ Coffee Shop", "Charming atmosphere and great cold brew coffee. Seating is somewhat cramped during morning rush."),
    ("📦 Broken Delivery", "Product arrived with cracked screen and missing power adapter. Terrible customer support refusing replacement."),
    ("🍕 Pizza Experience", "Best wood fired pizza in the city! Crust was crispy, sauce was vibrant and fresh."),
    ("🔋 Short Battery", "Battery died within two weeks of light usage. Extremely disappointed with the build quality."),
]


def render_live_tester(token: Optional[str] = None):
    """Interactive Live Sentiment & Aspect Testing Playground."""
    st.markdown("### ⚡ Live Sentiment & Aspect Playground")
    st.markdown(
        "Type or select a customer review to inspect real-time classification, confidence distributions, and extracted aspect tags."
    )

    # Preset Quick-Fill Buttons
    st.markdown("**Quick Preset Reviews:**")
    preset_cols = st.columns(len(SAMPLE_PROMPTS))
    for idx, (title, sample_text) in enumerate(SAMPLE_PROMPTS):
        with preset_cols[idx]:
            if st.button(title, key=f"preset_btn_{idx}", use_container_width=True):
                st.session_state["live_input_text"] = sample_text

    default_text = st.session_state.get(
        "live_input_text",
        "The sound quality is truly incredible with deep bass, but battery life is only average.",
    )

    input_text = st.text_area(
        "Customer Review Text:",
        value=default_text,
        height=110,
        placeholder="Enter raw customer review here...",
        key="live_text_area",
    )

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        model_choice = st.selectbox(
            "Routing Strategy",
            ["auto (Smart Dual-Path Router)", "primary (DistilBERT Transformer)", "fallback (TF-IDF + Logistic Regression)"],
            index=0,
            help="Auto tries DistilBERT with <250ms SLA and automatically falls back to TF-IDF+LR if constraints occur.",
        )
        routing_mode = model_choice.split(" ")[0]

    with c2:
        extract_aspects_flag = st.checkbox("Extract Aspects", value=True)

    with c3:
        analyze_btn = st.button("🚀 Analyze Now", type="primary", use_container_width=True)

    if analyze_btn or st.session_state.get("auto_run_live", False):
        if not input_text.strip():
            st.warning("Please enter review text to analyze.")
            return

        with st.spinner("Classifying sentiment & extracting aspects..."):
            try:
                res = api_client.predict(
                    text=input_text,
                    model_preference=routing_mode,
                    extract_aspects=extract_aspects_flag,
                    token=token,
                )

                sentiment = res.get("sentiment", "neutral").lower()
                confidence = res.get("confidence", 0.0)
                latency = res.get("latency_ms", 0.0)
                model_used = res.get("model_used", "distilbert")
                probs = res.get("probabilities", {})
                aspects = res.get("aspects", [])
                fallback_flag = res.get("fallback_triggered", False)

                # Sentiment Badge Styling
                if sentiment == "positive":
                    badge_html = f'<span class="badge-pos">● POSITIVE ({confidence * 100:.1f}%)</span>'
                    glow_color = "#10B981"
                elif sentiment == "negative":
                    badge_html = f'<span class="badge-neg">● NEGATIVE ({confidence * 100:.1f}%)</span>'
                    glow_color = "#F43F5E"
                else:
                    badge_html = f'<span class="badge-neu">● NEUTRAL ({confidence * 100:.1f}%)</span>'
                    glow_color = "#38BDF8"

                # Display Results in Modern Grid
                st.markdown("---")
                r_col1, r_col2 = st.columns([1.2, 1])

                with r_col1:
                    st.markdown("#### Prediction Summary")
                    st.markdown(
                        f"""
                        <div class="kpi-card" style="border-left: 4px solid {glow_color};">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div style="font-size: 20px; font-weight: 700;">{badge_html}</div>
                                <div style="font-size: 13px; color: #94A3B8;">⏱️ {latency:.1f} ms</div>
                            </div>
                            <div style="margin-top: 14px; font-size: 14px; color: #E2E8F0;">
                                <b>Model Pipeline:</b> <code style="color:#818CF8;">{model_used.upper()}</code>
                                {' <span style="color:#F59E0B; font-weight:600;">(Fallback Activated)</span>' if fallback_flag else ''}
                            </div>
                            <div style="margin-top: 6px; font-size: 13px; color: #94A3B8;">
                                <b>Cleaned Text:</b> <i>"{res.get('cleaned_text', '')}"</i>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    # Extracted Aspects
                    st.markdown("#### Extracted Aspects & Polarity")
                    if aspects:
                        aspect_html = ""
                        for asp in aspects:
                            asp_text = asp.get("aspect", "")
                            asp_sent = asp.get("sentiment", "neutral")
                            asp_rel = asp.get("relevance", 1.0)

                            if asp_sent == "positive":
                                chip_style = "border-color: #10B981; color: #34D399; background: rgba(16, 185, 129, 0.1);"
                            elif asp_sent == "negative":
                                chip_style = "border-color: #F43F5E; color: #FB7185; background: rgba(244, 63, 94, 0.1);"
                            else:
                                chip_style = "border-color: #38BDF8; color: #38BDF8; background: rgba(56, 189, 248, 0.1);"

                            aspect_html += f'<span class="aspect-chip" style="{chip_style}">{asp_text.title()} ({asp_sent})</span> '

                        st.markdown(aspect_html, unsafe_allow_html=True)
                    else:
                        st.info("No distinct product/service aspects extracted.")

                with r_col2:
                    st.markdown("#### Probability Distribution")
                    for cls_name, p_val in [("Positive", probs.get("positive", 0.0)), ("Neutral", probs.get("neutral", 0.0)), ("Negative", probs.get("negative", 0.0))]:
                        pct = round(p_val * 100, 1)
                        if cls_name == "Positive":
                            bar_color = "#10B981"
                        elif cls_name == "Negative":
                            bar_color = "#F43F5E"
                        else:
                            bar_color = "#38BDF8"

                        st.markdown(
                            f"""
                            <div style="margin-bottom: 12px;">
                                <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#F1F5F9;">
                                    <span>{cls_name}</span>
                                    <span>{pct}%</span>
                                </div>
                                <div class="conf-bar-container">
                                    <div class="conf-bar-fill" style="width: {pct}%; background: {bar_color};"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            except Exception as e:
                st.error(f"Prediction error: {e}")
