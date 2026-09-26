"""
migrate_db.py
─────────────
Safe, non-destructive migration script for SQLite database (app.db).

Performs:
1. Detects existing database schema via PRAGMA table_info.
2. Adds missing columns to `model_metrics` table without dropping tables or losing data.
3. Synchronizes ModelMetric rows with genuine evaluation results from `backend/models/evaluation_results.json`.
4. Maps `macro_f1` to the `f1` column for backward compatibility.
5. Idempotent — safe to execute multiple times.
"""

import os
import json
import sqlite3
from sqlalchemy.sql import text
from app.db.database import engine, Base, SessionLocal, SQLALCHEMY_DATABASE_URL
from app.db.models import ModelMetric

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
EVAL_RESULTS_PATH = os.path.join(MODELS_DIR, "evaluation_results.json")


def get_db_path():
    """Extract SQLite filesystem path from connection URL."""
    prefix = "sqlite:///"
    if SQLALCHEMY_DATABASE_URL.startswith(prefix):
        return SQLALCHEMY_DATABASE_URL[len(prefix):]
    return os.path.join(os.path.dirname(__file__), "data", "processed", "app.db")


def migrate():
    print("=" * 60)
    print("PHASE 3: SAFE DATABASE SCHEMA MIGRATION")
    print("=" * 60)

    db_path = get_db_path()
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    print(f"Database target path: {db_path}")

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    # Inspect current schema using raw sqlite3 connection for reliability
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(model_metrics);")
    columns_info = cursor.fetchall()
    existing_columns = [col[1] for col in columns_info]
    print(f"Existing columns in `model_metrics`: {existing_columns}")

    # Add missing columns safely via ALTER TABLE
    columns_to_add = [
        ("precision", "REAL"),
        ("recall", "REAL"),
        ("macro_precision", "REAL"),
        ("macro_recall", "REAL"),
        ("macro_f1", "REAL"),
        ("weighted_precision", "REAL"),
        ("weighted_recall", "REAL"),
        ("weighted_f1", "REAL"),
    ]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            print(f"  Adding missing column: {col_name} ({col_type}) ...")
            cursor.execute(f"ALTER TABLE model_metrics ADD COLUMN {col_name} {col_type};")
        else:
            print(f"  Column '{col_name}' already exists. No alteration needed.")

    conn.commit()

    # Re-verify columns
    cursor.execute("PRAGMA table_info(model_metrics);")
    final_columns = [col[1] for col in cursor.fetchall()]
    print(f"Final columns in `model_metrics`: {final_columns}")
    conn.close()

    # Populate / update metrics from evaluation_results.json
    if os.path.exists(EVAL_RESULTS_PATH):
        print(f"\nSynchronizing model metrics from {EVAL_RESULTS_PATH} ...")
        with open(EVAL_RESULTS_PATH, "r", encoding="utf-8") as f:
            eval_data = json.load(f)

        db = SessionLocal()
        try:
            for item in eval_data:
                model_name = item.get("model_name")
                acc = item.get("accuracy")
                prec = item.get("precision")
                rec = item.get("recall")
                macro_prec = item.get("macro_precision", prec)
                macro_rec = item.get("macro_recall", rec)
                macro_f1 = item.get("macro_f1", item.get("f1"))
                weighted_prec = item.get("weighted_precision")
                weighted_rec = item.get("weighted_recall")
                weighted_f1 = item.get("weighted_f1")
                latency = item.get("latency")

                existing = db.query(ModelMetric).filter(ModelMetric.model_name == model_name).first()
                if existing:
                    existing.accuracy = acc
                    existing.precision = prec
                    existing.recall = rec
                    existing.macro_precision = macro_prec
                    existing.macro_recall = macro_rec
                    existing.macro_f1 = macro_f1
                    existing.f1 = macro_f1
                    existing.weighted_precision = weighted_prec
                    existing.weighted_recall = weighted_rec
                    existing.weighted_f1 = weighted_f1
                    existing.latency = latency
                    print(f"  Updated existing metrics for: {model_name}")
                else:
                    new_metric = ModelMetric(
                        model_name=model_name,
                        accuracy=acc,
                        precision=prec,
                        recall=rec,
                        macro_precision=macro_prec,
                        macro_recall=macro_rec,
                        macro_f1=macro_f1,
                        f1=macro_f1,
                        weighted_precision=weighted_prec,
                        weighted_recall=weighted_rec,
                        weighted_f1=weighted_f1,
                        latency=latency,
                    )
                    db.add(new_metric)
                    print(f"  Inserted new metrics for: {model_name}")

            db.commit()
            print("  [OK] Database synchronization complete.")
        finally:
            db.close()
    else:
        print(f"  WARNING: {EVAL_RESULTS_PATH} not found. Skipping metric synchronization.")

    # Query and print final records in database
    db = SessionLocal()
    try:
        records = db.query(ModelMetric).all()
        print(f"\nCurrent `model_metrics` records in database ({len(records)} total):")
        for r in records:
            print(f"  - {r.model_name:<30} | Acc: {r.accuracy:.4f} | Prec: {r.precision:.4f} | Rec: {r.recall:.4f} | Macro F1: {r.f1:.4f} | Weighted F1: {r.weighted_f1:.4f} | Latency: {r.latency:.6f} ms")
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
