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
    # ── Hero Banner ───────────────────────────────────────────────────────────
    render_html("""
    <div style="
        background: linear-gradient(135deg, rgba(124,92,255,0.08) 0%, rgba(34,211,238,0.04) 50%, rgba(124,92,255,0.06) 100%);
        border: 1px solid rgba(124,92,255,0.12);
        border-radius: 16px;
        padding: 2rem 2.25rem 1.75rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.5s ease-out both;
    ">
        <div style="
            position: absolute; top: -40px; right: -40px; width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(124,92,255,0.1) 0%, transparent 70%);
            border-radius: 50%; pointer-events: none;
        "></div>
        <div style="
            position: absolute; bottom: -30px; left: -30px; width: 150px; height: 150px;
            background: radial-gradient(circle, rgba(34,211,238,0.06) 0%, transparent 70%);
            border-radius: 50%; pointer-events: none;
        "></div>
        <div style="display:flex;align-items:center;gap:0.65rem;margin-bottom:0.5rem;">
            <div style="
                width: 38px; height: 38px; border-radius: 10px;
                background: linear-gradient(135deg, #7C5CFF, #22D3EE);
                display: flex; align-items: center; justify-content: center;
                font-size: 1.2rem; box-shadow: 0 4px 16px rgba(124,92,255,0.3);
            ">🧠</div>
            <h1 style="
                font-size: 1.85rem; font-weight: 800; letter-spacing: -0.03em;
                margin: 0; line-height: 1.15;
                background: linear-gradient(135deg, #F5F7FA 0%, #98A2B3 100%);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                background-clip: text;
            ">CUSTOMER SENTIMENT INTELLIGENCE</h1>
        </div>
        <div style="color:#98A2B3;font-size:0.88rem;max-width:780px;line-height:1.65;margin-bottom:1.25rem;">
            A production-grade NLP intelligence system processing <b style="color:#F5F7FA;">81,700 Amazon reviews</b>
            using machine learning to extract sentiment, surface product pain points, and deliver
            actionable business insights through a real-time analytics dashboard.
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0.6rem;">
            <span style="
                background: rgba(124,92,255,0.1); border: 1px solid rgba(124,92,255,0.25);
                color: #A78BFA; font-size: 0.75rem; font-weight: 700;
                padding: 5px 14px; border-radius: 20px;
                display: flex; align-items: center; gap: 6px;
            ">
                <span style="font-size:0.85rem;">📊</span> 81,700 Reviews
            </span>
            <span style="
                background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2);
                color: #4ADE80; font-size: 0.75rem; font-weight: 700;
                padding: 5px 14px; border-radius: 20px;
                display: flex; align-items: center; gap: 6px;
            ">
                <span style="font-size:0.85rem;">🎯</span> 70.84% Macro Recall
            </span>
            <span style="
                background: rgba(34,211,238,0.08); border: 1px solid rgba(34,211,238,0.2);
                color: #22D3EE; font-size: 0.75rem; font-weight: 700;
                padding: 5px 14px; border-radius: 20px;
                display: flex; align-items: center; gap: 6px;
            ">
                <span style="font-size:0.85rem;">✅</span> 60 Tests Passing
            </span>
            <span style="
                background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2);
                color: #FBBF24; font-size: 0.75rem; font-weight: 700;
                padding: 5px 14px; border-radius: 20px;
                display: flex; align-items: center; gap: 6px;
            ">
                <span style="font-size:0.85rem;">🤖</span> 4 ML Models
            </span>
        </div>
    </div>
    """)

    # ── Executive System Overview ────────────────────────────────────────────
    render_html("""
    <div style="
        background: rgba(17,21,29,0.8); backdrop-filter: blur(16px);
        border: 1px solid rgba(36,42,53,0.6);
        border-left: 3px solid #7C5CFF;
        border-radius: 12px; padding: 1.2rem 1.5rem; margin-bottom: 1.25rem;
        animation: fadeInUp 0.4s ease-out both;
    ">
        <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                    letter-spacing:0.12em;margin-bottom:0.85rem;">🏛️ Executive System Overview</div>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:0.9rem;margin-bottom:1rem;">

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.85rem;text-align:center;">
                <div style="font-size:1.6rem;font-weight:900;color:#F5F7FA;line-height:1;">81,700</div>
                <div style="font-size:0.68rem;color:#98A2B3;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.06em;">Reviews Ingested</div>
                <div style="font-size:0.65rem;color:#667085;margin-top:2px;">Amazon All Beauty 2023</div>
            </div>

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.85rem;text-align:center;">
                <div style="font-size:1.6rem;font-weight:900;color:#A78BFA;line-height:1;">4</div>
                <div style="font-size:0.68rem;color:#98A2B3;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.06em;">Persistent ML Models</div>
                <div style="font-size:0.65rem;color:#667085;margin-top:2px;">Balanced LR · LR · SVC · DistilBERT</div>
            </div>

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.85rem;text-align:center;">
                <div style="font-size:1.6rem;font-weight:900;color:#22D3EE;line-height:1;">15+</div>
                <div style="font-size:0.68rem;color:#98A2B3;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.06em;">FastAPI Endpoints</div>
                <div style="font-size:0.65rem;color:#667085;margin-top:2px;">Predict · Auth · Stats · Places</div>
            </div>

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.85rem;text-align:center;">
                <div style="font-size:1.6rem;font-weight:900;color:#22C55E;line-height:1;">60</div>
                <div style="font-size:0.68rem;color:#98A2B3;font-weight:600;margin-top:4px;text-transform:uppercase;letter-spacing:0.06em;">Automated Tests</div>
                <div style="font-size:0.65rem;color:#667085;margin-top:2px;">100% pass rate · pytest</div>
            </div>
        </div>

        <div style="display:grid;grid-template-columns:1.4fr 1fr;gap:0.9rem;">

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.9rem 1rem;">
                <div style="font-size:0.68rem;font-weight:700;color:#22C55E;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;">
                    🎯 Core Metric: 70.84% Macro Recall
                </div>
                <div style="font-size:0.78rem;color:#D0D5DD;line-height:1.55;">
                    The dataset is <b style="color:#F5F7FA;">severely imbalanced (~70% positive)</b> — a naive classifier
                    predicting "positive" always would achieve 70% accuracy without detecting a single complaint.
                    We use <b style="color:#22C55E;">Macro Recall</b> (equal weight per class) as our decisive metric.
                    Balanced Logistic Regression achieves <b style="color:#22C55E;">70.84% Macro Recall</b>,
                    boosting Neutral class recall from 11% → 53% (+42 pts) while maintaining 76% Negative recall —
                    critical for surfacing real customer dissatisfaction.
                </div>
            </div>

            <div style="background:#11151D;border:1px solid #1E2533;border-radius:8px;padding:0.9rem 1rem;">
                <div style="font-size:0.68rem;font-weight:700;color:#38BDF8;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.55rem;">
                    🛠️ Production Architecture Stack
                </div>
                <div style="display:flex;flex-direction:column;gap:0.3rem;">
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#38BDF8;font-weight:700;">API Layer:</span> FastAPI (async REST, JWT/RBAC)</div>
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#A78BFA;font-weight:700;">ML Core:</span> Scikit-Learn TF-IDF + HuggingFace DistilBERT</div>
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#22D3EE;font-weight:700;">Semantics:</span> KeyBERT (MMR phrase extraction)</div>
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#4ADE80;font-weight:700;">Database:</span> SQLite + SQLAlchemy ORM</div>
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#F59E0B;font-weight:700;">Frontend:</span> Streamlit 6-page analytics suite</div>
                    <div style="font-size:0.76rem;color:#D0D5DD;"><span style="color:#F87171;font-weight:700;">External:</span> Google Places API (live ingestion)</div>
                </div>
            </div>

        </div>
    </div>
    """)

    # ── Row 1: Dataset + Model Performance ───────────────────────────────────
    col_data, col_models = st.columns([1, 1.8])

    with col_data:
        render_html("""
        <div style="
            background: rgba(17,21,29,0.65); backdrop-filter: blur(16px);
            border: 1px solid rgba(36,42,53,0.5);
            border-top: 2px solid; border-image: linear-gradient(90deg, #7C5CFF, #22D3EE) 1;
            border-image-slice: 1 1 0 1;
            border-radius: 12px; padding: 1.15rem 1.3rem; height: 100%;
            animation: fadeInUp 0.4s ease-out both;
        ">
            <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:0.8rem;">📦 Dataset Overview</div>
            <div style="display:flex;flex-direction:column;gap:0.5rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Total Reviews</span>
                    <span style="color:#F5F7FA;font-weight:800;font-size:1rem;">81,700</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Source</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">Amazon All Beauty 2023</span>
                </div>
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="color:#98A2B3;font-size:0.82rem;">Train / Test</span>
                    <span style="color:#F5F7FA;font-weight:600;font-size:0.82rem;">80% / 20% stratified</span>
                </div>
                <div style="border-top:1px solid rgba(30,37,51,0.6);margin:0.35rem 0;"></div>
                <div style="font-size:0.68rem;font-weight:700;color:#667085;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.1rem;">Class Distribution</div>
                <div style="margin-bottom:0.2rem;">
                    <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                        <span style="color:#22C55E;">● Positive</span><span style="color:#F5F7FA;font-weight:600;">~70%</span>
                    </div>
                    <div style="height:6px;background:#151A24;border-radius:3px;overflow:hidden;">
                        <div style="width:70%;height:100%;background:linear-gradient(90deg,#22C55E,#16A34A);border-radius:3px;"></div>
                    </div>
                </div>
                <div style="margin-bottom:0.2rem;">
                    <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                        <span style="color:#EF4444;">● Negative</span><span style="color:#F5F7FA;font-weight:600;">~22%</span>
                    </div>
                    <div style="height:6px;background:#151A24;border-radius:3px;overflow:hidden;">
                        <div style="width:22%;height:100%;background:linear-gradient(90deg,#EF4444,#DC2626);border-radius:3px;"></div>
                    </div>
                </div>
                <div style="margin-bottom:0.2rem;">
                    <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:3px;">
                        <span style="color:#F59E0B;">● Neutral</span><span style="color:#F5F7FA;font-weight:600;">~8%</span>
                    </div>
                    <div style="height:6px;background:#151A24;border-radius:3px;overflow:hidden;">
                        <div style="width:8%;height:100%;background:linear-gradient(90deg,#F59E0B,#D97706);border-radius:3px;"></div>
                    </div>
                </div>
                <div style="border-top:1px solid rgba(30,37,51,0.6);margin:0.25rem 0;"></div>
                <div style="color:#98A2B3;font-size:0.73rem;line-height:1.5;">
                    ⚠️ Severe imbalance → <span style="color:#A78BFA;font-weight:600;">Balanced LR</span> selected to correct minority class suppression.
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
        <div style="
            background: rgba(17,21,29,0.65); backdrop-filter: blur(16px);
            border: 1px solid rgba(36,42,53,0.5); border-radius: 12px;
            padding: 1.15rem 1.3rem; animation: fadeInUp 0.5s ease-out 0.2s both;
        ">
            <div style="font-size:0.68rem;font-weight:700;color:#7C5CFF;text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:0.85rem;">🏛️ System Architecture</div>
            <div style="display:flex;flex-direction:column;gap:0.7rem;">

                <!-- Tier 1 -->
                <div style="
                    background: rgba(21,26,36,0.8); border: 1px solid rgba(124,92,255,0.2);
                    border-radius: 10px; padding: 0.85rem 1rem;
                ">
                    <div style="display:flex;align-items:center;gap:0.7rem;">
                        <div style="
                            width:34px; height:34px; border-radius:8px; flex-shrink:0;
                            background: linear-gradient(135deg, #7C5CFF, #6342E8);
                            display:flex; align-items:center; justify-content:center;
                            font-size:0.9rem; color:#fff;
                        ">🎨</div>
                        <div style="flex:1;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">Client Analytics Tier</span>
                                <span style="background:rgba(124,92,255,0.12);color:#A78BFA;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid rgba(124,92,255,0.25);">:8501</span>
                            </div>
                            <div style="color:#A78BFA;font-size:0.72rem;font-weight:600;margin-top:2px;">Streamlit 6-Page Executive Suite</div>
                        </div>
                    </div>
                    <div style="color:#98A2B3;font-size:0.7rem;margin-top:6px;line-height:1.45;padding-left:42px;">
                        Interactive gauges, multi-model selectors, aspect pain points, and token-level explainability.
                    </div>
                </div>

                <!-- Tier 2 -->
                <div style="
                    background: rgba(21,26,36,0.8); border: 1px solid rgba(56,189,248,0.2);
                    border-radius: 10px; padding: 0.85rem 1rem;
                ">
                    <div style="display:flex;align-items:center;gap:0.7rem;">
                        <div style="
                            width:34px; height:34px; border-radius:8px; flex-shrink:0;
                            background: linear-gradient(135deg, #38BDF8, #0EA5E9);
                            display:flex; align-items:center; justify-content:center;
                            font-size:0.9rem; color:#fff;
                        ">⚙️</div>
                        <div style="flex:1;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">API Gateway Tier</span>
                                <span style="background:rgba(56,189,248,0.1);color:#38BDF8;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid rgba(56,189,248,0.25);">:8000</span>
                            </div>
                            <div style="color:#38BDF8;font-size:0.72rem;font-weight:600;margin-top:2px;">FastAPI Async REST Engine</div>
                        </div>
                    </div>
                    <div style="color:#98A2B3;font-size:0.7rem;margin-top:6px;line-height:1.45;padding-left:42px;">
                        Multi-model routing, Google Places ingestion, JWT RBAC security, and 60 automated test suites.
                    </div>
                </div>

                <!-- Tier 3 -->
                <div style="
                    background: rgba(21,26,36,0.8); border: 1px solid rgba(34,197,94,0.2);
                    border-radius: 10px; padding: 0.85rem 1rem;
                ">
                    <div style="display:flex;align-items:center;gap:0.7rem;">
                        <div style="
                            width:34px; height:34px; border-radius:8px; flex-shrink:0;
                            background: linear-gradient(135deg, #22C55E, #16A34A);
                            display:flex; align-items:center; justify-content:center;
                            font-size:0.9rem; color:#fff;
                        ">🧠</div>
                        <div style="flex:1;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <span style="color:#F5F7FA;font-weight:700;font-size:0.85rem;">Intelligence & Data Core</span>
                                <span style="background:rgba(34,197,94,0.1);color:#22C55E;font-size:0.65rem;font-weight:700;padding:2px 8px;border-radius:12px;border:1px solid rgba(34,197,94,0.25);">SQLite + ML</span>
                            </div>
                            <div style="color:#22C55E;font-size:0.72rem;font-weight:600;margin-top:2px;">DistilBERT · Scikit-Learn · KeyBERT</div>
                        </div>
                    </div>
                    <div style="color:#98A2B3;font-size:0.7rem;margin-top:6px;line-height:1.45;padding-left:42px;">
                        81,700 Amazon reviews, serialized models, sentiment persistence, and query logging.
                    </div>
                </div>

            </div>
        </div>
        """)


if __name__ == "__main__":
    render()
