"""
Script to generate synthetic Dataset-SA.csv and train + save the ML model.
Run this once before launching the Streamlit app.
"""
import pandas as pd
import numpy as np
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

np.random.seed(42)

# ── Product catalogue ────────────────────────────────────────────────────────
products = [
    ("cello Pack of 18 O...", 299),
    ("Lakm?? Eyeconic...", 450),
    ("Men Cargos", 799),
    ("MI 3i 10000 mAh...", 999),
    ("MI 5A 80 cm (32 In...", 12999),
    ("POCO C31 (Royal ...", 8999),
    ("SAMSUNG EVO Pl...", 2499),
    ("Singer FM 1409 El...", 1599),
    ("Home Sizzler 153 ...", 3499),
    ("Google Nest Mini ...", 3499),
    ("Men Black Sandal", 599),
    ("Men Graphic Prin...", 499),
    ("Men Regular Fit B...", 699),
    ("NIVIA Storm Foot...", 899),
    ("Pigeon Favourite ...", 649),
    ("Candes 12 L Room...", 3999),
    ("boAt Rockerz 450...", 1499),
    ("Philips BHH222...", 1299),
    ("Prestige PKPW 1.8L", 2199),
    ("Syska LED 9W Bulb", 199),
]

# ── Review templates ─────────────────────────────────────────────────────────
positive_reviews = [
    "super!", "awesome", "excellent product", "very happy with it",
    "best buy", "great value for money", "totally worth it", "love it",
    "amazing quality", "works perfectly", "highly recommend", "fantastic",
    "top notch quality", "exceeded expectations", "brilliant product",
    "very satisfied", "good product", "nice packaging", "great cooler excellent air flow",
    "best budget product nice quality",
]
negative_reviews = [
    "useless product", "very bad quality", "waste of money", "stopped working after one day",
    "poor build quality", "do not buy", "totally disappointed", "worst purchase ever",
    "not worth the price", "broke after a week", "terrible customer service",
    "very poor product", "defective item received", "stopped working immediately",
    "cheap material",
]
neutral_reviews = [
    "fair", "ok ok product", "average", "decent", "nothing special",
    "meets basic needs", "could be better", "its okay", "not bad not great",
    "satisfactory", "moderate quality", "works as described",
]

positive_summaries = [
    "great cooler excellent air flow and for this price totally worth it",
    "best budget product nice cooling",
    "the quality is good and delivery was fast",
    "amazing product highly recommended",
    "works great satisfied with purchase",
]
negative_summaries = [
    "very bad product its only a fan not a cooler",
    "stopped working after two days",
    "poor quality waste of money",
    "do not buy this product",
    "totally disappointed with the quality",
]
neutral_summaries = [
    "ok ok product average quality",
    "meets basic requirements nothing extra",
    "the quality is decent for the price",
    "works fine but could be better",
    "average product satisfactory",
]

N = 205052

sentiments = np.random.choice(
    ["positive", "negative", "neutral"],
    size=N,
    p=[0.812, 0.138, 0.05],
)

rows = []
for s in sentiments:
    product, price = products[np.random.randint(len(products))]
    if s == "positive":
        rate = np.random.choice([4, 5], p=[0.3, 0.7])
        review = np.random.choice(positive_reviews)
        summary = np.random.choice(positive_summaries)
    elif s == "negative":
        rate = np.random.choice([1, 2], p=[0.6, 0.4])
        review = np.random.choice(negative_reviews)
        summary = np.random.choice(negative_summaries)
    else:
        rate = 3
        review = np.random.choice(neutral_reviews)
        summary = np.random.choice(neutral_summaries)
    rows.append([product, price, rate, review, summary, s])

df = pd.DataFrame(rows, columns=["product_name", "product_price", "Rate", "Review", "Summary", "Sentiment"])

# Add ~24 k NaN in Review and ~11 NaN in Summary to match notebook
nan_review_idx = np.random.choice(df.index, size=24664, replace=False)
df.loc[nan_review_idx, "Review"] = np.nan
nan_summary_idx = np.random.choice(df.index, size=11, replace=False)
df.loc[nan_summary_idx, "Summary"] = np.nan

df.to_csv("Dataset-SA.csv", index=False)
print(f"✅ Dataset saved: {len(df):,} rows")

# ── Clean & preprocess (mirrors notebook) ────────────────────────────────────
df = df.drop_duplicates()
df = df.dropna(subset=["Review"])
df["text"] = df["Review"].fillna("") + " " + df["Summary"].fillna("")

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["clean_text"] = df["text"].apply(clean_text)
df["Rate"] = pd.to_numeric(df["Rate"], errors="coerce")
df["product_price"] = pd.to_numeric(df["product_price"], errors="coerce")
df = df.dropna(subset=["product_price", "Rate"])
df["Summary"] = df["Summary"].fillna("")

print(f"After cleaning: {df.shape}")
print(df["Sentiment"].value_counts())

# ── TF-IDF + Logistic Regression ─────────────────────────────────────────────
X = df["clean_text"]
y = df["Sentiment"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

tfidf = TfidfVectorizer(max_features=10000)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf  = tfidf.transform(X_test)

model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

acc = model.score(X_test_tfidf, y_test)
print(f"Logistic Regression Accuracy: {acc:.4f}")

joblib.dump(model, "sentiment_model.pkl")
joblib.dump(tfidf,  "tfidf_vectorizer.pkl")
print("✅ Model and vectorizer saved!")
