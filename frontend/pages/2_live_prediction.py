"""
2_live_prediction.py
────────────────────
Real-Time Customer Review Inference & Attribution Transparency.
Provides single-review inference and batch testing with clear separation
between TF-IDF linear attribution and transformer sequence evaluation.
"""

import streamlit as st
import pandas as pd
import os
import time
from frontend.ui_utils import render_html
from frontend.api_client import get_api_client
from frontend.components.aspect_analyzer import extract_aspects_and_issues

try:
    from backend.app.ml.keywords import explain_text
except ImportError:
    from app.ml.keywords import explain_text

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "models")


def render():
    render_html("""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:12px;">
        <div>
            <h1 style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;margin:0 0 4px;line-height:1.2;">
                Live Review Inference
            </h1>
            <div style="color:#9ca3af;font-size:13px;margin:0;">
                Real-time sentiment inference, aspect extraction, priority assignment, and attribution transparency
            </div>
        </div>
        <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
            <span style="background:rgba(16,185,129,0.1);border:1px solid rgba(255,255,255,0.07);color:#10b981;font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px;">
                ACTIVE PIPELINE
            </span>
        </div>
    </div>
    """)

    if "analysis_history" not in st.session_state:
        st.session_state["analysis_history"] = []

    client = get_api_client()

    tab_single, tab_batch = st.tabs(["01 · Single Review Analyzer", "02 · Batch Review Tester"])

    with tab_single:
        review_text = st.text_area(
            "Customer Review Text",
            value=st.session_state.get("live_text_val", "The moisturizer arrived with a broken pump and leaked inside the box, but the texture itself is very soothing on sensitive skin."),
            placeholder="Enter customer review text to evaluate...",
            height=110,
            key="live_text_input"
        )

        # Rule 7: Single high-contrast primary action button directly below text input
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"] {
            background-color: #10b981 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border: none !important;
            border-radius: 6px !important;
            height: 42px !important;
        }
        div[data-testid="stButton"] > button[kind="primary"]:hover {
            background-color: #059669 !important;
            color: #ffffff !important;
        }
        </style>
        """, unsafe_allow_html=True)

        analyze_clicked = st.button("Analyze Customer Sentiment", type="primary", width='stretch')

        col_m, col_r = st.columns([2, 1])
        with col_m:
            model_choice = st.selectbox(
                "Inference Engine",
                ["balanced_logistic_regression", "distilbert", "linearsvc", "logistic_regression"],
                index=0,
                format_func=lambda x: {
                    "balanced_logistic_regression": "Balanced Logistic Regression (Handles Class Imbalance)",
                    "distilbert": "DistilBERT Transformer (Deep Sequence Classifier)",
                    "linearsvc": "LinearSVC (Max-Margin Support Vector Machine)",
                    "logistic_regression": "Standard Logistic Regression",
                }.get(x, x),
                key="live_model_select"
            )
        with col_r:
            input_rating = st.select_slider("Customer Star Rating (for Mismatch Check)", options=[1, 2, 3, 4, 5], value=5)

        if analyze_clicked:
            if not review_text.strip():
                st.warning("Please enter review text to analyze.")
                return

            t0 = time.perf_counter()
            with st.spinner("Executing inference and aspect extraction..."):
                response = client.predict(review_text, model=model_choice)
                latency_ms = (time.perf_counter() - t0) * 1000
                explanation = explain_text(review_text, MODELS_DIR, model_name=model_choice)

            if response:
                sentiment = response.get("sentiment", "neutral").upper()
                confidence = response.get("confidence")
                model_used = response.get("model_used", model_choice)

                intel = extract_aspects_and_issues(review_text, sentiment=sentiment.lower(), rating=input_rating)

                is_mismatch = (
                    (input_rating >= 4 and sentiment == "NEGATIVE") or
                    (input_rating <= 2 and sentiment == "POSITIVE")
                )

                if sentiment == "POSITIVE":
                    c_badge_bg = "rgba(16, 185, 129, 0.12)"
                    c_badge_text = "#10b981"
                    c_badge_bdr = "rgba(16, 185, 129, 0.3)"
                elif sentiment == "NEGATIVE":
                    c_badge_bg = "rgba(239, 68, 68, 0.12)"
                    c_badge_text = "#ef4444"
                    c_badge_bdr = "rgba(239, 68, 68, 0.3)"
                else:
                    c_badge_bg = "rgba(245, 158, 11, 0.12)"
                    c_badge_text = "#f59e0b"
                    c_badge_bdr = "rgba(245, 158, 11, 0.3)"

                p_color = {
                    "HIGH": "#ef4444",
                    "MEDIUM": "#f59e0b",
                    "LOW": "#10b981"
                }.get(intel["priority"], "#9ca3af")

                conf_str = f"{confidence * 100:.1f}%" if confidence is not None else "N/A (LinearSVC)"

                mismatch_banner = ""
                if is_mismatch:
                    mismatch_banner = f"""
                    <div style="background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:6px;padding:10px 14px;margin-bottom:14px;color:#ef4444;font-size:12px;font-weight:600;">
                        Rating–Sentiment Mismatch: Selected rating is {input_rating}★, but model classified text as {sentiment}.
                    </div>
                    """

                # Attribution Block logic based on active model (Section 3.4)
                if model_choice == "distilbert":
                    attribution_block = f"""
                    <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:16px;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                            <div style="font-size:11px;font-weight:700;color:#10b981;text-transform:uppercase;letter-spacing:0.05em;">
                                Contextual Sequence Evaluation (DistilBERT Transformer)
                            </div>
                            <span style="font-size:11px;color:#6b7280;font-family:monospace;">
                                Latency: {latency_ms:.1f} ms
                            </span>
                        </div>
                        <div style="color:#9ca3af;font-size:12px;line-height:1.5;margin-bottom:12px;">
                            DistilBERT processes text as an unbroken contextual sequence via multi-head self-attention. Word-level linear weights are not applied.
                        </div>
                        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;margin-bottom:12px;">
                            <div style="display:flex;justify-content:space-between;font-size:11px;margin-bottom:6px;">
                                <span style="color:#9ca3af;">Predicted Class Confidence:</span>
                                <span style="color:#ffffff;font-weight:700;">{conf_str}</span>
                            </div>
                            <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden;">
                                <div style="height:100%;width:{confidence * 100 if confidence else 100}%;background:#10b981;"></div>
                            </div>
                        </div>
                        <div style="display:flex;gap:16px;font-size:11px;color:#6b7280;">
                            <span>Token sequence length: <b style="color:#ffffff;">{len(review_text.split())} tokens</b></span>
                            <span>Inference execution: <b style="color:#ffffff;">CPU optimized PyTorch runtime</b></span>
                        </div>
                    </div>
                    """
                else:
                    pos_chips = "".join([f'<span style="background:rgba(16,185,129,0.12);color:#10b981;border:1px solid rgba(16,185,129,0.3);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-right:6px;">{w} (+{s:.2f})</span>' for w, s in explanation.get("top_positive", [])]) or '<span style="color:#6b7280;font-size:11px;">None detected</span>'
                    neg_chips = "".join([f'<span style="background:rgba(239,68,68,0.12);color:#ef4444;border:1px solid rgba(239,68,68,0.3);padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600;margin-right:6px;">{w} (-{s:.2f})</span>' for w, s in explanation.get("top_negative", [])]) or '<span style="color:#6b7280;font-size:11px;">None detected</span>'

                    attribution_block = f"""
                    <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:16px;">
                        <div style="font-size:11px;font-weight:700;color:#ffffff;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">
                            Feature Attribution (TF-IDF Coefficients)
                        </div>
                        <div style="font-size:13px;line-height:1.6;color:#ffffff;background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;margin-bottom:12px;">
                            {explanation.get("highlighted_html", review_text)}
                        </div>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:12px;">
                            <div>
                                <span style="color:#9ca3af;font-weight:600;">Positive Drivers:</span>
                                <div style="margin-top:4px;">{pos_chips}</div>
                            </div>
                            <div>
                                <span style="color:#9ca3af;font-weight:600;">Negative Drivers:</span>
                                <div style="margin-top:4px;">{neg_chips}</div>
                            </div>
                        </div>
                    </div>
                    """

                result_card = f"""
                <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-top:16px;">
                    {mismatch_banner}
                    <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:12px;margin-bottom:14px;">
                        <div style="display:flex;align-items:center;gap:10px;">
                            <span style="font-size:11px;color:#9ca3af;font-weight:600;text-transform:uppercase;">PREDICTED SENTIMENT</span>
                            <span style="background:{c_badge_bg};color:{c_badge_text};border:1px solid {c_badge_bdr};padding:3px 10px;border-radius:4px;font-size:13px;font-weight:700;letter-spacing:0.04em;">
                                {sentiment}
                            </span>
                            <span style="color:#6b7280;font-size:11px;">via <code>{model_used}</code></span>
                        </div>
                        <div style="font-size:12px;color:#9ca3af;">
                            CONFIDENCE: <b style="color:#ffffff;">{conf_str}</b>
                        </div>
                    </div>

                    <div style="display:grid;grid-template-columns:repeat(3, 1fr);gap:10px;margin-bottom:14px;">
                        <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;">
                            <div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase;">PRIMARY ASPECT</div>
                            <div style="font-size:16px;font-weight:700;color:#ffffff;margin-top:2px;">{intel['primary_aspect']}</div>
                        </div>

                        <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;">
                            <div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase;">DETECTED ISSUE</div>
                            <div style="font-size:16px;font-weight:700;color:#ffffff;margin-top:2px;">{intel['issue']}</div>
                        </div>

                        <div style="background:#181b21;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:12px 14px;">
                            <div style="font-size:10px;color:#9ca3af;font-weight:600;text-transform:uppercase;">ACTION PRIORITY</div>
                            <div style="font-size:16px;font-weight:700;color:{p_color};margin-top:2px;">{intel['priority']}</div>
                        </div>
                    </div>

                    <div style="background:#181b21;border-left:3px solid #10b981;border-radius:0 6px 6px 0;padding:10px 14px;margin-bottom:14px;">
                        <div style="font-size:11px;font-weight:600;color:#10b981;text-transform:uppercase;margin-bottom:2px;">SUGGESTED INTERVENTION</div>
                        <div style="color:#d1d5db;font-size:13px;line-height:1.45;">{intel['suggested_action']}</div>
                    </div>

                    {attribution_block}
                </div>
                """
                render_html(result_card)

                st.session_state["analysis_history"].append({
                    "snippet": (review_text[:70] + "...") if len(review_text) > 70 else review_text,
                    "sentiment": sentiment,
                    "confidence": confidence,
                    "model": model_choice
                })

        if st.session_state.get("analysis_history"):
            st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
            render_html("""
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">
                Session Analysis History
            </div>
            """)
            badge_colors = {"POSITIVE": "#10b981", "NEGATIVE": "#ef4444", "NEUTRAL": "#f59e0b"}
            for entry in reversed(st.session_state["analysis_history"][-8:]):
                conf_txt = f"{entry['confidence']*100:.1f}%" if entry['confidence'] is not None else "N/A"
                badge_col = badge_colors.get(entry["sentiment"], "#9ca3af")
                st.markdown(f"""
                <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;
                            padding:10px 14px;margin-bottom:6px;
                            display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#d1d5db;font-size:12px;flex:1;margin-right:12px;">{entry['snippet']}</span>
                    <div style="display:flex;align-items:center;gap:10px;flex-shrink:0;">
                        <span style="background:{badge_col}22;border:1px solid {badge_col}55;
                                     color:{badge_col};font-size:11px;font-weight:700;
                                     padding:2px 8px;border-radius:4px;">{entry['sentiment']}</span>
                        <span style="color:#6b7280;font-size:11px;">{conf_txt}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
            if st.button("Clear History", key="clear_history_btn"):
                st.session_state["analysis_history"] = []
                st.rerun()

    with tab_batch:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:16px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                Batch Review Inference
            </div>
            <div style="color:#d1d5db;font-size:13px;">
                Run high-throughput classification across multiple customer review texts or uploaded CSV files.
            </div>
        </div>
        """)

        batch_mode = st.radio("Input Mode", ["Paste Text Lines", "Upload CSV File"], horizontal=True)

        batch_model = st.selectbox(
            "Batch Model",
            ["balanced_logistic_regression", "distilbert", "linearsvc", "logistic_regression"],
            format_func=lambda x: {
                "balanced_logistic_regression": "Balanced Logistic Regression (Fast TF-IDF Baseline)",
                "distilbert": "DistilBERT Transformer (Deep Sequence Classifier)",
                "linearsvc": "LinearSVC (High Accuracy SVM)",
                "logistic_regression": "Standard Logistic Regression",
            }.get(x, x),
            key="batch_model_select"
        )

        lines_to_process = []

        if batch_mode == "Paste Text Lines":
            batch_input = st.text_area(
                "Batch Review Lines (one per line)",
                value="Great moisturizer, leaves skin soft and hydrated all day.\nArrived damaged and leaking inside the box, very disappointed.\nAverage product, nothing special for the price point.",
                height=110,
                key="batch_text_input"
            )
            lines_to_process = [l.strip() for l in batch_input.split("\n") if l.strip()]
        else:
            uploaded_file = st.file_uploader("Upload CSV containing reviews", type=["csv"], key="batch_csv_upload")
            if uploaded_file:
                try:
                    user_df = pd.read_csv(uploaded_file)
                    st.caption(f"Uploaded CSV with {len(user_df):,} rows.")
                    text_col = st.selectbox("Select Text Column", options=list(user_df.columns), index=0)
                    lines_to_process = user_df[text_col].dropna().astype(str).tolist()
                except Exception as e:
                    st.error(f"Error reading CSV: {e}")

        if st.button("Run Batch Inference", type="primary", width='stretch'):
            if not lines_to_process:
                st.warning("Please provide review text or upload a valid CSV.")
                return

            with st.spinner(f"Analyzing {len(lines_to_process):,} reviews..."):
                results = client.predict_batch(lines_to_process, model=batch_model)

            if results:
                st.success(f"Successfully processed {len(results):,} reviews.")
                df_res = pd.DataFrame(results)

                counts = df_res["sentiment"].value_counts()
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px;text-align:center;">
                        <div style="font-size:11px;font-weight:600;color:#10b981;text-transform:uppercase;">Positive</div>
                        <div style="font-size:24px;font-weight:700;color:#ffffff;margin:2px 0;">{counts.get('positive', 0):,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px;text-align:center;">
                        <div style="font-size:11px;font-weight:600;color:#f59e0b;text-transform:uppercase;">Neutral</div>
                        <div style="font-size:24px;font-weight:700;color:#ffffff;margin:2px 0;">{counts.get('neutral', 0):,}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:6px;padding:14px;text-align:center;">
                        <div style="font-size:11px;font-weight:600;color:#ef4444;text-transform:uppercase;">Negative</div>
                        <div style="font-size:24px;font-weight:700;color:#ffffff;margin:2px 0;">{counts.get('negative', 0):,}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

                st.dataframe(
                    df_res[["text", "sentiment", "confidence", "model_used"]],
                    width='stretch'
                )

                csv_data = df_res.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Scored Batch CSV",
                    data=csv_data,
                    file_name="sentiment_batch_results.csv",
                    mime="text/csv",
                    width='stretch'
                )


if __name__ == "__main__":
    render()