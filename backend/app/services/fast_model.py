import time
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from backend.app.core.config import settings
from backend.app.services.preprocessor import preprocessor

# Seed training corpus for instant bootstrap if not yet trained
SEED_CORPUS: List[Tuple[str, str]] = [
    # Positive
    ("The sound quality is truly incredible, deep bass and crystal clear highs!", "positive"),
    ("Exceptional build quality and lightning fast delivery. Highly recommended!", "positive"),
    ("Best purchase I have made all year. Works flawlessly and exceeds expectations.", "positive"),
    ("Super comfortable, fits true to size, and fabric feels luxurious.", "positive"),
    ("Customer support resolved my question in 5 minutes with great kindness.", "positive"),
    ("Delicious authentic food, crispy crust, and amazing friendly staff.", "positive"),
    ("Battery life lasts 5 full days easily. Great display and very responsive.", "positive"),
    ("Flawless experience from start to finish. Five stars all the way!", "positive"),
    ("Very well packaged and arrived ahead of schedule. Love the sleek design.", "positive"),
    ("Smooth performance, easy setup, and top notch materials.", "positive"),
    ("The camera captures stunning vibrant photos even in low light.", "positive"),
    ("Ergonomic design relieved all my back pain after long hours of work.", "positive"),
    ("Quiet, efficient, and easy to clean. Perfect addition to the kitchen.", "positive"),
    ("Incredible value for the price. Would definitely buy again.", "positive"),
    ("Handcrafted perfection with durable stitching and soft premium leather.", "positive"),
    
    # Neutral
    ("It works as expected for a basic product. Nothing special but gets the job done.", "neutral"),
    ("Decent quality for the price. Average battery life and standard features.", "neutral"),
    ("Arrived on time. The color is slightly different than pictures but acceptable.", "neutral"),
    ("Standard diner experience with average food and prompt water refills.", "neutral"),
    ("The interface is okay once you get used to the menu navigation.", "neutral"),
    ("Fairly standard product with functional build and ordinary specifications.", "neutral"),
    ("It operates fine if you follow the manual instructions carefully.", "neutral"),
    ("Acceptable sound for casual listening, though not audiophile grade.", "neutral"),
    ("Moderate weight, simple design, works adequately for everyday use.", "neutral"),
    ("Neutral experience. Neither bad nor outstanding, just average.", "neutral"),
    
    # Negative
    ("Battery died within two weeks of light usage. Completely useless.", "negative"),
    ("Terrible customer service. Refused to issue a refund for defective item.", "negative"),
    ("Broke on the first day. Extremely cheap plastic and poor craftsmanship.", "negative"),
    ("Food was cold, soggy, and arrived two hours late. Never ordering again.", "negative"),
    ("Constantly disconnects and crashes. Horrible software and buggy firmware.", "negative"),
    ("Overpriced garbage. Sizing is completely wrong and material feels itchy.", "negative"),
    ("Arrived damaged with scratched screen and missing power adapter.", "negative"),
    ("Unbearable noise, loud fan rattling, and overheats within ten minutes.", "negative"),
    ("Do not waste your money on this awful product. Total disappointment.", "negative"),
    ("Wait staff was rude and dismissive. Inedible meal and dirty tables.", "negative"),
    ("Severe allergic reaction caused by overpowering synthetic fragrance.", "negative"),
    ("Sole detached after two rainy walks. Not water resistant as claimed.", "negative"),
    ("Lost all my data after power reboot. Very unstable and unreliable.", "negative"),
    ("Missing parts in the box and instructions were completely incomprehensible.", "negative"),
    ("Worst purchase ever. Broke immediately and company ignored my emails.", "negative"),
]


class FastSentimentClassifier:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = model_path or settings.FALLBACK_MODEL_PATH
        self.pipeline: Optional[Pipeline] = None
        self.classes_: List[str] = ["negative", "neutral", "positive"]
        self._load_or_train()

    def _load_or_train(self):
        """Load serialized model or train on seed corpus if file doesn't exist."""
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                return
            except Exception:
                pass
        
        self.train_and_save(SEED_CORPUS)

    def train_and_save(self, corpus: List[Tuple[str, str]]):
        """Train TF-IDF + Logistic Regression pipeline and serialize to disk."""
        texts, labels = zip(*corpus)
        cleaned_texts = [preprocessor.clean(t) for t in texts]

        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=5000,
                sublinear_tf=True,
                stop_words="english"
            )),
            ("clf", LogisticRegression(
                C=1.5,
                max_iter=500,
                class_weight="balanced",
                random_state=42
            ))
        ])

        pipeline.fit(cleaned_texts, labels)
        self.pipeline = pipeline
        self.classes_ = list(pipeline.classes_)

        # Ensure directory exists and save
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(pipeline, self.model_path)

    def predict(self, text: str) -> Dict:
        """Predict sentiment with latency profiling and probability distribution."""
        start_time = time.perf_counter()
        cleaned = preprocessor.clean(text)

        if not self.pipeline:
            self._load_or_train()

        probs = self.pipeline.predict_proba([cleaned])[0]
        classes = self.pipeline.classes_
        prob_dict = {cls: float(p) for cls, p in zip(classes, probs)}
        
        # Ensure all standard 3 classes exist in dict
        for c in ["positive", "neutral", "negative"]:
            if c not in prob_dict:
                prob_dict[c] = 0.0

        predicted_class = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[predicted_class]
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "sentiment": predicted_class,
            "confidence": round(float(confidence), 4),
            "probabilities": {k: round(v, 4) for k, v in prob_dict.items()},
            "model_used": "tfidf_lr",
            "latency_ms": round(float(latency_ms), 2),
            "cleaned_text": cleaned
        }

    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Batch predict sentiment."""
        start_time = time.perf_counter()
        cleaned_texts = [preprocessor.clean(t) for t in texts]
        probs_batch = self.pipeline.predict_proba(cleaned_texts)
        classes = self.pipeline.classes_
        
        results = []
        elapsed = (time.perf_counter() - start_time) * 1000.0
        avg_latency = elapsed / max(len(texts), 1)

        for text, cleaned, probs in zip(texts, cleaned_texts, probs_batch):
            prob_dict = {cls: float(p) for cls, p in zip(classes, probs)}
            for c in ["positive", "neutral", "negative"]:
                if c not in prob_dict:
                    prob_dict[c] = 0.0
            predicted_class = max(prob_dict, key=prob_dict.get)
            results.append({
                "sentiment": predicted_class,
                "confidence": round(float(prob_dict[predicted_class]), 4),
                "probabilities": {k: round(v, 4) for k, v in prob_dict.items()},
                "model_used": "tfidf_lr",
                "latency_ms": round(float(avg_latency), 2),
                "cleaned_text": cleaned,
                "review_text": text
            })
        return results


fast_classifier = FastSentimentClassifier()
