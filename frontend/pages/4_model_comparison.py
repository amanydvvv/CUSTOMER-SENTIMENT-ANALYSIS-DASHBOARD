import streamlit as st
import pandas as pd
import plotly.express as px
from api_client import get_stats

st.set_page_config(page_title="Model Comparison", layout="wide")
st.title("Model Performance Comparison")

try:
    stats = get_stats()
    df_metrics = pd.DataFrame(stats['model_metrics'])
    
    if not df_metrics.empty:
        fig_acc = px.bar(df_metrics, x='model_name', y='accuracy', title="Accuracy by Model", color='model_name')
        st.plotly_chart(fig_acc, use_container_width=True)
        
        fig_lat = px.bar(df_metrics, x='model_name', y='latency', title="Inference Latency (ms) by Model", color='model_name')
        st.plotly_chart(fig_lat, use_container_width=True)
    else:
        st.warning("No model metrics found.")
        
except Exception as e:
    st.error(f"Could not fetch metrics: {e}")
