import joblib
import os
import json
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def evaluate_models(models_dir):
    """
    Evaluates all three saved models against the held-out test set.

    Returns a list of dicts, each containing:
        model_name, accuracy, precision, recall,
        macro_f1, weighted_f1, latency, confusion_matrix
    Also writes evaluation_results.json to models_dir.
    """
    X_test_tfidf, y_test = joblib.load(os.path.join(models_dir, 'test_data.joblib'))

    # Load label order if available
    label_info_path = os.path.join(models_dir, 'label_info.json')
    if os.path.exists(label_info_path):
        with open(label_info_path) as f:
            label_info = json.load(f)
        labels = label_info.get('labels', sorted(y_test.unique().tolist()))
    else:
        labels = sorted(y_test.unique().tolist())

    model_names = ['logistic_regression', 'balanced_logistic_regression', 'linearsvc']
    results = []

    for name in model_names:
        model_path = os.path.join(models_dir, f'{name}.joblib')
        if not os.path.exists(model_path):
            print(f"  WARNING: {model_path} not found, skipping.")
            continue

        model = joblib.load(model_path)

        # Measure latency over entire test set, report per-sample ms
        start = time.time()
        y_pred = model.predict(X_test_tfidf)
        elapsed = time.time() - start
        latency_ms = (elapsed / len(y_test)) * 1000

        acc                = accuracy_score(y_test, y_pred)
        macro_precision    = precision_score(y_test, y_pred, average='macro', zero_division=0)
        macro_recall       = recall_score(y_test, y_pred, average='macro', zero_division=0)
        macro_f1           = f1_score(y_test, y_pred, average='macro', zero_division=0)
        weighted_precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        weighted_recall    = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        weighted_f1        = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        cm                 = confusion_matrix(y_test, y_pred, labels=labels).tolist()
        report             = classification_report(y_test, y_pred, labels=labels,
                                                 target_names=labels, zero_division=0)

        print(f"\n{'='*60}")
        print(f"Model: {name}")
        print(f"  Accuracy:           {acc:.4f}")
        print(f"  Macro Recall:       {macro_recall:.4f}")
        print(f"  Macro Precision:    {macro_precision:.4f}")
        print(f"  Macro F1:           {macro_f1:.4f}")
        print(f"  Weighted Precision: {weighted_precision:.4f}")
        print(f"  Weighted Recall:    {weighted_recall:.4f}")
        print(f"  Weighted F1:        {weighted_f1:.4f}")
        print(f"  Latency:            {latency_ms:.4f} ms/sample")
        print(f"\nClassification Report:\n{report}")
        print(f"Confusion Matrix (labels={labels}):")
        for row in cm:
            print(" ", row)

        results.append({
            'model_name':         name,
            'accuracy':           round(acc, 6),
            'precision':          round(macro_precision, 6),
            'recall':             round(macro_recall, 6),
            'macro_precision':    round(macro_precision, 6),
            'macro_recall':       round(macro_recall, 6),
            'macro_f1':           round(macro_f1, 6),
            'weighted_precision': round(weighted_precision, 6),
            'weighted_recall':    round(weighted_recall, 6),
            'weighted_f1':        round(weighted_f1, 6),
            'latency':            round(latency_ms, 6),
            'confusion_matrix':   cm,
            'labels':             labels,
        })

    # Persist results
    out_path = os.path.join(models_dir, 'evaluation_results.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nEvaluation results saved to {out_path}")

    return results


if __name__ == "__main__":
    if os.path.exists("models"):
        models_path = "models"
    elif os.path.exists(os.path.join("backend", "models")):
        models_path = os.path.join("backend", "models")
    else:
        models_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
    evaluate_models(models_path)
