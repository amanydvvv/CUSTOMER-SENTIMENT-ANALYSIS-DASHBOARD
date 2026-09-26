import joblib
import os
import json
import time

models_dir = os.path.join("backend", "models")

# 1. Load artifacts
print("Loading artifacts from:", models_dir)
tfidf = joblib.load(os.path.join(models_dir, 'tfidf_vectorizer.joblib'))
lr = joblib.load(os.path.join(models_dir, 'logistic_regression.joblib'))
blr = joblib.load(os.path.join(models_dir, 'balanced_logistic_regression.joblib'))
svc = joblib.load(os.path.join(models_dir, 'linearsvc.joblib'))
X_test_tfidf, y_test = joblib.load(os.path.join(models_dir, 'test_data.joblib'))

print("[OK] All artifacts loaded successfully.")

# 2. Latency benchmark
benchmark_samples = X_test_tfidf[:5000]
latencies = {}

for name, model in [('logistic_regression', lr), ('balanced_logistic_regression', blr), ('linearsvc', svc)]:
    # warmup
    model.predict(benchmark_samples[:100])
    start = time.perf_counter()
    iters = 10
    for _ in range(iters):
        model.predict(benchmark_samples)
    elapsed = time.perf_counter() - start
    ms_per_sample = (elapsed / (iters * 5000)) * 1000
    latencies[name] = round(ms_per_sample, 4)
    print(f"  {name:<30}: {ms_per_sample:.4f} ms/sample")

# 3. Sanity check predictions on test samples
sample_reviews = [
    "This moisturizer is fantastic, my skin feels so soft and hydrated!",
    "Terrible product. Arrived broken and caused an allergic rash.",
    "It is okay, nothing special but works as described."
]

print("\nSanity check predictions on sample reviews:")
for text in sample_reviews:
    vec = tfidf.transform([text])
    print(f"Text: '{text}'")
    print(f"  Logistic Regression         : {lr.predict(vec)[0]}")
    print(f"  Balanced Logistic Regression: {blr.predict(vec)[0]}")
    print(f"  LinearSVC                   : {svc.predict(vec)[0]}")

# 4. Update evaluation_results.json
results_path = os.path.join(models_dir, 'evaluation_results.json')
with open(results_path, 'r') as f:
    results = json.load(f)

for r in results:
    if r['model_name'] in latencies:
        r['latency'] = latencies[r['model_name']]

with open(results_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\n[OK] Updated {results_path} with high-precision latencies.")
