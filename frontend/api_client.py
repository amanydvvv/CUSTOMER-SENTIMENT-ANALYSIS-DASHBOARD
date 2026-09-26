import requests
import streamlit as st
from typing import Dict, List, Optional, Any
from functools import lru_cache

API_BASE_URL = "http://localhost:8000"


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30

    def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Make sure the API server is running on port 8000.")
            return None
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"API error: {str(e)}")
            return None

    def health_check(self) -> bool:
        result = self._request("GET", "/health")
        return result is not None

    def get_stats(self) -> Optional[Dict]:
        return self._request("GET", "/stats")

    def get_sentiment_distribution(self) -> Optional[Dict]:
        return self._request("GET", "/stats/sentiment-distribution")

    def get_rating_distribution(self) -> Optional[Dict]:
        return self._request("GET", "/stats/rating-distribution")

    def get_product_stats(self) -> Optional[List[Dict]]:
        return self._request("GET", "/stats/products")

    def get_keywords(self, sentiment: str, top_k: int = 20) -> Optional[List[Dict]]:
        return self._request("GET", f"/stats/keywords/{sentiment}", params={"top_k": top_k})

    def predict(self, text: str, model: str = "balanced_logistic_regression") -> Optional[Dict]:
        return self._request("POST", "/predict", json={"text": text, "model": model})

    def predict_batch(self, texts: List[str], model: str = "balanced_logistic_regression") -> Optional[List[Dict]]:
        return self._request("POST", "/predict/batch", json={"texts": texts, "model": model})

    def get_models(self) -> Optional[List[str]]:
        return self._request("GET", "/models")

    def get_model_metrics(self) -> Optional[Dict]:
        return self._request("GET", "/models/metrics")

    # Google Places Live Review API methods
    def search_places(self, query: str, api_key: Optional[str] = None) -> Optional[Dict]:
        params = {"query": query}
        if api_key:
            params["api_key"] = api_key
        return self._request("GET", "/places/search", params=params)

    def analyze_place_reviews(self, place_id: str, model: str = "balanced_logistic_regression", api_key: Optional[str] = None) -> Optional[Dict]:
        params = {"model_name": model}
        if api_key:
            params["api_key"] = api_key
        return self._request("GET", f"/places/{place_id}/analyze", params=params)


@st.cache_resource
def get_api_client() -> APIClient:
    return APIClient()


def load_stats() -> Optional[Dict]:
    client = get_api_client()
    return client.get_stats()


def load_sentiment_distribution() -> Optional[Dict]:
    client = get_api_client()
    return client.get_sentiment_distribution()


def load_rating_distribution() -> Optional[Dict]:
    client = get_api_client()
    return client.get_rating_distribution()


def load_product_stats() -> Optional[List[Dict]]:
    client = get_api_client()
    return client.get_product_stats()


def load_keywords(sentiment: str, top_k: int = 20) -> Optional[List[Dict]]:
    client = get_api_client()
    return client.get_keywords(sentiment, top_k)


def predict_sentiment(text: str, model: str) -> Optional[Dict]:
    client = get_api_client()
    return client.predict(text, model)


def predict_batch(texts: List[str], model: str) -> Optional[List[Dict]]:
    client = get_api_client()
    return client.predict_batch(texts, model)


def load_model_metrics() -> Optional[Dict]:
    client = get_api_client()
    return client.get_model_metrics()


def search_google_places(query: str, api_key: Optional[str] = None) -> Optional[Dict]:
    client = get_api_client()
    return client.search_places(query, api_key=api_key)


def analyze_google_place_reviews(place_id: str, model: str = "balanced_logistic_regression", api_key: Optional[str] = None) -> Optional[Dict]:
    client = get_api_client()
    return client.analyze_place_reviews(place_id, model=model, api_key=api_key)