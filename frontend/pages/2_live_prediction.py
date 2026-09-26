"""
2_live_prediction.py
────────────────────
Manual Review Analyzer & Live Review Intelligence.
Demonstrates practical ML inference:
INPUT REVIEW → AI NLP ANALYSIS → ACTIONABLE RESULT
Uses render_html from frontend.ui_utils to guarantee zero raw HTML leaks.
"""

import streamlit as st
import pandas as pd
from frontend.ui_utils import render_html
from frontend.api_client import get_api_client
from frontend.components.aspect_analyzer import extract_aspects_and_issues


def render():
    header_html = """
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:1rem;border-bottom:1px solid #1E2533;padding-bottom:0.75rem;">
        <div>
            <h1 style="font-size:1.6rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
                ANALYZE A NEW CUSTOMER REVIEW
            </h1>
            <div style="color:#98A2B3;font-size:0.82rem;margin:0;">
                Real-time inference pipeline: Sentiment Classification → Aspect Extraction → Priority → Action
            </div>
        </div>
        <div style="display:flex;gap:0.45rem;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(124,92,255,0.1);border:1px solid rgba(124,92,255,0.25);color:#7C5CFF;font-size:0.68rem;font-weight:700;padding:2px 8px;border-radius:4px;">
                INFERENCE TESTER
            </span>
        </div>
    </div>
    """
    render_html(header_html)

    client = get_api_client()

    tab_single, tab_batch = st.tabs(["Single Review Analyzer", "Batch Review Tester"])

    with tab_single:
        col_input, col_meta = st.columns([2, 1])

        with col_input:
            review_text = st.text_area(
                "Customer Review Text",
                placeholder="Paste or type a customer review here...\ne.g. 'The cream arrived with a broken pump and leaked all over the box, but it works well on my skin.'",
                height=130,
                key="live_text_input"
            )

        with col_meta:
            model_choice = st.selectbox(
                "Inference Model",
                ["balanced_logistic_regression", "logistic_regression", "linearsvc"],
                index=0,
                format_func=lambda x: {
                    "balanced_logistic_regression": "Balanced Logistic Regression (Recommended)",
                    "logistic_regression": "Standard Logistic Regression",
                    "linearsvc": "LinearSVC (High Accuracy)"
                }.get(x, x),
                key="live_model_select"
            )

            product_asin = st.text_input("Product ASIN (Optional)", placeholder="e.g. B00YQ6X8EO", key="live_asin_input")
            input_rating = st.select_slider("Customer Star Rating (Optional for Mismatch Check)", options=[1, 2, 3, 4, 5], value=5)

        if st.button("ANALYZE REVIEW", type="primary", use_container_width=True):
            if not review_text.strip():
                st.warning("Please enter review text to analyze.")
                return

            with st.spinner("Running ML inference & aspect extraction..."):
                response = client.predict(review_text, model=model_choice)

            if response:
                sentiment = response.get("sentiment", "neutral").upper()
                confidence = response.get("confidence")
                model_used = response.get("model_used", model_choice)

                intel = extract_aspects_and_issues(review_text, sentiment=sentiment, rating=input_rating)

                is_mismatch = (
                    (input_rating >= 4 and sentiment == "NEGATIVE") or
                    (input_rating <= 2 and sentiment == "POSITIVE")
                )

                if sentiment == "POSITIVE":
                    c_badge_bg = "rgba(34, 197, 94, 0.15)"
                    c_badge_text = "#22C55E"
                    c_badge_bdr = "rgba(34, 197, 94, 0.35)"
                elif sentiment == "NEGATIVE":
                    c_badge_bg = "rgba(239, 68, 68, 0.15)"
                    c_badge_text = "#EF4444"
                    c_badge_bdr = "rgba(239, 68, 68, 0.35)"
                else:
                    c_badge_bg = "rgba(245, 158, 11, 0.15)"
                    c_badge_text = "#F59E0B"
                    c_badge_bdr = "rgba(245, 158, 11, 0.35)"

                p_color = {
                    "HIGH": "#EF4444",
                    "MEDIUM": "#F59E0B",
                    "LOW": "#22C55E"
                }.get(intel["priority"], "#98A2B3")

                conf_str = f"{confidence * 100:.1f}%" if confidence is not None else "N/A (LinearSVC non-probabilistic)"

                mismatch_banner = ""
                if is_mismatch:
                    mismatch_banner = f"""
                    <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:0.6rem 0.85rem;margin-bottom:0.85rem;color:#EF4444;font-size:0.8rem;font-weight:600;">
                        Rating–Sentiment Mismatch: Selected rating is {input_rating}★, but ML classified text as {sentiment}.
                    </div>
                    """

                result_card = f"""
                <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1.15rem;margin-top:1.15rem;">
                    {mismatch_banner}
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #1E2533;padding-bottom:0.65rem;margin-bottom:0.85rem;">
                        <div style="display:flex;align-items:center;gap:0.65rem;">
                            <span style="font-size:0.72rem;color:#98A2B3;font-weight:700;text-transform:uppercase;">SENTIMENT</span>
                            <span style="background:{c_badge_bg};color:{c_badge_text};border:1px solid {c_badge_bdr};padding:2px 10px;border-radius:4px;font-size:0.82rem;font-weight:800;letter-spacing:0.06em;">
                                {sentiment}
                            </span>
                            <span style="color:#667085;font-size:0.72rem;">via <code>{model_used}</code></span>
                        </div>
                        <div style="font-size:0.75rem;color:#98A2B3;">
                            CONFIDENCE: <b style="color:#F5F7FA;">{conf_str}</b>
                        </div>
                    </div>

                    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:0.65rem;margin-bottom:0.85rem;">
                        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.75rem;">
                            <div style="font-size:0.65rem;color:#98A2B3;font-weight:700;text-transform:uppercase;">ASPECT</div>
                            <div style="font-size:1rem;font-weight:800;color:#F5F7FA;margin-top:2px;">{intel['primary_aspect']}</div>
                        </div>

                        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.75rem;">
                            <div style="font-size:0.65rem;color:#98A2B3;font-weight:700;text-transform:uppercase;">PAIN POINT / ISSUE</div>
                            <div style="font-size:1rem;font-weight:800;color:#F5F7FA;margin-top:2px;">{intel['issue']}</div>
                        </div>

                        <div style="background:#151A24;border:1px solid #242A35;border-radius:6px;padding:0.75rem;">
                            <div style="font-size:0.65rem;color:#98A2B3;font-weight:700;text-transform:uppercase;">PRIORITY</div>
                            <div style="font-size:1rem;font-weight:800;color:{p_color};margin-top:2px;">{intel['priority']}</div>
                        </div>
                    </div>

                    <div style="background:#151A24;border-left:3px solid #7C5CFF;border-radius:0 6px 6px 0;padding:0.65rem 0.85rem;">
                        <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;margin-bottom:2px;">SUGGESTED ACTION</div>
                        <div style="color:#F5F7FA;font-size:0.82rem;line-height:1.4;">{intel['suggested_action']}</div>
                    </div>
                </div>
                """
                render_html(result_card)

    with tab_batch:
        render_html("""
        <div style="font-size:0.85rem;color:#98A2B3;margin-bottom:0.75rem;">
            Paste multiple customer reviews (one per line) to run batch inference.
        </div>
        """)

        batch_input = st.text_area(
            "Batch Review Lines",
            value="Great moisturizer, leaves skin soft and hydrated all day!\nArrived damaged and leaking inside the box, very disappointed.\nAverage product, nothing special for the price.",
            height=110,
            key="batch_text_input"
        )

        batch_model = st.selectbox(
            "Batch Model",
            ["balanced_logistic_regression", "logistic_regression", "linearsvc"],
            key="batch_model_select"
        )

        if st.button("Run Batch Analysis", type="primary"):
            lines = [line.strip() for line in batch_input.split("\n") if line.strip()]
            if not lines:
                st.warning("Please provide at least one non-empty review line.")
                return

            with st.spinner(f"Analyzing {len(lines)} reviews in batch..."):
                results = client.predict_batch(lines, model=batch_model)

            if results:
                st.success(f"Processed {len(results)} reviews successfully.")
                df_res = pd.DataFrame(results)

                counts = df_res["sentiment"].value_counts()
                c1, c2, c3 = st.columns(3)
                c1.metric("Positive", counts.get("positive", 0))
                c2.metric("Neutral", counts.get("neutral", 0))
                c3.metric("Negative", counts.get("negative", 0))

                st.dataframe(
                    df_res[["text", "sentiment", "confidence", "model_used"]],
                    use_container_width=True
                )


if __name__ == "__main__":
    render()