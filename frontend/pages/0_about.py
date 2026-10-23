"""
0_about.py
──────────
Home / About page — executive overview of Customer Sentiment Intelligence.
Adheres strictly to Linear / Vercel Minimalist Dark aesthetic and the 7 Dashboard Design Rules.
Hero layout: [2, 1, 1, 1] — Decisive benchmark card + 3 supporting metrics above the fold.
"""

import streamlit as st
import json
import os
from frontend.ui_utils import render_html

EVAL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "backend", "models", "evaluation_results.json"
)


def _load_eval():
    try:
        if os.path.exists(EVAL_PATH):
            with open(EVAL_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def render():
    # ── 1. Page Header ─────────────────────────────────────────────────────────
    render_html("""
    <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.07); margin-bottom: 28px;">
        <h1 style="font-size: 1.75rem; font-weight: 600; letter-spacing: -0.02em; color: #ffffff; margin: 0 0 0.5rem 0; line-height: 1.2;">
            Customer Sentiment Intelligence
        </h1>
        <p style="color: #9ca3af; font-size: 0.88rem; font-weight: 400; line-height: 1.6; max-width: 820px; margin: 0;">
            A production-grade NLP intelligence system processing 81,700 Amazon reviews with machine learning
            to extract sentiment, surface product pain points, and deliver actionable business insights
            through a real-time analytics dashboard.
        </p>
    </div>
    """)

    # ── 2. Hero Metric Strip (Rule 1: Prioritize Key Metrics) — [2, 1, 1, 1] ───
    hero_col, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with hero_col:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 24px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;">
                Decisive Benchmark
            </div>
            <div style="font-size: 40px; font-weight: 700; color: #ffffff; line-height: 1.05; letter-spacing: -0.03em; margin-bottom: 10px;">
                70.84%
            </div>
            <div style="font-size: 12px; color: #10b981; font-weight: 500; margin-bottom: 6px;">
                Macro Recall · Balanced LR
            </div>
            <div style="font-size: 11px; color: #6b7280; line-height: 1.5;">
                +42% over Naive Baseline · Evaluated on 16,336 unseen test reviews
            </div>
        </div>
        """)

    with col2:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 6px;">81,700</div>
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Ingested Reviews</div>
            <div style="font-size: 10px; color: #6b7280;">Amazon 2023</div>
        </div>
        """)

    with col3:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 6px;">4 Models</div>
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Evaluated Zoo</div>
            <div style="font-size: 10px; color: #6b7280;">Balanced LR · LinearSVC · DistilBERT</div>
        </div>
        """)

    with col4:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 28px; font-weight: 700; color: #ffffff; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 6px;">60 / 60</div>
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Passing Tests</div>
            <div style="font-size: 10px; color: #6b7280;">100% CI Suite · pytest</div>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

    # ── 3. Production Metric Rationale & Architecture Stack ─────────────────────
    card_col1, card_col2 = st.columns([1.25, 1])

    with card_col1:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                Production Decision Metric
            </div>
            <div style="font-size: 1rem; font-weight: 600; color: #ffffff; letter-spacing: -0.02em; margin-bottom: 0.75rem;">
                Why Macro Recall Protects Against Class Imbalance
            </div>
            <p style="color: #9ca3af; font-size: 0.82rem; line-height: 1.6; margin: 0 0 0.75rem 0;">
                The Amazon All Beauty dataset is heavily skewed: ~70% positive, ~22% negative, ~8% neutral.
                A naive classifier predicting "positive" on every input attains ~70–85% raw accuracy
                while completely failing to surface critical customer complaints.
                Macro Recall applies equal weight per sentiment class regardless of support.
            </p>
            <p style="color: #9ca3af; font-size: 0.82rem; line-height: 1.6; margin: 0;">
                Balanced Logistic Regression achieves <span style="color: #10b981; font-weight: 500;">70.84% Macro Recall</span>,
                lifting neutral class recall from 11% to 53% (+42 points) while preserving 76% negative recall.
                Authentic dissatisfaction and operational pain points are captured reliably.
            </p>
        </div>
        """)

    with card_col2:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem;">
                Technical Architecture Stack
            </div>
            <p style="color: #9ca3af; font-size: 0.82rem; line-height: 1.6; margin: 0 0 0.85rem 0;">
                Modular three-tier system separating asynchronous REST orchestration, persistent NLP pipelines, and interactive analytics.
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem;">
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">FastAPI REST</span>
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">Scikit-Learn</span>
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">DistilBERT</span>
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">KeyBERT</span>
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">SQLite ORM</span>
                <span style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px; padding: 4px 10px; color: #d1d5db; font-size: 0.75rem; font-family: 'JetBrains Mono', monospace;">Streamlit</span>
            </div>
            <div style="border-top: 1px solid rgba(255, 255, 255, 0.07); padding-top: 0.75rem; display: flex; flex-direction: column; gap: 0.35rem; font-size: 0.76rem; color: #9ca3af;">
                <div><span style="color: #ffffff; font-weight: 500;">API Layer:</span> FastAPI async REST with JWT &amp; rate limiting</div>
                <div><span style="color: #ffffff; font-weight: 500;">NLP Engine:</span> Scikit-Learn TF-IDF + HuggingFace DistilBERT</div>
                <div><span style="color: #ffffff; font-weight: 500;">Analytics:</span> Streamlit 6-Page Executive Suite</div>
            </div>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

    # ── 4. Dataset Overview & Model Benchmark ───────────────────────────────────
    data_col, model_col = st.columns([1, 1.8])

    with data_col:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.85rem;">
                Dataset Overview
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.6rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9ca3af; font-size: 0.82rem;">Total Reviews</span>
                    <span style="color: #ffffff; font-weight: 600; font-size: 0.88rem;">81,700</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9ca3af; font-size: 0.82rem;">Source</span>
                    <span style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Amazon All Beauty 2023</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #9ca3af; font-size: 0.82rem;">Split</span>
                    <span style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">80% Train / 20% Held-Out</span>
                </div>

                <div style="border-top: 1px solid rgba(255, 255, 255, 0.07); margin: 0.4rem 0;"></div>

                <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.2rem;">
                    Class Distribution
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                        <span style="color: #9ca3af;">Positive</span>
                        <span style="color: #ffffff; font-weight: 500;">~70%</span>
                    </div>
                    <div style="height: 4px; background: #181b21; border-radius: 2px; overflow: hidden;">
                        <div style="width: 70%; height: 100%; background: #10b981; border-radius: 2px;"></div>
                    </div>
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                        <span style="color: #9ca3af;">Negative</span>
                        <span style="color: #ffffff; font-weight: 500;">~22%</span>
                    </div>
                    <div style="height: 4px; background: #181b21; border-radius: 2px; overflow: hidden;">
                        <div style="width: 22%; height: 100%; background: #ef4444; border-radius: 2px;"></div>
                    </div>
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; margin-bottom: 4px;">
                        <span style="color: #9ca3af;">Neutral</span>
                        <span style="color: #ffffff; font-weight: 500;">~8%</span>
                    </div>
                    <div style="height: 4px; background: #181b21; border-radius: 2px; overflow: hidden;">
                        <div style="width: 8%; height: 100%; background: #f59e0b; border-radius: 2px;"></div>
                    </div>
                </div>

                <div style="border-top: 1px solid rgba(255, 255, 255, 0.07); margin: 0.4rem 0 0.2rem 0;"></div>
                <div style="color: #6b7280; font-size: 0.72rem; line-height: 1.5;">
                    Severe imbalance handled via inverse-frequency class weighting in Balanced Logistic Regression.
                </div>
            </div>
        </div>
        """)

    with model_col:
        eval_data = _load_eval()
        model_labels = {
            "logistic_regression": "Standard LR",
            "balanced_logistic_regression": "Balanced LR (Production)",
            "linearsvc": "LinearSVC",
        }

        table_rows = []
        for item in eval_data:
            m_name = item.get("model_name", "")
            is_balanced = m_name == "balanced_logistic_regression"
            row_style = "background: rgba(255, 255, 255, 0.03);" if is_balanced else ""
            acc = f"{item.get('accuracy', 0) * 100:.2f}%"
            rec = f"{item.get('macro_recall', item.get('recall', 0)) * 100:.2f}%"
            f1 = f"{item.get('macro_f1', item.get('f1', 0)):.4f}"
            name_label = model_labels.get(m_name, m_name)

            table_rows.append(f"""
            <tr style="{row_style}">
                <td style="padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.07); color: {'#ffffff' if is_balanced else '#9ca3af'}; font-weight: {'600' if is_balanced else '400'};">
                    {name_label}
                </td>
                <td style="text-align: center; padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.07); color: #d1d5db; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
                    {acc}
                </td>
                <td style="text-align: center; padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.07); color: {'#10b981' if is_balanced else '#d1d5db'}; font-weight: {'600' if is_balanced else '400'}; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
                    {rec}
                </td>
                <td style="text-align: center; padding: 0.6rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.07); color: #d1d5db; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;">
                    {f1}
                </td>
            </tr>
            """)

        rows_html = "".join(table_rows)

        render_html(f"""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.75rem;">
                Model Benchmark (Held-out 16,336 Reviews)
            </div>
            <table style="width: 100%; border-collapse: collapse; font-size: 0.82rem;">
                <thead>
                    <tr>
                        <th style="text-align: left; color: #9ca3af; padding: 0.4rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Model</th>
                        <th style="text-align: center; color: #9ca3af; padding: 0.4rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Accuracy</th>
                        <th style="text-align: center; color: #9ca3af; padding: 0.4rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Macro Recall</th>
                        <th style="text-align: center; color: #9ca3af; padding: 0.4rem 0.75rem; border-bottom: 1px solid rgba(255, 255, 255, 0.1); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em;">Macro F1</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <div style="margin-top: 0.85rem; font-size: 0.74rem; color: #6b7280; line-height: 1.5;">
                Balanced LR trades ~5% overall accuracy for +9% Macro Recall, capturing critical neutral and negative reviews that unweighted models miss.
            </div>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

    # ── 5. Navigation Guide & System Architecture ───────────────────────────────
    nav_col, arch_col = st.columns([1.3, 1])

    with nav_col:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.85rem;">
                Navigation Guide
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.65rem;">
                <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #10b981; font-weight: 600; min-width: 18px; padding-top: 2px;">01</span>
                    <div>
                        <div style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Historical Pulse (Default)</div>
                        <div style="color: #9ca3af; font-size: 0.75rem; line-height: 1.4;">Global dataset metrics, rating distributions, macro sentiment trend, and review explorer.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #6b7280; font-weight: 600; min-width: 18px; padding-top: 2px;">02</span>
                    <div>
                        <div style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Live Inference</div>
                        <div style="color: #9ca3af; font-size: 0.75rem; line-height: 1.4;">Interactive multi-model inference with token-level feature attribution and sequence evaluation.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #6b7280; font-weight: 600; min-width: 18px; padding-top: 2px;">03</span>
                    <div>
                        <div style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Benchmark Zoo</div>
                        <div style="color: #9ca3af; font-size: 0.75rem; line-height: 1.4;">Head-to-head performance across models, confusion matrices, and latency comparisons.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #6b7280; font-weight: 600; min-width: 18px; padding-top: 2px;">04</span>
                    <div>
                        <div style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Product Insights</div>
                        <div style="color: #9ca3af; font-size: 0.75rem; line-height: 1.4;">ASIN-level deep dive with Semicircular Purchase Confidence Meter and Aspect Vibe Donut.</div>
                    </div>
                </div>
                <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #6b7280; font-weight: 600; min-width: 18px; padding-top: 2px;">05</span>
                    <div>
                        <div style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">System Overview</div>
                        <div style="color: #9ca3af; font-size: 0.75rem; line-height: 1.4;">Executive architecture, system benchmarks, SLA targets, and engineering telemetry.</div>
                    </div>
                </div>
            </div>
        </div>
        """)

    with arch_col:
        render_html("""
        <div style="background: #111317; border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; padding: 20px; height: 100%;">
            <div style="font-size: 11px; font-weight: 500; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.85rem;">
                System Architecture
            </div>
            <div style="display: flex; flex-direction: column; gap: 0.6rem;">
                <div style="background: #181b21; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; padding: 0.75rem 0.9rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Client Analytics Tier</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9ca3af;">:8501</span>
                    </div>
                    <div style="color: #6b7280; font-size: 0.73rem; margin-top: 3px; line-height: 1.4;">Streamlit 6-Page Executive Suite</div>
                </div>

                <div style="background: #181b21; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; padding: 0.75rem 0.9rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">API Gateway Tier</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9ca3af;">:8000</span>
                    </div>
                    <div style="color: #6b7280; font-size: 0.73rem; margin-top: 3px; line-height: 1.4;">FastAPI Async REST Engine · JWT RBAC</div>
                </div>

                <div style="background: #181b21; border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 6px; padding: 0.75rem 0.9rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #ffffff; font-weight: 500; font-size: 0.82rem;">Intelligence Core</span>
                        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #9ca3af;">SQLite + ML</span>
                    </div>
                    <div style="color: #6b7280; font-size: 0.73rem; margin-top: 3px; line-height: 1.4;">DistilBERT · Scikit-Learn · KeyBERT</div>
                </div>
            </div>
        </div>
        """)


if __name__ == "__main__":
    render()
