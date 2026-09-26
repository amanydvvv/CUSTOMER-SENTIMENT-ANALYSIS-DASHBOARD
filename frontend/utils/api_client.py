import os
import requests
from typing import Dict, Any, Optional, List

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000/api/v1")


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def check_health(self) -> Dict[str, Any]:
        try:
            resp = requests.get("http://127.0.0.1:8000/health", timeout=3.0)
            if resp.status_code == 200:
                return {"online": True, **resp.json()}
        except Exception:
            pass
        return {"online": False}

    # Auth Methods
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/login"
        resp = requests.post(
            url,
            json={"username_or_email": username_or_email, "password": password},
            timeout=5.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise Exception(resp.json().get("detail", "Login failed"))

    def get_me(self, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/auth/me"
        resp = requests.get(url, headers=self._get_headers(token), timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        raise Exception("Failed to fetch user profile")

    # Prediction Methods
    def predict(
        self,
        text: str,
        model_preference: str = "auto",
        extract_aspects: bool = True,
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/predict"
        payload = {
            "text": text,
            "model_preference": model_preference,
            "extract_aspects": extract_aspects,
        }
        resp = requests.post(url, json=payload, headers=self._get_headers(token), timeout=15.0)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(resp.json().get("detail", "Prediction request failed"))

    # Feedback Methods
    def get_feedback(
        self,
        skip: int = 0,
        limit: int = 50,
        sentiment: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        search: Optional[str] = None,
        token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/feedback"
        params = {"skip": skip, "limit": limit}
        if sentiment and sentiment != "All":
            params["sentiment"] = sentiment.lower()
        if category and category != "All":
            params["category"] = category
        if source and source != "All":
            params["source"] = source
        if search:
            params["search"] = search

        resp = requests.get(url, params=params, headers=self._get_headers(token), timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return []

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        source_name: str = "Batch Upload",
        token: Optional[str] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/feedback/upload"
        files = {"file": (filename, file_bytes)}
        data = {"source_name": source_name}
        resp = requests.post(url, files=files, data=data, headers=self._get_headers(token), timeout=60.0)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(resp.json().get("detail", "File upload failed"))

    def delete_feedback(self, feedback_id: int, token: str) -> Dict[str, Any]:
        url = f"{self.base_url}/feedback/{feedback_id}"
        resp = requests.delete(url, headers=self._get_headers(token), timeout=5.0)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(resp.json().get("detail", "Delete failed"))

    # Analytics Methods
    def get_kpis(self, category: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/summary"
        params = {}
        if category and category != "All":
            params["category"] = category
        if source and source != "All":
            params["source"] = source
        resp = requests.get(url, params=params, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return {}

    def get_distribution(self, category: Optional[str] = None, source: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/analytics/distribution"
        params = {}
        if category and category != "All":
            params["category"] = category
        if source and source != "All":
            params["source"] = source
        resp = requests.get(url, params=params, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return {"positive": 0, "neutral": 0, "negative": 0, "total": 0}

    def get_aspects(self, limit: int = 15, category: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/aspects"
        params = {"limit": limit}
        if category and category != "All":
            params["category"] = category
        resp = requests.get(url, params=params, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return []

    def get_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/analytics/trends"
        resp = requests.get(url, params={"days": days}, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return []

    # Benchmark Methods
    def run_benchmark(self, dataset: str = "amazon", sample_limit: Optional[int] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/benchmark/run"
        params = {"dataset": dataset}
        if sample_limit:
            params["sample_limit"] = sample_limit
        resp = requests.post(url, params=params, timeout=60.0)
        if resp.status_code == 200:
            return resp.json()
        raise Exception(resp.json().get("detail", "Benchmark execution failed"))

    def get_benchmark_history(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/benchmark/history"
        resp = requests.get(url, timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        return []


api_client = APIClient()
