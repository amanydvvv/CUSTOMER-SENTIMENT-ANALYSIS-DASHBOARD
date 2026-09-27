"""
0_about.py
──────────
Home / About page — the first page users see.
Provides full project context: dataset, models, tech stack, navigation guide, and team.
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
    # ── Header ────────────────────────────────────────────────────────────────
    render_html("""
    <div style="margin-bottom:1.5rem;border-bottom:1px solid #1E2533;padding-bottom:1rem;">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.4rem;">
            <span style="font-size:1.9rem;">🧠</span>
            <h1 style="font-size:1.85rem;font-weight:800;color:#F5F7FA;letter-spacing:-0.02em;margin:0;line-height:1.2;">
                CUSTOMER SENTIMENT INTELLIGENCE
            </h1>
        </div>
        <div style="color:#98A2B3;font-size:0.88rem;max-width:820px;line-height:1.6;">
            A production-grade NLP intelligence system that processes 81,700 Amazon customer reviews
            using machine learning to extract sentiment, surface product pain points, and deliver
            actionable business insights through a real-time analytics dashboard.
        </div>
    </div>
    """)

    # ── Row 1: Dataset + Model Performance ───────────────────────────────────
    col_data, col_models = st.columns([1, 1.8])

    with col_data:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1.1rem 1.25rem;height:100%;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.75rem;">📦 Dataset</div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Reviews</span>
                    <span style="color:#F5F7FA;font-weight:700;font-size:0.9rem;">81,700</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Source</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Amazon All Beauty 2023</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Train / Test</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">80% / 20% stratified</span>
                </div>
                <div style="border-top:1px solid #1E2533;margin:0.4rem 0;"></div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#22C55E;font-size:0.82rem;">● Positive</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">~70%</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#EF4444;font-size:0.82rem;">● Negative</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">~22%</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#F59E0B;font-size:0.82rem;">● Neutral</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">~8%</span>
                </div>
                <div style="border-top:1px solid #1E2533;margin:0.4rem 0;"></div>
                <div style="color:#98A2B3;font-size:0.75rem;line-height:1.5;">
                    ⚠️ Class imbalance present. Balanced LR selected as production model
                    to correct for minority class suppression.
                </div>
            </div>
        </div>
        """)

    with col_models:
        eval_data = _load_eval()
        model_labels = {
            "logistic_regression": "Standard LR",
            "balanced_logistic_regression": "Balanced LR ⭐",
            "linearsvc": "LinearSVC"
        }
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;
                    padding:1.1rem 1.25rem;margin-bottom:0.6rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.75rem;">📊 Model Performance (Held-out 16,336 reviews)</div>
            <table style="width:100%;border-collapse:collapse;font-size:0.82rem;">
                <thead>
                    <tr>
                        <th style="text-align:left;color:#98A2B3;padding:0.25rem 0.5rem;
                                   border-bottom:1px solid #1E2533;font-weight:600;">Model</th>
                        <th style="text-align:center;color:#98A2B3;padding:0.25rem 0.5rem;
                                   border-bottom:1px solid #1E2533;font-weight:600;">Accuracy</th>
                        <th style="text-align:center;color:#98A2B3;padding:0.25rem 0.5rem;
                                   border-bottom:1px solid #1E2533;font-weight:600;">Macro Recall</th>
                        <th style="text-align:center;color:#98A2B3;padding:0.25rem 0.5rem;
                                   border-bottom:1px solid #1E2533;font-weight:600;">Macro F1</th>
                    </tr>
                </thead>
                <tbody>
        """ + "".join([
            f"""<tr style="{'background:rgba(124,92,255,0.06);' if item.get('model_name')=='balanced_logistic_regression' else ''}">
                    <td style="padding:0.35rem 0.5rem;color:#F5F7FA;font-weight:{'700' if item.get('model_name')=='balanced_logistic_regression' else '400'};">
                        {model_labels.get(item.get('model_name',''), item.get('model_name',''))}
                    </td>
                    <td style="text-align:center;padding:0.35rem 0.5rem;color:#D0D5DD;">
                        {round(item.get('accuracy',0)*100,2)}%
                    </td>
                    <td style="text-align:center;padding:0.35rem 0.5rem;
                               color:{'#22C55E' if item.get('model_name')=='balanced_logistic_regression' else '#D0D5DD'};">
                        {round(item.get('macro_recall', item.get('recall',0))*100,2)}%
                    </td>
                    <td style="text-align:center;padding:0.35rem 0.5rem;color:#D0D5DD;">
                        {round(item.get('macro_f1', item.get('f1',0)),4)}
                    </td>
                </tr>"""
            for item in eval_data
        ]) + """
                </tbody>
            </table>
            <div style="margin-top:0.6rem;font-size:0.73rem;color:#98A2B3;line-height:1.5;">
                ⭐ <b style="color:#F5F7FA;">Balanced LR</b> is the recommended production model.
                It sacrifices 5% raw accuracy to gain +9% Macro Recall — correctly identifying
                negative and neutral reviews that standard models miss.
            </div>
        </div>
        """)

    st.markdown("")

    # ── Row 2: Tech Stack ─────────────────────────────────────────────────────
    render_html("""
    <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;
                padding:1rem 1.25rem;margin-bottom:0.75rem;">
        <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:0.65rem;">🛠️ Tech Stack</div>
        <div style="display:flex;flex-wrap:wrap;gap:0.45rem;">
            <span style="background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);
                         color:#60A5FA;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                Python 3.10
            </span>
            <span style="background:rgba(0,150,136,0.12);border:1px solid rgba(0,150,136,0.3);
                         color:#4DB6AC;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                FastAPI
            </span>
            <span style="background:rgba(255,75,75,0.12);border:1px solid rgba(255,75,75,0.3);
                         color:#FF6B6B;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                Streamlit
            </span>
            <span style="background:rgba(247,147,30,0.12);border:1px solid rgba(247,147,30,0.3);
                         color:#F7931E;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                Scikit-Learn
            </span>
            <span style="background:rgba(124,92,255,0.12);border:1px solid rgba(124,92,255,0.3);
                         color:#7C5CFF;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                TF-IDF NLP
            </span>
            <span style="background:rgba(71,85,105,0.2);border:1px solid rgba(100,116,139,0.3);
                         color:#94A3B8;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                SQLite + SQLAlchemy
            </span>
            <span style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);
                         color:#4ADE80;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                Google Places API
            </span>
            <span style="background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.25);
                         color:#38BDF8;font-size:0.75rem;font-weight:600;padding:3px 10px;border-radius:5px;">
                Plotly
            </span>
        </div>
    </div>
    """)

    # ── Row 3: Navigation Guide + Team ────────────────────────────────────────
    col_nav, col_team = st.columns([1.4, 1])

    with col_nav:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1.1rem 1.25rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.75rem;">🗺️ How to Navigate</div>
            <div style="display:flex;flex-direction:column;gap:0.55rem;">
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <span style="color:#7C5CFF;font-weight:700;font-size:0.82rem;min-width:20px;">1</span>
                    <div>
                        <div style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Overview</div>
                        <div style="color:#98A2B3;font-size:0.75rem;">Filter &amp; explore all 81K reviews. View sentiment KPIs, pain points, and mismatch analysis.</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <span style="color:#7C5CFF;font-weight:700;font-size:0.82rem;min-width:20px;">2</span>
                    <div>
                        <div style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Analyze Review</div>
                        <div style="color:#98A2B3;font-size:0.75rem;">Type any review and get real-time sentiment prediction with word-level explainability.</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <span style="color:#7C5CFF;font-weight:700;font-size:0.82rem;min-width:20px;">3</span>
                    <div>
                        <div style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Keyword Insights</div>
                        <div style="color:#98A2B3;font-size:0.75rem;">Explore TF-IDF vocabulary and the strongest predictive terms per sentiment class.</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <span style="color:#7C5CFF;font-weight:700;font-size:0.82rem;min-width:20px;">4</span>
                    <div>
                        <div style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Model Benchmark</div>
                        <div style="color:#98A2B3;font-size:0.75rem;">Compare all 3 models across accuracy, macro recall, and F1. View confusion matrices.</div>
                    </div>
                </div>
                <div style="display:flex;gap:0.75rem;align-items:flex-start;">
                    <span style="color:#7C5CFF;font-weight:700;font-size:0.82rem;min-width:20px;">5</span>
                    <div>
                        <div style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Product Intelligence</div>
                        <div style="color:#98A2B3;font-size:0.75rem;">Select any product ASIN for deep feedback analysis: pain points, evidence, trends, comparison.</div>
                    </div>
                </div>
            </div>
        </div>
        """)

    with col_team:
        render_html("""
        <div style="background:#11151D;border:1px solid #242A35;border-radius:10px;padding:1.1rem 1.25rem;">
            <div style="font-size:0.72rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:0.75rem;">👥 Team</div>
            <div style="display:flex;flex-direction:column;gap:0.75rem;">
                <div style="background:#151A24;border:1px solid #242A35;border-radius:7px;padding:0.65rem 0.85rem;">
                    <div style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">Aman</div>
                    <div style="color:#7C5CFF;font-size:0.73rem;font-weight:600;margin-top:2px;">Project Lead · ML Engineer</div>
                    <div style="color:#98A2B3;font-size:0.72rem;margin-top:4px;line-height:1.4;">
                        Architecture, ML pipeline, backend API, full-stack integration
                    </div>
                </div>
                <div style="background:#151A24;border:1px solid #242A35;border-radius:7px;padding:0.65rem 0.85rem;">
                    <div style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">Pasha</div>
                    <div style="color:#22C55E;font-size:0.73rem;font-weight:600;margin-top:2px;">Frontend Developer</div>
                    <div style="color:#98A2B3;font-size:0.72rem;margin-top:4px;line-height:1.4;">
                        Dashboard UI enhancements, filters, export, session history
                    </div>
                </div>
                <div style="background:#151A24;border:1px solid #242A35;border-radius:7px;padding:0.65rem 0.85rem;">
                    <div style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">Guru</div>
                    <div style="color:#38BDF8;font-size:0.73rem;font-weight:600;margin-top:2px;">Backend Developer</div>
                    <div style="color:#98A2B3;font-size:0.72rem;margin-top:4px;line-height:1.4;">
                        API endpoints, health monitoring, rate limiting, CSV export
                    </div>
                </div>
            </div>
        </div>
        """)


if __name__ == "__main__":
    render()
