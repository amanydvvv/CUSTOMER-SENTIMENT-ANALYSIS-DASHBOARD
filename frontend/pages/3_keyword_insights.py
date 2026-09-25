import streamlit as st
import pandas as pd
from api_client import get_stats

st.set_page_config(page_title="Keyword Insights", layout="wide")
st.title("Top Keywords by Sentiment")

try:
    stats = get_stats()
    keywords = stats.get('top_keywords', {})
    
    cols = st.columns(len(keywords))
    for i, (sentiment, words) in enumerate(keywords.items()):
        with cols[i]:
            st.subheader(sentiment.capitalize())
            for w in words:
                st.markdown(f"- {w}")
                
except Exception as e:
    st.error(f"Could not fetch keyword insights: {e}")
