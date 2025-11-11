import re
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import nltk
from nltk.corpus import stopwords
import requests
import json

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class SentimentAnalyzer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=5000)
        self.model = MultinomialNB()
        self.is_trained = False
    
    def preprocess_text(self, text):
        """Clean and preprocess text"""
        if not isinstance(text, str):
            return ""
        
        # Remove URLs, mentions, and hashtags
        text = re.sub(r'http\S+', '', text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#\w+', '', text)
        
        # Remove emojis and special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove stopwords
        try:
            stop_words = set(stopwords.words('english'))
            words = text.split()
            words = [word for word in words if word not in stop_words and len(word) > 2]
            return ' '.join(words)
        except:
            return text
    
    def get_textblob_sentiment(self, text):
        """Get sentiment using TextBlob (rule-based)"""
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    
    def get_huggingface_sentiment(self, text):
        """Get sentiment using Hugging Face API (free)"""
        try:
            API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
            headers = {"Authorization": "Bearer hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}
            
            payload = {"inputs": text[:512]}  # Truncate for API
            
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    # Get the label with highest score
                    best_result = max(result[0], key=lambda x: x['score'])
                    label = best_result['label'].lower()
                    
                    if 'positive' in label:
                        return 'positive'
                    elif 'negative' in label:
                        return 'negative'
                    else:
                        return 'neutral'
        except:
            pass
        
        # Fallback to TextBlob if API fails
        return self.get_textblob_sentiment(text)
    
    def train_ml_model(self, texts, labels):
        """Train ML model on labeled data"""
        # Preprocess texts
        processed_texts = [self.preprocess_text(text) for text in texts]
        
        # Vectorize texts
        X = self.vectorizer.fit_transform(processed_texts)
        
        # Train model
        self.model.fit(X, labels)
        self.is_trained = True
        
        # Evaluate model
        X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
        y_pred = self.model.predict(X_test)
        
        f1 = f1_score(y_test, y_pred, average='weighted')
        print(f"Model trained with F1-score: {f1:.4f}")
        print("Classification Report:")
        print(classification_report(y_test, y_pred))
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
    
    def predict_sentiment(self, text, method='textblob'):
        """Predict sentiment using specified method"""
        if method == 'textblob':
            return self.get_textblob_sentiment(text)
        elif method == 'huggingface':
            return self.get_huggingface_sentiment(text)
        elif method == 'ml' and self.is_trained:
            processed_text = self.preprocess_text(text)
            X = self.vectorizer.transform([processed_text])
            return self.model.predict(X)[0]
        else:
            return self.get_textblob_sentiment(text)  # Default to TextBlob

# Create global analyzer instance
analyzer = SentimentAnalyzer()

# Sample training data
def create_sample_data():
    """Create sample training data"""
    texts = [
        "I love this product! It's amazing!",
        "This is the worst experience ever.",
        "The product is okay, nothing special.",
        "Fantastic service and great quality!",
        "Terrible customer support, very disappointed.",
        "It's fine, works as expected.",
        "Outstanding performance and excellent value!",
        "Poor quality and bad packaging.",
        "Average product, meets basic needs.",
        "Brilliant features and wonderful design!",
        "Absolutely hate this, waste of money!",
        "Good value for the price paid.",
        "Not bad but could be better.",
        "Excellent product highly recommended!",
        "Very poor quality do not buy!"
    ]
    labels = ['positive', 'negative', 'neutral', 'positive', 'negative', 
              'neutral', 'positive', 'negative', 'neutral', 'positive',
              'negative', 'positive', 'neutral', 'positive', 'negative']
    
    return texts, labels

# Train the model on sample data
try:
    texts, labels = create_sample_data()
    analyzer.train_ml_model(texts, labels)
    print("✓ ML model trained successfully")
except Exception as e:
    print(f"✗ ML model training failed: {e}")
    print("✓ Using TextBlob sentiment analysis as fallback")