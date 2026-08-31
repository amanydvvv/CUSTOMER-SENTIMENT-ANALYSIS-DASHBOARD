import pytest
from backend.app.services.evaluator import evaluator


def test_benchmark_evaluation_structure():
    results = evaluator.run_comparative_benchmark(dataset_name="amazon", sample_limit=20)
    assert "transformer_metrics" in results
    assert "fallback_metrics" in results
    assert "speedup_factor" in results
    assert results["sample_size"] == 20

    fallback = results["fallback_metrics"]
    assert fallback["latency_avg_ms"] < 50.0
    assert fallback["macro_f1"] >= 0.70  # Validated against benchmark samples


def test_yelp_benchmark_execution():
    results = evaluator.run_comparative_benchmark(dataset_name="yelp", sample_limit=20)
    assert results["target_macro_f1"] == 0.88
    assert results["sample_size"] == 20
    assert results["speedup_factor"] > 0
