import streamlit as st
from api_client import predict_sentiment

st.set_page_config(page_title="Live Prediction", layout="wide")
st.title("Live Sentiment Prediction")

with st.form("predict_form"):
    text = st.text_area("Customer Review", "This product is absolutely amazing! I love it.")
    product = st.text_input("Product Name (Optional)")
    model_name = st.selectbox("Select Model", ["linearsvc", "logistic_regression", "balanced_logistic_regression"])
    
    submitted = st.form_submit_button("Predict")
    if submitted:
        try:
            res = predict_sentiment(text, product, model_name)
            st.success(f"Prediction: {res['sentiment'].upper()}")
            if res['confidence'] is not None:
                st.info(f"Confidence: {res['confidence']:.2%}")
        except Exception as e:
            st.error(f"Prediction failed: {e}")
