import json
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from backend.app.api.deps import get_db
from backend.app.models.benchmark import BenchmarkRun
from backend.app.services.evaluator import evaluator

router = APIRouter()


@router.post("/run")
def run_benchmark(
    dataset: str = Query("amazon", description="'amazon', 'yelp', or 'combined'"),
    sample_limit: Optional[int] = Query(None, ge=5, le=500),
    db: Session = Depends(get_db),
) -> Any:
    """
    Execute live dual-path model benchmark testing Macro F1, accuracy, and latency profiles.
    Saves benchmark execution history to database.
    """
    try:
        results = evaluator.run_comparative_benchmark(dataset_name=dataset, sample_limit=sample_limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark execution failed: {str(e)}",
        )

    # Save to database
    trans_m = results["transformer_metrics"]
    fall_m = results["fallback_metrics"]

    run_record = BenchmarkRun(
        dataset_name=dataset,
        sample_size=results["sample_size"],
        transformer_latency_avg_ms=trans_m["latency_avg_ms"],
        transformer_latency_p95_ms=trans_m["latency_p95_ms"],
        transformer_macro_f1=trans_m["macro_f1"],
        transformer_accuracy=trans_m["accuracy"],
        fallback_latency_avg_ms=fall_m["latency_avg_ms"],
        fallback_latency_p95_ms=fall_m["latency_p95_ms"],
        fallback_macro_f1=fall_m["macro_f1"],
        fallback_accuracy=fall_m["accuracy"],
        speedup_factor=results["speedup_factor"],
        status="PASSED" if results["target_f1_achieved"] else "REVIEW",
        details_json=json.dumps(results),
    )
    db.add(run_record)
    db.commit()
    db.refresh(run_record)

    results["run_id"] = run_record.id
    results["created_at"] = run_record.created_at.isoformat()
    return results


@router.get("/history")
def get_benchmark_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> Any:
    """Retrieve historical benchmark runs and performance logs."""
    runs = db.query(BenchmarkRun).order_by(desc(BenchmarkRun.created_at)).limit(limit).all()
    results = []
    for r in runs:
        results.append({
            "id": r.id,
            "dataset_name": r.dataset_name,
            "sample_size": r.sample_size,
            "transformer_latency_avg_ms": r.transformer_latency_avg_ms,
            "transformer_macro_f1": r.transformer_macro_f1,
            "transformer_accuracy": r.transformer_accuracy,
            "fallback_latency_avg_ms": r.fallback_latency_avg_ms,
            "fallback_macro_f1": r.fallback_macro_f1,
            "fallback_accuracy": r.fallback_accuracy,
            "speedup_factor": r.speedup_factor,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return results
