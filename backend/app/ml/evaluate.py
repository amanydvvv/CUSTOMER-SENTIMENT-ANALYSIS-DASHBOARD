import joblib
import os
import time
from sklearn.metrics import accuracy_score, f1_score

def evaluate_models(models_dir):
    X_test_tfidf, y_test = joblib.load(os.path.join(models_dir, 'test_data.joblib'))
    
    model_names = ['logistic_regression', 'balanced_logistic_regression', 'linearsvc']
    results = []
    
    for name in model_names:
        model = joblib.load(os.path.join(models_dir, f'{name}.joblib'))
        
        start_time = time.time()
        y_pred = model.predict(X_test_tfidf)
        inference_time = (time.time() - start_time) / len(y_test) * 1000
        
        acc = accuracy_score(y_test, y_pred)
        macro_f1 = f1_score(y_test, y_pred, average='macro')
        
        results.append({
            'model_name': name,
            'accuracy': acc,
            'f1': macro_f1,
            'latency': inference_time
        })
        
    return results

if __name__ == "__main__":
    print(evaluate_models("models"))
