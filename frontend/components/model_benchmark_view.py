import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional
from frontend.utils.api_client import api_client


def render_model_benchmark_view(token: Optional[str] = None):
    """Comparative Model Benchmark & Evaluation Center."""
    st.markdown("### 🏆 Dual-Path Model Comparator & Benchmark Suite")
    st.markdown(
        "Benchmarking **Primary DistilBERT Classifier** against **Fast-Path Fallback (TF-IDF + Logistic Regression)** to validate Macro F1 ($\ge 88\%$) and latency targets (<250ms transformer, <30ms fallback)."
    )

    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        dataset_choice = st.selectbox(
            "Benchmark Test Dataset",
            ["Amazon Customer Reviews (Electronics & Home)", "Yelp Open Dataset (Hospitality & Services)", "Combined Multi-Domain Dataset"],
            index=0,
            key="benchmark_dataset_select",
        )
        ds_code = "amazon" if "Amazon" in dataset_choice else ("yelp" if "Yelp" in dataset_choice else "combined")

    with c2:
        sample_limit = st.selectbox(
            "Evaluation Sample Limit",
            [50, 100, "All Samples"],
            index=1,
            key="benchmark_sample_limit",
        )
        limit_val = None if sample_limit == "All Samples" else int(sample_limit)

    with c3:
        st.write("")
        st.write("")
        run_btn = st.button("🚀 Run Live Benchmark", type="primary", use_container_width=True)

    if run_btn:
        with st.spinner("Executing rigorous dual-path benchmark across test datasets..."):
            try:
                res = api_client.run_benchmark(dataset=ds_code, sample_limit=limit_val)
                st.session_state["last_benchmark_result"] = res
            except Exception as e:
                st.error(f"Benchmark run failed: {e}")

    result = st.session_state.get("last_benchmark_result")
    if result:
        st.markdown("---")
        t_metrics = result["transformer_metrics"]
        f_metrics = result["fallback_metrics"]
        speedup = result["speedup_factor"]
        target_f1_met = result["target_f1_achieved"]

        # High-level comparison scorecard
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Primary (DistilBERT) F1</div>
                    <div class="kpi-value" style="color: {'#10B981' if t_metrics['macro_f1'] >= 0.88 else '#F59E0B'};">
                        {t_metrics['macro_f1']:.3f}
                    </div>
                    <div class="kpi-subtitle">Accuracy: {t_metrics['accuracy'] * 100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc2:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Fallback (TF-IDF+LR) F1</div>
                    <div class="kpi-value" style="color: #38BDF8;">
                        {f_metrics['macro_f1']:.3f}
                    </div>
                    <div class="kpi-subtitle">Accuracy: {f_metrics['accuracy'] * 100:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc3:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-title">Latency Comparison</div>
                    <div class="kpi-value" style="color: #A78BFA;">
                        {f_metrics['latency_avg_ms']:.1f} <span style="font-size:16px;color:#94A3B8;">vs {t_metrics['latency_avg_ms']:.1f}ms</span>
                    </div>
                    <div class="kpi-subtitle">Fast-Path vs DistilBERT</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with sc4:
            st.markdown(
                f"""
                <div class="kpi-card positive">
                    <div class="kpi-title">Speedup Factor</div>
                    <div class="kpi-value" style="color: #34D399;">
                        {speedup:.1f}x
                    </div>
                    <div class="kpi-subtitle">Throughput Acceleration</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Detailed Latency & Confusion Matrix Charts
        st.markdown("#### 📊 Latency Profiling & Confusion Matrices")
        ch_col1, ch_col2 = st.columns(2)

        with ch_col1:
            lat_fig = go.Figure()
            categories = ["Average (P50)", "95th Percentile (P95)", "99th Percentile (P99)"]
            t_lats = [t_metrics["latency_avg_ms"], t_metrics["latency_p95_ms"], t_metrics["latency_p99_ms"]]
            f_lats = [f_metrics["latency_avg_ms"], f_metrics["latency_p95_ms"], f_metrics["latency_p99_ms"]]

            lat_fig.add_trace(go.Bar(name="DistilBERT (<250ms SLA)", x=categories, y=t_lats, marker_color="#6366F1"))
            lat_fig.add_trace(go.Bar(name="TF-IDF + LR (<30ms SLA)", x=categories, y=f_lats, marker_color="#10B981"))

            lat_fig.update_layout(
                title="Latency Profile Comparison (ms)",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                font=dict(color="#F1F5F9", family="Outfit"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Milliseconds (ms)", gridcolor="rgba(255,255,255,0.05)"),
                xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
            )
            st.plotly_chart(lat_fig, use_container_width=True)

        with ch_col2:
            # Confusion matrix heatmap for primary model
            labels = ["Negative", "Neutral", "Positive"]
            cm = t_metrics["confusion_matrix"]
            cm_fig = px.imshow(
                cm,
                x=labels,
                y=labels,
                color_continuous_scale="Viridis",
                text_auto=True,
                labels=dict(x="Predicted Sentiment", y="True Sentiment", color="Count"),
                title="DistilBERT Confusion Matrix (3x3)",
            )
            cm_fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=320,
                font=dict(color="#F1F5F9", family="Outfit"),
            )
            st.plotly_chart(cm_fig, use_container_width=True)

    # Historical Benchmark Runs
    st.markdown("#### 📜 Historical Benchmark Executions")
    try:
        history = api_client.get_benchmark_history()
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(
                df_hist[[
                    "id", "dataset_name", "sample_size",
                    "transformer_macro_f1", "fallback_macro_f1",
                    "transformer_latency_avg_ms", "fallback_latency_avg_ms",
                    "speedup_factor", "status", "created_at"
                ]],
                use_container_width=True,
            )
        else:
            st.info("No prior benchmark executions recorded. Click 'Run Live Benchmark' above to execute.")
    except Exception:
        pass
