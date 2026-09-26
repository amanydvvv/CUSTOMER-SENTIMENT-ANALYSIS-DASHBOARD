import sys
import os

sys.path.insert(0, os.getcwd())

from frontend.data_loader import load_historical_dataset, filter_dataset
from frontend.components.aspect_analyzer import extract_aspects_and_issues
from frontend.pages import overview, live_prediction, keyword_insights, model_comparison

print("[1/4] Testing Data Loader...")
df = load_historical_dataset(sample_limit=1000)
print(f"  Loaded dataset slice: {len(df)} rows, columns: {list(df.columns)}")
filtered = filter_dataset(df, selected_ratings=["5.0"])
print(f"  Filtered 5.0 stars: {len(filtered)} rows")

print("\n[2/4] Testing Aspect & Pain Point Intelligence...")
samples = [
    ("The moisturizer gave me a severe red burning rash after 2 days.", "negative", 1.0),
    ("Delivery was delayed by 2 weeks and box was completely crushed.", "negative", 1.0),
    ("Fantastic shampoo, my hair is soft and smells wonderful!", "positive", 5.0),
    ("The spray nozzle broke and leaked all over my counter.", "negative", 2.0)
]
for text, sent, rating in samples:
    intel = extract_aspects_and_issues(text, sentiment=sent, rating=rating)
    print(f"  Text: {text[:45]}...")
    print(f"    Aspect: {intel['primary_aspect']} | Issue: {intel['issue']} | Priority: {intel['priority']}")
    print(f"    Action: {intel['suggested_action']}")

print("\n[3/4] Testing Page Module Exports...")
assert hasattr(overview, "render"), "overview.render missing"
assert hasattr(live_prediction, "render"), "live_prediction.render missing"
assert hasattr(keyword_insights, "render"), "keyword_insights.render missing"
assert hasattr(model_comparison, "render"), "model_comparison.render missing"
print("  [OK] All page modules loaded and verified.")

print("\n[4/4] All Frontend Smoke Tests Passed Successfully!")
