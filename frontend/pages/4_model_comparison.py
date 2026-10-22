"""
4_model_comparison.py
─────────────────────
Model Performance & Comparison page.
Dark-themed, objective empirical benchmark presentation without gimmicks.
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
    render_html("""
    <div style="margin-bottom:20px;border-bottom:1px solid rgba(255,255,255,0.06);padding-bottom:16px;">
        <h1 style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:-0.02em;margin:0 0 4px;line-height:1.2;">
            Model Benchmark &amp; Evaluation
        </h1>
        <div style="color:#9ca3af;font-size:13px;margin:0;">
            Objective empirical evaluation on held-out test split (16,336 Amazon Customer Reviews)
        </div>
    </div>
    """)

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
            <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:20px;margin-bottom:12px;">
                <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:8px;">
                    {m_name}
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px;">
                    <div style="background:#181b21;padding:12px;border-radius:6px;border:1px solid rgba(255,255,255,0.07);">
                        <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;">Accuracy</div>
                        <div style="font-size:20px;font-weight:700;color:#ffffff;">{item['accuracy'] * 100:.2f}%</div>
                    </div>
                    <div style="background:#181b21;padding:12px;border-radius:6px;border:1px solid rgba(255,255,255,0.07);">
                        <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;">Macro F1</div>
                        <div style="font-size:20px;font-weight:700;color:#10b981;">{item.get('macro_f1', item.get('f1', 0.0)):.4f}</div>
                    </div>
                    <div style="background:#181b21;padding:12px;border-radius:6px;border:1px solid rgba(255,255,255,0.07);">
                        <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;">Weighted F1</div>
                        <div style="font-size:20px;font-weight:700;color:#ffffff;">{item.get('weighted_f1', 0.0):.4f}</div>
                    </div>
                    <div style="background:#181b21;padding:12px;border-radius:6px;border:1px solid rgba(255,255,255,0.07);">
                        <div style="font-size:10px;color:#9ca3af;text-transform:uppercase;">Macro Recall</div>
                        <div style="font-size:20px;font-weight:700;color:#10b981;">{item.get('macro_recall', item.get('recall', 0.0)) * 100:.2f}%</div>
                    </div>
                </div>
            </div>
            """
            render_html(card_html)

    # Explanatory Evaluation Protocol Callout
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-left:3px solid #10b981;border-radius:0 8px 8px 0;padding:14px 18px;margin:12px 0 16px 0;">
        <div style="font-size:11px;font-weight:600;color:#10b981;margin-bottom:4px;text-transform:uppercase;letter-spacing:0.05em;">
            Evaluation Protocol: Macro vs. Weighted Metrics
        </div>
        <div style="font-size:13px;color:#9ca3af;line-height:1.5;">
            Due to natural customer review class imbalance (~70% positive), <b>Macro Recall and Macro Precision</b> evaluate unweighted per-class performance across Positive, Neutral, and Negative categories. 
            While Standard LR achieves higher raw accuracy by prioritizing majority-class positive samples, <b>Balanced Logistic Regression achieves higher Macro Recall (70.84% vs 61.89%) and Macro F1 (0.6677 vs 0.6253)</b>, reliably surfacing critical customer friction.
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
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:14px 18px;margin-bottom:12px;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;">
            Comparative Metrics Table
        </div>
    </div>
    """)
    st.dataframe(df_metrics, width='stretch', hide_index=True)

    # Visual Comparison Bar Charts (Rule 4: side-by-side st.columns(2))
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
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                Macro F1 Score (Minority Class Balance)
            </div>
            <div style="font-size:12px;color:#6b7280;margin-bottom:12px;">
                Higher Macro F1 reflects balanced detection across Positive, Neutral, Negative
            </div>
        </div>
        """)

        fig_f1 = px.bar(
            df_chart,
            x="Model",
            y="Macro F1",
            text="Macro F1",
            color_discrete_sequence=["#10b981"]
        )
        fig_f1.update_traces(texttemplate="%{text:.4f}", textposition="outside", textfont=dict(color="#ffffff"))
        fig_f1.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af")),
            xaxis=dict(tickfont=dict(color="#ffffff")),
            showlegend=False
        )
        st.plotly_chart(fig_f1, width='stretch', config={"displayModeBar": False})

    with col_acc:
        render_html("""
        <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;">
            <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
                Overall Classification Accuracy
            </div>
            <div style="font-size:12px;color:#6b7280;margin-bottom:12px;">
                Percentage of correct predictions over 16,336 test samples
            </div>
        </div>
        """)

        fig_acc = px.bar(
            df_chart,
            x="Model",
            y="Accuracy",
            text="Accuracy",
            color_discrete_sequence=["#3b82f6"]
        )
        fig_acc.update_traces(texttemplate="%{text:.2%}", textposition="outside", textfont=dict(color="#ffffff"))
        fig_acc.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=25, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(range=[0, 1.0], showgrid=True, gridcolor="rgba(255,255,255,0.06)", tickfont=dict(color="#9ca3af")),
            xaxis=dict(tickfont=dict(color="#ffffff")),
            showlegend=False
        )
        st.plotly_chart(fig_acc, width='stretch', config={"displayModeBar": False})

    # Confusion Matrices
    render_html("""
    <div style="background:#111317;border:1px solid rgba(255,255,255,0.07);border-radius:8px;padding:16px 20px;margin-top:20px;margin-bottom:14px;">
        <div style="font-size:11px;font-weight:600;color:#9ca3af;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:4px;">
            Confusion Matrices on Held-Out Test Set (16,336 Reviews)
        </div>
        <div style="font-size:12px;color:#6b7280;">
            Breakdown of True vs. Predicted classes across all three benchmark models
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
                    color_continuous_scale=[[0, "#111317"], [0.5, "#1e293b"], [1, "#10b981"]]
                )
                fig_cm.update_layout(
                    title=f"<b style='color:#ffffff;font-size:13px;'>{m_name}</b>",
                    height=260,
                    margin=dict(l=10, r=10, t=30, b=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff"),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_cm, width='stretch', config={"displayModeBar": False})


if __name__ == "__main__":
    render()