# #!/usr/bin/env python3
# """
# Samsung Feedback AI - NLP Preprocessing Script

# This script handles text cleaning and embeddings generation for collected reviews.
# """

# import json
# import re
# import pandas as pd
# import numpy as np
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sentence_transformers import SentenceTransformer
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from nltk.stem import WordNetLemmatizer
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class NLPPreprocessor:
#     def __init__(self):
#         self.lemmatizer = WordNetLemmatizer()
#         self.stop_words = set(stopwords.words('english'))
#         self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
#     def clean_text(self, text):
#         """Clean and preprocess text data"""
#         if not isinstance(text, str):
#             return ""
            
#         # Convert to lowercase
#         text = text.lower()
        
#         # Remove URLs, mentions, hashtags
#         text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
#         text = re.sub(r'@\w+|#\w+', '', text)
        
#         # Remove special characters and digits
#         text = re.sub(r'[^a-zA-Z\s]', '', text)
        
#         # Tokenize
#         tokens = word_tokenize(text)
        
#         # Remove stopwords and lemmatize
#         tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
#                  if token not in self.stop_words and len(token) > 2]
        
#         return ' '.join(tokens)
    
#     def generate_embeddings(self, texts):
#         """Generate sentence embeddings using transformer model"""
#         logger.info(f"Generating embeddings for {len(texts)} texts")
#         embeddings = self.model.encode(texts)
#         return embeddings
    
#     def process_reviews(self, input_file, output_file):
#         """Process reviews from JSON file"""
#         logger.info(f"Processing reviews from {input_file}")
        
#         with open(f"../data/{input_file}", 'r') as f:
#             reviews = json.load(f)
        
#         processed_reviews = []
#         texts = []
        
#         for review in reviews:
#             cleaned_text = self.clean_text(review.get('text', ''))
#             if cleaned_text:
#                 processed_review = {
#                     'original_text': review.get('text', ''),
#                     'cleaned_text': cleaned_text,
#                     'rating': review.get('rating', 0),
#                     'source': review.get('source', 'unknown'),
#                     'date': review.get('date', '')
#                 }
#                 processed_reviews.append(processed_review)
#                 texts.append(cleaned_text)
        
#         # Generate embeddings
#         if texts:
#             embeddings = self.generate_embeddings(texts)
#             for i, review in enumerate(processed_reviews):
#                 review['embedding'] = embeddings[i].tolist()
        
#         # Save processed data
#         with open(f"../data/{output_file}", 'w') as f:
#             json.dump(processed_reviews, f, indent=2)
        
#         logger.info(f"Processed {len(processed_reviews)} reviews and saved to {output_file}")
#         return processed_reviews

# if __name__ == "__main__":
#     preprocessor = NLPPreprocessor()
    
#     # Download required NLTK data
#     try:
#         nltk.download('punkt')
#         nltk.download('stopwords')
#         nltk.download('wordnet')
#     except:
#         logger.warning("Could not download NLTK data")
    
#     # Process reviews
#     preprocessor.process_reviews("raw_reviews.json", "processed_reviews.json")



#------------------ New code added 12 August 2.34 PM

# preprocess_nlp.py
import json
import argparse
import string
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from keybert import KeyBERT

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

PLATFORM_KEYWORDS = ["app", "login", "crash", "payment", "checkout", "install", "update"]
PRODUCT_KEYWORDS = ["defect", "defective", "broken", "quality", "warranty", "replacement", "battery"]
SERVICE_KEYWORDS = ["customer", "support", "customer care", "delivery", "refund", "delay"]

SEVERE_TERMS = ["worst", "fraud", "pathetic", "unusable", "defective", "broken", "refund"]
MODULE_MAP = {
    "checkout": "Checkout",
    "payment": "Payment",
    "delivery": "Delivery",
    "customer": "Customer Support",
    "refund": "Returns & Refund",
    "login": "Authentication",
    "app": "Mobile App",
    "website": "Website",
    "screen": "Hardware - Screen",
    "battery": "Hardware - Battery",
    "freeze": "Appliances",
}

def preprocess_text(text):
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)

def categorize_issue(text: str) -> str:
    if any(k in text for k in PRODUCT_KEYWORDS):
        return "Product"
    if any(k in text for k in PLATFORM_KEYWORDS):
        return "Platform"
    if any(k in text for k in SERVICE_KEYWORDS):
        return "Service"
    return "Other"

def detect_module(sample_texts) -> str:
    combined = " ".join(sample_texts)
    scores = Counter({module: combined.count(k) for k, module in MODULE_MAP.items() if k in combined})
    if scores:
        return scores.most_common(1)[0][0]
    return "General"

def severity_score(text: str) -> int:
    count = sum(1 for s in SEVERE_TERMS if s in text)
    return min(10, int(count * 3 + 2))

def preprocess(input_path, output_path, num_clusters=3):
    with open(input_path, 'r', encoding='utf-8') as f:
        mock_data = json.load(f)

    processed_feedback = [preprocess_text(item["text"]) for item in mock_data if "text" in item]

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(processed_feedback)

    clustering_model = KMeans(n_clusters=num_clusters, random_state=42)
    labels = clustering_model.fit_predict(embeddings)

    clusters = {i: [] for i in range(num_clusters)}
    for idx, label in enumerate(labels):
        clusters[label].append(mock_data[idx]["text"])

    kw_model = KeyBERT()
    cluster_summaries = {}
    for cluster_id, feedbacks in clusters.items():
        joined_text = " ".join(feedbacks)
        keywords = kw_model.extract_keywords(joined_text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=3)
        category = categorize_issue(joined_text.lower())
        module = detect_module(feedbacks)
        severity = severity_score(joined_text.lower())

        cluster_summaries[cluster_id] = {
            "feedback_count": len(feedbacks),
            "sample_feedback": feedbacks[:2],
            "keywords": [kw for kw, _ in keywords],
            "category": category,
            "module": module,
            "severity_score": severity
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cluster_summaries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/mock_data.json')
    parser.add_argument('--output', default='data/summarize_problems.json')

    args = parser.parse_args()
    preprocess(args.input, args.output)