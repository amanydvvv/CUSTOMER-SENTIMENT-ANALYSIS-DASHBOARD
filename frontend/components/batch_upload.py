import streamlit as st
import pandas as pd
from typing import Optional
from frontend.utils.api_client import api_client


def render_batch_upload(token: Optional[str] = None):
    """CSV / Excel Batch Feedback Ingestion Component."""
    st.markdown("### 📥 Batch Customer Feedback Ingestion")
    st.markdown(
        "Upload raw customer feedback datasets in CSV or Excel format. The backend NLP engine will asynchronously process sentiment classifications, extract aspects, and persist records into the database."
    )

    c1, c2 = st.columns([2, 1])

    with c1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=["csv", "xlsx", "xls"],
            key="batch_file_uploader",
        )

    with c2:
        source_name = st.text_input("Dataset Source Tag", value="CSV Upload", key="batch_source_input")
        auto_seed_amz = st.button("📦 Load Amazon Benchmark Sample", use_container_width=True)
        auto_seed_ylp = st.button("🍽️ Load Yelp Benchmark Sample", use_container_width=True)

    # Handle quick benchmark loaders
    if auto_seed_amz:
        try:
            with open("data/amazon_reviews_sample.csv", "rb") as f:
                file_bytes = f.read()
            res = api_client.upload_file(file_bytes, "amazon_reviews_sample.csv", source_name="Amazon Batch", token=token)
            st.success(f"Successfully ingested Amazon Benchmark: {res.get('inserted_records')} records added!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load Amazon dataset: {e}")

    if auto_seed_ylp:
        try:
            with open("data/yelp_reviews_sample.csv", "rb") as f:
                file_bytes = f.read()
            res = api_client.upload_file(file_bytes, "yelp_reviews_sample.csv", source_name="Yelp Batch", token=token)
            st.success(f"Successfully ingested Yelp Benchmark: {res.get('inserted_records')} records added!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to load Yelp dataset: {e}")

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        filename = uploaded_file.name

        try:
            if filename.endswith(".csv"):
                df_preview = pd.read_csv(uploaded_file)
            else:
                df_preview = pd.read_excel(uploaded_file)

            st.markdown(f"**Previewing `{filename}` ({len(df_preview)} rows):**")
            st.dataframe(df_preview.head(5), use_container_width=True)

            if st.button("⚡ Process & Ingest Batch", type="primary", use_container_width=True):
                with st.spinner("Analyzing sentiments & extracting aspects for all records..."):
                    res = api_client.upload_file(
                        file_bytes=file_bytes,
                        filename=filename,
                        source_name=source_name,
                        token=token,
                    )
                    st.success(f"🎉 {res.get('message', 'Upload successful')}")
                    
                    # Display summary cards
                    stats = res.get("summary_stats", {}).get("sentiment_distribution", {})
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.metric("Positive Added", stats.get("positive", 0))
                    with sc2:
                        st.metric("Neutral Added", stats.get("neutral", 0))
                    with sc3:
                        st.metric("Negative Added", stats.get("negative", 0))

        except Exception as e:
            st.error(f"Error parsing file: {e}")
