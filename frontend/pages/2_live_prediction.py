import streamlit as st
import plotly.graph_objects as go
from frontend.api_client import predict_sentiment, predict_batch


SENTIMENT_COLORS = {
    "positive": {"bg": "#dcfce7", "text": "#166534", "fill": "confidence-positive", "icon": "😊"},
    "negative": {"bg": "#fee2e2", "text": "#991b1b", "fill": "confidence-negative", "icon": "☹️"},
    "neutral": {"bg": "#fef3c7", "text": "#92400e", "fill": "confidence-neutral", "icon": "😐"},
}

EXAMPLE_REVIEWS = {
    "Positive": "This product exceeded my expectations! The quality is amazing and it works perfectly. Highly recommend to anyone looking for a reliable option.",
    "Negative": "Terrible product. Stopped working after just two days. Poor build quality and waste of money. Do not buy this.",
    "Neutral": "It's an okay product. Nothing special but does the job. Average quality for the price point.",
}


def render_confidence_gauge(confidence: float, sentiment: str):
    color = SENTIMENT_COLORS[sentiment]["text"]
    fill_class = SENTIMENT_COLORS[sentiment]["fill"]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Confidence", "font": {"size": 16, "family": "Inter", "color": "#475569"}},
        number={"font": {"size": 32, "family": "Inter", "color": color}, "suffix": "%"},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e2e8f0"},
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "#f1f5f9",
            "borderwidth": 2,
            "bordercolor": "#e2e8f0",
            "steps": [
                {"range": [0, 50], "color": "#fef3c7"},
                {"range": [50, 75], "color": "#dbeafe"},
                {"range": [75, 100], "color": "#dcfce7"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": confidence * 100,
            },
        },
    ))
    fig.update_layout(
        height=200,
        margin=dict(t=30, b=10, l=10, r=10),
        font={"family": "Inter"},
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Live Prediction</h1>
        <p class="page-subtitle">Analyze sentiment in real-time with multiple model options</p>
    </div>
    """, unsafe_allow_html=True)

    col_input, col_output = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Input Text</h3>', unsafe_allow_html=True)

        model = st.session_state.get("selected_model", "Balanced Logistic Regression")
        model_key = model.lower().replace(" ", "_")

        text = st.text_area(
            "Enter review text",
            height=200,
            placeholder="Type or paste a product review here...\n\nExample: \"This product is amazing! Great quality and fast delivery.\"",
            label_visibility="collapsed",
        )

        col_ex1, col_ex2, col_ex3 = st.columns(3)
        with col_ex1:
            if st.button("😊 Positive", use_container_width=True):
                st.session_state["prediction_text"] = EXAMPLE_REVIEWS["Positive"]
                st.rerun()
        with col_ex2:
            if st.button("😐 Neutral", use_container_width=True):
                st.session_state["prediction_text"] = EXAMPLE_REVIEWS["Neutral"]
                st.rerun()
        with col_ex3:
            if st.button("☹️ Negative", use_container_width=True):
                st.session_state["prediction_text"] = EXAMPLE_REVIEWS["Negative"]
                st.rerun()

        if "prediction_text" in st.session_state:
            text = st.session_state.pop("prediction_text")

        analyze_btn = st.button("🔍 Analyze Sentiment", type="primary", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Batch Analysis</h3>', unsafe_allow_html=True)

        batch_text = st.text_area(
            "Multiple reviews (one per line)",
            height=120,
            placeholder="Review 1\nReview 2\nReview 3",
            label_visibility="collapsed",
        )

        batch_btn = st.button("📊 Analyze Batch", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_output:
        if analyze_btn and text.strip():
            with st.spinner("Analyzing sentiment..."):
                result = predict_sentiment(text.strip(), model_key)

            if result:
                sentiment = result.get("sentiment", "neutral")
                confidence = result.get("confidence", 0.0)
                probabilities = result.get("probabilities", {})

                colors = SENTIMENT_COLORS[sentiment]

                st.markdown(f"""
                <div class="prediction-card">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <span style="font-size: 2.5rem;">{colors['icon']}</span>
                        <div>
                            <div class="sentiment-badge" style="background: {colors['bg']}; color: {colors['text']};">
                                {sentiment.capitalize()}
                            </div>
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                                Model: {model}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.plotly_chart(
                    render_confidence_gauge(confidence, sentiment),
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

                st.markdown("### Class Probabilities")
                for label, prob in probabilities.items():
                    pct = prob * 100
                    label_colors = SENTIMENT_COLORS.get(label, SENTIMENT_COLORS["neutral"])
                    st.markdown(f"""
                    <div style="margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                            <span class="sentiment-badge" style="background: {label_colors['bg']}; color: {label_colors['text']}; font-size: 0.75rem;">{label.capitalize()}</span>
                            <span style="font-weight: 600; color: var(--text-primary);">{pct:.1f}%</span>
                        </div>
                        <div class="confidence-bar">
                            <div class="confidence-fill {label_colors['fill']}" style="width: {pct}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        elif analyze_btn and not text.strip():
            st.warning("Please enter some text to analyze.")

        if batch_btn and batch_text.strip():
            reviews = [r.strip() for r in batch_text.strip().split("\n") if r.strip()]
            with st.spinner(f"Analyzing {len(reviews)} reviews..."):
                results = predict_batch(reviews, model_key)

            if results:
                st.markdown(f"### Batch Results ({len(results)} reviews)")

                sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
                for r in results:
                    sentiment_counts[r.get("sentiment", "neutral")] += 1

                col_p, col_n, col_neu = st.columns(3)
                with col_p:
                    st.metric("Positive", sentiment_counts["positive"])
                with col_n:
                    st.metric("Negative", sentiment_counts["negative"])
                with col_neu:
                    st.metric("Neutral", sentiment_counts["neutral"])

                for i, (review, result) in enumerate(zip(reviews, results)):
                    sentiment = result.get("sentiment", "neutral")
                    confidence = result.get("confidence", 0.0)
                    colors = SENTIMENT_COLORS[sentiment]

                    with st.expander(f"Review {i+1}: {sentiment.capitalize()} ({confidence:.0%})"):
                        st.write(review[:200] + ("..." if len(review) > 200 else ""))
                        st.markdown(f"""
                        <div class="sentiment-badge" style="background: {colors['bg']}; color: {colors['text']};">
                            {sentiment.capitalize()} • {confidence:.0%} confidence
                        </div>
                        """, unsafe_allow_html=True)

        elif batch_btn and not batch_text.strip():
            st.warning("Please enter at least one review for batch analysis.")

        if not analyze_btn and not batch_btn:
            st.markdown("""
            <div class="chart-container" style="text-align: center; padding: 3rem 1.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="color: var(--text-muted); margin-bottom: 1rem;">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <h3 style="color: var(--text-secondary); margin: 0 0 0.5rem;">Ready to Analyze</h3>
                <p style="color: var(--text-muted); margin: 0;">Enter a review on the left and click <strong>Analyze Sentiment</strong> to get started.</p>
            </div>
            """, unsafe_allow_html=True)


def render_batch_results(results: list):
    pass