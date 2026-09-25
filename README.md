# Customer Sentiment Analysis Dashboard

## 1. Project Title
**Customer Sentiment Analysis Dashboard**
A B.Tech CSE/ISE mini-project focused on analyzing customer feedback using Natural Language Processing (NLP) and Machine Learning to classify sentiments into Positive, Negative, and Neutral.

## 2. Problem Statement
Businesses receive thousands of customer reviews across various products. Manually reading and analyzing these reviews is time-consuming and inefficient. There is a need for an automated system capable of analyzing large volumes of customer text to derive actionable business insights and monitor brand reputation.

## 3. Objectives
- Build an end-to-end NLP pipeline for text preprocessing and feature extraction.
- Train and evaluate multiple Machine Learning classification models on customer review data.
- Deploy the best-performing model as part of an interactive web dashboard.
- Provide live sentiment prediction capabilities for new reviews.
- Generate aggregated business insights based on product and sentiment categories.

## 4. Features
- **Data Preprocessing:** Handles missing values, removes HTML tags, normalizes case, and preserves negations while removing standard stopwords.
- **TF-IDF Feature Extraction:** Utilizes unigram and bigram features for accurate text representation.
- **Machine Learning Models:** Logistic Regression, Balanced Logistic Regression, and LinearSVC.
- **Interactive Dashboard:** Built using Streamlit, featuring real-time KPI metrics, sentiment distributions, and interactive filtering.
- **Live Prediction:** A dedicated module for predicting sentiment on unseen user input, complete with confidence scores.
- **Review Explorer:** Allows direct inspection of processed reviews to cross-check predictions.

## 5. Architecture
The project follows a standard 2-tier architecture separating the Data Science/Machine Learning pipeline from the Application layer.
1. **ML Pipeline (`src/`):** Processes the raw dataset, extracts features, trains models, evaluates performance, and saves serialized artifacts.
2. **Dashboard Application (`app.py`):** A Streamlit front-end that loads the pre-trained models and cached datasets to deliver a highly interactive user experience without redundant training.

## 6. Dataset Description
The dataset contains synthetic E-Commerce reviews.
- **Number of Records:** ~150,000 to ~200,000 depending on preprocessing.
- **Columns:** `product_name`, `product_price`, `Rate`, `Review`, `Summary`, `Sentiment`.
- **Classes:** Positive, Negative, Neutral.

## 7. Technologies Used
- **Language:** Python
- **Data Manipulation:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn
- **Natural Language Processing:** NLTK
- **Visualizations:** Plotly, Matplotlib
- **Web Framework:** Streamlit
- **Serialization:** Joblib

## 8. Machine Learning Approach
1. **Cleaning:** Dropping duplicates and NaNs, concatenating `Review` and `Summary`.
2. **Text Normalization:** Lowercasing, removing special characters, and filtering stopwords while carefully keeping negations (e.g., *don't*, *wasn't*).
3. **Vectorization:** TF-IDF Vectorizer with `max_features=10000` and `ngram_range=(1, 2)`.
4. **Splitting:** 80:20 Stratified Split using a fixed `random_state=42`.
5. **Training:** Supervised classification over the TF-IDF matrix.

## 9. Model Comparison

| Model | Accuracy | Macro F1 | Weighted F1 |
|-------|----------|----------|-------------|
| Logistic Regression | 1.00 | 1.00 | 1.00 |
| Balanced Logistic Regression | 1.00 | 1.00 | 1.00 |
| LinearSVC | 1.00 | 1.00 | 1.00 |

*(Note: The models achieve perfect metrics due to the highly structured, synthetic nature of the generated text dataset. In a real-world messy dataset, these metrics would naturally vary. LinearSVC or Logistic Regression are highly effective for these sparse TF-IDF spaces.)*

## 10. Dashboard Screenshots
*(Add screenshots of your dashboard here before submitting the project)*
- `Dashboard_Overview.png`
- `Live_Prediction.png`
- `Customer_Insights.png`

## 11. Installation
Ensure you have Python 3.8+ installed.

1. Clone or extract the project repository.
2. Open a terminal/command prompt in the project root folder.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 12. Running Instructions
**Step 1: Data Generation (If necessary)**
If `data/raw/Dataset-SA.csv` is missing, you may need to run the dataset generation script first (if provided in your workspace).

**Step 2: Train the Models**
From the project root, navigate to the source directory and run the training pipeline:
```bash
cd src
python train.py
python evaluate.py
cd ..
```

**Step 3: Launch the Dashboard**
```bash
streamlit run app.py
```
The application will launch in your default web browser at `http://localhost:8501`.

## 13. Project Structure
```
customer-sentiment-dashboard/
├── data/
│   ├── raw/                 # Contains the raw CSV datasets
│   └── processed/           # Contains generated metrics CSV
├── models/                  # Serialized joblib models and TF-IDF vectorizers
├── src/
│   ├── preprocessing.py     # NLP cleaning functions
│   ├── train.py             # ML training pipeline
│   ├── evaluate.py          # Model evaluation script
│   └── prediction.py        # Live inference logic
├── app.py                   # Streamlit dashboard application
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## 14. Team Contributions
- **Member 1:** Data Collection & NLP Preprocessing Pipeline.
- **Member 2:** Machine Learning Model Training & Evaluation.
- **Member 3:** Streamlit Dashboard Design & Integration.

## 15. Future Enhancements
- **Aspect-Based Sentiment Analysis:** Identifying sentiments directed specifically at 'Delivery', 'Price', or 'Quality'.
- **Database Integration:** Moving from static CSVs to a live relational database (SQLite/PostgreSQL) with SQLAlchemy.
- **Advanced NLP:** Exploring Transformer-based models like BERT or DistilBERT for contextual embeddings.
- **FastAPI Backend:** Fully decoupling the ML inference logic into an independent REST API.
