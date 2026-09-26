import pytest
from backend.app.services.preprocessor import preprocessor
from backend.app.services.fast_model import fast_classifier
from backend.app.services.aspect_extractor import aspect_extractor
from backend.app.services.nlp_pipeline import nlp_orchestrator


def test_preprocessor_cleaning():
    raw_text = "<b>Amazing</b> sound quality! Check http://test.com & won't fail."
    cleaned = preprocessor.clean(raw_text)
    assert "<b>" not in cleaned
    assert "http" not in cleaned
    assert "will not" in cleaned
    assert "amazing" in cleaned.lower()


def test_fast_classifier_latency_and_output():
    text = "The headphones have incredible bass and great build quality."
    result = fast_classifier.predict(text)
    assert result["sentiment"] == "positive"
    assert result["confidence"] > 0.5
    assert result["latency_ms"] < 100.0  # sub-30ms fast path target
    assert "positive" in result["probabilities"]
    assert "negative" in result["probabilities"]


def test_aspect_extractor():
    text = "Battery died within two days but screen resolution was brilliant."
    aspects = aspect_extractor.extract_aspects(text, overall_sentiment="negative")
    assert len(aspects) > 0
    aspect_names = [a["aspect"].lower() for a in aspects]
    assert any("battery" in name or "screen" in name for name in aspect_names)


def test_dual_path_nlp_orchestrator():
    text = "Fast delivery and delicious crust pizza!"
    res = nlp_orchestrator.predict(text, model_preference="auto", extract_aspects=True)
    assert res.sentiment == "positive"
    assert res.confidence > 0.5
    assert len(res.aspects) >= 1
    assert res.model_used in ["distilbert", "tfidf_lr"]
