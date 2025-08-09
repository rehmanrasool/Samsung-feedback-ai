#!/usr/bin/env python3
"""
Samsung Feedback AI - NLP Preprocessing Script

This script handles text cleaning and embeddings generation for collected reviews.
"""

import json
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NLPPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
    def clean_text(self, text):
        """Clean and preprocess text data"""
        if not isinstance(text, str):
            return ""
            
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs, mentions, hashtags
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'@\w+|#\w+', '', text)
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def generate_embeddings(self, texts):
        """Generate sentence embeddings using transformer model"""
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts)
        return embeddings
    
    def process_reviews(self, input_file, output_file):
        """Process reviews from JSON file"""
        logger.info(f"Processing reviews from {input_file}")
        
        with open(f"../data/{input_file}", 'r') as f:
            reviews = json.load(f)
        
        processed_reviews = []
        texts = []
        
        for review in reviews:
            cleaned_text = self.clean_text(review.get('text', ''))
            if cleaned_text:
                processed_review = {
                    'original_text': review.get('text', ''),
                    'cleaned_text': cleaned_text,
                    'rating': review.get('rating', 0),
                    'source': review.get('source', 'unknown'),
                    'date': review.get('date', '')
                }
                processed_reviews.append(processed_review)
                texts.append(cleaned_text)
        
        # Generate embeddings
        if texts:
            embeddings = self.generate_embeddings(texts)
            for i, review in enumerate(processed_reviews):
                review['embedding'] = embeddings[i].tolist()
        
        # Save processed data
        with open(f"../data/{output_file}", 'w') as f:
            json.dump(processed_reviews, f, indent=2)
        
        logger.info(f"Processed {len(processed_reviews)} reviews and saved to {output_file}")
        return processed_reviews

if __name__ == "__main__":
    preprocessor = NLPPreprocessor()
    
    # Download required NLTK data
    try:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
    except:
        logger.warning("Could not download NLTK data")
    
    # Process reviews
    preprocessor.process_reviews("raw_reviews.json", "processed_reviews.json")
