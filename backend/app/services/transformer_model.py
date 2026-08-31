import time
from typing import Dict, List, Optional
from backend.app.core.config import settings
from backend.app.services.preprocessor import preprocessor

_transformer_pipeline = None
_pipeline_loading_error = None


class TransformerSentimentClassifier:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.DISTILBERT_MODEL_NAME
        self._pipeline = None
        self._is_ready = False

    def initialize(self):
        """Attempt to load transformer model pipeline."""
        global _transformer_pipeline, _pipeline_loading_error
        if _transformer_pipeline is not None:
            self._pipeline = _transformer_pipeline
            self._is_ready = True
            return True

        try:
            from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
            import torch

            # Load lightweight pipeline
            device = 0 if torch.cuda.is_available() else -1
            self._pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                top_k=None,
                device=device,
            )
            _transformer_pipeline = self._pipeline
            self._is_ready = True
            return True
        except Exception as e:
            _pipeline_loading_error = str(e)
            self._is_ready = False
            return False

    @property
    def is_available(self) -> bool:
        if not self._is_ready:
            return self.initialize()
        return True

    def predict(self, text: str) -> Dict:
        """Run DistilBERT inference with latency measurement and 3-class normalized output."""
        start_time = time.perf_counter()
        cleaned = preprocessor.clean(text)

        if not self.is_available or self._pipeline is None:
            raise RuntimeError(f"Transformer model unavailable: {_pipeline_loading_error}")

        # Truncate text for safety
        input_text = cleaned[:512] if len(cleaned) > 512 else cleaned
        raw_outputs = self._pipeline(input_text)
        
        # Flatten raw outputs if nested
        if isinstance(raw_outputs, list) and len(raw_outputs) > 0 and isinstance(raw_outputs[0], list):
            scores_list = raw_outputs[0]
        else:
            scores_list = raw_outputs

        # Map labels (e.g. POSITIVE -> positive, NEGATIVE -> negative, LABEL_0/1/2)
        prob_dict = {"positive": 0.0, "neutral": 0.0, "negative": 0.0}
        
        for item in scores_list:
            label = item.get("label", "").upper()
            score = float(item.get("score", 0.0))
            if "POS" in label or label == "LABEL_2":
                prob_dict["positive"] = score
            elif "NEG" in label or label == "LABEL_0":
                prob_dict["negative"] = score
            elif "NEU" in label or label == "LABEL_1":
                prob_dict["neutral"] = score

        # If model is 2-class (SST-2 without explicit neutral), calculate neutral confidence for borderline cases
        if prob_dict["neutral"] == 0.0:
            diff = abs(prob_dict["positive"] - prob_dict["negative"])
            if diff < 0.25:  # Close probability indicates neutral nuance
                neutral_weight = 1.0 - diff
                prob_dict["neutral"] = round(neutral_weight * 0.5, 4)
                prob_dict["positive"] = round(prob_dict["positive"] * 0.75, 4)
                prob_dict["negative"] = round(prob_dict["negative"] * 0.75, 4)

        # Normalize probabilities sum to 1.0
        total_p = sum(prob_dict.values())
        if total_p > 0:
            prob_dict = {k: round(v / total_p, 4) for k, v in prob_dict.items()}

        predicted_class = max(prob_dict, key=prob_dict.get)
        confidence = prob_dict[predicted_class]
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "sentiment": predicted_class,
            "confidence": round(float(confidence), 4),
            "probabilities": prob_dict,
            "model_used": "distilbert",
            "latency_ms": round(float(latency_ms), 2),
            "cleaned_text": cleaned,
        }


transformer_classifier = TransformerSentimentClassifier()
