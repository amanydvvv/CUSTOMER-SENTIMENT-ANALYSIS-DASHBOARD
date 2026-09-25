from sklearn.feature_extraction.text import TfidfVectorizer

def get_vectorizer():
    return TfidfVectorizer(ngram_range=(1, 2), max_features=10000, lowercase=True)
