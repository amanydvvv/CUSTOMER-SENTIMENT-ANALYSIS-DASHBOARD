"""
4_model_comparison.py
─────────────────────
Model Performance & Comparison page.
Dark-themed, objective benchmark presentation without rankings or gimmicks.
Uses render_html from frontend.ui_utils to guarantee zero raw HTML leaks.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from frontend.ui_utils import render_html
from frontend.api_client import load_model_metrics

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "backend", "models")
EVAL_RESULTS_PATH = os.path.join(MODELS_DIR, "evaluation_results.json")


def _load_eval_details():
    if os.path.exists(EVAL_RESULTS_PATH):
        try:
            with open(EVAL_RESULTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def render():
    header_html = """
    <div style="margin-bottom:1.25rem;border-bottom:1px solid #1E2533;padding-bottom:1rem;">
        <h1 style="font-size:1.85rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0 0 0.2rem;line-height:1.2;">
            MODEL BENCHMARK & EVALUATION
        </h1>
        <div style="color:#98A2B3;font-size:0.88rem;margin:0;">
            Objective empirical evaluation on held-out test split (16,336 Amazon Customer Reviews)
        </div>
    </div>
    """
    render_html(header_html)

    eval_data = _load_eval_details()
    if not eval_data:
        metrics_from_api = load_model_metrics()
        if metrics_from_api:
            eval_data = metrics_from_api

    if not eval_data:
        st.error("No model evaluation metrics found. Please verify backend/models/evaluation_results.json.")
        return

    # Benchmark Summary Cards
    col1, col2, col3 = st.columns(3)
    for i, item in enumerate(eval_data):
        m_name = {
            "logistic_regression": "Standard Logistic Regression",
            "balanced_logistic_regression": "Balanced Logistic Regression",
            "linearsvc": "Linear Support Vector Classifier"
        }.get(item["model_name"], item["model_name"])

        with [col1, col2, col3][i % 3]:
            card_html = f"""
            <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1rem;margin-bottom:0.75rem;">
                <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.3rem;">
                    {m_name}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
                    <div style="background:#151A24;padding:0.5rem;border-radius:4px;border:1px solid #242A35;">
                        <div style="font-size:0.65rem;color:#98A2B3;text-transform:uppercase;">Accuracy</div>
                        <div style="font-size:1.15rem;font-weight:800;color:#F5F7FA;">{item['accuracy'] * 100:.2f}%</div>
                    </div>
                    <div style="background:#151A24;padding:0.5rem;border-radius:4px;border:1px solid #242A35;">
                        <div style="font-size:0.65rem;color:#98A2B3;text-transform:uppercase;">Macro F1</div>
                        <div style="font-size:1.15rem;font-weight:800;color:#22D3EE;">{item.get('macro_f1', item.get('f1', 0.0)):.4f}</div>
                    </div>
                    <div style="background:#151A24;padding:0.5rem;border-radius:4px;border:1px solid #242A35;">
                        <div style="font-size:0.65rem;color:#98A2B3;text-transform:uppercase;">Weighted F1</div>
                    <div style="background:#151A24;padding:0.5rem;border-radius:4px;border:1px solid #242A35;">
                        <div style="font-size:0.65rem;color:#98A2B3;text-transform:uppercase;">Macro Recall</div>
                        <div style="font-size:1.15rem;font-weight:800;color:#22C55E;">{item.get('macro_recall', item.get('recall', 0.0)) * 100:.2f}%</div>
                    </div>
                </div>
            </div>
            """
            render_html(card_html)

    # Explanatory Evaluation Protocol Callout
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-left:4px solid #7C5CFF;border-radius:6px;padding:0.75rem 1rem;margin:0.5rem 0 0.85rem 0;">
        <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;margin-bottom:0.2rem;display:flex;align-items:center;gap:6px;text-transform:uppercase;letter-spacing:0.05em;">
            <span>⚡</span> <span>Evaluation Protocol: Macro vs. Weighted Metrics</span>
        </div>
        <div style="font-size:0.74rem;color:#98A2B3;line-height:1.45;">
            Due to customer review class imbalance (~70% positive), <b>Macro Recall & Macro Precision</b> evaluate unweighted per-class performance across Positive, Neutral, and Negative categories. 
            While Standard LR achieves higher raw accuracy by defaulting to positive, <b>Balanced Logistic Regression achieves higher Macro Recall (70.84% vs 61.89%) and Macro F1 (0.6677 vs 0.6253)</b>, accurately detecting customer dissatisfaction.
        </div>
    </div>
    """)

    # Comparison Table
    df_metrics = pd.DataFrame([
        {
            "Model": {
                "logistic_regression": "Standard Logistic Regression",
                "balanced_logistic_regression": "Balanced Logistic Regression",
                "linearsvc": "LinearSVC"
            }.get(item["model_name"], item["model_name"]),
            "Accuracy": f"{item['accuracy'] * 100:.2f}%",
            "Macro Recall": f"{item.get('macro_recall', item.get('recall', 0.0)) * 100:.2f}%",
            "Macro Precision": f"{item.get('macro_precision', item.get('precision', 0.0)) * 100:.2f}%",
            "Macro F1": f"{item.get('macro_f1', item.get('f1', 0.0)):.4f}",
            "Weighted F1": f"{item.get('weighted_f1', 0.0):.4f}",
            "Batch Latency": f"{item.get('latency', 0.0):.4f} ms/sample",
        }
        for item in eval_data
    ])

    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:0.75rem 1rem;margin-top:0.5rem;margin-bottom:0.85rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;">
            Comparative Metrics Table
        </div>
    </div>
    """)
    st.dataframe(df_metrics, use_container_width=True, hide_index=True)

    # Visual Comparison Bar Charts
    col_f1, col_acc = st.columns(2)

    df_chart = pd.DataFrame([
        {
            "Model": item["model_name"].replace("_", " ").title(),
            "Accuracy": item["accuracy"],
            "Macro F1": item.get("macro_f1", item.get("f1", 0.0)),
            "Weighted F1": item.get("weighted_f1", 0.0)
        }
        for item in eval_data
    ])

    with col_f1:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1rem 1.25rem;">
            <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
                Macro F1 Score (Minority Class Balance)
            </div>
            <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.75rem;">
                Higher Macro F1 reflects balanced detection across Positive, Neutral, Negative
            </div>
        </div>
        """)

        fig_f1 = px.bar(
            df_chart,
            x="Model",
            y="Macro F1",
            color="Model",
            text="Macro F1",
            color_discrete_sequence=["#7C5CFF", "#22D3EE", "#22C55E"]
        )
        fig_f1.update_traces(texttemplate="%{text:.4f}", textposition="outside", textfont=dict(color="#F5F7FA"))
        fig_f1.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3")),
            xaxis=dict(tickfont=dict(color="#F5F7FA")),
            showlegend=False
        )
        st.plotly_chart(fig_f1, use_container_width=True, config={"displayModeBar": False})

    with col_acc:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1rem 1.25rem;">
            <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
                Overall Classification Accuracy
            </div>
            <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:0.75rem;">
                Percentage of correct predictions over 16,336 test samples
            </div>
        </div>
        """)

        fig_acc = px.bar(
            df_chart,
            x="Model",
            y="Accuracy",
            color="Model",
            text="Accuracy",
            color_discrete_sequence=["#7C5CFF", "#22D3EE", "#22C55E"]
        )
        fig_acc.update_traces(texttemplate="%{text:.2%}", textposition="outside", textfont=dict(color="#F5F7FA"))
        fig_acc.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="#1E2533", tickfont=dict(color="#98A2B3")),
            xaxis=dict(tickfont=dict(color="#F5F7FA")),
            showlegend=False
        )
        st.plotly_chart(fig_acc, use_container_width=True, config={"displayModeBar": False})

    # Confusion Matrices
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:8px;padding:1.1rem 1.25rem;margin-top:1.25rem;">
        <div style="font-size:0.75rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.25rem;">
            Confusion Matrices on Held-Out Test Set (16,336 Reviews)
        </div>
        <div style="font-size:0.78rem;color:#98A2B3;margin-bottom:1rem;">
            Breakdown of True vs. Predicted classes across all three models
        </div>
    </div>
    """)

    cm_cols = st.columns(len(eval_data))
    labels = ["Negative", "Neutral", "Positive"]

    for i, item in enumerate(eval_data):
        with cm_cols[i]:
            m_name = item["model_name"].replace("_", " ").title()
            cm = item.get("confusion_matrix", [])
            if cm:
                fig_cm = px.imshow(
                    cm,
                    labels=dict(x="Predicted", y="True Label", color="Count"),
                    x=labels,
                    y=labels,
                    text_auto=True,
                    color_continuous_scale=[[0, "#151A24"], [0.5, "#3730A3"], [1, "#7C5CFF"]]
                )
                fig_cm.update_layout(
                    title=f"<b style='color:#F5F7FA;font-size:13px;'>{m_name}</b>",
                    height=260,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#F5F7FA"),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_cm, use_container_width=True, config={"displayModeBar": False})


if __name__ == "__main__":
    render()