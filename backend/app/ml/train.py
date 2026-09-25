import pandas as pd
import joblib
import os
import time
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from .preprocessing import preprocess_df
from .features import get_vectorizer

def train_all(raw_data_path, models_dir):
    print("Loading data...")
    df = pd.read_csv(raw_data_path)
    df = preprocess_df(df)
    
    X = df['clean_text']
    y = df['Sentiment']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Fitting TF-IDF...")
    tfidf = get_vectorizer()
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    
    os.makedirs(models_dir, exist_ok=True)
    joblib.dump(tfidf, os.path.join(models_dir, 'tfidf_vectorizer.joblib'))
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Balanced Logistic Regression': LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42),
        'LinearSVC': LinearSVC(random_state=42, max_iter=2000)
    }
    
    for name, model in models.items():
        print(f"Training {name}...")
        model.fit(X_train_tfidf, y_train)
        joblib.dump(model, os.path.join(models_dir, f"{name.replace(' ', '_').lower()}.joblib"))
        
    joblib.dump((X_test_tfidf, y_test), os.path.join(models_dir, 'test_data.joblib'))
    print("Training complete.")

if __name__ == "__main__":
    train_all("data/raw/Dataset-SA.csv", "models")
