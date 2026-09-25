import streamlit as st
import pandas as pd
from api_client import get_stats

st.set_page_config(page_title="Overview", layout="wide")
st.title("System Overview")

try:
    stats = get_stats()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Reviews Processed", stats['total_reviews'])
    with col2:
        st.metric("Total Live Predictions Made", stats['total_predictions'])
        
    st.subheader("Available Models")
    df_metrics = pd.DataFrame(stats['model_metrics'])
    if not df_metrics.empty:
        st.dataframe(df_metrics[['model_name', 'accuracy', 'f1']].style.format("{:.4f}", subset=['accuracy', 'f1']))
        
except Exception as e:
    st.error(f"Could not connect to backend API: {e}")
