import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from typing import List, Dict, Any


def render_wordcloud_view(feedback_records: List[Dict[str, Any]]):
    """Generate and display visual word clouds filtered by sentiment polarity."""
    if not feedback_records:
        st.info("No feedback records available to generate word cloud.")
        return

    st.markdown("### ☁️ Customer Sentiment & Keyword Word Clouds")

    c1, c2 = st.columns([1, 3])
    with c1:
        sentiment_filter = st.selectbox(
            "Filter Word Cloud Polarity",
            ["All Reviews", "Positive Only", "Negative Only", "Neutral Only"],
            key="wc_polarity_select",
        )
        max_words = st.slider("Max Keywords", 20, 100, 50, key="wc_max_words")

    # Filter texts based on selection
    if sentiment_filter == "Positive Only":
        filtered = [r["review_text"] for r in feedback_records if r.get("sentiment") == "positive"]
        colormap = "Greens"
        bg_color = "#0F172A"
    elif sentiment_filter == "Negative Only":
        filtered = [r["review_text"] for r in feedback_records if r.get("sentiment") == "negative"]
        colormap = "Reds"
        bg_color = "#0F172A"
    elif sentiment_filter == "Neutral Only":
        filtered = [r["review_text"] for r in feedback_records if r.get("sentiment") == "neutral"]
        colormap = "Blues"
        bg_color = "#0F172A"
    else:
        filtered = [r["review_text"] for r in feedback_records]
        colormap = "plasma"
        bg_color = "#0F172A"

    if not filtered:
        st.warning(f"No records found matching '{sentiment_filter}'")
        return

    combined_text = " ".join(filtered)

    with c2:
        try:
            wc = WordCloud(
                width=800,
                height=360,
                background_color=bg_color,
                colormap=colormap,
                max_words=max_words,
                collocations=True,
                stopwords={
                    "the", "and", "is", "it", "to", "for", "with", "my", "was",
                    "of", "this", "in", "on", "that", "very", "have", "are", "but", "so"
                }
            ).generate(combined_text)

            fig, ax = plt.subplots(figsize=(10, 4.5), facecolor=bg_color)
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig)
            plt.close(fig)
        except Exception as e:
            st.error(f"Error generating word cloud: {e}")
