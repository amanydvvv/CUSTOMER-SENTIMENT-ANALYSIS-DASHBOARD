import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'http\S+|www\S+|https\S+', ' ', text, flags=re.MULTILINE)
    
    negation_map = {
        "don't": "do not", "doesn't": "does not", "didn't": "did not",
        "can't": "cannot", "couldn't": "could not", "won't": "will not",
        "wouldn't": "would not", "aren't": "are not", "isn't": "is not",
        "wasn't": "was not", "weren't": "were not", "hasn't": "has not",
        "haven't": "have not", "hadn't": "had not", "shouldn't": "should not",
        "mightn't": "might not", "mustn't": "must not"
    }
    
    for word, replacement in negation_map.items():
        text = text.replace(word, replacement)
        
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    stop_words = set(stopwords.words('english'))
    neg_words = {'no', 'not', 'nor', 'against', 'but', 'do', 'does', 'did', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'should', 'could', 'would', 'might', 'must', 'can', 'will'}
    custom_stop_words = stop_words - neg_words
    
    words = text.split()
    filtered_words = [w for w in words if w not in custom_stop_words]
    return " ".join(filtered_words)

def preprocess_df(df):
    if 'Review' in df.columns and 'Summary' in df.columns:
        df['Review'] = df['Review'].fillna("")
        df['Summary'] = df['Summary'].fillna("")
        df['text'] = df['Review'] + " " + df['Summary']
    
    df = df[df['text'].str.strip() != ""]
    df = df.drop_duplicates()
    
    if 'Sentiment' in df.columns:
        df = df.dropna(subset=['Sentiment'])
    
    df['clean_text'] = df['text'].apply(clean_text)
    df = df[df['clean_text'].str.strip() != ""]
    return df
