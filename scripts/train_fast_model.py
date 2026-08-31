import os
import sys
from pathlib import Path
import pandas as pd

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.core.config import DATA_DIR, settings
from backend.app.services.fast_model import fast_classifier


def train_on_benchmark_data():
    print("Training TF-IDF + Logistic Regression Model on Benchmark Datasets...")
    
    corpus = []
    
    # Load Amazon
    amz_path = DATA_DIR / "amazon_reviews_sample.csv"
    if os.path.exists(amz_path):
        df_amz = pd.read_csv(amz_path)
        for _, row in df_amz.iterrows():
            corpus.append((str(row["review_text"]), str(row["sentiment"]).lower()))
            
    # Load Yelp
    ylp_path = DATA_DIR / "yelp_reviews_sample.csv"
    if os.path.exists(ylp_path):
        df_ylp = pd.read_csv(ylp_path)
        for _, row in df_ylp.iterrows():
            corpus.append((str(row["review_text"]), str(row["sentiment"]).lower()))
            
    print(f"Total training samples: {len(corpus)}")
    fast_classifier.train_and_save(corpus)
    print(f"Model saved successfully to: {settings.FALLBACK_MODEL_PATH}")


if __name__ == "__main__":
    train_on_benchmark_data()
