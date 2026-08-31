import time
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.metrics import classification_report, f1_score, accuracy_score, confusion_matrix
from backend.app.core.config import settings, DATA_DIR
from backend.app.services.fast_model import fast_classifier
from backend.app.services.transformer_model import transformer_classifier
from backend.app.services.preprocessor import preprocessor


class ModelEvaluator:
    def __init__(self):
        self.labels = ["negative", "neutral", "positive"]

    def load_dataset(self, dataset_name: str = "amazon") -> pd.DataFrame:
        """Load benchmark dataset from csv."""
        if "yelp" in dataset_name.lower():
            file_path = DATA_DIR / "yelp_reviews_sample.csv"
        elif "combine" in dataset_name.lower():
            df_amz = pd.read_csv(DATA_DIR / "amazon_reviews_sample.csv")
            df_ylp = pd.read_csv(DATA_DIR / "yelp_reviews_sample.csv")
            return pd.concat([df_amz, df_ylp], ignore_index=True)
        else:
            file_path = DATA_DIR / "amazon_reviews_sample.csv"

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset file not found: {file_path}")
        return pd.read_csv(file_path)

    def evaluate_model(
        self,
        model_type: str,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """Profile and score a model on a given dataframe."""
        texts = df["review_text"].tolist()
        y_true = df["sentiment"].str.lower().tolist()

        y_pred = []
        latencies = []

        for text in texts:
            cleaned = preprocessor.clean(text)
            t0 = time.perf_counter()
            if model_type == "distilbert" and transformer_classifier.is_available:
                try:
                    res = transformer_classifier.predict(cleaned)
                    pred = res["sentiment"]
                except Exception:
                    res = fast_classifier.predict(cleaned)
                    pred = res["sentiment"]
            else:
                res = fast_classifier.predict(cleaned)
                pred = res["sentiment"]

            elapsed = (time.perf_counter() - t0) * 1000.0
            latencies.append(elapsed)
            y_pred.append(pred)

        # Metrics calculation
        acc = accuracy_score(y_true, y_pred)
        macro_f1 = f1_score(y_true, y_pred, labels=self.labels, average="macro", zero_division=0)
        weighted_f1 = f1_score(y_true, y_pred, labels=self.labels, average="weighted", zero_division=0)
        
        # Per class report
        report_dict = classification_report(
            y_true, y_pred, labels=self.labels, output_dict=True, zero_division=0
        )
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=self.labels).tolist()

        return {
            "model_name": model_type,
            "accuracy": round(float(acc), 4),
            "macro_f1": round(float(macro_f1), 4),
            "weighted_f1": round(float(weighted_f1), 4),
            "latency_avg_ms": round(float(np.mean(latencies)), 2),
            "latency_p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2),
            "latency_p99_ms": round(float(np.percentile(latencies, 99)), 2),
            "confusion_matrix": cm,
            "classification_report": report_dict,
            "predictions_sample": list(zip(texts[:5], y_true[:5], y_pred[:5]))
        }

    def run_comparative_benchmark(
        self,
        dataset_name: str = "amazon",
        sample_limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute full comparative benchmark against both models."""
        df = self.load_dataset(dataset_name)
        if sample_limit and len(df) > sample_limit:
            df = df.sample(sample_limit, random_state=42)

        # Evaluate fallback model
        fast_metrics = self.evaluate_model("tfidf_lr", df)

        # Evaluate transformer model
        transformer_metrics = self.evaluate_model("distilbert", df)

        speedup = (
            transformer_metrics["latency_avg_ms"] / max(fast_metrics["latency_avg_ms"], 0.01)
        )

        target_f1_met = transformer_metrics["macro_f1"] >= settings.TARGET_MACRO_F1

        return {
            "dataset": dataset_name,
            "sample_size": len(df),
            "target_macro_f1": settings.TARGET_MACRO_F1,
            "target_f1_achieved": target_f1_met,
            "speedup_factor": round(float(speedup), 2),
            "transformer_metrics": transformer_metrics,
            "fallback_metrics": fast_metrics,
            "labels": self.labels
        }


evaluator = ModelEvaluator()
