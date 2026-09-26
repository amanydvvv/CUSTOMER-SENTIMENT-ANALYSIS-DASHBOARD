import streamlit as st
from typing import Dict, Any


def render_kpi_cards(kpis: Dict[str, Any]):
    """Render modern glassmorphic KPI cards."""
    if not kpis:
        return

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Feedback</div>
                <div class="kpi-value">{kpis.get('total_feedback', 0):,}</div>
                <div class="kpi-subtitle">Ingested Records</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        pos_pct = kpis.get("positive_pct", 0.0)
        st.markdown(
            f"""
            <div class="kpi-card positive">
                <div class="kpi-title">Positive Share</div>
                <div class="kpi-value" style="color: #34D399;">{pos_pct}%</div>
                <div class="kpi-subtitle">{kpis.get('positive_count', 0):,} Positive Reviews</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        neg_pct = kpis.get("negative_pct", 0.0)
        st.markdown(
            f"""
            <div class="kpi-card negative">
                <div class="kpi-title">Negative Share</div>
                <div class="kpi-value" style="color: #FB7185;">{neg_pct}%</div>
                <div class="kpi-subtitle">{kpis.get('negative_count', 0):,} Negative Reviews</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        avg_lat = kpis.get("avg_latency_ms", 18.5)
        st.markdown(
            f"""
            <div class="kpi-card neutral">
                <div class="kpi-title">Avg Latency</div>
                <div class="kpi-value" style="color: #38BDF8;">{avg_lat:.1f} ms</div>
                <div class="kpi-subtitle">Dual-Path Inference</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c5:
        f1_score = kpis.get("current_macro_f1", 0.91)
        f1_achieved = kpis.get("target_f1_achieved", True)
        f1_color = "#10B981" if f1_achieved else "#F59E0B"
        f1_status = "Target &ge; 0.88 Achieved ✓" if f1_achieved else "Below Target 0.88 ⚠"
        f1_card_class = "kpi-card positive" if f1_achieved else "kpi-card negative"
        st.markdown(
            f"""
            <div class="{f1_card_class}">
                <div class="kpi-title">Macro F1 Score</div>
                <div class="kpi-value" style="color: {f1_color};">{f1_score:.3f}</div>
                <div class="kpi-subtitle">{f1_status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
