#!/usr/bin/env python3
"""
Samsung Feedback AI - Problem Summarization Script

This script uses GPT-based models to summarize problems from clustered feedback.
"""

import json
import openai
from collections import Counter
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProblemSummarizer:
    def __init__(self, api_key=None):
        """Initialize with OpenAI API key"""
        if api_key:
            openai.api_key = api_key
        else:
            logger.warning("No OpenAI API key provided. Set OPENAI_API_KEY environment variable.")
        
        self.clustered_reviews = None
        self.summaries = {}
    
    def load_clustered_data(self, filename):
        """Load clustered reviews data"""
        logger.info(f"Loading clustered data from {filename}")
        
        with open(f"../data/{filename}", 'r') as f:
            self.clustered_reviews = json.load(f)
        
        logger.info(f"Loaded {len(self.clustered_reviews)} clustered reviews")
    
    def extract_cluster_texts(self, cluster_id):
        """Extract all texts from a specific cluster"""
        cluster_texts = []
        for review in self.clustered_reviews:
            if review.get('cluster') == cluster_id:
                cluster_texts.append(review.get('cleaned_text', ''))
        
        return cluster_texts
    
    def generate_cluster_summary(self, cluster_id, max_reviews=50):
        """Generate summary for a specific cluster using GPT"""
        cluster_texts = self.extract_cluster_texts(cluster_id)
        
        if not cluster_texts:
            return "No reviews found for this cluster"
        
        # Limit number of reviews to avoid token limits
        if len(cluster_texts) > max_reviews:
            cluster_texts = cluster_texts[:max_reviews]
        
        # Combine texts for analysis
        combined_text = "\n".join(cluster_texts[:20])  # Use first 20 for summary
        
        prompt = f"""
        Analyze the following customer feedback reviews and provide a concise summary of the main problems and issues mentioned:

        Reviews:
        {combined_text}

        Please provide:
        1. Main problem themes (2-3 key issues)
        2. Severity level (High/Medium/Low)
        3. Affected features or components
        4. Brief description of the impact on users

        Format your response as a structured summary.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing customer feedback and identifying key problems."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary for cluster {cluster_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for cluster {cluster_id}: {str(e)}")
            return self.generate_fallback_summary(cluster_texts)
    
    def generate_fallback_summary(self, texts):
        """Generate basic summary without GPT when API is unavailable"""
        if not texts:
            return "No reviews available"
        
        # Simple keyword extraction
        all_words = []
        for text in texts:
            words = text.lower().split()
            all_words.extend(words)
        
        # Get most common words (excluding common stopwords)
        stopwords = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those'}
        filtered_words = [word for word in all_words if word not in stopwords and len(word) > 3]
        
        common_words = Counter(filtered_words).most_common(10)
        
        summary = f"""
        Cluster Summary (Fallback Analysis):
        - Number of reviews: {len(texts)}
        - Common themes: {', '.join([word for word, count in common_words[:5]])}
        - This cluster requires manual review for detailed analysis
        """
        
        return summary
    
    def summarize_all_clusters(self):
        """Generate summaries for all clusters"""
        if not self.clustered_reviews:
            logger.error("No clustered data loaded")
            return
        
        # Get unique cluster IDs
        cluster_ids = set(review.get('cluster', -1) for review in self.clustered_reviews)
        cluster_ids.discard(-1)  # Remove noise cluster
        
        logger.info(f"Generating summaries for {len(cluster_ids)} clusters")
        
        for cluster_id in sorted(cluster_ids):
            cluster_size = sum(1 for review in self.clustered_reviews if review.get('cluster') == cluster_id)
            logger.info(f"Processing cluster {cluster_id} with {cluster_size} reviews")
            
            summary = self.generate_cluster_summary(cluster_id)
            self.summaries[cluster_id] = {
                'cluster_id': cluster_id,
                'size': cluster_size,
                'summary': summary
            }
    
    def generate_overall_summary(self):
        """Generate an overall summary of all problems"""
        if not self.summaries:
            logger.error("No cluster summaries available")
            return
        
        # Combine all cluster summaries
        all_summaries = [info['summary'] for info in self.summaries.values()]
        combined_summaries = "\n\n".join(all_summaries)
        
        prompt = f"""
        Based on the following cluster summaries of customer feedback, provide an executive summary of the main problems affecting Samsung products:

        Cluster Summaries:
        {combined_summaries}

        Please provide:
        1. Top 5 critical issues that need immediate attention
        2. Overall sentiment analysis
        3. Priority recommendations for product improvement
        4. Estimated impact on customer satisfaction

        Keep the summary concise and actionable.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a product manager analyzing customer feedback to identify critical issues."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            overall_summary = response.choices[0].message.content.strip()
            logger.info("Generated overall summary")
            return overall_summary
            
        except Exception as e:
            logger.error(f"Error generating overall summary: {str(e)}")
            return "Overall summary generation failed. Please review individual cluster summaries."
    
    def save_summaries(self, filename):
        """Save all summaries to JSON file"""
        if not self.summaries:
            logger.error("No summaries to save")
            return
        
        # Add overall summary
        overall_summary = self.generate_overall_summary()
        
        output_data = {
            'overall_summary': overall_summary,
            'cluster_summaries': self.summaries,
            'total_clusters': len(self.summaries),
            'total_reviews': len(self.clustered_reviews) if self.clustered_reviews else 0
        }
        
        with open(f"../data/{filename}", 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Saved summaries to {filename}")
    
    def print_summaries(self):
        """Print summaries to console"""
        if not self.summaries:
            logger.error("No summaries available")
            return
        
        print("\n" + "="*80)
        print("SAMSUNG FEEDBACK ANALYSIS - PROBLEM SUMMARIES")
        print("="*80)
        
        for cluster_id, info in sorted(self.summaries.items()):
            print(f"\nCLUSTER {cluster_id} ({info['size']} reviews):")
            print("-" * 50)
            print(info['summary'])
        
        print("\n" + "="*80)
        print("OVERALL SUMMARY:")
        print("="*80)
        overall = self.generate_overall_summary()
        print(overall)

if __name__ == "__main__":
    import os
    
    # Initialize summarizer
    api_key = os.getenv('OPENAI_API_KEY')
    summarizer = ProblemSummarizer(api_key)
    
    # Load and process data
    summarizer.load_clustered_data("clustered_reviews.json")
    summarizer.summarize_all_clusters()
    
    # Save and display results
    summarizer.save_summaries("problem_summaries.json")
    summarizer.print_summaries()
