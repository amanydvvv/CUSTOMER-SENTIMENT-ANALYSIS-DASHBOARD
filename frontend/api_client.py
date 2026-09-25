import requests

BASE_URL = "http://127.0.0.1:8000"

def predict_sentiment(text: str, product: str = None, model_name: str = 'linearsvc'):
    res = requests.post(f"{BASE_URL}/predict/", json={
        "text": text,
        "product": product,
        "model_name": model_name
    })
    res.raise_for_status()
    return res.json()

def get_stats():
    res = requests.get(f"{BASE_URL}/stats/")
    res.raise_for_status()
    return res.json()

def get_reviews(product: str = None, skip: int = 0, limit: int = 100):
    params = {"skip": skip, "limit": limit}
    if product:
        params["product"] = product
    res = requests.get(f"{BASE_URL}/reviews/", params=params)
    res.raise_for_status()
    return res.json()
