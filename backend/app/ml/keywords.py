import joblib
import numpy as np

def extract_keywords(model_dir, top_n=10):
    vectorizer = joblib.load(f"{model_dir}/tfidf_vectorizer.joblib")
    model = joblib.load(f"{model_dir}/logistic_regression.joblib")
    
    feature_names = np.array(vectorizer.get_feature_names_out())
    
    keywords = {}
    for i, class_label in enumerate(model.classes_):
        top_indices = np.argsort(model.coef_[i])[-top_n:]
        keywords[class_label] = feature_names[top_indices].tolist()
        
    return keywords
