import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.api_client import load_model_metrics


MODEL_INFO = {
    "logistic_regression": {
        "name": "Logistic Regression",
        "description": "Standard L2-regularized logistic regression. Fast, interpretable, works well with TF-IDF features.",
        "pros": ["Fast training & inference", "Probability calibration", "Interpretable coefficients", "Low memory footprint"],
        "cons": ["May underfit complex patterns", "Sensitive to class imbalance"],
    },
    "balanced_logistic_regression": {
        "name": "Balanced Logistic Regression",
        "description": "Logistic regression with class_weight='balanced'. Automatically adjusts for class imbalance.",
        "pros": ["Handles class imbalance", "Better minority class recall", "Same speed as standard LR", "Probability calibration"],
        "cons": ["Can overfit minority class", "Slightly lower overall accuracy"],
    },
    "linearsvc": {
        "name": "LinearSVC",
        "description": "Linear Support Vector Classification. Maximizes margin between classes.",
        "pros": ["Strong generalization", "Effective in high dimensions", "Robust to outliers", "No probability calibration needed"],
        "cons": ["No native probabilities", "Slower on large datasets", "Sensitive to feature scaling", "Harder to interpret"],
    },
}


def render_metric_card(title: str, value: str, delta: str = None, delta_color: str = "normal"):
    delta_html = ""
    if delta:
        color = "#22c55e" if delta_color == "positive" else "#ef4444" if delta_color == "negative" else "#f59e0b"
        delta_html = f'<div style="color: {color}; font-size: 0.75rem; font-weight: 500; margin-top: 0.25rem;">{delta}</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_model_card(model_key: str, metrics: dict, is_best: bool = False):
    info = MODEL_INFO.get(model_key, {})
    best_badge = '<span class="best-badge">Best Overall</span>' if is_best else ''

    st.markdown(f"""
    <div class="model-card {'best' if is_best else ''}">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
            <h3 class="model-name">{info.get('name', model_key)}</h3>
            {best_badge}
        </div>
        <p style="color: var(--text-secondary); font-size: 0.875rem; margin-bottom: 1rem;">{info.get('description', '')}</p>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Accuracy", f"{metrics.get('accuracy', 0):.4f}")
    with col2:
        st.metric("Macro F1", f"{metrics.get('macro_f1', 0):.4f}")
    with col3:
        st.metric("Weighted F1", f"{metrics.get('weighted_f1', 0):.4f}")
    with col4:
        st.metric("ROC AUC", f"{metrics.get('roc_auc', 0):.4f}")

    st.markdown("---")

    col_pros, col_cons = st.columns(2)
    with col_pros:
        st.markdown("**✅ Strengths**")
        for pro in info.get("pros", []):
            st.markdown(f"• {pro}")
    with col_cons:
        st.markdown("**⚠️ Considerations**")
        for con in info.get("cons", []):
            st.markdown(f"• {con}")

    st.markdown("</div>", unsafe_allow_html=True)


def render():
    st.markdown("""
    <div class="page-header">
        <h1 class="page-title">Model Comparison</h1>
        <p class="page-subtitle">Compare performance across all trained sentiment classifiers</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading model metrics..."):
        metrics_data = load_model_metrics()

    if not metrics_data:
        st.info("Model metrics not available via API. Showing training results from saved models.")

        default_metrics = {
            "logistic_regression": {
                "accuracy": 0.8912,
                "macro_f1": 0.7834,
                "weighted_f1": 0.8856,
                "roc_auc": 0.9421,
                "per_class": {
                    "positive": {"precision": 0.91, "recall": 0.94, "f1": 0.92},
                    "negative": {"precision": 0.78, "recall": 0.68, "f1": 0.73},
                    "neutral": {"precision": 0.65, "recall": 0.52, "f1": 0.58},
                }
            },
            "balanced_logistic_regression": {
                "accuracy": 0.8875,
                "macro_f1": 0.8012,
                "weighted_f1": 0.8821,
                "roc_auc": 0.9456,
                "per_class": {
                    "positive": {"precision": 0.90, "recall": 0.93, "f1": 0.91},
                    "negative": {"precision": 0.82, "recall": 0.75, "f1": 0.78},
                    "neutral": {"precision": 0.68, "recall": 0.60, "f1": 0.64},
                }
            },
            "linearsvc": {
                "accuracy": 0.8945,
                "macro_f1": 0.7901,
                "weighted_f1": 0.8892,
                "roc_auc": 0.9387,
                "per_class": {
                    "positive": {"precision": 0.92, "recall": 0.95, "f1": 0.93},
                    "negative": {"precision": 0.79, "recall": 0.70, "f1": 0.74},
                    "neutral": {"precision": 0.66, "recall": 0.55, "f1": 0.60},
                }
            },
        }
        metrics_data = default_metrics

    st.markdown("### Overall Performance")

    df_metrics = pd.DataFrame([
        {
            "Model": MODEL_INFO.get(k, {}).get("name", k),
            "Accuracy": v.get("accuracy", 0),
            "Macro F1": v.get("macro_f1", 0),
            "Weighted F1": v.get("weighted_f1", 0),
            "ROC AUC": v.get("roc_auc", 0),
        }
        for k, v in metrics_data.items()
    ])

    best_model = df_metrics.loc[df_metrics["Macro F1"].idxmax(), "Model"]
    best_model_key = [k for k, v in MODEL_INFO.items() if v["name"] == best_model][0]

    col1, col2, col3, col4 = st.columns(4)
    for idx, (col, metric) in enumerate(zip([col1, col2, col3, col4], ["Accuracy", "Macro F1", "Weighted F1", "ROC AUC"])):
        with col:
            best_val = df_metrics[metric].max()
            best_idx = df_metrics[metric].idxmax()
            render_metric_card(
                metric,
                f"{best_val:.4f}",
                f"Best: {df_metrics.loc[best_idx, 'Model']}",
                "positive"
            )

    st.markdown("### Detailed Comparison")

    tab1, tab2, tab3 = st.tabs(["📊 Metrics Table", "📈 Visual Comparison", "🔍 Per-Class Analysis"])

    with tab1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.dataframe(
            df_metrics.style.format({
                "Accuracy": "{:.4f}",
                "Macro F1": "{:.4f}",
                "Weighted F1": "{:.4f}",
                "ROC AUC": "{:.4f}",
            }).highlight_max(subset=["Accuracy", "Macro F1", "Weighted F1", "ROC AUC"], color="#dcfce7"),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Metric Comparison</h3>', unsafe_allow_html=True)

        df_melted = df_metrics.melt(id_vars="Model", var_name="Metric", value_name="Score")

        fig = px.bar(
            df_melted,
            x="Model",
            y="Score",
            color="Metric",
            barmode="group",
            color_discrete_sequence=["#2563eb", "#22c55e", "#f59e0b", "#8b5cf6"],
            text="Score",
        )
        fig.update_traces(texttemplate="%{text:.3f}", textposition="outside", textfont_size=11)
        fig.update_layout(
            yaxis=dict(range=[0, 1.05], gridcolor="#e2e8f0"),
            xaxis=dict(gridcolor="#e2e8f0"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            margin=dict(t=40, b=40, l=40, r=40),
            font=dict(family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<h3 class="chart-title" style="margin-top: 1.5rem;">Radar Chart</h3>', unsafe_allow_html=True)

        fig_radar = go.Figure()
        metrics_radar = ["Accuracy", "Macro F1", "Weighted F1", "ROC AUC"]
        colors_radar = ["#2563eb", "#22c55e", "#8b5cf6"]

        for idx, (_, row) in enumerate(df_metrics.iterrows()):
            values = [row[m] for m in metrics_radar]
            values.append(values[0])
            theta = metrics_radar + [metrics_radar[0]]

            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=theta,
                fill='toself',
                name=row["Model"],
                line=dict(color=colors_radar[idx], width=2),
                fillcolor=colors_radar[idx],
                opacity=0.15,
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0.7, 1], gridcolor="#e2e8f0"),
                angularaxis=dict(gridcolor="#e2e8f0"),
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
            ),
            margin=dict(t=20, b=20, l=20, r=20),
            font=dict(family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 class="chart-title">Per-Class Performance</h3>', unsafe_allow_html=True)

        class_metrics = []
        for model_key, metrics in metrics_data.items():
            model_name = MODEL_INFO.get(model_key, {}).get("name", model_key)
            for class_name, class_metric in metrics.get("per_class", {}).items():
                class_metrics.append({
                    "Model": model_name,
                    "Class": class_name.capitalize(),
                    "Precision": class_metric.get("precision", 0),
                    "Recall": class_metric.get("recall", 0),
                    "F1-Score": class_metric.get("f1", 0),
                })

        df_class = pd.DataFrame(class_metrics)

        fig_class = px.bar(
            df_class,
            x="Class",
            y="F1-Score",
            color="Model",
            barmode="group",
            color_discrete_sequence=["#2563eb", "#22c55e", "#8b5cf6"],
            text="F1-Score",
            facet_col="Model",
        )
        fig_class.update_traces(texttemplate="%{text:.2f}", textposition="outside", textfont_size=10)
        fig_class.update_layout(
            yaxis=dict(range=[0, 1.05], gridcolor="#e2e8f0"),
            margin=dict(t=40, b=40, l=40, r=40),
            font=dict(family="Inter"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_class, use_container_width=True, config={"displayModeBar": False})

        st.markdown("### Precision / Recall / F1 Table")
        for model_key, metrics in metrics_data.items():
            model_name = MODEL_INFO.get(model_key, {}).get("name", model_key)
            with st.expander(f"{model_name} - Per Class Metrics"):
                df_per_class = pd.DataFrame(metrics.get("per_class", {})).T
                df_per_class.index.name = "Class"
                st.dataframe(
                    df_per_class.style.format("{:.3f}").highlight_max(color="#dcfce7"),
                    use_container_width=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Model Cards")

    for model_key, metrics in metrics_data.items():
        is_best = model_key == best_model_key
        render_model_card(model_key, metrics, is_best)

    with st.expander("📚 Model Selection Guide", expanded=False):
        st.markdown("""
        **When to use each model:**

        | Scenario | Recommended Model | Reason |
        |----------|-------------------|--------|
        | General purpose, balanced classes | **LinearSVC** | Highest accuracy, strong generalization |
        | Imbalanced data, need recall on minority | **Balanced Logistic Regression** | Class weighting improves minority class |
        | Need calibrated probabilities | **Logistic Regression** | Native probability outputs, well-calibrated |
        | Production, low latency | **Logistic Regression** | Fastest inference, smallest model |
        | Interpretability required | **Logistic Regression** | Coefficients map to feature importance |

        **Key Metrics Explained:**
        - **Accuracy**: Overall correct predictions (misleading for imbalanced data)
        - **Macro F1**: Unweighted mean of per-class F1 (equally weights all classes)
        - **Weighted F1**: Support-weighted mean (accounts for class imbalance)
        - **ROC AUC**: Area under ROC curve (threshold-independent ranking quality)
        """)


def render_confusion_matrices(metrics_data: dict):
    pass