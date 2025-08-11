# #!/usr/bin/env python3
# """
# Samsung Feedback AI - Feedback Clustering Script

# This script performs clustering on processed reviews using DBSCAN or KMeans.
# """

# import json
# import numpy as np
# import pandas as pd
# from sklearn.cluster import DBSCAN, KMeans
# from sklearn.metrics import silhouette_score
# from sklearn.decomposition import PCA
# import matplotlib.pyplot as plt
# import seaborn as sns
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# class FeedbackClusterer:
#     def __init__(self):
#         self.embeddings = None
#         self.reviews = None
#         self.clusters = None
        
#     def load_processed_data(self, filename):
#         """Load processed reviews with embeddings"""
#         logger.info(f"Loading processed data from {filename}")
        
#         with open(f"../data/{filename}", 'r') as f:
#             self.reviews = json.load(f)
        
#         # Extract embeddings
#         self.embeddings = np.array([review['embedding'] for review in self.reviews])
#         logger.info(f"Loaded {len(self.reviews)} reviews with {self.embeddings.shape[1]}D embeddings")
        
#     def perform_dbscan_clustering(self, eps=0.5, min_samples=5):
#         """Perform DBSCAN clustering"""
#         logger.info(f"Performing DBSCAN clustering with eps={eps}, min_samples={min_samples}")
        
#         dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
#         self.clusters = dbscan.fit_predict(self.embeddings)
        
#         n_clusters = len(set(self.clusters)) - (1 if -1 in self.clusters else 0)
#         n_noise = list(self.clusters).count(-1)
        
#         logger.info(f"Found {n_clusters} clusters and {n_noise} noise points")
        
#         if n_clusters > 1:
#             silhouette_avg = silhouette_score(self.embeddings, self.clusters)
#             logger.info(f"Silhouette score: {silhouette_avg:.3f}")
        
#         return self.clusters
    
#     def perform_kmeans_clustering(self, n_clusters=5):
#         """Perform KMeans clustering"""
#         logger.info(f"Performing KMeans clustering with {n_clusters} clusters")
        
#         kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
#         self.clusters = kmeans.fit_predict(self.embeddings)
        
#         silhouette_avg = silhouette_score(self.embeddings, self.clusters)
#         logger.info(f"Silhouette score: {silhouette_avg:.3f}")
        
#         return self.clusters
    
#     def find_optimal_clusters(self, max_clusters=10):
#         """Find optimal number of clusters using elbow method"""
#         logger.info("Finding optimal number of clusters")
        
#         inertias = []
#         silhouette_scores = []
#         k_range = range(2, max_clusters + 1)
        
#         for k in k_range:
#             kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
#             cluster_labels = kmeans.fit_predict(self.embeddings)
            
#             inertias.append(kmeans.inertia_)
#             silhouette_scores.append(silhouette_score(self.embeddings, cluster_labels))
        
#         # Find optimal k (highest silhouette score)
#         optimal_k = k_range[np.argmax(silhouette_scores)]
#         logger.info(f"Optimal number of clusters: {optimal_k}")
        
#         return optimal_k, inertias, silhouette_scores
    
#     def analyze_clusters(self):
#         """Analyze cluster characteristics"""
#         if self.clusters is None:
#             logger.error("No clustering performed yet")
#             return
        
#         cluster_analysis = {}
#         unique_clusters = set(self.clusters)
        
#         for cluster_id in unique_clusters:
#             if cluster_id == -1:  # Noise points in DBSCAN
#                 continue
                
#             cluster_reviews = [self.reviews[i] for i, c in enumerate(self.clusters) if c == cluster_id]
            
#             # Calculate average rating
#             ratings = [r.get('rating', 0) for r in cluster_reviews if r.get('rating', 0) > 0]
#             avg_rating = np.mean(ratings) if ratings else 0
            
#             # Get sample texts
#             sample_texts = [r['cleaned_text'][:100] + '...' for r in cluster_reviews[:3]]
            
#             cluster_analysis[cluster_id] = {
#                 'size': len(cluster_reviews),
#                 'avg_rating': avg_rating,
#                 'sample_texts': sample_texts
#             }
        
#         return cluster_analysis
    
#     def save_clustered_data(self, filename):
#         """Save reviews with cluster labels"""
#         if self.clusters is None:
#             logger.error("No clustering performed yet")
#             return
        
#         # Add cluster labels to reviews
#         for i, review in enumerate(self.reviews):
#             review['cluster'] = int(self.clusters[i])
        
#         with open(f"../data/{filename}", 'w') as f:
#             json.dump(self.reviews, f, indent=2)
        
#         logger.info(f"Saved clustered data to {filename}")
    
#     def visualize_clusters(self, filename="cluster_visualization.png"):
#         """Create 2D visualization of clusters using PCA"""
#         if self.clusters is None:
#             logger.error("No clustering performed yet")
#             return
        
#         # Reduce dimensionality for visualization
#         pca = PCA(n_components=2)
#         embeddings_2d = pca.fit_transform(self.embeddings)
        
#         plt.figure(figsize=(10, 8))
#         scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
#                             c=self.clusters, cmap='viridis', alpha=0.6)
#         plt.colorbar(scatter)
#         plt.title('Feedback Clusters Visualization (PCA)')
#         plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} variance)')
#         plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} variance)')
        
#         plt.tight_layout()
#         plt.savefig(f"../data/{filename}", dpi=300, bbox_inches='tight')
#         plt.close()
        
#         logger.info(f"Saved cluster visualization to {filename}")

# if __name__ == "__main__":
#     clusterer = FeedbackClusterer()
    
#     # Load processed data
#     clusterer.load_processed_data("processed_reviews.json")
    
#     # Find optimal number of clusters
#     optimal_k, _, _ = clusterer.find_optimal_clusters()
    
#     # Perform clustering
#     clusterer.perform_kmeans_clustering(optimal_k)
    
#     # Analyze clusters
#     analysis = clusterer.analyze_clusters()
#     print("\nCluster Analysis:")
#     for cluster_id, info in analysis.items():
#         print(f"Cluster {cluster_id}: {info['size']} reviews, avg rating: {info['avg_rating']:.2f}")
    
#     # Save results
#     clusterer.save_clustered_data("clustered_reviews.json")
#     clusterer.visualize_clusters()
 

# New code Added by rehman 9 Aug 1.29 PM 2025


#!/usr/bin/env python3
"""
scripts/cluster_feedback.py

Usage:
  python3 scripts/cluster_feedback.py \
    --input ./data/mock_data.json \
    --output ./exports/cluster_summaries.json \
    --clusters 5

This:
- Loads JSON list of review objects (expects each object to have 'id' and 'text' keys).
- Cleans & preprocesses text.
- Computes sentence embeddings with sentence-transformers.
- Clusters embeddings (KMeans by default).
- Extracts keywords per cluster using KeyBERT.
- Writes cluster summary JSON to disk.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from keybert import KeyBERT
from tqdm import tqdm

# Ensure NLTK resources (safe to call multiple times)
nltk_packages = ["punkt", "stopwords", "wordnet"]
for pkg in nltk_packages:
    try:
        nltk.data.find(f"tokenizers/{pkg}")  # crude check (works for punkt)
    except Exception:
        nltk.download(pkg)

STOP_WORDS = set(stopwords.words("english"))
LEM = WordNetLemmatizer()

URL_RE = re.compile(r"https?://\S+|www\.\S+")
HTML_RE = re.compile(r"<.*?>")
NON_ALPHA_RE = re.compile(r"[^a-zA-Z\s]")

def clean_text(text: str) -> str:
    if not text:
        return ""
    t = str(text)
    t = URL_RE.sub(" ", t)
    t = HTML_RE.sub(" ", t)
    t = NON_ALPHA_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def preprocess_text(text: str) -> str:
    t = clean_text(text).lower()
    tokens = nltk.word_tokenize(t)
    tokens = [tok for tok in tokens if tok.isalpha() and tok not in STOP_WORDS]
    tokens = [LEM.lemmatize(tok) for tok in tokens]
    return " ".join(tokens)

def load_json(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        return data["data"]
    if isinstance(data, list):
        return data
    raise ValueError("Unsupported JSON structure: expected list or {'data': [...]}")

def main(args):
    inp = Path(args.input)
    outp = Path(args.output)
    outp.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading {inp} ...")
    data = load_json(inp)
    print(f"Loaded {len(data)} items")

    # Extract text safely
    texts = []
    original_texts = []
    ids = []
    for item in data:
        ids.append(item.get("id") or item.get("reviewId") or None)
        # support keys 'text' or 'feedback'
        t = item.get("text") or item.get("feedback") or item.get("review") or ""
        original_texts.append(t)
        texts.append(preprocess_text(t))

    # Embeddings
    print("Loading embedding model...")
    model = SentenceTransformer(args.model)
    print("Encoding texts (this may take a while)...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Clustering (KMeans)
    n_clusters = args.clusters
    print(f"Clustering embeddings into {n_clusters} clusters (KMeans)...")
    clustering_model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = clustering_model.fit_predict(embeddings)

    # Group original (unpreprocessed) texts per cluster
    clusters = {}
    for i, lbl in enumerate(labels):
        clusters.setdefault(int(lbl), []).append(original_texts[i])

    # Keyword extraction
    kw_model = KeyBERT(model)  # uses same model for embeddings
    cluster_summaries = {}
    for cid, feedbacks in clusters.items():
        joined = " ".join(feedbacks)
        # guard if joined is empty
        if not joined.strip():
            keywords = []
        else:
            keywords = kw_model.extract_keywords(joined,
                                                 keyphrase_ngram_range=(1, 2),
                                                 stop_words="english",
                                                 top_n=args.top_n)
            keywords = [kw for kw, score in keywords]
        cluster_summaries[cid] = {
            "cluster_id": cid,
            "feedback_count": len(feedbacks),
            "sample_feedback": feedbacks[: min(len(feedbacks), 5)],
            "keywords": keywords
        }

    # Save JSON
    outp.write_text(json.dumps(cluster_summaries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved cluster summaries to {outp}")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="./data/mock_data.json")
    p.add_argument("--output", "-o", default="./exports/cluster_summaries.json")
    p.add_argument("--clusters", "-k", type=int, default=3)
    p.add_argument("--top-n", "-t", type=int, default=3)
    p.add_argument("--model", default="all-MiniLM-L6-v2")
    args = p.parse_args()
    main(args)
