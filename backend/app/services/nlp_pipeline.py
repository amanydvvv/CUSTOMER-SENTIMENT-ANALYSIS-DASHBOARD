import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from backend.app.core.config import settings
from backend.app.services.preprocessor import preprocessor
from backend.app.services.fast_model import fast_classifier
from backend.app.services.transformer_model import transformer_classifier
from backend.app.services.aspect_extractor import aspect_extractor
from backend.app.schemas.feedback import PredictResponse, AspectItem

logger = logging.getLogger(__name__)


class DualPathNLPOrchestrator:
    def __init__(self):
        self.transformer_timeout_ms = settings.TRANSFORMER_TIMEOUT_MS

    def predict(
        self,
        text: str,
        model_preference: str = "auto",
        extract_aspects: bool = True,
    ) -> PredictResponse:
        """
        Execute dual-path sentiment classification with automatic failover and aspect extraction.
        """
        start_time = time.perf_counter()
        cleaned_text = preprocessor.clean(text)
        fallback_triggered = False
        prediction_result = None

        # Route 1: Explicit Fallback requested
        if model_preference == "fallback":
            prediction_result = fast_classifier.predict(cleaned_text)
            prediction_result["model_used"] = "tfidf_lr"

        # Route 2: Explicit Primary or Auto Routing
        else:
            try:
                # Attempt primary transformer inference
                if transformer_classifier.is_available:
                    t_start = time.perf_counter()
                    prediction_result = transformer_classifier.predict(cleaned_text)
                    t_latency = (time.perf_counter() - t_start) * 1000.0
                    
                    # If transformer took longer than configured threshold, log warning
                    if t_latency > self.transformer_timeout_ms:
                        logger.warning(
                            f"Transformer latency {t_latency:.1f}ms exceeded threshold {self.transformer_timeout_ms}ms"
                        )
                else:
                    # Transformer not available, fallback seamlessly
                    fallback_triggered = True
                    prediction_result = fast_classifier.predict(cleaned_text)
            except Exception as ex:
                logger.error(f"Transformer model error: {ex}. Falling back to TF-IDF+LR.")
                fallback_triggered = True
                prediction_result = fast_classifier.predict(cleaned_text)

        # Safety guarantee
        if not prediction_result:
            fallback_triggered = True
            prediction_result = fast_classifier.predict(cleaned_text)

        total_latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Extract Aspects
        aspect_items = []
        if extract_aspects:
            raw_aspects = aspect_extractor.extract_aspects(
                cleaned_text,
                overall_sentiment=prediction_result["sentiment"]
            )
            aspect_items = [
                AspectItem(
                    aspect=a["aspect"],
                    sentiment=a["sentiment"],
                    relevance=a["relevance"]
                )
                for a in raw_aspects
            ]

        return PredictResponse(
            review_text=text,
            cleaned_text=cleaned_text,
            sentiment=prediction_result["sentiment"],
            confidence=prediction_result["confidence"],
            probabilities=prediction_result["probabilities"],
            model_used=prediction_result.get("model_used", "tfidf_lr"),
            latency_ms=round(total_latency_ms, 2),
            aspects=aspect_items,
            fallback_triggered=fallback_triggered
        )

    def predict_batch(
        self,
        texts: List[str],
        model_preference: str = "auto",
        extract_aspects: bool = True
    ) -> List[PredictResponse]:
        """Batch inference pipeline with parallel ThreadPoolExecutor throughput."""
        def _predict_single(text: str) -> PredictResponse:
            return self.predict(
                text=text,
                model_preference=model_preference,
                extract_aspects=extract_aspects
            )

        # Use up to 4 threads for parallel inference
        max_workers = min(4, len(texts)) if texts else 1
        results: List[PredictResponse] = [None] * len(texts)  # type: ignore

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(_predict_single, text): idx
                for idx, text in enumerate(texts)
            }
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                results[idx] = future.result()

        return results


nlp_orchestrator = DualPathNLPOrchestrator()
