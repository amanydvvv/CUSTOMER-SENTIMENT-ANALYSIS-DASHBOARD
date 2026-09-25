import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.api_client import load_keywords


SENTIMENT_CONFIG = {
    "positive": {"color": "#22c55e", "bg": "#dcfce7", "text": "#166534", "icon": "😊", "label": "Positive"},
    "negative": {"color": "#ef4444", "bg": "#fee2e2", "text": "#991b1b", "icon": "☹️", "label": "Negative"},
    "neutral": {"color": "#f59e0b", "bg": "#fef3c7", "text": "#92400e", "icon": "😐", "label": "Neutral"},
}


def render_keyword_chips(keywords: list, sentiment: str, max_chips: int = 30):
    config = SENTIMENT_CONFIG[sentiment]
    chips_html = ""
    for kw in keywords[:max_chips]:
        term = kw.get("term", "")
        score = kw.get("score", 0)
        chips_html += f"""
        <span class="keyword-chip">
            {term}
            <span class="score">{score:.3f}</span>
        </span>
        """
    return chips_html


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Keyword Insights</h1>
        <p class="page-subtitle">Top TF-IDF terms driving sentiment classification</p>
    </div>
    """, unsafe_allow_html=True)

    col_controls = st.columns([3, 1, 1])
    with col_controls[1]:
        top_k = st.selectbox("Top K terms", [15, 20, 30, 50], index=1, key="kw_top_k")
    with col_controls[2]:
        view_mode = st.selectbox("View", ["Charts", "Chips", "Table"], index=0, key="kw_view_mode")

    tabs = st.tabs(["😊 Positive", "☹️ Negative", "😐 Neutral", "📊 Comparison"])

    for sentiment in ["positive", "negative", "neutral"]:
        with tabs[["positive", "negative", "neutral"].index(sentiment)]:
            config = SENTIMENT_CONFIG[sentiment]

            with st.spinner(f"Loading {config['label']} keywords..."):
                keywords = load_keywords(sentiment, top_k)

            if not keywords:
                st.warning(f"No keyword data available for {config['label']} sentiment.")
                continue

            df_kw = pd.DataFrame(keywords)
            df_kw = df_kw.sort_values("score", ascending=True)

            if view_mode == "Charts":
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<h3 class="chart-title">Top {top_k} {config["label"]} Keywords</h3>', unsafe_allow_html=True)

                fig = px.bar(
                    df_kw.tail(top_k),
                    x="score",
                    y="term",
                    orientation="h",
                    color="score",
                    color_continuous_scale=[[0, "#e2e8f0"], [1, config["color"]]],
                )
                fig.update_layout(
                    xaxis_title="TF-IDF Score",
                    yaxis_title="",
                    coloraxis_showscale=False,
                    margin=dict(t=10, b=40, l=10, r=10),
                    font=dict(family="Inter"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=max(400, top_k * 25),
                )
                fig.update_traces(
                    hovertemplate="<b>%{y}</b><br>Score: %{x:.4f}<extra></extra>",
                    marker_line_width=0,
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                st.markdown('</div>', unsafe_allow_html=True)

            elif view_mode == "Chips":
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<h3 class="chart-title">Top {top_k} {config["label"]} Keywords</h3>', unsafe_allow_html=True)

                chips_html = render_keyword_chips(keywords, sentiment, top_k)
                st.markdown(f'<div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">{chips_html}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            else:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown(f'<h3 class="chart-title">Top {top_k} {config["label"]} Keywords</h3>', unsafe_allow_html=True)

                display_df = df_kw.tail(top_k)[::-1].reset_index(drop=True)
                display_df.index += 1
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=False,
                    column_config={
                        "term": st.column_config.TextColumn("Keyword", width="medium"),
                        "score": st.column_config.NumberColumn("TF-IDF Score", format="%.4f", width="small"),
                    },
                )
                st.markdown('</div>', unsafe_allow_html=True)

    with tabs[3]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Cross-Sentiment Keyword Comparison</h3>', unsafe_allow_html=True)

        all_keywords = {}
        for sentiment in ["positive", "negative", "neutral"]:
            kw = load_keywords(sentiment, top_k)
            if kw:
                all_keywords[sentiment] = {item["term"]: item["score"] for item in kw}

        if all_keywords:
            all_terms = set()
            for kw_dict in all_keywords.values():
                all_terms.update(kw_dict.keys())

            comparison_data = []
            for term in all_terms:
                row = {"Keyword": term}
                for sentiment in ["positive", "negative", "neutral"]:
                    row[SENTIMENT_CONFIG[sentiment]["label"]] = all_keywords.get(sentiment, {}).get(term, 0)
                comparison_data.append(row)

            df_comp = pd.DataFrame(comparison_data)
            df_comp["Max Score"] = df_comp[["Positive", "Negative", "Neutral"]].max(axis=1)
            df_comp["Dominant"] = df_comp[["Positive", "Negative", "Neutral"]].idxmax(axis=1)
            df_comp = df_comp.sort_values("Max Score", ascending=False).head(top_k)

            fig = go.Figure()
            for sentiment in ["positive", "negative", "neutral"]:
                config = SENTIMENT_CONFIG[sentiment]
                label = config["label"]
                fig.add_trace(go.Bar(
                    name=label,
                    x=df_comp["Keyword"][::-1],
                    y=df_comp[label][::-1],
                    marker_color=config["color"],
                    hovertemplate=f"<b>%{{x}}</b><br>{label}: %{{y:.4f}}<extra></extra>",
                ))

            fig.update_layout(
                barmode="group",
                xaxis_title="",
                yaxis_title="TF-IDF Score",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=12, family="Inter"),
                ),
                margin=dict(t=40, b=100, l=40, r=40),
                font=dict(family="Inter"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=500,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            st.markdown("### Unique Keywords per Sentiment")
            col_p, col_n, col_neu = st.columns(3)

            for sentiment, col in zip(["positive", "negative", "neutral"], [col_p, col_n, col_neu]):
                config = SENTIMENT_CONFIG[sentiment]
                with col:
                    st.markdown(f"**{config['label']} Unique**")
                    unique_terms = set(all_keywords.get(sentiment, {}).keys())
                    other_terms = set()
                    for s in ["positive", "negative", "neutral"]:
                        if s != sentiment:
                            other_terms.update(all_keywords.get(s, {}).keys())
                    unique = unique_terms - other_terms
                    for term in sorted(unique, key=lambda x: all_keywords[sentiment].get(x, 0), reverse=True)[:10]:
                        score = all_keywords[sentiment].get(term, 0)
                        st.markdown(f"""
                        <span class="keyword-chip" style="background: {config['bg']}; color: {config['text']};">
                            {term}
                            <span class="score" style="background: var(--bg-primary);">{score:.3f}</span>
                        </span>
                        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("ℹ️ About TF-IDF Keywords", expanded=False):
        st.markdown("""
        **Term Frequency-Inverse Document Frequency (TF-IDF)** measures how important a word is to a document in a collection.

        - **TF (Term Frequency)**: How often a term appears in a review
        - **IDF (Inverse Document Frequency)**: How rare the term is across all reviews
        - **TF-IDF Score**: High scores indicate terms that are frequent in specific reviews but rare overall — strong sentiment indicators

        **Configuration used:**
        - N-gram range: (1, 2) — unigrams and bigrams
        - Max features: 10,000
        - Stopwords: NLTK English (negations preserved)
        - Preprocessing: Lowercase, HTML/URL removal, contraction expansion
        """)


def render_keyword_comparison(keywords_by_sentiment: dict, top_k: int):
    pass